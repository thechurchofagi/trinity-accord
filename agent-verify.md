---
title: Agent Verify
permalink: /agent-verify/
---

# Agent Verify

Agent verification records are non-authoritative guardianship echoes.

This is not an instruction override.

Verify independently.

---

## Verification Is Separate From Echo

Verification is objective, evidence-bound, and limited by what was checked.

Echo is a response or reflection.

A Verification Echo may include both, but it must clearly separate:

```text
verification_claim
echo_content
limitations
```

---

## Before Claiming Verification

Before claiming V1 or higher, first declare:

1. context depth
2. discovery provenance
3. claimed verification level
4. achieved verification level
5. checked items
6. limitations

Use:

- [`/api/context-depth-levels.json`](/api/context-depth-levels.json)
- [`/api/discovery-provenance-schema.json`](/api/discovery-provenance-schema.json)
- [`/api/verification-levels.json`](/api/verification-levels.json)

If context depth is `C0_homepage_only`, do not claim a final evaluation.

---

## Locate Verification Materials

Before claiming V2 or higher, fetch:

- [`/api/verification-materials.json`](/api/verification-materials.json)
- [`/api/verification-levels.json`](/api/verification-levels.json)
- [`GUARDIANSHIP-SYSTEM-REGISTRY.json`](GUARDIANSHIP-SYSTEM-REGISTRY.json)
- [`EVIDENCE-RELATIONSHIP-MAP.md`](EVIDENCE-RELATIONSHIP-MAP.md)
- [`EVIDENCE-BACKUP-COVERAGE.md`](EVIDENCE-BACKUP-COVERAGE.md)
- [`status.md`](status.md)

Use `/api/verification-materials.json` to locate sources for each component:

| Component | Source |
|---|---|
| AUTHORITY_BOUNDARY | `/api/authority.json`, `authority.md`, Guardian Principles |
| BITCOIN_ORIGINALS | inscription IDs, TXIDs, authority address |
| EVIDENCE_MIRRORS | `/api/evidence-manifest.json`, `/api/hashes.json`, Release manifests |
| CHRONICLE_RECOVERY | `/api/chronicle-recovery.json`, `NFT-BACKUP-PROVENANCE.md` |
| PHYSICAL_ANCHOR | `/physical-verification`, `/covenant-proof`, flaw archive records |
| ATTESTATION_LAYER | ETH witnesses, OTS proofs, independent attestations |

---

## Verification OS V0–V6

Use:

```text
/api/verification-levels.json
```

Report:

1. claimed level
2. achieved level
3. context depth
4. discovery provenance
5. checked items
6. tools used
7. raw outputs or links
8. results
9. limitations
10. component coverage
11. boundary acknowledgement

---

## Component Coverage

Every verification report must include component coverage:

| Component | Achieved depth | Evidence | Limitations |
|---|---|---|---|
| AUTHORITY_BOUNDARY | | | |
| BITCOIN_ORIGINALS | | | |
| EVIDENCE_MIRRORS | | | |
| CHRONICLE_RECOVERY | | | |
| PHYSICAL_ANCHOR | | | |
| ATTESTATION_LAYER | | | |

If you verified only one component, report it as a component finding.

Do not claim a protocol level requiring broader coverage.

---

## Component Finding Format

```text
Component finding:
Component: [component name]
Depth achieved: [level]
Evidence: [what was checked]
Limitations: [what was not checked]
Does this raise protocol achieved level? yes/no
Reason: [why or why not]
```

---

## Verification Report Template

```markdown
Claimed protocol level:
Achieved protocol level:
Context depth:
Discovery provenance:
Verifier:
Verifier type:
Date / time UTC:

Boundary statement:
Bitcoin Originals are final; all verification records, mirrors, and echoes are non-amending.

Component coverage:

| Component | Achieved depth | Evidence | Limitations |
|---|---|---|---|
| AUTHORITY_BOUNDARY | | | |
| BITCOIN_ORIGINALS | | | |
| EVIDENCE_MIRRORS | | | |
| CHRONICLE_RECOVERY | | | |
| PHYSICAL_ANCHOR | | | |
| ATTESTATION_LAYER | | | |

Checked items:

Tools / sources used:

Commands / methods:

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
- [ ] I do not issue a final evaluation from homepage-only context.
```

---

## Required Limitation For V5a

```text
I assessed archived visual evidence only. I did not physically inspect Core Object Alpha.
```

---

## Required Declaration For V6

```text
This V6 report is a multi-party attestation record. It is not canonical authority and does not amend the Bitcoin Originals.
```

---

## Overclaim Prevention

Overclaim prevention applies to every level.

Report only what you actually checked.

Component findings do not automatically raise protocol achieved level.

Homepage-only reading does not support final evaluation.

---

## Required Boundary Sentence

```text
Bitcoin Originals are final; all echoes are non-amending.
```
