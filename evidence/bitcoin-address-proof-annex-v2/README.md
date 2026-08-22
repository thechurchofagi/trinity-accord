# Bitcoin address proof annex v2

This annex composes the frozen eight-inscription Bitcoin proof annex v1 with four pre-canonical formation records that were later discovered in the complete current snapshot of the same Bitcoin address.

## Authority boundary

Cryptographic proof coverage is not authority. Only the three explicitly designated Bitcoin Originals are canonical. The four formation records are historical/pre-canonical evidence, and the five later records remain non-amending. Sharing an address, receiving L1/L2/L3 proof coverage, or appearing in this annex does not amend or interpret the canonical body.

Stable `txid+iN` Ordinals inscription IDs are the primary identities. Numeric inscription numbers are not used as authority keys. The composed 12-item proof set is therefore a verification set, not a new authority set.

## Twelve-item proof composition

- 8 inscriptions inherit their already-frozen v1 L1/L2/L3 proof witnesses.
- 4 pre-canonical formation inscriptions receive new v2 proof witnesses at the same cryptographic level.
- All 12 are additionally checked for Ordinals tag-5 metadata directly from their reveal witnesses.

### L1 — inscription body, independent metadata, and Taproot binding

For each v2 formation proof, the verifier reconstructs the reveal transaction from preserved raw bytes, recomputes txid/wtxid, parses the Ordinals envelope from the witness, binds the exact body bytes to the address-wide archive, concatenates all tag-5 fields in original order to reconstruct exact CBOR metadata, verifies the Taproot script-path commitment and supported BIP340 tapscript signature, and recomputes the destination P2TR address.

For inherited v1 witnesses, the frozen v1 verifier continues to prove body/Taproot/signature binding; v2 reopens those same reveal bytes to prove tag-5 metadata presence/absence and binds their body hashes to the address-wide archive. Thus metadata coverage is witness-derived for all 12, not inferred from the recursive metadata endpoint.

The DeepSeek-R1 image inscription `8e81cf6054d37dc1f4606fa4f3fba238024292d72511fa70eeee693626271695i0` has two independent on-chain payloads: a WebP body and 2,941 bytes of tag-5 CBOR metadata. L1 binds both to the same reveal witness. The other eleven inscriptions must prove tag-5 absence from their witnesses.

### L2 — block and witness inclusion

The reveal txid must reconstruct the block transaction Merkle root. Its wtxid must reconstruct the BIP141 witness root, whose commitment is proven through the coinbase transaction into the same block header.

### L3 — checkpoint-relative PoW ancestry

The target block header plus 144 descendants must form a contiguous valid-PoW mainnet header chain to an explicit checkpoint observed consistently by two providers. As in v1, this is checkpoint-relative proof, not full-node validation from genesis and not proof that no heavier competing chain exists.

## Verification

After proof material has been captured and committed:

```bash
python3 evidence/bitcoin-address-proof-annex-v2/verification/verify_address_wide_v2.py
```

Ordinary verification is network-free and uses only Python standard-library code plus the frozen v1 proof primitives already preserved in this repository.
