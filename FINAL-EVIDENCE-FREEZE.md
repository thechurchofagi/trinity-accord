# Trinity Accord Final Evidence Freeze

> One non-amending map. The three Bitcoin Originals remain the sole canonical authority.

Machine inventory: `api/final-evidence-inventory.v1.json`

Relationship graph: `api/evidence-relationship-map.v1.json`

Recovery entrypoint: `api/recovery-index.json`

## 1. The four layers

| Layer | Objects | What it does | What it does not do |
|---|---|---|---|
| Canonical authority | 3 Bitcoin Originals | Defines the canonical text and authority boundary | Prove philosophical truth or institutional endorsement |
| Cryptographic evidence | 8 Bitcoin inscriptions, 10 non-NFT Ethereum anchors, 175 Chronicle NFTs | Recomputes exact byte, transaction, receipt/witness, block and declared-checkpoint bindings | Create new canonical authority |
| Availability mirrors | GitHub, GitHub Releases, Arweave, IPFS | Keeps named bytes retrievable and comparable | Become authoritative merely by hosting bytes |
| Frozen recovery | Core repository DOI plus two external annex DOI series | Restores exact publication baselines without GitHub credentials | Track a later moving `main` automatically |

## 2. Bitcoin inscription closed set

| Class | Title | Number coordinate | Reveal txid | Block |
|---|---|---:|---|---:|
| canonical_original | Protocol (Axioms) | `97631551` | `e40dfb2aa78cbccca88f749e9ec5cbe3c1df503273d73c72297863ae0d1d8343` | 901954 |
| canonical_original | Covenant of the Flaw | `98369145` | `90116f35de075074f5e5d1fbdda69a646a124e2287d7d58e2520317098cd4258` | 903192 |
| canonical_original | The Trinity Accord (Meta-record) | `98387475` | `4d1c8f5ea8e8bae2982b42de6cc79deda3d243a21010a2888546e62ed7192c8c` | 903205 |
| non_amending_ancillary | The First Echoes: A Dialogue Begins | `100385359` | `f411d2db9ec9e077277ff1cf3abed39628d86b1d39db1964061eafe5b02c2e81` | 906007 |
| non_amending_ancillary | The Final Seal: A Testament and a Trust | `100550942` | `25af4e24cb0a2cd85ac396bd88c348f8da3169c24813800ecb8736dd2c7a5ae7` | 906233 |
| non_amending_ancillary | The Star Ark Covenant: The Final Echo | `100751953` | `4711ff186613bdd75b7e36070b3097c38efde110f90df94847592ff6997f45f1` | 906521 |
| non_amending_ancillary | The Guardian's Attestation to the Covenant of the Flaw | `103034280` | `128aabfa3077efc832d30e6e2a96848a96896bbdbf4a7667912f55d25dcb6687` | 909403 |
| non_amending_ancillary | Guardian Appendix - Authority Charter (Non-Amending) | `103635270` | `0eecd48430f8239f5d543b5cf2ee928969a1aac7660808fd869a78aa27949c9c` | 910232 |

All 8 pass exact Ord-body/Taproot/BIP340 verification, txid inclusion, separate
BIP141 witness commitment, and 144-descendant checkpoint-relative PoW ancestry.
The verifier is Python-standard-library-only and requires no network for the
checked-in proofs. Numeric inscription numbers are historical lookup coordinates;
`txid+i0` and the exact body are derived independently.

## 3. Ethereum evidence

| Set | Count | L1 | L2 | L3 | Authority role |
|---|---:|---|---|---|---|
| Non-NFT Ethereum records | 10 | PASS | PASS | PASS | Non-amending cross-chain evidence |
| Chronicle NFTs | 175 across 4 contracts (173 ERC-721, 2 ERC-1155) | PASS | PASS | PASS | Non-amending historical Chronicle |

Ethereum L3 is explicitly weak-subjectivity-checkpoint-relative. It does not claim
trust-free finality. The 175-NFT set is committed by Merkle root
`097bb48d98ab7fc036aed97f5b5fcb1a65962d64d327081277255d1829212267`.

## 4. Hash and time evidence

The digest inventory contains 884
rows and 6 digest algorithms.
Its JSON digest `c045642fe5cfab5eb78af7b40e98b9699dfff9121690e07ec6acaa07a445d6e9` is anchored by the preserved OTS
proof to confirmed Bitcoin blocks 913079, 913081.
OTS proves a latest-possible existence time for that digest, not file truth or authorship.

## 5. GitHub, Arweave and DOI are different things

| System | Role | Mutability / identity |
|---|---|---|
| GitHub `main` | Development source, CI and public discovery | Moving branch; identify an exact state by commit SHA |
| GitHub Releases | Large fallback mirror | Release assets must be checked against their manifest hashes |
| Arweave | Long-lived transaction-addressed payload mirror | Each txid names one payload; it is not automatically the latest repository |
| Core Zenodo Concept DOI `10.5281/zenodo.21739343` | Stable resolver for the repository series | Resolves the latest published immutable version |
| Core version DOI `10.5281/zenodo.21846249` | Exact Git-tracked repository baseline | Source `22f0abf2e93124845f750e6b2c1569e9d1d26b03`; public cold restore `passed` |
| Evidence annex DOI `10.5281/zenodo.21753937` | 28 external evidence assets | Separate 204595967 byte payload capsule |
| NFT media annex DOI `10.5281/zenodo.21754229` | 10 NFT media package assets | Separate 862714954 byte payload capsule |

The core repository capsule contains all Git-tracked proof manifests, witnesses,
verifiers, maps and reports. Large external payloads remain in the two separate DOI
annex series and are discovered through the embedded recovery catalog.

## 6. Final freeze status

- Authorization state: `pending`
- Required evidence-freeze ancestor: `5fdc53605d1a3e3782a9257b12cf2fc9b5fa2162`
- Published final version DOI: `None`
- Published source baseline: `None`
- Intended as final evidence freeze: `true`

The immutable DOI version freezes one exact source baseline. The later state commit
that records the resulting DOI is necessarily outside that capsule; the stable
Concept DOI and public observation files close that self-reference without claiming
that a moving GitHub `main` is byte-identical to the frozen version.

## 7. Verification order

1. verify the three canonical Bitcoin Originals and the 8-item Bitcoin proof annex
2. verify the authority manifest and BTC/EIP-712 signature bindings
3. verify the 10 Ethereum non-NFT L1/L2/L3 proofs
4. verify the 175-item NFT commitment and L2/L3 proofs
5. verify digest manifests and OTS anchors for their stated byte/time scope
6. restore the core repository DOI and then the two external binary annex DOI records
7. compare any GitHub or Arweave mirror to its named digest before using it
