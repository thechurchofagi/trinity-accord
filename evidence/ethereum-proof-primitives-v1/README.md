# Frozen Ethereum Proof Primitives v1

This directory is a small, versioned verification dependency shared by Trinity Accord's Ethereum proof annexes.

`ethereum_proof_primitives_v1.py` contains only deterministic offline primitives for:

- Ethereum execution-header hashing;
- transaction / receipt MPT root reconstruction;
- Beacon header SSZ root computation;
- single SSZ Merkle-branch verification;
- Ethereum mainnet Beacon genesis/slot constants used by the frozen v1 proof model.

`PRIMITIVES-MANIFEST.json` records the exact module path and SHA-256. Repository contract tests additionally pin the expected v1 digest to:

```text
d605cc3d7aad3b846d998f4192aae9cceb8ce3c1f0efa4e4578a22a2b5d47dc2
```

## Immutability rule

Version 1 is frozen. Do not modify this module in place. A semantic change must be published as a new versioned primitives directory and the consuming verifier must opt into that new version explicitly.

The NFT verifier directly loads this digest-bound module. The non-NFT Ethereum verifier retains its standalone v1 implementation for compatibility, while permanent parity tests run the complete set of ten real Ethereum witnesses through both implementations. Any divergence in execution-header, MPT, Beacon-header or SSZ behavior therefore fails CI.

This module is a verification utility only. It does not create authority, alter proof bytes, amend the Accord, or turn checkpoint-relative Ethereum PoS finality into trust-free finality.
