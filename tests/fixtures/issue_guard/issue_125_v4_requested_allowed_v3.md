# Issue #125 — V4/V4+ Requested, Claim Gate Allowed V3

## Classification
- Type: guardian-test / human_solicited_agent_response
- Requested level: V4, V4+
- Claim Gate allowed level: V3
- Archive status: issue_submission_only
- Counts as independent attestation: false

## Content
This is a guardian test with human-solicited agent response.
Requested V4/V4+ but Claim Gate downgraded to V3 minimal.

## Claim Gate Output
```json
{
  "allowed_protocol_level": "V3",
  "requested_level": "V4",
  "downgrades": [
    {
      "from": "V4",
      "to": "V3",
      "reason": "Official scripts only, not independent implementation"
    }
  ],
  "limitations": [
    "PASS with 1 skip — partial, not all-green"
  ]
}
```

## Wrong title
Guardian Test V4/V4+: Script Audit & Independent Reproduction

## Correct title
Guardian Test — requested V4/V4+, Claim Gate allowed V3
