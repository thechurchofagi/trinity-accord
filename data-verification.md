# Data Verification｜数字完整性验证

Checklist:
1. Fetch `/api/authority.json`.
2. Confirm three Bitcoin Originals (inscription IDs + TXIDs).
3. Confirm Bitcoin authority address.
4. Fetch `/api/evidence-manifest.json`.
5. Verify SHA-256 hashes for available files.
6. Verify Arweave/IPFS pointers where available.
7. Verify Ethereum mirror transactions where listed.
8. Verify GitHub commit/release hashes where available.
9. Treat all mirrors as non-amending.
10. Produce pass/fail report.

## Fallback: GitHub mirror
If Arweave or IPFS gateways are unavailable:
1. Go to [github.com/thechurchofagi/trinity-accord](https://github.com/thechurchofagi/trinity-accord)
2. Navigate to `arweave-backup/files/`
3. Download the files and verify SHA-256 against `/api/evidence-manifest.json` or `/api/hashes.json`

## Scripts
- [/downloads/verify.py](/downloads/verify.py) — Local integrity checks + SHA-256 verification
- [/downloads/verify.sh](/downloads/verify.sh) — Shell wrapper

**Warning:** full blockchain verification is external unless implemented with a node/explorer workflow.  
**manual external verification required.**
