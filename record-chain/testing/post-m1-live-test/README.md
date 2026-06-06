# Post-M1 Live-Test Progress

This directory stores durable, sanitized progress for the post-M1 test program.

Authoritative manual:
- docs/testing/post-m1-sandbox-resumable-source-level-test-manual.md

Authoritative progress file:
- record-chain/testing/post-m1-live-test/progress.v1.json

Rules:
- Never store private key material.
- Never store authorship-private.pem contents.
- Do not use these files to bypass external no-token tests.
- External tests must still be performed in EXT mode.
- INT-CHECKPOINT may only store sanitized progress summaries.
