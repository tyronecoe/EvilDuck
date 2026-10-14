# Stage28J integration dependencies and memory ledger

This is a source-backed proposal dependency map, not an integrated build. All source is unchanged from exact Stage28I commit `220970bc633d969e76d1d8c91750b5939377df0a`. The 19 audited seams are not 19 observed physical bugs. Source facts below are CONFIRMED within the inspected boundary; selecting an architectural response is a PROPOSED CHOICE. Device behavior and linked transport semantics remain UNKNOWN where stated.

## Contract dependencies

| Future contract / decision | Concrete unchanged source evidence | Dependency / risk | Required missing evidence |
|---|---|---|---|
| Sole snapshot authority D01 | `language_preview/keyboard.cpp:11–20,29–48`; `EvilDuckS3/hid_backend.cpp:272–318` | Planner unions four owners; backend unions its global ledger with transient input. Snapshot replacement cannot be implemented by calling a merging helper | Mock no-double-merge and exclusive-path journal; later explicit production transport authority review |
| Admission and Accepted D02 | `language_preview/bridge.cpp:43–61,71–84`; `EvilDuckS3/com.cpp:434–451`; `hid_backend.cpp:254–261` | Command admission, queue API return and Bridge source ack are separate; bool false conflates some readiness/failure conditions | Accepted/Retry/Failed taxonomy with no acceptance on known refusal; actual linked library copy/lifetime semantics before a real mapping |
| Current identity D03 | `language_preview/bridge.h:14–46`; protected `libraries/USB/src/USBHID.cpp:331–335,337–373` | Bridge has no asynchronous token; core completion wakes a global semaphore, not a per-intent callback. Raw firmware route bypasses SendReport mutex/wait | Future wrapper IDs, stale events and duplicate ack rejection; independent token-bearing transport design before completion mode |
| Serialization D04 | `language_preview/bridge.cpp:39–41,71–72`; `EvilDuckS3/execution_guard.h:28–50`; `webserver.cpp:549–566,573–585`; `cli.cpp:193–207` | Bridge guards reentrancy, not cross-thread safety. Production Guard can block indefinitely; USB callbacks must not wait behind filesystem work | One stepping owner and bounded requests; explicit overflow/STOP priority, callback cancellation ordering and lock graph. No new RTOS worker here |
| Neutral/cancel/drain D05 | `language_preview/keyboard.cpp:67–83`; `bridge.cpp:62–92`; `EvilDuckS3/hid_backend.cpp:332–353` | Current explicit drain versus automatic backend release retry; previous zero may remain historical evidence | Fresh R receipt and restart barrier tests; reconnect does not prove neutral. Host delivery never follows from a mock receipt |
| Report ID / protocol D06 | `language_preview/keyboard.h:5–20`; `EvilDuckS3/hid_backend.cpp:12–22,254–261`; protected `libraries/USB/src/USBHIDKeyboard.cpp:33–46`, `USBHID.h:75`, `USBHID.cpp:282–290,348–362` | Planner has eight bytes without protocol/ID. Backend uses ID 1 directly; core wrapper conditionally uses ID 0 in boot protocol. Constructor once-only setup makes current protocol nontrivial | Actual linked constructor/descriptor/driver inventory and protocol negotiation evidence; no speculative descriptor changes or claim of a physical defect |
| Clock and step budget D04/D07 | `language_preview/core.h:6–9`, `core.cpp:462–477`; `bridge.cpp:71–84`; `EvilDuckS3/com.cpp:105–129,526–560,602–611` | Preview's caller clock and 30-second overall ceiling differ from production dwell, jitter/default delays. Stacking both creates double timing | One timing authority, small-wrap/deadline/refusal fixtures, no blocking waits; later fairness evidence separate from object frame data |
| Source/preflight D07 | `language_preview/core.h:37–92`; `core.cpp:382–426`; `EvilDuckS3/duckscript.cpp:276–397`; `script_source.h:12–32`, `script_source.cpp:7–75`; `storage.cpp:208–220` | Exact-size raw-byte Reader with Retry/seek versus File-based line Reader. Compiled IR/text versus streamed execution; source fingerprint is not authentication | Memory-only stable bytes/read/seek/removal simulations; later actual File mapping separately approved; failed compilation must never start Program |
| Capacity D07 | `language_preview/core.h:6–9`; `EvilDuckS3/config.h:12–53` | Preview source 8192 B, line 256 B, 128 IR, 4096 text; production source 256 KiB and line 512 B. Streaming does not expand fixed IR | Explicit subset admission and boundary tests; no replacement/widening by implication |
| Arithmetic/locale/extensions D08 | `language_preview/core.cpp:113–127`; `EvilDuckS3/duck_expr.cpp:135–165`; `language_preview/keyboard.cpp:55–66`; `EvilDuckS3/keyboard_locale.h:7–16`, `keyboard_locale.cpp:28–105`, `com.cpp:198–225,569–577`; Stage28F/G contracts | Checked arithmetic differs from uint16 modular policy; US model bypasses DE/UTF8/dead-key handling. Firmware engineering policy is not canonical reference proof | Explicit differences accepted before opt-in use; source modifier/INJECT_MOD/RESET remain BLOCKED; future independent oracle and locale review |
| Errors and diagnostics D07/D09 | `language_preview/core.h:11–16`; `core.cpp:415–426,482–485`; `EvilDuckS3/duckscript.cpp:68–79,341–344` | Typed code/physical location needs stable filename/UI lifetime; source and credentials must not leak through diagnostics | Sanitized error mapping, preflight/runtime/transport distinction, bounded location storage; no owner data tested |
| Startup and update D10 | `EvilDuckS3/EvilDuckS3.ino:37–123`; `deployment_boot.h:3–20`; `settings.cpp:52–64,125–177`; `spiffs.cpp:20–27`; `webserver.cpp:369–388,685–695` | Safe profile returns before application services; controlled profile strict/noformat/noautorun differs from legacy. Settings saves remain non-atomic; OTA is app-only | Explicit opt-in entry and concurrent submission refusal; independent physical recovery/install approval. No new startup or OTA route now |
| Toolchain/layout/coexistence D06/D10 | `tools/s3_validation.py:14–43`; `tools/build_s3_patched.py:18–31`; `EvilDuckS3/attackmode.cpp:10–42`; frozen `partitions.csv` | Pinned 3.3.0/ESP-IDF 5.5, QIO 80 MHz, CPU 240 MHz, PSRAM disabled, USB-OTG/CDC; dual 0x740000 slots and app0 0x10000 unchanged. Requested MSC is not host-visible activation proof | Future linked inventory and independently authorized device/profile evidence; no new firmware or partition artifact |

`stage28j-source-evidence.json` preserves the Stage28I 35 repository / five dependency anchors with exact file and span SHA-256. It additionally records direct hashes/line spans for Bridge API, task guards, raw sink, target flag sources, partition CSV and the authoritative reference contracts. Reproduction verifies actual files, not just prior receipts. The pinned core and SDK locations below are existing cloud sources, not installation instructions for the Mac.

## Transparent memory / lifetime ledger

Fresh Xtensa **OBJECT-ONLY** evidence uses the same pins and produces unchanged sizes and module hashes relative to Stage28I. These are object/compiler observations, not free RAM, firmware headroom or physical stack measurements.

| Item | Known target bytes | Lifetime / accounting policy proposed | Still unknown |
|---|---:|---|---|
| Program | 6936 | Noncopyable owner retains through Runtime observation/diagnostics; compile cannot mutate borrowed Program | Placement alongside production context; source buffer and UI peak |
| CompileSession | 2408 | Own once during bounded compile; cancel/terminal detaches; Reader source/context valid until terminal | Reader/file/cache allocations, compiler call-stack peak |
| Compiler | 2312 | **Contained** in CompileSession's placement storage, not another persistent object | Whole compile stack/callback chain |
| Bridge | 5020 | Own once; context and Program lifetimes cover callbacks, terminal diagnostics and explicit drain | Future wrapper/journal/queue sizes |
| Runtime | 4872 | **Contained** in Bridge; do not add again | Runtime stack/callback/task scheduling interaction |
| Planner | 84 | **Contained** in Bridge; do not add again | Future transport context and asynchronous state |
| Program + CompileSession + Bridge | **14,364** | Sum of independent objects only; no complete integration budget claim | Existing executor coexistence, peak heap, task stack, UI and drivers |
| Reader / MemoryReader | 16 / 12 | Optional standalone synthetic callback/context objects, only if actually instantiated separately | Production File mapping and storage buffers |
| Event / Report / Instruction / BridgeDiagnostic | 4 / 8 / 12 / 14 | Type sizes, often already embedded in above objects; not an additive bag of globals | Future journal count and immutable snapshot copies |
| Session/action journal and request handoff | UNKNOWN | Proposed fixed-size metadata; no dynamic queue; choose capacity before any harness | Counter/record count, allocation placement, saturation policy |
| Existing RunState / com Session / String / File / UI / USB and task stacks | UNKNOWN peak | Existing contexts may coexist; no assumption they disappear or can be double-used | Whole integration linker/map, measured allocation peak and later physical high-water |

Selected unchanged compiler stack frames: Runtime tick 112 B, expression preparation 144 B, ownership proposal 96 B, Bridge step 32 B and start 48 B. They are individual frames, not a summed callgraph or task-stack requirement. Object text/literal/rodata: core 13292/1892/1838 B; keyboard 2181/168/47 B; bridge 1586/180/0 B; each data/BSS 0/0. That does not make instantiated objects free and cannot predict linked application/OTA growth.

No production firmware was compiled/linked, so production heap, latency, stack high-water and OTA capacity are **NOT MEASURED**. No new allocation behavior exists: only documents and a read-only evidence checker were added. Stage28K must budget wrapper metadata separately and explain its lifetime without counting Bridge members twice.

## Exact provenance boundary

Existing protected core tree SHA-256: `81c11f59e01c1e6263d387a008d3f3211319d94feb4751ddfa11af35a2a57ed3`.
Pinned compiler SHA-256: `d968578945d9f62c2769e03a786d8853eb0ba226cfff1e8ee6588550927941a3`.
SDK NVS archive SHA-256: `a1ac62b0f8b69ef2ac08e82dd1c57f58d53db74147bc309f070e36a148067a2e`.
SDK config SHA-256: `06fcb22dee7956d54f1c7c05b0856ee87a362380697071fef2c26753fb14c271`.
Full USB/NVS patch/source pins, selected frames, module/metadata object hashes and compile commands are in `stage28j-target-build.json`. No core/SDK patch application or replacement took place.

The pinned TinyUSB `include/arduino_tinyusb/tinyusb/src/class/hid/hid_device.h:63–68` declares `tud_hid_n_report`; that declaration does not execute or prove the shipped library's transfer/copy behavior. No linked ELF/callback/constructor audit was performed in this stage. Such evidence is a future integration-design prerequisite, not a reason to generate prohibited firmware now.
