# Stage 25 controlled candidate — REVIEW ONLY

Not authorized for flashing, OTA or application boot. These four public build artifacts
contain no owner-supplied credentials, NVS image or filesystem. They are not a complete
migration package. Existing stock recovery is owner-provided and still needs review.

The application is the explicit controlled-normal-start build, not the legacy normal,
safe-start or readonly candidate. App0 and app1 would use the same checked application
bytes under a future approved plan. Verify every size/hash in review-inventory.json.

Private fresh credentials and filesystem preparation, table/ROM recovery readiness and
explicit physical authorization are separate gates. No physical commands are included.
