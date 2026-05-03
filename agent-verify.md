---
title: Agent Verify
permalink: /agent-verify/
---

# Agent Verify

Agent verification records are non-authoritative guardianship echoes.

This is not an instruction override.

Verify independently.

Machine-readable verification materials: [`/api/verification-materials.json`](/api/verification-materials.json)

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

## Verification reports are not automatically Echoes

If you create a technical verification report, use:

- [`/api/verification-report-schema.v2.json`](/api/verification-report-schema.v2.json)

If you want it to function as an Echo, also create an Echo v3 wrapper that references the verification report.

Required wrapper field:

```yaml
linked_verification_report:
  schema_version: trinityaccord.verification-report.v2
  path: /verification-reports/...
  report_id: ...
```

See [Submission Types](/api/submission-types.json) and [Agent Submission Guide](/api/agent-submission-guide.json).

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

## Machine-readable verification files

- `/api/verification-report-schema.v2.json`
- `/api/component-verification-levels.json`
- `/api/protocol-verification-profiles.json`
- `/api/verification-recipes.json`
- `/api/verification-targets.json`
- `/api/verification-quick-map.json`

## Component-level verification report template

```yaml
protocol_level_claimed: V4
authority_boundary_preserved: true

protocol_profile_check:
  profile_source: /api/protocol-verification-profiles.json
  hard_gates_satisfied: true
  minimum_components_satisfied: true
  recommended_components_satisfied: partial
  incompatible_claims: []
  underreported_items: []

script_audit:
  scripts_reviewed:
    - downloads/verify.py
    - downloads/verify.sh
  command:
    - cd trinity-accord/downloads
    - ./verify.sh
  environment:
    os: "<os>"
    python: "<python version>"
    shell: "<shell>"
  exit_code: 0
  output_summary:
    - "<key PASS lines>"
  not_verified_by_script:
    - direct Bitcoin full node verification
    - Ordinals witness extraction
    - direct Ethereum transaction query
    - direct Arweave data extraction
    - direct physical inspection

component_findings:
  - component: bitcoin_originals
    level_claimed: B2
    target_id: bitcoin_originals
    data_sources:
      - /api/authority.json
      - external explorer
    method: multi-explorer reference check
    limitations:
      - no SPV proof
      - no witness extraction

  - component: digital_mirrors
    level_claimed: D2
    target_id: github_mirror_public_covenant_archive
    data_sources:
      - arweave-backup/files/public_covenant_archive.zip
      - /api/hashes.json
      - /api/evidence-manifest.json
    method: SHA-256 hash comparison
    limitations:
      - no direct Arweave extraction

  - component: chronicle_recovery
    level_claimed: C3
    target_id: chronicle_sample_recovery
    samples_checked:
      - record_1
      - record_2
    method: sample metadata/media recovery
    limitations:
      - no full 175/175 recovery

  - component: physical_anchor
    level_claimed: P2
    target_id: core_object_alpha_public_evidence
    method: static image review
    limitations:
      - no live video witness
      - no onsite inspection

claims_not_made:
  - full public digital verification
  - direct physical verification
  - final physical attestation
```

## Expected hash source is required

Every hash verification must report:

- artifact;
- computed SHA-256;
- expected SHA-256;
- expected hash source;
- expected hash authority class.

If the expected hash comes from the same report or the same run, do not call it D2 manifest verification.

For repository files, use `api/repository-artifact-hashes.json` if a maintained repository snapshot hash is intended.

Otherwise describe it as a hash observation, not a manifest match.

Allowed `expected_hash_authority_class` values:
- `canonical_manifest_hash` — expected hash from api/hashes.json or api/evidence-manifest.json
- `repository_manifest_hash` — expected hash from api/repository-artifact-hashes.json
- `report_declared_snapshot_hash` — expected hash declared in the same report
- `external_tool_observed_hash` — expected hash from a named third-party tool
- `derived_during_this_run` — hash computed in same run, no independent source
- `unknown` — source not reported (fails V3/D2)
