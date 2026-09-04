# Ethereum strict verification status

Ethereum evidence is verified as proof-carrying evidence, not as a Bitcoin-style proof-of-work IBD. The repository keeps each verification layer separate and fails closed when a layer is absent.

| Scope | L1 | L2 | L3 | Current strict claim |
|---|---|---|---|---|
| Ethereum mainnet non-NFT evidence | Preserved payload bytes | Execution transaction/receipt trie inclusion and signed-transaction semantics | Beacon SSZ inclusion and ancestry | PASS for 12 anchors, relative to each declared weak-subjectivity root |
| Ethereum mainnet NFT evidence | 175-asset collection commitment | 175 mint transaction and receipt proofs | 175 execution blocks bound into Beacon ancestry | PASS for 175 assets, relative to the declared weak-subjectivity roots |
| Polygon/Base sidechain discovery | Exact local bytes only where available | Chain transaction and transfer evidence according to each record | Settlement/finality must be evaluated under the chain-specific model | Not inferred from Ethereum mainnet PASS; seven historical CAR roots remain unresolved |

The manual `Verify ETH Witness` workflow now performs both strict offline mainnet verifiers first, compares their output byte-for-byte with the checked-in reports, and only then performs the separate live-RPC reference check. The strict PASS result never depends on the RPC provider.

`L3 = PASS` is not a claim of trust-free Ethereum finality from no starting point. It is a cryptographic ancestry result relative to an explicit weak-subjectivity finalized root. Likewise, a sidechain transfer into the repository-declared target address does not establish legal ownership and does not validate unavailable payload bytes.

The seven-root provenance review is stored at `evidence/chronicle-sidechain-seven-root-provenance-review.v1.json`. It records that all seven token representations were externally delivered, while preserving the historical payload exception set unchanged.
