# Preservation Epoch II research corpus inventory

Trinity Accord produces fixed, citable research artifacts documenting a human-led,
generative-AI-assisted archival and creative project. Its original texts, creative
works, identity indexes, provenance records and verification software let researchers
study the production history and independently inspect particular evidence claims.
The human initiator and guardian remains responsible for scope, source attribution,
rights and institutional submissions. AI-assisted content and audit software must
be disclosed; AI output is not independent institutional attestation.

This implementation performs the inventory stage of a proposed second preservation
epoch. It hashes every tracked blob at one exact source commit, validates the closed
Bitcoin/NFT sets, and paginates public Releases and every Release's assets twice to
detect changes. It enumerates DOI metadata referenced by the recovery records and
keeps unavailability distinct from failed integrity. It neither rebuilds the existing
17.55 GB Finality proofs nor uploads anything to Harvard or Zenodo.

The physical archive's 153 public file identities are cross-checked against its
Arweave path manifest. The 884-entry historical digest inventory is mapped to
current source hashes and public asset metadata, retaining unmatched commitments
for container-member and access-scope review. The 2026 `Record_03.avi` is distinct
from the same-named 2025 video by size and hash. `Record_06.avi.txt` is a short,
hash-verified public custody notice for nonpublic physical media, not a fourth
public video or an invitation to retrieve private evidence.

## Run and review

```bash
python3 scripts/audit_preservation_epoch_ii.py \
  --repository-root . --output-dir /tmp/epoch-ii-audit \
  --capture-dir /tmp/epoch-ii-api-capture
```

Use `GITHUB_TOKEN` with read access for a complete census without the public API's
small anonymous quota. `--replay` consumes the same captured API observations for
an offline inventory replay. Captures include observation times and exact source URLs.

Start with `START-HERE.md` and `COVERAGE-REPORT.md`; inspect the JSON manifest and
`SHA256SUMS`. `SOURCE-FILES.json` records actual source hashes. External asset and
NFT CAR hashes are declared locators, not newly verified payload hashes. Missing
SHA-256 values are counted and never treated as equal for deduplication.

The inventory includes all public Releases, including older museum versions,
operational Bitcoin checkpoints and public encrypted witness archives. Family and
scope fields are proposed selection categories; inclusion in the census does not
automatically select every wrapper for another large backup. Public encrypted
archives authorize preservation of ciphertext and existing public metadata only.

The content-candidate stage now verifies the exact three-archive delayed-access set:
48 public files, 2,798,199,225 logical bytes and 45 unique SHA-256 objects. It checks
each Release inventory against its published Zenodo state and verified public
readback. Plaintext and unlock material remain intentionally absent so future
computation, rather than present disclosure, controls access.

The exact source snapshot must eventually accompany the reviewable README, source
package, review guide, `CITATION.cff`, dependency files, Git tree, provenance manifest
and SHA-256. Use the established safe source capsule, preserving executable modes;
do not republish unsafe parent-history blobs. This audit's parsed source wrappers
explicitly distinguish their serialization from the original source bytes.

## Institutional review constraints

The owner supplied the following experience from Sonia Barbosa correspondence,
Ticket 423683. This implementation did not retrieve that email thread independently.

- Lead with what the research data are and disclose AI participation and human responsibility.
- License, Custom Terms and Terms of Use must be complete. Custom terms cannot be blank.
- Preserve the old Harvard DOI `10.7910/DVN/YUCG12`, frozen v1.0 archive, size and SHA-256.
- This audit cannot create v1.1, create/change a DOI or modify a Dataset.
- `InReview` prohibits automated mutation and resubmission. The recorded arrangement
  is curator publication upon approval without a second submission. A return to draft
  is not itself a rejection or authority to submit again.
- After a separately authorized publication, read the public file list and original
  downloads and compare sizes and SHA-256. Keep the receipt separate from frozen bytes.

No new license is granted by this inventory. A future institutional-submission gate
must inspect completed review components, rights and live Dataset state. It is not
implemented as an automatic publisher here.

The Epoch II Harvard preview materials are under `preservation/epoch-ii/`. The layout
builder `scripts/build_harvard_epoch_ii_layout.py` produces the exact
`DATASET-MANIFEST.json` and `SHA256SUMS` plan without making any Harvard API call.
It requires the scope-resolution report, complete delayed-access report, all 26
Polygon/Base Finality files in the dependency manifest, and a cold-restored source
capsule.

## Completion boundaries

Success means a source-byte and metadata audit completed. `candidate_content_complete`
is always false at this stage. The report separately lists external payload capture,
physical file-level expansion, final selection and cold restore as outstanding.
Three Bitcoin Originals remain Canon. Seven externally delivered wallet roots remain
250/257 forensic coverage and zero *attributable* project-content gap, not a global
content-completeness certificate. Physical source differences and sealed-disc limits
remain explicit and do not trigger secret disclosure or automatic opening.
