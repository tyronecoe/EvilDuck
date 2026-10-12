// Execute pinned SDK Storage/Page components on synthetic flash only.
// Reuse Stage 19's bounded partition, CRC implementation and assertion helper.
#define main stage19_recovery_main
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#include "../stage19/sdk_recovery.cpp"
#pragma GCC diagnostic pop
#undef main
#include <filesystem>
#include <fstream>

static void boundedOperations(const Flash& flash) {
    for (const auto& op : flash.ops) {
        check(op.address >= 0x9000 && op.address <= 0xe000
              && op.bytes <= 0xe000 - op.address, "synthetic operation inside NVS");
    }
}

static unsigned indexVersion(const Flash& flash) {
    unsigned found = 0;
    unsigned version = 0xffff;
    for (unsigned page = 0; page < 5; ++page) {
        for (unsigned entry = 0; entry < 126;) {
            const size_t address = page * 4096 + 64 + entry * 32;
            const unsigned state = (flash.data[page * 4096 + 32 + entry / 4]
                                    >> ((entry % 4) * 2)) & 3;
            if (state != 2) { ++entry; continue; }
            const unsigned span = flash.data[address + 2];
            check(span != 0 && span <= 126 - entry, "SDK-written span bounded");
            if (flash.data[address + 1] == static_cast<unsigned>(nvs::ItemType::BLOB_IDX)) {
                ++found;
                version = flash.data[address + 29];
            }
            entry += span;
        }
    }
    check(found == 1, "exactly one live blob index after SDK update");
    return version;
}

int main(int argc, char** argv) {
    try {
        check(argc == 3, "case and fresh output image required");
        const std::string name = argv[1];
        const bool update = name == "sdk_blob_update33" || name == "sdk_blob_update4000";
        const size_t bytes = name == "sdk_blob_0" ? 0 :
                             (name == "sdk_blob_33" || name == "sdk_blob_update33") ? 33 :
                             (name == "sdk_blob_4000" || name == "sdk_blob_update4000") ? 4000 :
                             name == "sdk_blob_8000" ? 8000 : 0xffff;
        check(bytes != 0xffff, "known synthetic case");
        check(!std::filesystem::exists(argv[2]), "output image must not exist");
        Flash flash;
        uint8_t namespaceIndex = 0;
        std::vector<uint8_t> value(bytes);
        for (size_t index = 0; index < bytes; ++index)
            value[index] = static_cast<uint8_t>((index * 37 + 11) % 251);
        {
            nvs::Storage writer(&flash);
            check(writer.init(0, 5) == ESP_OK, "initialize synthetic empty partition");
            check(writer.createOrOpenNamespace("synthetic", true, namespaceIndex) == ESP_OK,
                  "create synthetic namespace");
            check(writer.writeItem(namespaceIndex, nvs::ItemType::BLOB, "fixture",
                                   value.data(), value.size()) == ESP_OK, "SDK writes synthetic blob");
            check(indexVersion(flash) == 0, "first blob generation zero");
            if (update) {
                for (auto& byte : value) byte ^= 0x5a;
                check(writer.writeItem(namespaceIndex, nvs::ItemType::BLOB, "fixture",
                                       value.data(), value.size()) == ESP_OK, "SDK replaces synthetic blob");
                check(indexVersion(flash) == 0x80, "replacement blob generation 0x80");
            }
        }
        boundedOperations(flash);
        for (const auto& operation : flash.ops)
            std::cout << "PREP_OP " << operation.kind << " " << operation.address << " "
                      << operation.bytes << " " << operation.success << "\n";
        flash.ops.clear();
        flash.writes = flash.erases = 0;
        const auto before = flash.data;
        {
            nvs::Storage reader(&flash);
            check(reader.init(0, 5) == ESP_OK, "reinitialize healthy SDK-written blob");
            check(flash.data == before && flash.ops.empty(), "healthy initialization no mutation");
            check(reader.createOrOpenNamespace("synthetic", false, namespaceIndex) == ESP_OK,
                  "open existing synthetic namespace read-only");
            size_t actual = 0;
            check(reader.getItemDataSize(namespaceIndex, nvs::ItemType::BLOB, "fixture", actual) == ESP_OK,
                  "SDK reads blob length");
            check(actual == value.size(), "SDK blob length preserved");
            std::vector<uint8_t> recovered(bytes);
            check(reader.readItem(namespaceIndex, nvs::ItemType::BLOB, "fixture",
                                  recovered.data(), recovered.size()) == ESP_OK,
                  "SDK reads synthetic blob");
            check(recovered == value, "SDK read exact synthetic bytes");
            check(reader.init(0, 5) == ESP_OK, "repeat healthy SDK initialization");
            check(flash.data == before && flash.ops.empty() && flash.writes == 0 && flash.erases == 0,
                  "healthy reads and repeated initialization no writes or erases");
        }
        check(flash.data == before && flash.ops.empty(), "SDK teardown no mutation");
        boundedOperations(flash);
        std::ofstream image(argv[2], std::ios::binary | std::ios::out);
        check(image.good(), "create disposable synthetic image");
        image.write(reinterpret_cast<const char*>(flash.data.data()), flash.data.size());
        image.close();
        check(image.good() && std::filesystem::file_size(argv[2]) == 0x5000,
              "synthetic image exact size");
        std::cout << "PASS " << name << " (" << assertions << " assertions)\n";
    } catch (const std::exception& error) {
        std::cerr << error.what() << '\n';
        return 1;
    }
}
