# Stage 24 fresh provisioning contract — offline review only

No installation, physical format, flash, erase or OTA is authorized. Exact old firmware,
NVS/settings/scripts/filesystem preservation is optional; existing backups stay untouched.
Stock recovery is owner-provided and must be verified later. No stock-image search occurred.

## Selected architecture

Prepare complete fresh images offline, before any future separately reviewed installation.
Do not introduce runtime namespace provisioning or automatic repair. This avoids pretending
multi-key NVS commits are atomic. A complete generated image has all existing typed keys;
repeated preparation in new output directories yields identical bytes for identical inputs.
The existing settings schema is unchanged; no runtime version or commit marker is invented.

The future writable fresh NVS image is exactly 0x5000 bytes for offset 0x9000. Its `duck`
namespace has explicit owner SSID/AP password/web password, channel 1, autorun false,
empty autorun path, zero delay bounds, stealth/hidden/LED-disable false and the existing
0x28 idle LED color. These non-secret defaults match healthy settings behavior. Credentials
have no defaults: the private input must explicitly specify all three fields and a nonempty
web password. Nothing is uploaded or committed. NVS generation uses source-pinned official
format tooling, then checks structural compatibility and exact size.

This is an OFFLINE fresh writable review resource, incompatible with the readonly candidate.
The candidate never imports this tool, mounts media or provisions settings. Existing protected
migration planners remain unchanged and reject writes to NVS. A future fresh-install write
plan would require its own explicit NVS-range authorization; these images are not such a plan.

## Settings states and application behavior

| State | Verified existing behavior / required policy |
|---|---|
| Generated healthy settings | Real settings source reads through selected real SDK components; autorun stays false, no startup settings setters/commit |
| Blank writable NVS | SDK may initialize page metadata; this is legitimate fresh-region mutation, not immutability. Missing `duck` uses in-memory legacy defaults without settings writes |
| Missing keys | Existing typed loader uses per-key in-memory defaults; it is not a complete factory-image certification |
| Invalid type/value or read failure | Existing error latch stops application services; no automatic repair or save |
| Full NVS, write/commit failure | Existing checked save reports first error; partial multi-key persistence remains possible; no rollback guarantee |
| Unsupported SDK format | Initialization can fail/recover under ordinary writable SDK rules; Arduino whole-partition auto-erase stays disabled |
| Readonly partition | SDK rejects ordinary writes; quiescent candidate never loads application settings; no writable retry |
| Interrupted offline generation | No validated publication; temporary input disappears; no owner image overwritten |
| Interrupted publication | Partial new private directory may remain. Missing inventory fails verification; destination cannot be reused automatically |

The legacy missing-namespace defaults include a known AP credential and empty web password.
Empty web password bypasses existing authentication. This stage does not silently change
normal behavior or weaken authentication. Those defaults are NOT an approved fresh-deployment
configuration. Full semantic certification of arbitrary owner-generated NVS images is still
a deployment gate; structural compatibility alone is insufficient. The mock SDK startup test
checks the generated synthetic factory image, not owner files or a complete target boot.

## SPIFFS

Fresh SPIFFS is 0x160000 bytes at 0xE90000, block 4096/page 256 and pinned mkspiffs 0.2.3
configuration. It contains zero files and no owner/bundled payload. Generation unpacks and
checks every file (empty set), exact size and capacity. Repeated builds across different
seconds match. An earlier file sentinel proved timestamp-dependent and would not prevent
the production library installer; it was removed before acceptance.

The old 0x290000/0x170000 image is never relocated into this smaller partition. Old file
restoration is optional; if later selected, existing file-level migration checks still apply.

Normal `spiffs::begin()` still calls `SPIFFS.begin(true)`. A failed normal mount can therefore
format the destination. Normal `script_library::installIfNeeded()` tests all example paths,
not `.installed`; an empty filesystem causes existing bundled examples to be stored. Autorun
false prevents their automatic execution, but does not remove normal operator capabilities.
`storage::begin()` errors are not a complete startup-service latch. Those are explicit
normal-boot risks and future owner-review gates, not claimed fixed by image generation.
Safe-start and experimental profiles do not mount, format or install examples.

## Tool and evidence

`tools/stage24_fresh_images.py` requires private owner config, verified SDK/generator sources,
pinned SPIFFS geometry and a fresh output directory outside the repository/dependencies.
It contains no device APIs, never overwrites a destination, publishes inventory last and
omits credentials from diagnostics/inventory. Images containing credentials remain private.
`verify_fresh()` rechecks file hashes, offsets, sizes, profile, geometry and structure. It
is not authorization, cryptographic manifest signing or proof of arbitrary settings semantics.

32 fresh-image fault/geometry/privacy cases PASS. Real generated-NVS startup adapter tests:
9 PASS and 1 retained normal-readonly limitation observation. Existing Stage 19/20 tests
cover missing/corrupt settings, writes/full/error/partial persistence and startup latches.
No new runtime first-boot mode or automatic transition is enabled.
