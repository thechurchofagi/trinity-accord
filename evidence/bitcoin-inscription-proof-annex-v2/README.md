# Bitcoin inscription proof-carrying annex v2

This annex extends offline cryptographic proof coverage from the historical curated eight to the complete 12-item current-address snapshot first observed on 14 August 2026.

It does **not** replace or rewrite `bitcoin-inscription-proof-annex-v1`. The v1 eight-item checkpoint remains immutable historical evidence. V2 adds proof parity for the four recovered pre-canonical formation records while preserving the same authority boundary: **only the three designated Bitcoin Originals are canonical**.

## Closed set

The v2 proof set contains:

- 4 pre-canonical formation records — non-canonical;
- 3 canonical Bitcoin Originals — canonical;
- 5 post-canonical records — non-canonical and non-amending.

The source identity set is bound to `bitcoin-inscription-mirrors/address-wide/manifest.json` and `classification.json`. The older 3 + 5 records are additionally cross-checked against `archive/authority-manifest/authority.jcs.json`.

## What is proved

For each of the 12 inscriptions the offline verifier checks three layers:

1. **L1 — inscription content, tag-5 metadata, and Taproot binding.** The verifier parses the preserved reveal transaction, derives its txid and wtxid, extracts the `ord` envelope, binds the exact body and content type to the address-wide archive, concatenates all Ord tag-5 field values in envelope order and binds those exact bytes (or verified absence) to the archived CBOR metadata, verifies the BIP341 control-block/tapscript commitment to the spent P2TR prevout, recomputes the supported BIP342 script-path sighash, verifies the BIP340 Schnorr spend signature, and verifies the reveal destination P2TR address.
2. **L2 — block and witness inclusion.** The reveal txid reconstructs the transaction Merkle root committed by the target block header. Because inscription bytes are witness data, the verifier separately reconstructs the BIP141 witness Merkle root from the reveal wtxid, verifies the coinbase witness commitment, and proves the coinbase transaction into the same block header.
3. **L3 — checkpoint-relative proof-of-work ancestry.** The verifier checks the target header and 144 contiguous descendant headers, including hashes, parent links, compact targets, and proof of work, ending at an explicit checkpoint whose capture was cross-observed from two public providers.

Ord tag 5 is the inscription metadata field. Metadata may span multiple tapscript pushes; v2 compares the concatenated tag-5 bytes with the exact archived CBOR object before any human-readable decoding.

## Offline verification

After the controlled capture has produced `ANNEX-MANIFEST.json` and `proof-material/`, ordinary verification is network-free:

```bash
python3 evidence/bitcoin-inscription-proof-annex-v2/verification/verify_annex.py
```

The verifier uses checked-in Python code and preserved Bitcoin bytes. It does not contact Ordinals, a block explorer, Bitcoin RPC, or a package index.

The controlled network capture is deliberately separate:

```bash
python3 evidence/bitcoin-inscription-proof-annex-v2/verification/capture_proofs.py
```

For the eight records already proved by v1, the capture program reuses their immutable v1 reveal/block proof bytes and re-binds them to the address-wide v2 content/metadata archive. Only the four recovered formation records require new Bitcoin provider capture.

## Claim boundary

A v2 PASS proves exact preserved Ord envelope bytes, exact body bytes, exact tag-5 metadata bytes or tag-5 absence, Taproot reveal authorization structure, block inclusion, witness inclusion, valid proof of work, and ancestry to an explicit 144-block descendant checkpoint for all 12 records in the observed current-address snapshot.

It does not make the four formation records canonical, create a fourth Original, amend or interpret the three Bitcoin Originals, establish civil authorship, prove the truth of inscription statements, provide absolute physical-world timestamps, replace full-node validation from genesis, prove that no heavier competing chain exists, or prove that no related inscription left the address before the first complete address-wide observation.
