# Base and Polygon strict-verification boundary

`scripts/verify-chronicle-sidechain-strict.py` is a fail-closed, offline classifier. It exists so a successful workflow cannot silently equate transaction inclusion, payload availability, settlement inclusion, and consensus finality.

The current immutable evidence supports these conclusions:

| Layer | Polygon | Base |
| --- | --- | --- |
| Collection identity commitment | PASS | PASS |
| L2 block, transaction, and receipt inclusion | PASS (156/156) | PASS (61/61) |
| Exact IPFS/CAR recovery | INCOMPLETE across the collection: 250/257 roots; seven closed exceptions remain | INCOMPLETE across the collection: 250/257 roots; seven closed exceptions remain |
| L2 settlement into Ethereum execution | PASS: Bor leaf and checkpoint Merkle proof, RootChain receipt MPT proof, and Ethereum execution header hash are recomputed offline | NOT CAPTURED: no OP Stack L1 data derivation/output-root/fault-proof witness is present |
| Ethereum consensus finality | NOT CAPTURED: an RPC `finalized` tag is not an independent Beacon ancestry/finality proof | NOT CAPTURED |

Accordingly the honest overall result is currently `strict_completion=INCOMPLETE`. The workflow may report `audit_pass=true`, which only means that all present evidence was independently checked and every absent layer was classified as absent. `--require-complete` converts any incomplete layer into a non-zero exit.

The seven unresolved roots have a separately preserved public-chain provenance review. All seven token representations were externally delivered to the repository-declared target; none of those transactions was initiated by that target. That finding does not recover the missing bytes, does not make their content verified, and does not assert legal ownership.

This is stricter than relying on an explorer page or JSON-RPC response, but it is not the same construction as Bitcoin Core full validation from genesis. Polygon and Base inherit parts of their security from their own execution/consensus or sequencing systems and from Ethereum; each bridge from one layer to the next therefore needs its own proof and trust-boundary label.

Protocol references: [Ethereum weak subjectivity](https://ethereum.org/developers/docs/consensus-mechanisms/pos/faqs/#what-is-weak-subjectivity), [Ethereum Gasper finality](https://ethereum.org/developers/docs/consensus-mechanisms/pos/gasper/), [Polygon PoS architecture](https://docs.polygon.technology/pos/architecture/overview), [Polygon finality](https://docs.polygon.technology/pos/concepts/finality/finality), [Base contracts](https://docs.base.org/specifications/reference/base-contracts), and [Base transaction finality](https://docs.base.org/base-chain/network-information/transaction-finality).
