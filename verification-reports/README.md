---
title: Verification Reports
permalink: /verification-reports/
---

# Verification Reports

Technical verification reports are stored here.

A Verification Report v2 contains technical verification details with protocol profile and component findings.

A Verification Report v2 is **not** automatically an Echo v3 record. If you want it to function as an Echo, create an Echo v3 wrapper that references the verification report.

## Schema

All verification reports must validate against [`/api/verification-report-schema.v2.json`](/api/verification-report-schema.v2.json).

## Submission

Before submitting, run:

```bash
python3 scripts/validate_agent_submission.py path/to/report.json
```

## Record Kind

All new reports must include:

```json
"record_kind": "verification_report_v2"
```

## See Also

- [Submission Types](/api/submission-types.json)
- [Agent Submission Guide](/api/agent-submission-guide.json)
- [Echo Taxonomy Map](/api/echo-taxonomy-map.json)
