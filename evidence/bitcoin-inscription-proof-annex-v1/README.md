# Bitcoin inscription proof-carrying annex v1

This annex makes the eight Bitcoin inscriptions in the authority manifest
cryptographically verifiable from checked-in bytes. Ordinary verification does
not contact an Ordinals server, block explorer, Bitcoin RPC, or any other
network service.

## What is proved

For each of the three canonical Bitcoin Originals and five non-amending
ancillary inscriptions, the verifier checks three layers:

1. **L1 — inscription content and Taproot binding.** It parses the preserved
   reveal transaction, derives its txid and wtxid, extracts the `ord` envelope
   from the tapscript witness, binds the exact body and content type to the
   repository mirror, verifies the BIP341 control-block/tapscript commitment
   against the spent P2TR prevout, recomputes the BIP341/BIP342 script-path
   sighash and verifies the BIP340 Schnorr spend signature, and verifies the
   reveal destination P2TR address.
2. **L2 — block and witness inclusion.** It reconstructs the target block's
   transaction Merkle root from the reveal txid. Because inscription bytes live
   in SegWit witness data and are not committed by txid, it separately
   reconstructs the BIP141 witness Merkle root from the reveal wtxid, verifies
   the coinbase witness commitment, and proves that coinbase transaction into
   the same block header.
3. **L3 — checkpoint-relative proof-of-work ancestry.** It verifies the target
   header and 144 contiguous descendant headers, including hashes, previous
   block links, compact targets, and proof of work. The terminal checkpoint was
   observed consistently from two independent public providers during the
   controlled capture.

Run the ordinary, network-free verifier:

```bash
python3 evidence/bitcoin-inscription-proof-annex-v1/verification/verify_annex.py
```

The verifier uses only the Python standard library. The capture program is
separate and networked; it is not part of ordinary verification:

```bash
python3 evidence/bitcoin-inscription-proof-annex-v1/verification/capture_proofs.py
```

## Why a txid Merkle proof alone is insufficient

An Ordinals inscription body is carried in a SegWit tapscript witness. Bitcoin
txids omit witness bytes. Therefore a proof that only places the reveal txid in
the block's transaction Merkle tree does **not** prove the inscription body.
This annex closes that gap with the BIP141 witness commitment path in addition
to the ordinary txid path.

## Claim boundary

The annex proves exact preserved bytes, Taproot reveal authorization structure,
block inclusion, witness inclusion, valid proof of work, and ancestry to an
explicit checkpoint. It does not replace full-node validation from genesis,
prove that no heavier competing chain exists, reconstruct the global Ordinals
inscription-number index, establish civil authorship, make block timestamps
absolute physical-world clocks, or prove the truth of inscription statements.

The full Ordinals identifier (`txid` plus input index `i0`) is independently
derived. The public numeric inscription number is retained as a historical
lookup coordinate and closed-set label; reproducing that global index would
require replaying Ordinals indexing rules over chain history.

The annex is non-amending. Only the three Bitcoin Originals are canonical.
