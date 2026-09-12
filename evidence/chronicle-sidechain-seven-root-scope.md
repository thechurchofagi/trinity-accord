# Seven historical sidechain roots — provenance and scope resolution

## Conclusion

The seven unavailable historical IPFS roots are **not Trinity Accord project-content gaps**.

A reproducible on-chain provenance audit checked all seven ERC-1155 asset coordinates against Polygon/Base transfer history for `0xbc63566a41cbfdb9c266a5941cbe47894daa54a8`.

Result:

- 7/7 were externally delivered and not self-minted by the target wallet.
- 2/7 were minted from the zero address directly to the target wallet by external transaction initiators.
- 5/7 were transferred to the target wallet by external addresses.
- 0/7 transactions were initiated by the target wallet.
- 0/7 contracts are official Trinity Accord NFT contracts.
- Project-content gap count attributable to these seven roots: **0**.

The raw historical fact is preserved: the exact IPFS payload bytes for these seven external-wallet observations remain unavailable. No payload recovery is claimed. The earlier `250/257` figure therefore remains valid as a raw-wallet historical payload observation, but it must not be described as seven missing Trinity Accord works or seven missing Trinity Accord project payloads.

## Reproducible audit

- Script: `scripts/audit-seven-root-provenance.py`
- GitHub Actions workflow: `Audit seven-root provenance`
- Passing run: `34664447583`
- Passing job: `103473421558`
- Audit artifact: `10288620613`
- Source commit tested: `6aeff93510aa7e9f3c2a39ae606d5938174cb656`

The audit is fail-closed: it succeeds only when the live chain data reproduces exactly 7 external deliveries, consisting of 2 zero-address mints and 5 external transfers, with 0 project-originated items.

## Evidence record

The detailed per-item chain, contract, token ID, block, timestamp, transaction hash, sender, transaction initiator, and classification are recorded in:

`evidence/chronicle-sidechain-seven-root-provenance.json`

The operational exception registry remains in:

`evidence/chronicle-sidechain-historical-payload-exceptions.json`

Those seven entries remain marked `historical_payload_unavailable`, but recovery is no longer required for Trinity Accord project completeness. Optional future recovery would be external-asset forensics only.
