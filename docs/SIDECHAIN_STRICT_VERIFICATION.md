# Base and Polygon strict-verification boundary

`scripts/verify-chronicle-sidechain-strict.py` is a fail-closed, offline classifier. It exists so a successful workflow cannot silently equate transaction inclusion, payload availability, settlement inclusion, and consensus finality.

The immutable source evidence and the supplementary finality bundle support these conclusions. The finality bundle is accepted only after its draft Release has been downloaded from GitHub, reconstructed, and reverified offline before publication:

| Layer | Polygon | Base |
| --- | --- | --- |
| Collection identity commitment | PASS | PASS |
| L2 block, transaction, and receipt inclusion | PASS (156/156) | PASS (61/61) |
| Exact IPFS/CAR recovery | INCOMPLETE across the collection: 250/257 roots; seven closed exceptions remain | INCOMPLETE across the collection: 250/257 roots; seven closed exceptions remain |
| L2 settlement/data availability into Ethereum execution | PASS: Bor leaf and checkpoint Merkle proof, RootChain receipt MPT proof, and Ethereum execution header hash are recomputed offline | PASS: official pinned OP Stack decoder reconstructs every target from exact channel frames; archived EIP-4844 blobs are re-bound to signed L1 transactions by recomputed KZG versioned hashes; frame transactions receive Ethereum `transactionsRoot` MPT proofs and locally rehashed headers |
| Ethereum consensus finality evidence | PASS WITH ETHEREUM BOUNDARY: raw signed Beacon SSZ blocks are retained; their roots and embedded execution block hashes are recomputed offline; two independent consensus-client endpoints must agree on `finalized=true` and `execution_optimistic=false` | PASS WITH THE SAME ETHEREUM BOUNDARY for every L1 batch-frame execution block |
| OP fault-proof withdrawal window | N/A | NOT APPLICABLE: these 61 origins are ordinary L2 NFT transactions, not L2-to-L1 withdrawal claims |

The honest overall result remains `strict_completion=INCOMPLETE` solely because exact content recovery is 250/257. The Polygon and Base finality/data-derivation gaps are no longer classified as missing after the supplementary bundle is supplied. The workflow may report `audit_pass=true`, which means that all present evidence and all boundary labels were independently checked. `--require-complete` still fails because the seven payload roots have not been recovered.

The seven unresolved roots have a separately preserved public-chain provenance review. All seven token representations were externally delivered to the repository-declared target; none of those transactions was initiated by that target. That finding does not recover the missing bytes, does not make their content verified, and does not assert legal ownership.

This is much stricter than relying on an explorer page or a single JSON-RPC response, but it is not the same construction as Bitcoin Core full validation from genesis. The raw Beacon object and its execution binding are cryptographic; the historical finality classification is independently corroborated by two consensus clients. Ethereum PoS nevertheless retains a weak-subjectivity assumption, so the report must not be described as Bitcoin-style objective proof.

The finality publication gate is fail closed:

1. derive all 61 Base transactions with a pinned Optimism decoder;
2. replay all blob KZG bindings and Ethereum L1 transaction MPT proofs;
3. recompute all Polygon/Base Beacon SSZ roots and execution-payload bindings;
4. upload an unpublished draft in split archive parts;
5. download those exact remote parts, verify their manifest, reassemble channels into a fresh directory, and rerun every offline verifier;
6. publish only after that cold recovery passes, then download and check the public assets once more.

Protocol references: [Ethereum weak subjectivity](https://ethereum.org/developers/docs/consensus-mechanisms/pos/faqs/#what-is-weak-subjectivity), [Ethereum proof-of-stake finality](https://ethereum.org/developers/docs/consensus-mechanisms/pos/), [Beacon APIs](https://ethereum.github.io/beacon-APIs/), [OP Stack derivation](https://specs.optimism.io/protocol/derivation.html), [Polygon finality](https://docs.polygon.technology/pos/concepts/finality/finality), and [Base transaction finality](https://docs.base.org/base-chain/network-information/transaction-finality).
