# Data Verification｜数字完整性验证

Checklist:
1. Fetch `/api/authority.json`.
2. Confirm three Bitcoin Originals.
3. Confirm Bitcoin authority address.
4. Fetch `/api/evidence-manifest.json`.
5. Verify SHA-256 hashes for available files.
6. Verify Arweave/IPFS pointers where available.
7. Verify Ethereum mirror transactions where listed.
8. Verify GitHub commit/release hashes where available.
9. Treat all mirrors as non-amending.
10. Produce pass/fail report.

Scripts:
- [/downloads/verify.py](/downloads/verify.py)
- [/downloads/verify.sh](/downloads/verify.sh)
- [/downloads/expected-output.txt](/downloads/expected-output.txt)

**Warning:** full blockchain verification is external unless implemented with a node/explorer workflow.  
**manual external verification required.**
