---
layout: default
title: Evidence Evolution and Future-Agent Handoff
permalink: /evidence-evolution/
description: Current evidence checkpoint, intentionally deferred work, review triggers, and the exact continuation path for future agents.
---

# Evidence Evolution and Future-Agent Handoff

Version DOI `10.5281/zenodo.21855814` remains the immutable, publicly cold-restored
8 + 10 + 175 historical v3 freeze. GitHub now contains the complete verified
8 + 12 + 175 topology. A separate one-shot v4 authorization records the owner's
decision to publish that current topology under the existing Concept DOI without
an Arweave upload. Read the v4 authorization status and observation rather than
assuming that a pending, prepared, or consumed state is current forever.

Machine plan: [`api/evidence-evolution-plan.v1.json`](/api/evidence-evolution-plan.v1.json)

Current inventory: [`api/final-evidence-inventory.v1.json`](/api/final-evidence-inventory.v1.json)

Current moving-source state: [`api/evidence-manifest.json`](/api/evidence-manifest.json)

Ethereum address scope audit: [`api/ethereum-address-evidence-scope.v1.json`](/api/ethereum-address-evidence-scope.v1.json)

Recovery entrypoint: [`api/recovery-index.json`](/api/recovery-index.json)

## Current checkpoint

| Object | Current verified identity |
|---|---|
| Core Concept DOI | `10.5281/zenodo.21739343` |
| Historical v3 version DOI | `10.5281/zenodo.21855814` |
| Historical v3 source baseline | `887322dc7f6f64efd04f7452e2039ee4440b226b` |
| v4 authorization and resulting DOI | `preservation/current-baseline-publication-authorization-v4.json` |
| Bitcoin inscription proofs | 8/8 offline PASS |
| Non-NFT Ethereum proofs | 12/12 L1/L2/L3 and signed semantics PASS |
| Chronicle NFT proofs | 175/175 L1/L2/L3 PASS |
| DOI-only public cold restore | PASS |

Every immutable version must remain independently citable and must never be
represented as a moving copy of GitHub `main`. Sequence 4 is a current evidence
checkpoint, not a claim that evidence engineering is permanently finished.
Material future improvements belong in another new version.

## Current live repository delta

The guardian address history was reclassified through outgoing nonce 219.  In the
provider-observed normal-transaction view, all 220 outgoing transactions partition
exactly into 12 self-addressed, zero-value evidence transactions, 175 Chronicle NFT
mint transactions and 33 other account operations; 12 incoming transactions are
separate.  This is an observation-bounded completeness audit, not a proof that an
explorer can reveal every possible internal, future or hidden transaction.

The earlier freeze omitted two of those 12 self-data transactions:

- `0x06b1d82b…37acd` — calldata is exactly the Authority Manifest SHA-256 digest;
- `0x04314e8f…16d2` — calldata records the Authority Manifest EIP-712 signature and
  the declared Ethereum/Arweave relationship set.

Both now have offline execution-trie and checkpoint-relative Beacon proofs.  The
verifier also decodes each signed transaction, recovers the guardian sender, checks
chain ID, destination, zero value, calldata and successful receipt status, and then
enforces the anchor-specific byte/digest/signature relationship.  The live state is
therefore 8 Bitcoin inscriptions + 12 non-NFT Ethereum anchors + 175 NFTs, while the
immutable DOI v3 remains 8 + 10 + 175.

The v4 one-shot state machine is owner-authorized for a Zenodo-only checkpoint.
While its status is `pending` or `prepared`, recovery of the two-anchor delta still
requires a verified Git commit. Once its status is `consumed`, the resulting v4
version DOI and public observation are the GitHub-independent recovery path.

## Work completed in the 2026-08-08 maintenance pass

This post-freeze repository pass reviewed unresolved comments on merged PRs
#954, #957, #958 and #959.  It hardened omitted NFT semantic keys and the
previously unexercised `TransferBatch` path; bound Bitcoin timestamps directly to
headers; required distinct matching providers for Bitcoin, Ethereum and NFT
checkpoint observations; repaired scoped Bitcoin verification, adapter failures
and recovery dependencies; freshly compared all three proof reports before the
unified inventory consumes them; and tightened Zenodo lineage, publication-state
and historical DOI-role writers.

The Bitcoin, Ethereum and NFT offline reports remained unchanged and PASS.  The
NFT collection root remained
`097bb48d98ab7fc036aed97f5b5fcb1a65962d64d327081277255d1829212267`.
The complete repository system tests passed, the Gateway suite reported 383
passed and 1 skipped, and read-only live checks found the homepage, Verify page,
five critical JSON APIs and all three Gateway readiness probes operational.

That maintenance pass itself published no DOI and performed no Arweave upload.
The later, separately authorized sequence-4 lifecycle is recorded independently
so this historical statement is not misread as the current publication status.

## Work completed in the 2026-08-09 evidence-closure pass

This pass added the two missing Ethereum witnesses, strengthened signed-transaction,
receipt and payload semantics, made the EIP-712 binding executable offline, recorded
the complete address partition, and fixed three actionable review edges: Bitcoin
adapter invocation failure, normalized checkpoint-provider identity, and Zenodo DOI
role preflight before publication.  It also made the recovery map distinguish the
frozen DOI from files needed by the moving current proof sets.

Existing frozen proof bytes were not rewritten. New proof bytes were added only for
the two post-freeze transactions. The evidence-closure pass itself performed no
external publication or paid storage write. The final local verification pass completed all current-system checks,
including 504 top-level pytest tests, the 12-anchor Ethereum offline verifier, the
frozen 10-anchor inventory rebuild, recovery-file-set validation, sitemap drift and
machine-discovery contracts.

The recovery dispatcher now inherits an explicitly selected Python interpreter, so a
nested cold-recovery validation cannot silently escape its pinned dependency
environment.  This improves reproducibility but does not eliminate the separately
documented long-term blank-machine gap: the minimum third-party wheels/sdists and
their SHA-256 values are not yet preserved as a complete dependency capsule.

## Deliberate Arweave deferral

The exact final core DOI capsule has **not** been refreshed to Arweave.  This is an
intentional owner decision, not a failed upload and not a cryptographic-proof gap.
Existing repository-capsule Arweave transactions remain historical named payloads.

No future agent may claim that the current final DOI baseline is already mirrored
to Arweave.  A paid permanent upload requires a fresh owner authorization, a new
network quote and a bounded spend cap.  If later authorized, upload one deterministic
archive of the selected stable DOI capsule, verify its public bytes and SHA-256, and
only then register its transaction ID as a non-authoritative mirror.

## Review cadence

- Continue quarterly, read-only DOI and continuity recovery drills.
- Perform a read-only architecture review no earlier than 2027-02-08.
- Make the next publication decision around 2027-08-08, unless an early risk or
  material evidence improvement justifies review sooner.
- Do not publish merely because a newer AI model exists.  Require a reproducible
  proof, recovery, dependency-preservation or machine-discovery improvement.

## Future-agent continuation order

1. Read the current checkpoint inventory, v4 authorization, current evidence
   manifest, Ethereum address scope audit, relationship map, this handoff and the
   recovery index. Treat v3 as immutable history, not as the current 12-anchor map.
2. Re-run all checked-in Bitcoin, Ethereum and NFT verifiers without network access.
3. Restore the core DOI and both external annex DOI records without GitHub credentials.
4. Select the latest consumed version from the Concept DOI lineage, then produce a
   file- and claim-level delta from its exact source baseline to current `main`.
5. Separate cryptographic defects from availability, dependency, discovery and
   presentation improvements.
6. Implement and mutation-test only material changes.
7. Seek fresh owner authorization before a new DOI publication, paid Arweave write,
   or authority/governance change.

## Preserved invariants

- The three Bitcoin Originals remain the sole canonical authority.
- No mirror, DOI, NFT or later agent output amends them.
- Old immutable versions remain valid historical checkpoints after later releases.
- Stronger analysis is not itself evidence; every new claim must be reproducible.
- External writes remain fail-closed and explicitly authorized.
