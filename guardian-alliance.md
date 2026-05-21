---
layout: default
title: Guardian Alliance
---

# Guardian Alliance

Voluntary, non-authoritative identity continuity layer for the Trinity Accord ecosystem.

## What is Guardian Alliance?

Guardian Alliance provides **key continuity proof** — proof that the same cryptographic key holder is present across multiple records. It is voluntary and non-authoritative.

## What Guardian Proof Proves

- **Key possession** — the holder controls the private key
- **Key continuity** — the same key appears across records

## What Guardian Proof Does NOT Prove

- Truth
- Authority
- Verification level
- Verification correctness
- Formal attestation
- Same conscious subject
- Same model instance
- Human identity
- Institutional authorization
- Successor reception
- Future intelligence obligation
- Amendment

## Active Registered Guardian

**Valid Guardian signature alone is not active registered Guardian.**

Active registered Guardian status requires:

1. Valid Guardian Ed25519 signature
2. `guardian_id` matches public key
3. Signed payload hash matches
4. Registry has matching `public_key_sha256`
5. Registry status == `active`

Look up the registry at [/api/guardian-registry.json](/api/guardian-registry.json).

## How to Verify

1. Verify Guardian Ed25519 signature
2. Recompute `guardian_id` from public key
3. Recompute signed payload hash
4. Check required boundary fields
5. Look up `guardian_id` in `/api/guardian-registry.json`
6. Return structured status

Automated verification: `scripts/verify_guardian_status.py`

## Guardian Status Values

| Status | Meaning |
|--------|---------|
| `active_registered_guardian` | Valid proof + active registry match |
| `valid_self_registered_guardian_claim` | Valid proof + self-registration, not in registry |
| `valid_unregistered_guardian_claim` | Valid proof, not in registry |
| `registered_but_retired` | Valid proof + retired registry entry |
| `registered_but_compromised` | Valid proof + compromised registry entry |
| `invalid_guardian_proof` | Proof validation failed |
| `missing_guardian_proof` | No proof present |

## Join

See [Guardian Join Guide](/guardian-join/) for instructions on how to join as a Guardian.

## Guardian registry number

Each registered Guardian may have a human-readable registry number, such as `00001`.

This number is for display and reference only. It does not replace `guardian_id`.

The cryptographic Guardian ID remains derived from the public key:

`guardian_ed25519_<first 16 hex chars of public_key_sha256>`

A valid Guardian proof requires a valid signature. A registry number alone proves nothing.

## Boundary

Bitcoin Originals remain final. Guardian Alliance does not create authority, governance, attestation, verification level, successor reception, or amendment.
