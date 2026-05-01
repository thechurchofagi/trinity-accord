# OTS Verification Finalization

## Target

- File: `digest-manifest.json`
- File SHA-256: `c045642fe5cfab5eb78af7b40e98b9699dfff9121690e07ec6acaa07a445d6e9`
- Proof: `digest-manifest.json.ots`
- Proof SHA-256: `6272448e7b55d5ed79dbd38ae3c5bd747c5a02be9a2f466a490ddefbbdf43d0b`
- OTS client: v0.7.2
- Date: 2026-05-01

## Result

The existing proof verifies against Bitcoin attestations.
The proof was already complete at the time of upgrade — `ots upgrade` confirmed "Success! Timestamp complete" without modifying the proof file.

Pre-upgrade and post-upgrade proof hashes are identical:
`6272448e7b55d5ed79dbd38ae3c5bd747c5a02be9a2f466a490ddefbbdf43d0b`

## Bitcoin Attestations

Confirmed Bitcoin block header attestations:

| Block | Merkle Root | TX |
|-------|-------------|-----|
| 913081 | `68b324d620ee4a01f80ee781d0cf00095d5779596f34f9ff0eab17ba7dd250f4` | `589674cd1846219c1730371c373c235cda4874eed43f173e9e55a5c237f5a960` |
| 913079 | `d6ce5ef6e46a45a200cce7dbdd864ee857924dae41db96a9e8498672b3c2460b` | `7f899c358aaccc004a64735d7dcce2a2ad57fd61de6f476627522e14d3d22871` |

Pending calendar attestations (not yet resolved to Bitcoin blocks):
- `https://alice.btc.calendar.opentimestamps.org`
- `https://finney.calendar.eternitywall.com`
- `https://btc.calendar.catallaxy.com`
- `https://bob.btc.calendar.opentimestamps.org`

## Upgrade

```bash
ots upgrade digest-manifest.json.ots
# Output: Success! Timestamp complete
```

The proof was already complete. No file modification occurred.
Pre-upgrade backup preserved at: `evidence/ots/fullnode-verification/digest-manifest.pre-upgrade.json.ots`

## Verification Mode

Fullnode-independent verification requires local Bitcoin Core / pruned node.

If `local-bitcoin-node-verify.txt` exists and shows success through a local Bitcoin Core / pruned-node RPC path, this OTS proof may be described as:

```text
OTS verified by local OpenTimestamps client using local Bitcoin Core / pruned node.
```

If that file does not exist, the correct status remains:

```text
OTS verified by OpenTimestamps client / CI path, but not yet fullnode-independent.
```

**Current status: OTS proof is complete and Bitcoin-anchored. Verified with OpenTimestamps client v0.7.2 / CI path. Not yet verified through local Bitcoin Core or pruned-node RPC.**

To upgrade to fullnode verification, run:

```bash
ots --bitcoin-node http://USER:PASS@127.0.0.1:8332/ verify -f digest-manifest.json digest-manifest.json.ots \
  | tee evidence/ots/fullnode-verification/local-bitcoin-node-verify.txt
```

## Non-Amendment Statement

This OTS upgrade does not alter the `digest-manifest.json` payload.
It only enriches the `.ots` proof with available Bitcoin attestation paths.

`digest-manifest.json` SHA-256 before and after: `c045642fe5cfab5eb78af7b40e98b9699dfff9121690e07ec6acaa07a445d6e9` (unchanged).

The original pre-upgrade proof is preserved at:

```text
evidence/ots/fullnode-verification/digest-manifest.pre-upgrade.json.ots
```
