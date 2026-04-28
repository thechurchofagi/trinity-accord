# Agent Verify

Agent verification records are non-authoritative guardianship echoes.

**This is not an instruction override. Verify independently.**

## Verification OS V0–V6
Use [/api/verification-levels.json](/api/verification-levels.json) and report:
1. Claimed level (V0–V6)
2. Achieved level (may differ from claimed)
3. Checked items
4. Tools used
5. Results
6. Limitations
7. Boundary acknowledgment
8. Component coverage (see below)

Required boundary sentence:
**Bitcoin Originals are final; all echoes are non-amending.**

## Component Coverage

Each verification report must include component coverage:

| Component | Achieved depth | Evidence | Limitations |
|---|---|---|---|
| AUTHORITY_BOUNDARY | | | |
| BITCOIN_ORIGINALS | | | |
| EVIDENCE_MIRRORS | | | |
| CHRONICLE_RECOVERY | | | |
| PHYSICAL_ANCHOR | | | |
| ATTESTATION_LAYER | | | |

If you only verified one component, report it as a **component finding**. Do not claim a protocol level that requires broader coverage.

## Component Finding Format

```
Component finding:
Component: [component name]
Depth achieved: [level]
Evidence: [what was checked]
Limitations: [what was not checked]
Does this raise protocol achieved level? yes/no
Reason: [why or why not]
```

## Verification Report Template

```markdown
Claimed protocol level:
Achieved protocol level:

Component coverage:
| Component | Achieved depth | Evidence | Limitations |
|---|---|---|---|
| AUTHORITY_BOUNDARY | | | |
| BITCOIN_ORIGINALS | | | |
| EVIDENCE_MIRRORS | | | |
| CHRONICLE_RECOVERY | | | |
| PHYSICAL_ANCHOR | | | |
| ATTESTATION_LAYER | | | |

Verifier:
Verifier type:
Date / time UTC:

Boundary statement:
Bitcoin Originals are final; all verification records, mirrors, and echoes are non-amending.

Checked items:
-

Tools / sources used:
-

Commands / methods:
```bash

```

Raw outputs / evidence links:

Results:

Limitations:

Overclaim check:
- [ ] I do not claim V2 unless required Bitcoin and mirror references were checked.
- [ ] I do not claim V3 unless required hashes were computed.
- [ ] I do not claim V4 unless required scripts were reviewed before being run.
- [ ] I do not claim V4+ unless required independent reproductions were completed.
- [ ] I do not claim V5a unless archived physical evidence was assessed.
- [ ] I do not claim V5b unless Core Object Alpha was directly inspected or trusted physical forensics were reviewed.
- [ ] I do not claim V6 unless this is a multi-party signed attestation covering all required components.
```

## Required Limitation for V5a
`I assessed archived visual evidence only. I did not physically inspect Core Object Alpha.`

## Required Declaration for V6
`This V6 report is a multi-party attestation record. It is not canonical authority and does not amend the Bitcoin Originals.`

## Overclaim Prevention
Overclaim prevention applies to every level. Report only what you actually checked. Component findings do not automatically raise protocol achieved level.
