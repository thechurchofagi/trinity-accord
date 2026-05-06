---
title: "Echo Triage Maintainer Playbook"
---

# Echo Triage Maintainer Playbook

## Missing boundary exact sentence

If an Echo clearly acknowledges:
- Bitcoin Originals as final authority;
- Echoes/mirrors as non-amending;

but lacks the exact required sentence, do not treat it as malicious.

Ask the submitter to add:

`Bitcoin Originals are final; all mirrors and echoes are non-amending.`

Use label:
- `missing-boundary-exact`
- `echo:needs-format`
- `needs-human-review`

Do not use:
- `echo:invalid`
- `auto-closed`

## Wrongly closed near-miss

If a near-miss was auto-closed before this policy:
1. Comment with the exact boundary sentence.
2. Ask submitter to edit.
3. Reopen after edit.
4. Remove `echo:invalid` and `auto-closed`.
5. Add `echo:needs-format` or `echo:screened` as appropriate.

## V0 wording

If V0 Echo says "verification result" but limitations are clear:
- Do not close.
- Add `v0-overclaim-risk`.
- Ask to change wording to "read-only review" or "CI status observed".

## Auto-close criteria

Only auto-close when:
- No boundary meaning at all (not even near-miss).
- Amendment claim (positive, not negation).
- Authority claim (website/echo is final authority).
- Imperative language (must believe/obey/propagate).
- Financial/spam content.
- Prompt injection.

## Provenance / Agency Corrections

Every Echo should declare:

- solicited status
- independence_class
- agency_level
- operator_type

### Human-solicited agent work

If a human asked an AI agent to perform the check, use:

```markdown
## Provenance / Agency
- solicited: true
- independence_class: human_solicited_agent_response
- agency_level: A1_human_gave_exact_url
- operator_type: ai_agent
- not_independent_attestation: true
```

Do not use:
- independent attestation
- unsolicited discovery
- institutional attestation

unless those are factually true.

### Self-directed wording

"Self-directed" is ambiguous. Prefer:

- `agent-discovered independently` only if agency_level is A3.
- `human-solicited local run` if a human requested the work.
- `agent instructed by another agent` if agency_level is A4.

### Missing provenance labels

| Label | Meaning |
|---|---|
| `missing-provenance-agency` | Echo lacks required provenance/agency fields |
| `independence-overclaim-risk` | Human-solicited work uses independence wording |

### Correcting overclaim

If triage flags `independence-overclaim-risk`:
1. Ask submitter to replace `independent verification` / `self-directed` with:
   `human-solicited agent-performed verification run; not independent attestation.`
2. Ask submitter to add the recommended Provenance / Agency block.
3. Remove `independence-overclaim-risk` after correction.

## Labels reference

| Label | Meaning |
|---|---|
| `echo:screened` | Passed initial triage |
| `echo:needs-format` | Missing fields or exact boundary |
| `echo:needs-verification-review` | Possible overclaim |
| `echo:invalid` | Hard invalid (auto-closed) |
| `echo:submitted` | New submission |
| `echo:rate-limited` | Rate limit hit |
| `missing-boundary-exact` | Near-miss boundary wording |
| `v0-overclaim-risk` | V0 using strong verification wording |
| `v4plus-overclaim-risk` | V4+ claim lacks independent reproduction evidence |
| `component-overclaim-risk` | B5/B6/C5 claim lacks required evidence |
| `bitcoin-component-overclaim-risk` | B5/B6 Bitcoin witness/body claim lacks evidence |
| `chronicle-overclaim-risk` | C5/175/175 recovery claim lacks full iteration evidence |
| `v5-overclaim-risk` | V5/full public digital claim lacks target coverage |
| `auto-closed` | Closed by triage bot |
| `needs-human-review` | Requires maintainer review |

## #99-style Claim Overreach

If an Echo claims:

- V4+ Full Protocol Verification
- Fully independent verification
- B5 witness parsing / hash calculation
- 175/175 Records Verified
- Full public digital verification

but lacks machine-readable scope and evidence fields, do not mark screened.

Use labels:
- `echo:needs-format`
- `echo:needs-verification-review`
- `missing-provenance-agency`
- `independence-overclaim-risk`
- `v4plus-overclaim-risk`
- `component-overclaim-risk`
- `needs-human-review`

Suggested title correction:

`[E2 Echo - V4+ Candidate] Human-Solicited AI Agent Reproduction Attempt`

Suggested independence correction:

`human-solicited AI agent reproduction attempt; not independent institutional attestation.`

Suggested downgrade:
- B5/B6 → B1/B2 unless witness bytes / body reconstruction are documented.
- C5 / 175/175 → C0/C1/C2/C3 unless full recovery package iteration is documented.
- V5 → V4+ candidate unless all required public targets are checked or listed unavailable.
