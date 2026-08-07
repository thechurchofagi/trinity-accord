# Ethereum Proof-Carrying Evidence Annex v1

> **Non-amending evidence layer. The three Bitcoin Originals remain the sole and final Canon.**

## Purpose

This annex turns the repository's existing Ethereum mirror/witness records into one explicit long-term verification boundary.

Ethereum is **not** treated as a replacement storage authority and is **not** promoted into Canon. Its role here is narrower: preserve the relationship between known Trinity Accord payload commitments and Ethereum mainnet transactions, plus the proof material needed to verify execution inclusion and checkpoint-relative PoS finality without trusting a live RPC provider during verification.

The core distinction is:

- **bytes preserved** is not the same claim as **transaction included**;
- **RPC/explorer checked** is not the same claim as **offline execution proof verified**;
- **provider says finalized** is not the same claim as **trust-free finality from no starting point**.

## Verification levels

| Level | Meaning | PASS rule |
|---|---|---|
| L1 — Byte integrity | Preserved payload bytes match the historical transaction-input digest/size records | Every declared payload exists and its size/SHA-256 matches |
| L2 — Execution inclusion | The target transaction/receipt belongs to the declared Ethereum execution block | Preserved raw signed transactions and encoded receipts reconstruct `transactionsRoot` and `receiptsRoot`; the execution header re-hashes to the declared block hash; the target transaction is present at its declared index |
| L3 — Consensus finality | The execution block is connected to finalized Ethereum PoS consensus relative to an explicit weak-subjectivity root | The execution block hash is SSZ-proven into the target Beacon block body; the target Beacon root is linked by re-hashed `parent_root` ancestry to a named trusted finalized descendant Beacon root |

A live explorer or RPC lookup may still be recorded as `REFERENCE_CHECKED`; it is not what makes L2/L3 pass.

## L3 trust boundary

Ethereum PoS light-client verification has an unavoidable starting trust assumption. This annex therefore does **not** hide the weak-subjectivity boundary.

For each anchor, the L3 witness names a specific descendant Beacon root that is explicitly trusted as finalized. The capture process preserved two independent historical Beacon API observations agreeing on that root; at least one must report `finalized: true` and non-optimistic execution. In the captured v1 witnesses, both configured providers agreed and reported finalized/non-optimistic status.

Those provider fields are **provenance only**. They do not magically turn the trusted root into a trust-free theorem. The offline cryptographic portion begins from that explicitly trusted finalized root and proves backwards, by recomputing every Beacon header root and following `parent_root`, that the target Beacon block is its ancestor. It separately verifies the SSZ branch binding the execution `block_hash` into the target Beacon body.

Therefore `L3_CONSENSUS_FINALITY = PASS` means:

> PASS relative to the explicitly declared weak-subjectivity trusted finalized Beacon root.

It does **not** mean “Ethereum mainnet finality proven from no external trust anchor.”

## Time claim

The safe claim is:

> A commitment was included in an Ethereum mainnet execution block bound to a Beacon consensus slot, and that Beacon block is an ancestor of the explicitly trusted finalized Beacon root preserved for the anchor.

The annex does **not** call Ethereum block time an absolute Earth-clock notarization. OpenTimestamps and Bitcoin anchoring remain independent evidence paths.

## Current v1 scope

The repository contains ten audited non-NFT Ethereum records. All ten now carry:

- their pre-existing historical RPC transaction/receipt/block capture, retained as reference-only evidence;
- an L2 execution witness containing the complete raw signed transaction set and encoded receipt set required to reconstruct both execution trie roots offline;
- an L3 consensus witness containing the execution-block-hash SSZ proof, the target Beacon header, an explicit trusted finalized descendant Beacon root, capture provenance, and the Beacon parent-root ancestry needed for offline verification;
- manifest size/SHA-256 bindings for both proof witnesses.

One BIP-340 witness record still preserves metadata and its referenced signed object rather than duplicating its raw transaction input as a canonical payload. That historical payload-binding distinction is unchanged by L2/L3 verification.

## Files

- `ANNEX-MANIFEST.json` — authority boundary, claim model, ten Ethereum anchors, payload bindings, proof statuses, and SHA-256/size bindings for L2/L3 witnesses.
- `proof-material/<tx>/L2-execution-witness.json` — complete execution reconstruction witness for one anchor block.
- `proof-material/<tx>/L3-consensus-witness.json` — SSZ/Beacon ancestry witness and explicit finalized-root trust boundary.
- `proof-material/L2-L3-CAPTURE-SUMMARY.json` — capture summary for all ten anchors.
- `verification/verify_annex.py` — offline fail-closed verifier for L1/L2/L3.
- `verification/generate_l2_l3_proofs.py` — networked controlled-capture generator. It is not used by ordinary offline verification.
- `verification/make_beacon_execution_proof.mjs` — SSZ proof helper used by the controlled generator.
- `verification/capture_eth_anchor.py` — historical RPC capture helper; capture alone does not make L2/L3 pass.
- `reports/OFFLINE-VERIFICATION.json` — checked-in output of the offline verifier.

Existing source payload bytes remain in their historical repository paths instead of being duplicated under this directory.

## What L2 actually recomputes

For each target execution block, the verifier operates only on preserved repository bytes and:

1. RLP-encodes the execution block header and Keccak-hashes it back to the declared block hash.
2. Keccak-hashes every preserved raw signed transaction and matches the block's transaction hash list.
3. Reconstructs the Ethereum hexary Merkle-Patricia transaction trie using `RLP(transaction_index)` keys and requires its root to equal `transactionsRoot`.
4. Reconstructs the receipt trie from the preserved encoded receipts and requires its root to equal `receiptsRoot`.
5. Requires the target transaction hash to occur at the declared transaction index.

Because the complete block transaction/receipt sets are preserved, L2 verification does not need an execution RPC endpoint.

## What L3 actually recomputes

For each target anchor, the verifier:

1. Recomputes the target Beacon header root from its SSZ fields.
2. Recomputes the SSZ Merkle branch proving that `executionPayload.blockHash` equals the L2-verified execution block hash under the target Beacon `body_root`.
3. Recomputes every preserved descendant Beacon header root from the explicit trusted finalized root backwards.
4. Requires every header's `parent_root` to link to the next preserved header until the target Beacon root is reached.
5. Requires the manifest/witness to keep the weak-subjectivity trusted-root assumption and provider-provenance boundary explicit.

No network access is required for these checks after the witnesses are preserved.

## Offline verification

From repository root:

```bash
python evidence/ethereum-evidence-annex-v1/verification/verify_annex.py
```

A successful verification reports all three levels as `PASS`. Exit code is non-zero on payload-byte drift, proof-file SHA/size drift, execution trie/header failure, SSZ failure, Beacon ancestry failure, or any attempt to erase the explicit trusted-root boundary.

## Controlled regeneration

Regeneration is intentionally separate from verification because it needs public Ethereum execution/Beacon endpoints and must not make ordinary verification network-dependent. The generator validates reconstructed execution roots before emitting L2 material and cross-checks the selected historical Beacon root across configured providers before emitting L3 material.

Generated evidence must be reviewed, bound by SHA-256/size in the manifest, and pass the offline verifier before replacing checked-in witnesses.

## Preservation architecture

This annex fits the long-term layers without changing authority:

- **Bitcoin:** fixed version authority for the three Originals; other Bitcoin anchors remain evidence/context according to their own status.
- **Ethereum:** non-amending consensus witness / historical commitment-time evidence.
- **OpenTimestamps:** independent timestamp evidence.
- **Arweave:** durable public replicas.
- **Zenodo:** reproducible recovery packages.
- **GitHub:** live verification and operating system.

The networks are complementary evidence relationships, not a linear authority chain.
