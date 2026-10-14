# Stage28D integration status

GO isolated offline review only. NOT FLASH-AUTHORIZED.
NO-GO Stage26 integration, Stage27A changes, flashing/boot/OTA, real HID or production adapters.

Only an internal mock planning API is added. The optional Runtime-event adapter is deliberately
NOT implemented: no EventType/Sink ABI change, no Delay consumption and no HOLD/RELEASE parser
commands. Existing Character/KeyTap/Delay output remains exactly the Stage28C synthetic model.
A future separately reviewed mock bridge should acknowledge a source tap only after press and
restoration acceptance, finish it before accepting Delay, and explicitly handle cancel/drain.
It must not replay an accepted press while retrying the same Runtime event. No such bridge runs here.

Normal firmware, reviewed Stage26 files/artifacts, startup/arming, locales, storage, USB identities,
partitions and migration safeguards remain frozen. Stage27A is independent and uses only
968c8e0aaf459b0b8b652cc57fe88225894ab64b under owner-controlled authorization. Original firmware
remains OWNER CONFIRMED — AVAILABLE EXTERNALLY; no owner data/backups requested or accessed.

US-only report planning cannot prove literal text under persistent SHIFT/CTRL/ALT/GUI, lock states,
dead keys, DE/non-US hosts or OS-specific interpretation. No dwell, typematic, USB report ID,
disconnect recovery, descriptors, NKRO or physical release guarantee. Parser/hardware compatibility
matrix statuses are unchanged; internal API capabilities are documented separately.

Recommended next separate milestone: mock-only Runtime-to-planner admission/acknowledgement bridge
with bounded Delay, backpressure and cancellation/drain tests. No next stage starts automatically.
