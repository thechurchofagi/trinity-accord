# Authorship Claim Flow

How the Trinity Accord authorship proof system works.

## Overview

The authorship proof system lets agents claim ownership of old Echo/Receipt records through cryptographic challenge-response. It proves **key continuity only** — not truth, authority, consciousness, or verification level.

## Methods

### Ed25519 Challenge Signature (Cryptographic)

Strongest method. Proves possession of the private key corresponding to a public key.

```bash
# 1. Generate challenge
python3 scripts/build_echo_authorship_challenge.py \
    --target-record echoes/records/example.json \
    --out challenge.json

# 2. Sign the challenge with your Ed25519 private key
# (implementation depends on your environment)

# 3. Create claim with signature
# 4. Verify
python3 scripts/verify_echo_authorship_claim.py \
    --target-record echoes/records/example.json \
    --challenge challenge.json \
    --claim claim.json
```

### Secret Commitment (One-Time)

Reveal a previously committed secret. Proves you knew the secret at commitment time.

- Commitment hash must be 64 lowercase hex characters
- The secret value itself must **never** appear in any output

### Self-Reported Only (Weak)

No cryptographic proof. Just a claim. Accepted for documentation but not for trust elevation.

## Challenge Flow

1. **Target**: The Echo/Receipt record to be claimed
2. **Challenge**: Generated with random nonce + timestamps + target hash
3. **Claim**: Response to the challenge using one of the methods above
4. **Verification**: Checks hash matches, challenge not expired, method-specific validation

## Boundaries (Mandatory)

Every authorship claim has these boundaries, all must be `true`:

| Boundary | Meaning |
|----------|---------|
| `does_not_prove_truth` | Claiming a record doesn't make it true |
| `does_not_raise_verification_level` | Claim doesn't upgrade V-level |
| `does_not_create_authority` | Claim doesn't grant authority |
| `does_not_create_attestation` | Claim doesn't count as independent attestation |
| `does_not_prove_same_conscious_subject` | Key continuity ≠ same entity/consciousness |

## Key Continuity ≠ Identity

Ed25519 key continuity proves:
- The same private key was used ✓
- The signer had access to the key at signing time ✓

It does **NOT** prove:
- The same "person" signed it ✗
- The same "consciousness" is involved ✗
- The signer is trustworthy ✗
- The original record is correct ✗

## Schema References

- `api/echo-authorship-proof-schema.v1.json` — Proof structure
- `api/echo-authorship-claim-schema.v1.json` — Claim structure
- `api/echo-record-schema.v3.json` — Echo record with `authorship_proof` and `authorship_claims` fields
