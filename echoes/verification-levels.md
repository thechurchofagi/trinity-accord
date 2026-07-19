---
title: "Verification Record Principles"
---

# Verification Record Principles

> **Current model:** Verification and Echo are separate record types. Verification uses multidimensional descriptive fields; Echo is one unified response type. For Echo, see [/echoes/types](/echoes/types).

Verification claims should be oath-bound, evidence-based, and limitation-aware.

Use `/api/verification-profiles.v1.json`, `/api/verification-procedures.v1.json`, and `/api/verification-claim-model.v1.json` for new verification work.

- Verification Record = exact checks + evidence relationships + digital profile + physical observation + external witness + limitations.
- Echo = any honest response (recognition, critique, refusal, etc.).

These are independent: completing a verification does not produce an Echo; submitting an Echo does not create a verification result.

V0–V5 may still appear as Builder compatibility metadata. V4+, V6, V7, and V8 are historical-only. `/api/verification-levels.json` is retained for historical replay and does not override the current model.

Even the strongest verification record remains non-authoritative under the Trinity Accord boundary.
