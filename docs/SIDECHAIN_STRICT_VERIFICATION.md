# Base and Polygon strict-verification boundary

`scripts/verify-chronicle-sidechain-strict.py` is a fail-closed, offline classifier. It exists so a successful workflow cannot silently equate transaction inclusion, raw-wallet payload availability, Trinity Accord project-content completeness, settlement inclusion, and consensus finality.

The immutable source evidence and the supplementary finality bundle support these conclusions. The finality bundle is accepted only after its draft Release has been downloaded from GitHub, reconstructed, and reverified offline before publication:

| Layer | Polygon | Base |
| --- | --- | --- |
| Collection identity commitment | PASS | PASS |
| L2 block, transaction, and receipt inclusion | PASS (156/156) | PASS (61/61) |
| Raw-wallet exact IPFS/CAR recovery | FORENSIC INCOMPLETE: 250/257 roots; the remaining seven are provenance-resolved external wallet deliveries | FORENSIC INCOMPLETE: 250/257 roots; the remaining seven are provenance-resolved external wallet deliveries |
| Trinity Accord project-content completeness | PASS: project-content gap attributable to the seven roots is 0; their contracts are outside the official Trinity Accord NFT set and their inbound transactions were not initiated by the monitored target | PASS: same scope rule; unresolved external-wallet payload bytes are not required for Trinity Accord project completeness |
| L2 settlement/data availability into Ethereum execution | PASS: Bor leaf and checkpoint Merkle proof, RootChain receipt MPT proof, and Ethereum execution header hash are recomputed offline | PASS: official pinned OP Stack decoder reconstructs every target from exact channel frames; archived EIP-4844 blobs are re-bound to signed L1 transactions by recomputed KZG versioned hashes; frame transactions receive Ethereum `transactionsRoot` MPT proofs and locally rehashed headers |
| Ethereum consensus finality evidence | PASS WITH ETHEREUM BOUNDARY: raw signed Beacon SSZ blocks are retained; their roots and embedded execution block hashes are recomputed offline; two independent consensus-client endpoints must agree on `finalized=true` and `execution_optimistic=false` | PASS WITH THE SAME ETHEREUM BOUNDARY for every L1 batch-frame execution block |
| OP fault-proof withdrawal window | N/A | NOT APPLICABLE: these 61 origins are ordinary L2 NFT transactions, not L2-to-L1 withdrawal claims |

The historical `250/257` figure is preserved as a truthful **raw-wallet inventory** observation. It must not be rewritten as `257/257`, because the seven external payload byte sets have not been recovered or verified. A reproducible provenance audit instead resolved their scope: all seven token representations were externally delivered, none of the corresponding transactions was initiated by the monitored target, and none of the seven contracts belongs to the official Trinity Accord NFT contract set. Therefore the Trinity Accord **project-content gap attributable to those roots is 0**.

`strict_completion` is a **Trinity Accord project-required-layer** result. The optional raw-wallet forensic layer remains visibly incomplete but is marked `required_for_project_completeness=false`, so it does not block project completion. `--require-complete` still fails whenever any project-required layer is missing or failed—for example, when the supplementary finality bundle is not captured or does not verify—but it does not require recovery of unrelated externally delivered wallet assets.

The seven external roots remain preserved in the historical exception and provenance records for auditability. Their exact payload recovery is optional external-asset forensics only. Recovering those bytes in the future would improve the raw-wallet historical inventory, but it would not change the already resolved Trinity Accord project-content completeness classification. The provenance finding does not validate the missing external payload content and does not assert legal ownership.

This is much stricter than relying on an explorer page or a single JSON-RPC response, but it is not the same construction as Bitcoin Core full validation from genesis. The raw Beacon object and its execution binding are cryptographic; the historical finality classification is independently corroborated by two consensus clients. Ethereum PoS nevertheless retains a weak-subjectivity assumption, so the report must not be described as Bitcoin-style objective proof.

The finality publication gate is fail closed:

1. derive all 61 Base transactions with a pinned Optimism decoder;
2. replay all blob KZG bindings and Ethereum L1 transaction MPT proofs;
3. recompute all Polygon/Base Beacon SSZ roots and execution-payload bindings;
4. upload an unpublished draft in split archive parts;
5. download those exact remote parts, verify their manifest, reassemble channels into a fresh directory, and rerun every offline verifier;
6. publish only after that cold recovery passes, then download and check the public assets once more.

Protocol references: [Ethereum weak subjectivity](https://ethereum.org/developers/docs/consensus-mechanisms/pos/faqs/#what-is-weak-subjectivity), [Ethereum proof-of-stake finality](https://ethereum.org/developers/docs/consensus-mechanisms/pos/), [Beacon APIs](https://ethereum.github.io/beacon-APIs/), [OP Stack derivation](https://specs.optimism.io/protocol/derivation.html), [Polygon finality](https://docs.polygon.technology/pos/concepts/finality/finality), and [Base transaction finality](https://docs.base.org/base-chain/network-information/transaction-finality).
