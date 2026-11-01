# Privacy-only owner acceptance — future separate approval required

These checks are prepared instructions. Codex has not installed, booted or tested
this candidate on hardware. Do not repeat the accepted right-modifier, STOP or
three-group lock-wait milestones for this repair. No payload execution is needed.

Before any physical check, preserve the current working package/backups and
follow the separately approved installation review. Confirm the exact candidate
application identity from the reviewed package and successful installation
comparisons: **1,415,968 bytes**, SHA-256
**9e4d3b615d78e87521882a35c4b43ce66403168a15b6b39bcebc81bb32a6b96e**.
The unchanged H1 dashboard build ID alone is insufficient. An installer-recorded
hash is not independent device readback unless that operation actually occurred.

**Do not issue `settings` on an unidentified/older firmware to obtain screenshots:
older firmware can print saved passwords.** No credentials should be entered in
shell command lines or shared through screenshots, Terminal logs or HTTP headers.

## Short checks on the identified candidate

1. Privately authenticate to the existing dashboard. Open **Settings**. Both AP
   and Web UI password **replacement** fields must be blank, with configured/
   leave-blank guidance. Press **Reload**: neither saved password should appear.
   Record only PASS/FAIL and the candidate identity; crop out SSID, authentication
   inputs, personal filenames and any private values if retaining a screenshot.

2. Leave both replacements blank. Save one benign unrelated setting, such as a
   small LED color change, then **Reload**. Confirm the selected setting persists
   in the settings display and the existing dashboard/AP credentials still work
   when reauthenticating/reconnecting as appropriate. Restore the unrelated
   setting if desired, again leaving password replacements blank. Do not select
   settings reset, filesystem format or autorun.

3. If a local USB console session is separately approved, send only the literal
   command **`settings`** on the identified candidate. Expect
   `password_configured=1` and `web_password_configured=1`, with no raw
   `password=`/`web_password=` values. Inspect privately before retaining output;
   report only that the two configured indicators appeared and secrets did not.
   No password-setting command is required.

The dashboard omits blank replacement fields from HTTP requests. Explicit empty
HTTP replacements also mean "keep existing", independently for both passwords;
that direct-request behavior is covered by composed software tests, not claimed
as physically exercised by the UI. No credential-bearing curl command, developer
console script or network capture is needed for this acceptance.

Do not replace passwords merely to complete these checks. If deliberately
replacing the **Web UI password** later, privately retain the intended value;
subsequent requests require the new password and the old browser session is not
automatically migrated. AP configuration timing remains the existing firmware
behavior. Blank does not erase a password or disable authentication.

Persistence remains **non-atomic**. A failed save can leave RAM or a persisted
prefix changed. Preserve a sanitized failure indication and stop for review;
do not assume rollback, automatically retry, reset settings or disclose values.
Restoring the older rollback application does not restore past settings.

Record the date, host OS, exact candidate/package/installer identity, which checks
were attempted and scoped observations. Missing or ambiguous evidence remains
unverified. A pass covers this privacy workflow on the tested configuration, not
complete security, physical flash immutability or universal host compatibility.
