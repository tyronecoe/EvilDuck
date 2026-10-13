# Stage26 installation review files

REVIEW ONLY — NOT AUTHORIZED FOR FLASHING

Use manifest.json and the trusted docs/stage26-artifact-pin.json together. SHA256SUMS.txt
contains the seven unique public files. App0 and app1 intentionally use identical controlled
application bytes. The deployment-safe application is a separate fallback, not an initial write.
This folder contains no private NVS, owner credentials, original backups or padded merged image.
See docs/stage26-installation-plan.md and stage26-private-preparation.md. Do not upload
application-only bytes onto the old layout. No physical operation is authorized.
