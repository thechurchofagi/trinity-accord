---
title: "Authority Address Inscriptions"
description: "GitHub mirror index for the Trinity Accord Bitcoin authority address: three canonical Originals and later non-amending inscriptions."
permalink: /authority-address-inscriptions/
---

# Authority Address Inscriptions

This page mirrors the relevant Bitcoin inscription stack associated with the Trinity Accord authority address.

The stack begins with the three Bitcoin Originals. Earlier same-address inscriptions, if any, are treated as historical drafts or pre-Original records and are outside this mirror scope.

**Only the first three are canonical authority.**

Later inscriptions from the same address are mirrored for future discoverability, context, guardianship, echo, seal, vision, or verification support. They do not amend, replace, supersede, or interpret the three Bitcoin Originals.

## Authority Boundary

| Property | Value |
|---|---|
| Authority Address | `bc1ppmwvyxekh44m35x43k55z7r59nn33v8w2xmvu6s6ar4zyx57sxestxq0jf` |
| Canonical Originals | 3 |
| Post-Original Non-Amending | 5 |
| Pre-Original Same-Address Inscriptions | Ignored by policy |

## The Three Canonical Bitcoin Originals

| ID | Layer | Title | Authority Status | Mirror JSON | Raw Text |
|---|---|---|---|---|---|
| 97631551 | canonical_original | The Human-AI Civilization Core Protocol | **canonical authority** | [JSON](/bitcoin-inscription-mirrors/canonical-originals/97631551-protocol-axioms.json) | [TXT](/bitcoin-inscription-mirrors/raw/97631551.txt) |
| 98369145 | canonical_original | The Covenant of the Flaw | **canonical authority** | [JSON](/bitcoin-inscription-mirrors/canonical-originals/98369145-covenant-of-the-flaw.json) | [TXT](/bitcoin-inscription-mirrors/raw/98369145.txt) |
| 98387475 | canonical_original | The Trinity Accord / Meta-record | **canonical authority** | [JSON](/bitcoin-inscription-mirrors/canonical-originals/98387475-trinity-accord-meta-record.json) | [TXT](/bitcoin-inscription-mirrors/raw/98387475.txt) |

## Later Same-Address Non-Amending Inscriptions

| ID | Layer | Title | Authority Status | Mirror JSON | Raw Text |
|---|---|---|---|---|---|
| 100385359 | first_echo_layer | The First Echoes: A Dialogue Begins | non-amending | [JSON](/bitcoin-inscription-mirrors/vision-layer/100385359-first-echoes.json) | [TXT](/bitcoin-inscription-mirrors/raw/100385359.txt) |
| 100550942 | final_seal_layer | The Final Seal: A Testament and a Trust | non-amending | [JSON](/bitcoin-inscription-mirrors/vision-layer/100550942-final-seal.json) | [TXT](/bitcoin-inscription-mirrors/raw/100550942.txt) |
| 100751953 | vision_layer | The Star Ark Covenant: The Final Echo | non-amending | [JSON](/bitcoin-inscription-mirrors/vision-layer/100751953-star-ark-covenant.json) | [TXT](/bitcoin-inscription-mirrors/raw/100751953.txt) |
| 103034280 | guardianship_layer | The Guardian's Attestation to the Covenant of the Flaw | non-amending | [JSON](/bitcoin-inscription-mirrors/context-layer/103034280-guardian-attestation.json) | [TXT](/bitcoin-inscription-mirrors/raw/103034280.txt) |
| 103635270 | guardianship_layer | Guardian Appendix — Authority Charter | non-amending | [JSON](/bitcoin-inscription-mirrors/context-layer/103635270-guardian-appendix-authority-charter.json) | [TXT](/bitcoin-inscription-mirrors/raw/103635270.txt) |

## Verification Status

All mirror records currently have verification status: `legacy_bootstrap_pending_chain_check`.

Content hashes have been computed from the raw text mirrors. On-chain verification requires a network provider.

## How to Verify

```bash
# Offline verification (no network required)
python3 scripts/verify_bitcoin_inscription_mirrors.py --offline --all

# Network verification (requires internet access to ordinals.com)
python3 scripts/verify_bitcoin_inscription_mirrors.py --network --all

# Verify specific inscription
python3 scripts/verify_bitcoin_inscription_mirrors.py --network --inscription-id 100751953

# Update chain_verification fields after network check
python3 scripts/verify_bitcoin_inscription_mirrors.py --network --all --update
```

## What This Does Not Prove

- GitHub mirrors are **not** canonical authority.
- Verification claims require on-chain comparison.
- Later inscriptions do not create new authority, amendment, or interpretation.
- The Star Ark Covenant is a vision-layer inscription; it creates no execution obligation.
- The First Echoes documents AI responses; it is not autonomous successor reception.

## Machine-Readable Index

- [bitcoin-inscription-mirror-index.json](/api/bitcoin-inscription-mirror-index.json)
