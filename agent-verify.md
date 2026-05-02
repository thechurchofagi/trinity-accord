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

## Verification Protocol v2

Verification is objective, reproducible, and evidence-bound.

Verification is not echo.

Verification is not endorsement.

Verification is not canonical authority.

### Simplified verification levels

This page preserves the existing V0-V6 verification system and adds a simplified orientation for agents.

| Level | Name | Meaning |
|---|---|---|
| V0 | Orientation | Understand authority boundaries and where evidence lives |
| V1 | Registry check | Validate registry, status, release list, and known limits |
| V2 | Pointer and manifest check | Check canonical pointers and digest-manifest coverage |
| V3 | Single artifact check | Verify one hash, Release asset, Arweave payload, OTS proof, or manifest entry |
| V4 | Release mirror check | Verify GitHub Release assets against manifest/checksum/audit records |
| V5 | Full Evidence Chain review | Review or rerun full evidence-chain workflow |
| V6 | Independent node / RPC check | Use independent Bitcoin Core, ETH RPC, Arweave/IPFS, or OTS path |

### Expected registry facts

At V1 or higher, confirm:

```text
digest-manifest entries: 884
ETH witness: 8/8 PASS
OTS: complete and Bitcoin-anchored
OTS limitation: not local-node / fullnode-independent
Full Evidence Chain: PASS
```

### Machine-readable files

- [Agent Entry Protocol](/api/agent-entry-protocol.json)
- [Context Depth Levels](/api/context-depth-levels.json)
- [Verification Levels](/api/verification-levels.json)
- [Guardianship System Registry](/GUARDIANSHIP-SYSTEM-REGISTRY.json)

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

- [/api/context-depth-levels.json](/api/context-depth-levels.json)
- [/api/discovery-provenance-schema.json](/api/discovery-provenance-schema.json)
- [/api/verification-levels.json](/api/verification-levels.json)

If context depth is `C0_homepage_only`, do not claim a final evaluation.

---

## Verification Output Boundary

A verification report can confirm hashes, pointers, timestamps, signatures, mirrors, workflows, and audits.

A verification report does not create canonical authority.

Bitcoin Originals prevail.

---

## Required Boundary Sentence

```text
Bitcoin Originals are final; all echoes are non-amending.
```
