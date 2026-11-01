// Actual composed handlers, CLI, settings and execution dependencies over RAM mocks.
#include "right_modifiers_parent_cases.inc"
#include "nvs_fixture.h"
#include "nvs.h"

static const std::string oldAp(16, 'p'), oldWeb(16, 'w');
static const std::string newAp = "Synthetic AP 123", newWeb = "Synthetic Web 456";
static std::string privacyOutput;
static void privacyPrint(const char *text) { if (text) privacyOutput += text; }
static std::string bytes(const String &text) { return std::string(text.c_str(), text.length()); }
static void noSecrets(const std::string &text, const std::vector<std::string> &extra = {}) {
  for (const auto &value : {oldAp, oldWeb, newAp, newWeb})
    check(text.find(value) == std::string::npos, "response omits synthetic credential values");
  for (const auto &value : extra)
    if (!value.empty()) check(text.find(value) == std::string::npos, "response omits supplied replacement");
}
static void passwords(const std::string &ap, const std::string &web) {
  check(bytes(settings::getPassword()) == ap && bytes(settings::getWebPassword()) == web,
        "actual settings retain expected credential values");
  check(nvsMock::persistedString("ap_password") == ap && nvsMock::persistedString("web_pw") == web,
        "recorded persisted credential values agree");
}
static void reload(const std::string &ap, const std::string &web) {
  settings::load();
  check(settings::ready(), "actual typed settings reload succeeds");
  passwords(ap, web);
}
static void saved(AsyncWebServerRequest &request, const std::string &ap, const std::string &web) {
  auto before = nvsMock::commits;
  handleSaveSettings(&request);
  check(request.code == 200 && request.replies == 1 && nvsMock::commits == before+1,
        "one successful settings response and checked commit");
  noSecrets(bytes(request.response), {ap, web});
  passwords(ap, web);
  reload(ap, web);
}
static void command(const std::string &input, bool echo) {
  privacyOutput.clear();
  cli::parse(input.c_str(), privacyPrint, echo);
}
static void cliSaved(const std::string &input, bool echo,
                     const std::string &ap, const std::string &web) {
  auto before = nvsMock::commits;
  command(input, echo);
  check(nvsMock::commits == before+1 && settings::saveError() == ESP_OK,
        "credential CLI command performs checked save");
  check(!privacyOutput.empty(), "CLI acknowledges result");
  noSecrets(privacyOutput, {ap, web});
  passwords(ap, web);
  reload(ap, web);
}
static void invalidHttp(const char *field, const std::string &value) {
  auto request = req();
  request.body["ssid"] = {"must-not-apply"};
  request.body[field] = {String(value)};
  const auto beforeWrites = nvsMock::writes, beforeCommits = nvsMock::commits;
  const auto beforeSsid = settings::getSSID();
  handleSaveSettings(&request);
  check(request.code == 400 && request.replies == 1, "invalid replacement explicitly rejected");
  check(nvsMock::writes == beforeWrites && nvsMock::commits == beforeCommits,
        "invalid replacement writes no NVS keys");
  check(settings::getSSID() == beforeSsid, "replacement validation precedes other setters");
  noSecrets(bytes(request.response), {value});
  passwords(oldAp, oldWeb);
}
static void invalidCli(const std::string &name, const std::string &value, bool echo) {
  const auto beforeWrites = nvsMock::writes, beforeCommits = nvsMock::commits;
  command("  SeT " + name + " \"" + value + "\"  ", echo);
  check(nvsMock::writes == beforeWrites && nvsMock::commits == beforeCommits,
        "invalid CLI replacement writes nothing");
  check(privacyOutput.find("Invalid") != std::string::npos, "CLI reports invalid replacement");
  noSecrets(privacyOutput, {value});
  passwords(oldAp, oldWeb);
}

int main(int argc, char **argv) {
  if (argc != 2) return 2;
  if (std::strncmp(argv[1], "PF", 2)) return right_modifiers_main(argc, argv);
  try {
    nvsMock::reset(); mscMock::reset(); mock::reset(); setup();
    check(startupControlledReady && settings::ready() && route_u::bindOwner(),
          "actual composed controlled startup and owner bind");
    lower::reset(); led_mock::nowUs = 0; rng_mock::reset();
    const std::string id = argv[1];
    auto request = req();
    if (id == "PF01") {
      const auto writes = nvsMock::writes;
      handleGetSettings(&request);
      check(request.code == 200 && request.replies == 1, "authenticated settings GET succeeds once");
      const auto result = bytes(request.response);
      noSecrets(result);
      check(result.find("\"password\":") == std::string::npos &&
            result.find("\"web_password\":") == std::string::npos, "raw password fields are absent");
      check(result.find("\"password_configured\":true") != std::string::npos &&
            result.find("\"web_password_configured\":true") != std::string::npos,
            "only nonsecret configured flags represent credentials");
      check(result.find("\"channel\":1") != std::string::npos && nvsMock::writes == writes,
            "other settings remain available and GET performs no writes");
    } else if (id == "PF02") {
      for (bool wrong : {false, true}) {
        auto denied = req(); denied.headers.clear();
        if (wrong) denied.headers["X-Duck-Password"] = "incorrect-synthetic-auth";
        handleGetSettings(&denied);
        check(denied.code == 401 && denied.replies == 1, "unauthorized settings GET denied");
        noSecrets(bytes(denied.response));
        denied = AsyncWebServerRequest{};
        if (wrong) denied.headers["X-Duck-Password"] = "incorrect-synthetic-auth";
        denied.body["password"] = {newAp}; denied.body["web_password"] = {newWeb};
        const auto writes = nvsMock::writes;
        handleSaveSettings(&denied);
        check(denied.code == 401 && denied.replies == 1 && nvsMock::writes == writes,
              "unauthorized replacement denied before writes");
        noSecrets(bytes(denied.response)); passwords(oldAp, oldWeb);
      }
    } else if (id == "PF03") {
      request.body["channel"] = {"6"};
      saved(request, oldAp, oldWeb);
      check(settings::getChannel() == 6, "unrelated save remains effective through reload");
    } else if (id == "PF04") {
      request.body["password"] = {""}; request.body["web_password"] = {""};
      request.body["channel"] = {"11"};
      saved(request, oldAp, oldWeb);
      check(settings::getChannel() == 11, "explicit empty replacements preserve passwords");
    } else if (id == "PF05") {
      request.body["password"] = {newAp}; saved(request, newAp, oldWeb);
    } else if (id == "PF06") {
      request.body["web_password"] = {newWeb}; saved(request, oldAp, newWeb);
    } else if (id == "PF07") {
      request.body["password"] = {newAp}; request.body["web_password"] = {newWeb};
      saved(request, newAp, newWeb);
    } else if (id == "PF08") {
      const std::string nul = std::string("Valid123") + char(0) + "suffix";
      for (const auto &value : std::vector<std::string>{"short", std::string(64, 'a'), nul,
             "Valid123\nSecret", "Valid123\rSecret", WIFI_PASSWORD}) invalidHttp("password", value);
    } else if (id == "PF09") {
      const std::string nul = std::string("ValidWeb") + char(0) + "suffix";
      for (const auto &value : std::vector<std::string>{std::string(4000, 'b'), nul,
             "ValidWeb\nSecret", "ValidWeb\rSecret"}) invalidHttp("web_password", value);
      // A valid AP replacement must not precede rejection of the other field.
      request.body["password"] = {newAp}; request.body["web_password"] = {"bad\nweb"};
      const auto writes = nvsMock::writes;
      handleSaveSettings(&request);
      check(request.code == 400 && nvsMock::writes == writes, "both replacements validated before setters");
      passwords(oldAp, oldWeb); noSecrets(bytes(request.response));
    } else if (id == "PF10") {
      for (const auto &pair : std::vector<std::pair<std::string, std::string>>{
              {std::string(8, 'a'), "x"}, {std::string(63, 'c'), std::string(3999, 'd')}}) {
        auto bounds = req(); bounds.headers["X-Duck-Password"] = settings::getWebPassword();
        bounds.body["password"] = {pair.first}; bounds.body["web_password"] = {pair.second};
        saved(bounds, pair.first, pair.second);
      }
    } else if (id == "PF11" || id == "PF12" || id == "PF13") {
      request.body["password"] = {newAp}; request.body["web_password"] = {newWeb};
      const auto writes = nvsMock::writes, commits = nvsMock::commits;
      if (id == "PF11") nvsMock::fail = true;
      if (id == "PF12") nvsMock::failWriteAt = writes+5;
      if (id == "PF13") nvsMock::failCommit = true;
      handleSaveSettings(&request);
      check(request.code == 503 && request.replies == 1, "save error remains explicit");
      check(bytes(request.response).find("partial persistence possible") != std::string::npos,
            "error does not fabricate atomic rollback");
      noSecrets(bytes(request.response));
      if (id == "PF11") {
        check(nvsMock::writes == writes && nvsMock::commits == commits, "open failure writes nothing");
        check(nvsMock::persistedString("ap_password") == oldAp && nvsMock::persistedString("web_pw") == oldWeb,
              "open failure leaves persisted credentials unchanged");
      } else if (id == "PF12") {
        check(nvsMock::writes == writes+5 && nvsMock::commits == commits,
              "setter error stops at first failing set");
        check(nvsMock::persistedString("ap_password") == newAp && nvsMock::persistedString("web_pw") == oldWeb,
              "fixture exposes possible prefix persistence");
      } else {
        check(nvsMock::writes == writes+12 && nvsMock::commits == commits+1,
              "commit error follows all checked setters");
        check(nvsMock::persistedString("ap_password") == newAp && nvsMock::persistedString("web_pw") == newWeb,
              "fixture does not invent rollback after commit error");
      }
      nvsMock::fail = nvsMock::failCommit = false; nvsMock::failWriteAt = 0;
      reload(id == "PF11" ? oldAp : newAp, id == "PF13" ? newWeb : oldWeb);
    } else if (id == "PF14") {
      for (bool echo : {false, true}) {
        const auto writes = nvsMock::writes; command("settings", echo);
        noSecrets(privacyOutput);
        check(privacyOutput.find("password_configured=1") != std::string::npos &&
              privacyOutput.find("web_password_configured=1") != std::string::npos,
              "CLI reports nonsecret configured flags");
        check(privacyOutput.find("password=") == std::string::npos &&
              privacyOutput.find("web_password=") == std::string::npos && nvsMock::writes == writes,
              "CLI readback omits raw credential fields and writes nothing");
      }
    } else if (id == "PF15") {
      cliSaved("set password \""+newAp+"\"", false, newAp, oldWeb);
      cliSaved("set web_password \""+newWeb+"\"", false, newAp, newWeb);
    } else if (id == "PF16") {
      cliSaved("  SeT   PaSsWoRd   \""+newAp+"\"   ", true, newAp, oldWeb);
      cliSaved("  SeT   WeB_PaSsWoRd   \""+newWeb+"\"   ", true, newAp, newWeb);
      check(privacyOutput.find("# set [value omitted]") != std::string::npos,
            "public echo API redacts raw setting input");
    } else if (id == "PF17") {
      const std::string value = "Synthetic SSID private text";
      const std::string input = "  SeT ssid \""+value+"\"  ";
      command(input, true);
      check(settings::getSSID() == value && settings::saveError() == ESP_OK, "nonsecret settings still update");
      noSecrets(privacyOutput, {value});
      check(privacyOutput.find(input) == std::string::npos, "generic settings input is not echoed");
      passwords(oldAp, oldWeb);
    } else if (id == "PF18") {
      for (bool echo : {false, true}) for (const char *name : {"password", "web_password"}) {
        const auto writes = nvsMock::writes, commits = nvsMock::commits;
        command(std::string("set ")+name+" \"\"", echo);
        check(nvsMock::writes == writes && nvsMock::commits == commits,
              "empty CLI replacement is a no-write operation");
        check(privacyOutput.find("unchanged") != std::string::npos, "empty CLI replacement clearly keeps value");
        noSecrets(privacyOutput); passwords(oldAp, oldWeb);
      }
    } else if (id == "PF19") {
      for (bool echo : {false, true}) for (const auto &value : std::vector<std::string>{
          "short", std::string(64, 'a'), "Valid123\nSecret", "Valid123\rSecret", WIFI_PASSWORD})
        invalidCli("PaSsWoRd", value, echo);
    } else if (id == "PF20") {
      for (bool echo : {false, true}) for (const auto &value : std::vector<std::string>{
          std::string(4000, 'b'), "ValidWeb\nSecret", "ValidWeb\rSecret"})
        invalidCli("WeB_PaSsWoRd", value, echo);
    } else if (id == "PF21" || id == "PF22") {
      for (const char *name : {"password", "web_password"}) {
        const auto writes = nvsMock::writes, commits = nvsMock::commits;
        if (id == "PF21") nvsMock::fail = true;
        else nvsMock::failWriteAt = writes+5;
        command(std::string("set ")+name+" \""+newAp+"\"", true);
        check(privacyOutput.find("Settings save failed; partial persistence possible") != std::string::npos,
              "CLI failure remains truthful and explicit");
        noSecrets(privacyOutput);
        check(nvsMock::commits == commits, "failed CLI save never commits");
        check(nvsMock::writes == writes+(id == "PF21" ? 0u : 5u), "CLI write failure stops correctly");
        nvsMock::fail = false; nvsMock::failWriteAt = 0;
        settings::load(); check(settings::ready(), "failure fixture can reload its actual persisted prefix");
      }
    } else if (id == "PF23") {
      nvsMock::failCommit = true;
      command("set web_password \""+newWeb+"\"", true);
      check(nvsMock::commits == 1 && privacyOutput.find("partial persistence possible") != std::string::npos,
            "CLI checked commit failure is not suppressed");
      noSecrets(privacyOutput);
      nvsMock::failCommit = false; reload(oldAp, newWeb);
    } else if (id == "PF24") {
      serialMock::output.clear();
      serialMock::set("settings\nset password \""+newAp+"\"\n"); readAll();
      noSecrets(serialMock::output);
      check(serialMock::output.find("password_configured=1") != std::string::npos,
            "real bounded serial path uses redacted settings output");
      reload(newAp, oldWeb);
      serialMock::output.clear();
      serialMock::set(std::string("set password short")+char(0)+"hidden\n"); readAll();
      check(serialMock::output.find("line rejected") != std::string::npos,
            "serial embedded NUL still rejects complete line");
      noSecrets(serialMock::output); passwords(newAp, oldWeb);
    } else if (id == "PF25") {
      for (unsigned failure = 0; failure < 3; ++failure) {
        auto unrelated = req(); unrelated.body["channel"] = {"6"};
        if (failure == 0) nvsMock::fail = true;
        if (failure == 1) nvsMock::failWriteAt = nvsMock::writes+5;
        if (failure == 2) nvsMock::failCommit = true;
        handleSaveSettings(&unrelated);
        check(unrelated.code == 503, "unrelated save still reports injected failure");
        noSecrets(bytes(unrelated.response)); passwords(oldAp, oldWeb);
        nvsMock::fail = nvsMock::failCommit = false; nvsMock::failWriteAt = 0;
        reload(oldAp, oldWeb);
      }
    } else if (id == "PF26") {
      for (const char *input : {"set channel 6", "set disable_led 1", "set hidden_ap 1"}) {
        cliSaved(input, true, oldAp, oldWeb);
      }
    } else if (id == "PF27") {
      request.body["password"] = {newAp}; request.body["web_password"] = {newWeb};
      saved(request, newAp, newWeb);
      auto current = req(); current.headers["X-Duck-Password"] = newWeb;
      handleGetSettings(&current);
      check(current.code == 200, "new password authenticates after replacement");
      noSecrets(bytes(current.response));
      command("settings", true); noSecrets(privacyOutput);
      auto oldAuth = req(); handleGetSettings(&oldAuth);
      check(oldAuth.code == 401, "old password is not silently retained for authentication");
    } else if (id == "PF28") {
      request.body["password"] = {""}; request.body["web_password"] = {newWeb};
      saved(request, oldAp, newWeb);
      auto second = req(); second.headers["X-Duck-Password"] = newWeb;
      second.body["password"] = {newAp}; second.body["web_password"] = {""};
      saved(second, newAp, newWeb);
    } else check(false, "unknown privacy case");
    check(lower::count == 0 && !route_u::owned(), "privacy cases generate no HID output or execution request");
    std::cout << "PASS " << id << " (" << assertions << " assertions)\n";
    return 0;
  } catch (const std::exception &error) {
    std::cerr << "FAIL " << argv[1] << ": " << error.what() << " (" << assertions << ")\n";
    return 1;
  }
}
