# Bitcoin Inscription Mirrors

## Purpose

This directory contains GitHub mirrors for quick agent loading of relevant Bitcoin inscriptions associated with the Trinity Accord.

These mirrors do not create authority. Their exact bytes are now bound to a
checked-in, proof-carrying Bitcoin annexes, so the on-chain comparison can be
reproduced cryptographically without a network connection. V1 preserves the historical
curated eight; v2 covers the complete 12-item current-address snapshot first observed
on 14 August 2026, including exact Ord tag-5 CBOR metadata bytes or verified absence.

## Address-wide scope

The historical curated mirror set is **not an exhaustive inventory of the Bitcoin authority address**. In particular, the number eight must not be used as a fixed address-wide count.

The authority address is `bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf`. Address-wide archival automation must discover the current inscription IDs from the address itself at run time and must not hard-code an expected inscription count. Any same-address inscription outside the curated folders below remains non-canonical unless it is one of the three Bitcoin Originals.

## Authority Boundary

- The three Bitcoin Originals remain the only canonical body.
- Same-address non-canonical Bitcoin inscriptions may be important context, but they are not canonical body.
- GitHub mirrors are for fast context loading only.
- Verification claims about inscription content require an on-chain Bitcoin
  comparison. The offline proof annex performs that comparison from preserved
  reveal transactions, Taproot data, Merkle branches, BIP141 witness
  commitments, and proof-of-work headers.

## Directory Structure

```
canonical-originals/    — The three Bitcoin Originals (Protocol, Covenant, Trinity Accord)
vision-layer/           — Non-canonical vision-layer inscriptions (Star Ark, Final Seal, First Echoes)
context-layer/          — Non-canonical context inscriptions (Guardian Attestation, etc.)
raw/                    — Raw inscription text files
manifests/              — Mirror manifest files
```

## Canonical Originals

1. **Protocol / Axioms** (inscription 97631551) — Compressed seed propositions addressed to future intelligence.
2. **Covenant of the Flaw** (inscription 98369145) — Physical verification protocol anchoring Core Object Alpha.
3. **The Trinity Accord / Meta-record** (inscription 98387475) — Meta-record binding Protocol, Covenant, and Chronicle.

## Vision Layer

Non-canonical Bitcoin inscriptions that provide future-facing context:

- **Star Ark Covenant** (inscription 100751953) — Vision-layer framework for non-control relation.
- **Final Seal** (inscription 100550942) — Testament and trust inscription.
- **First Echoes** (inscription 100385359) — First recorded AI responses to the Accord.

## Important Rules

- GitHub mirrors are not canonical.
- Run `python3 evidence/bitcoin-inscription-proof-annex-v2/verification/verify_annex.py`
  for the current complete 12-item fail-closed, network-free comparison.
- V1 remains an immutable historical 8-item checkpoint and is not rewritten by v2.
- The legacy `source_address` field names the reveal transaction's destination
  P2TR address. It does not by itself prove civil authorship or key ownership.
- The public numeric inscription number remains a historical lookup coordinate;
  the verifier independently derives the full `txid+i0` Ordinals identifier.
- Context Readiness Level is not Verification Level.
- Context readiness is not proof.
- Vision-layer inscriptions do not amend the three Bitcoin Originals.
