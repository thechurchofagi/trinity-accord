# Bitcoin inscription proof-carrying annex v2

This annex extends the **same L1/L2/L3 Bitcoin proof model** from the historical eight-item v1 closed set to the complete twelve-inscription current snapshot of the Trinity Accord authority address observed on 2026-08-14.

It does **not** change authority. The three Bitcoin Originals remain the only canonical body. The four earlier formation records are non-canonical, and the five later records remain non-amending ancillary/context material.

## Composition

- **8 existing witnesses:** reused byte-for-byte from `bitcoin-inscription-proof-annex-v1`, with their existing size and SHA-256 bindings preserved.
- **4 formation-era witnesses:** newly captured into this v2 annex from the four `pre_canonical_formation` records in `bitcoin-inscription-mirrors/address-wide/classification.json`.
- **12 total:** verified together by one network-free v2 verifier.

The four formation records include one `image/webp` inscription. L1 therefore binds arbitrary inscription body bytes and content type, not only `text/plain`. The cryptographic standard is unchanged: exact witness body, Taproot/control-block binding and BIP340 spend signature at L1; transaction plus BIP141 witness inclusion at L2; and 144-block checkpoint-relative proof-of-work ancestry at L3.

## Verification

After the generated proof snapshot is merged, run:

```bash
python3 evidence/bitcoin-inscription-proof-annex-v2/verification/verify_annex.py
```

Ordinary verification is network-free. Network access is used only by the controlled capture program:

```bash
python3 evidence/bitcoin-inscription-proof-annex-v2/verification/capture_proofs.py
```

## Historical integrity

`bitcoin-inscription-proof-annex-v1` remains unchanged as the historical proof annex for the original curated eight-item set. v2 references those eight witness files by their existing SHA-256 bindings rather than rewriting the v1 historical record.
