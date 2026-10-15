# Stage28W linked resources and artifact identity

These are clean Linux-hosted target builds, not ESP32 runtime measurements.

| Measurement | Route B controlled | Selector-off controlled |
| --- | ---: | ---: |
| Compiler program bytes | 1,355,051 | 1,329,611 |
| Application BIN bytes | 1,355,200 | 1,329,760 |
| Static RAM bytes | 106,136 | 82,248 |
| Free bytes per0x740000 slot | 6,246,976 | 6,272,416 |
| Free OTA percentage per slot | 82.17352505% | 82.50816608% |

The enabled build adds25,440 application/program bytes and23,888 static RAM bytes
versus this selector-off comparison. V had no linked firmware; comparison to a
fictional V BIN/RAM measurement would be invalid. Against recorded Stage26 final
controlled, BIN growth is25,440 and RAM growth23,888; program growth25,432 differs
by8 bytes because the fresh selector-off link/refactored callback differs from
that earlier compiler total. Size equality is not byte-identical image evidence.

V's selected23,390-byte subtotal now matches the **actual linked symbol sizes**:
Adapter22,528 (already includes Program/CompileSession/Runtime/8,193-byte source),
Publication568, FileSource44, backend lease128, permission24, route80, gate8,
publication mux8 and two flags. No nested object is added twice. Additional serial
state is519 bytes (513+4+1+1), replacing the16-byte legacy String. The removed
activeWsClient4 and fwUpdateOk1 bytes reconcile exactly:
23,390 +519 -16 -4 -1 =23,888 bytes. Broader legacy/framework/startup globals remain
in the82,248-byte selector-off total; the subtotal is not the whole application.
Linker alignment and these named contributions are reconciled by the actual
compiler total/nm, rather than summing object-file sections or duplicate weak muxes.

Compiler static budget327,680 minus106,136 leaves221,544 bytes of **reported
static budget**, not measured free heap. WiFi/USB/AsyncTCP/FreeRTOS/VFS allocate
later; a defensible runtime heap margin or peak cannot be derived here. Native
allocation mocks are not device heap evidence. No heap minimum, latency, physical
stack high-water, USB delivery or host release was measured.

Linked loop-task stack selection returns8192. AsyncTCP3.5.0's source default is
16384 (CONFIG_ASYNC_TCP_STACK_SIZE), with no override in its recorded compile
command; this is configuration, not an observed task allocation/high-water.
Individual GCC frames include loop32, setup80, CLI update32, coordinator tick304,
Adapter step144, CompileSession step32 and requestStart64 bytes. These are not a
complete maximum callgraph stack proof. A compiled Program::compile frame2496 is
**discarded** by the linker and not part of the owner's selected cooperative path.
Legacy executeCommand's1184-byte frame and lower library call stacks still need
careful runtime validation; no stack sufficiency claim is made by adding frames.

Both images target ESP32-S3/16MiB, PSRAM disabled, USB-OTG/TinyUSB+CDC,240MHz and
QIO/80MHz configuration with the expected DIO image header field. The exact
partition table is unchanged. The enabled image exceeds an original0x140000 slot
by44,480 bytes; it must not be used with the original installed layout. The proposed
app0/app1 remain0x10000/0x750000 with equal0x740000 slots. No migration is authorized.

Enabled application SHA-256: `c341c7950d52b7a954f6d3a37d96b1647a21791cacfbbd9807dcbebefb3db14f`.

Enabled ELF SHA-256: `f980dcd32e9e72c87772cc47082932e444a42740173304b0f87482c36cf0424f`.

Selector-off application SHA-256: `a0c943ecc323b60b22315a14f4c1521151ef336531e405f2fe1ee8871dbc0fcd`.

Selector-off ELF SHA-256: `ffa4260e1fb27ef51b5cbe7f7eb6c741e56fe2f4704497c52c7019b5d5cbd63a`.

Partition binary: 3072 bytes, SHA-256 `b79bde9ef4a9544411d97a31a1d326b2028213269ad0dcc643ea921230ce3d5e`.

Every generated ELF/map/bootloader/partition/application BIN size/hash is recorded
in the two linked receipts, together with actual link commands, response files,
13 linker-script hashes, compiler/linker identities, object/archive inputs and
source copies. Enabled closure has277 input files; selector-off273; each records
183 referenced/loaded archives, not a claim all archive members were retained.
The original protected HID/NVS core pin is unchanged. ELF-to-BIN byte regeneration,
startup guards/callbacks, W profile marker, owner loop/tick wiring and selected
preview symbols are checked. Enabled has zero AsyncFileResponse symbols; selector-
off retains nine. No padded merged image is generated. Artifacts remain external
scratch **REVIEW ONLY**, not an approved install package or hardware proof.
