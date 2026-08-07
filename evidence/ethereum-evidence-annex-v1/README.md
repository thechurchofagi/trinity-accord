# Ethereum Proof-Carrying Evidence Annex v1

> **Non-amending evidence layer. The three Bitcoin Originals remain the sole and final Canon.**

## Purpose

This annex turns the repository's existing Ethereum mirror/witness records into one explicit long-term verification boundary.

Ethereum is **not** treated as a replacement storage authority and is **not** promoted into Canon. Its role here is narrower: preserve the relationship between known Trinity Accord payload commitments and Ethereum mainnet transactions, and define what additional proof material is required before a future verifier may claim execution inclusion or PoS finality without trusting a live RPC provider.

The core distinction is:

- **bytes preserved** is not the same claim as **transaction included**;
- **RPC/explorer checked** is not the same claim as **offline execution proof verified**;
- **block timestamp observed** is not the same claim as **PoS finality cryptographically verified**.

## Verification levels

| Level | Meaning | PASS rule |
|---|---|---|
| L1 — Byte integrity | Preserved payload bytes match the historical transaction-input digest/size records | Every declared payload exists and its size/SHA-256 matches |
| L2 — Execution inclusion | Transaction/receipt is included under an execution block commitment | Preserved raw transaction/receipt + block header + independently verifiable inclusion proof |
| L3 — Consensus finality | The execution block is connected to finalized Ethereum PoS consensus | Preserved beacon/finality material verifies under an explicit trusted finalized checkpoint |

A live explorer or RPC lookup may be recorded as `REFERENCE_CHECKED`; it must never be upgraded to L2/L3 `PASS` merely because a provider returned the expected fields.

## Time claim

The safe claim is:

> A commitment was included in an Ethereum mainnet block assigned to a consensus slot/time, subject to the preserved inclusion/finality proof and the documented trusted-checkpoint assumption.

The annex does **not** call Ethereum block time an absolute Earth-clock notarization. OpenTimestamps and Bitcoin anchoring remain independent evidence paths.

## Current v1 scope

The current repository already contains ten audited non-NFT Ethereum records. Nine have an exact transaction-input byte mirror (six dedicated/reused payload mirrors plus three canonical-text reuses); one BIP-340 witness preserves metadata and its referenced signed object rather than duplicating the raw input. `ANNEX-MANIFEST.json` imports those bindings without changing their historical status.

This v1 intentionally does **not** invent missing MPT/receipt/finality proof objects. Until those objects are captured and verified:

- L1 may pass.
- A historically checked transaction/block may be reported as `REFERENCE_CHECKED`.
- L2 remains `UNVERIFIED`.
- L3 remains `UNVERIFIED`.

That is a feature, not a failure: the annex is fail-closed.

## Files

- `ANNEX-MANIFEST.json` — authority boundary, claim model, ten Ethereum anchors, payload bindings, known chain references, and proof requirements.
- `verification/verify_annex.py` — offline stdlib verifier for schema, anchor uniqueness, payload size/SHA-256, and proof-status discipline.
- `verification/capture_eth_anchor.py` — deterministic RPC capture helper for transaction, receipt, and block JSON. Capture alone does not make L2/L3 pass.
- `reports/OFFLINE-VERIFICATION.json` — checked-in report generated from the current repository state.

Existing source bytes remain in their historical repository paths instead of being duplicated under this directory.

## Capture path for future hardening

For an anchor:

```bash
python evidence/ethereum-evidence-annex-v1/verification/capture_eth_anchor.py \
  --rpc "$ETH_MAINNET_RPC" \
  --tx 0x... \
  --out evidence/ethereum-evidence-annex-v1/proof-material/0x...
```

The helper records:

- `transaction.json`
- `receipt.json`
- `block.json`
- `capture-manifest.json`

The next hardening step is to add independently verifiable transaction/receipt inclusion material and beacon finality material. Merely adding these RPC JSON files is insufficient for L2/L3.

## Offline verification

From repository root:

```bash
python evidence/ethereum-evidence-annex-v1/verification/verify_annex.py
```

Exit code is non-zero on any byte-integrity failure or dishonest proof-status claim.

## Preservation architecture

This annex fits the long-term layers without changing authority:

- **Bitcoin:** fixed version authority for the three Originals; other Bitcoin anchors remain evidence/context according to their own status.
- **Ethereum:** non-amending consensus witness / historical commitment-time evidence.
- **OpenTimestamps:** independent timestamp evidence.
- **Arweave:** durable public replicas.
- **Zenodo:** reproducible recovery packages.
- **GitHub:** live verification and operating system.

The networks are complementary evidence relationships, not a linear authority chain.
