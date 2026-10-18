# Owner acceptance — one trial at a time

No physical test was performed by Codex. Installation is a separate owner action.
Keep the existing private backup untouched. Use the new package's deliberate
rollback to the exact current `2c657f0c...` application if necessary.

1. After separately approved installation/manual reset, confirm buildId
   `CAPS-DURATION-20261018-v1`. Confirm ordinary harmless typing and STOP first.
2. With no trial/script active, use the Mac physical Caps key OFF/ON/OFF and capture
   fresh diagnostics with buildId, bootMarker, feedbackSession and uptime.
3. Set physical Caps OFF. Select baseline,100,250 or500ms. Click **Start ONE trial**
   once, then focus a blank TextEdit document within five seconds. The phone UI
   remains the controller. STOP can cancel focus delay or dwell.
4. Manually type `abc` without Shift. Record exact case and physical keyboard light.
   Refresh trial evidence and LED diagnostics. Save the request/trial IDs, duration,
   phase/reason, submission/completion timestamps, boot/session and incoming counts.
   Compare requestId==trialId before attributing evidence. Do not infer success from
   local completion or from uppercase STRING output.
5. Stop repeating a trial once the needed result exists. Restore desired Caps state
   deliberately with the physical key. Refresh does not replay. Failure/timeout is
   not a prompt for automatic retry. Use STOP / check execution when uncertain.

A: Caps output changed the Mac's lock state and manually typed case.
B: Genuine host LED OUTPUT reached and was accepted by the receiver.
Report A and B separately. Caps and Num feedback, High Sierra service behavior and
host release are physically unverified for this candidate. Windows is not tested.

## Optional read-only High Sierra service check

This is owner-operated, optional and diagnostic only. No sudo, driver, compiler,
helper download, remapping, plist changes or data upload is required. Terminal's
built-in commands read I/O Registry properties; they do not send keystrokes.

```bash
/usr/sbin/ioreg -p IOUSB -l -w 0
/usr/sbin/ioreg -r -c IOHIDDevice -l -w 0
```

These may show unrelated devices locally. Do not paste the entire output. Locate
only the EvilDuck USB device by its known owner-observed VID/PID and serial, then
its matching IOHIDDevice service (VendorID/ProductID/SerialNumber or parent path).
Report only whether that matching service exists, PrimaryUsagePage/PrimaryUsage,
ReportDescriptor hex if present, and the matching interface class/subclass/protocol
and endpoint properties if exposed. Redact serial/path if desired. An absent
property is UNKNOWN, not proof the descriptor is absent on USB. If the output is
unclear, stop and report only that fact; no broader system dump is requested.

A Generic Desktop Keyboard collection with reportID1 and LED OUTPUT fields supports
host recognition. No matching keyboard service points toward enumeration/descriptor
binding. A matching service with correct LED fields but zero firmware raw arrivals
leaves host report emission/transfer routing unresolved; a separately authorized
USB capture or another host comparison would be a later decision, not presumed
possible on High Sierra and not part of this cloud task.
