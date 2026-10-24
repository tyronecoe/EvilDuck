# Exact current-application rollback — review only

Rollback application is `ROUTEB-PREPROCESS-20261024-v1`, 1,409,616 bytes, SHA-256 `4251f320019dd813f2f0f4810c96f084f08127fa6a35ea6c99faece336e3ad5d`. It comes from the untouched public `evilduck-routeb-source-compat-macos-v1.zip` (SHA-256 `bf230c9950a2d46db294fd11b0913a44e8f33137dbbbb7ed1fd1ed8240425601`), not from assumed owner flash contents. The older `de0d34…` keyboard-control application is not this candidate's rollback target.

Package assembly checks exact size/hash/image identity, partition table, source receipts and installer binding. Future restoration requires the same independently verified installed geometry/security/ROM recovery prerequisites and separate explicit owner approval as installation. Stop on any mismatch. No flash command is executed or physical recovery newly verified in this stage. Preserve current working package and backups and do not reset NVS or format SPIFFS. A rollback of application bytes does not promise transactional restoration of settings or arbitrary files; this candidate introduces no settings schema changes.

After a separate owner-controlled review and explicit authorization, the existing bound launcher's future command shape is:

```bash
bash rollback-macos.sh --port OWNER_CONFIRMED_SERIAL_PORT
```

This is a review example, not an instruction to perform recovery now. Use only an independently confirmed port and the package's exact current-application rollback, with all installed-layout, image and security prerequisites satisfied. No command was executed against hardware.
