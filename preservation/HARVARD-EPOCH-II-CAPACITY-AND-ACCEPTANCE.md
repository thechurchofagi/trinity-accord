# Harvard Epoch II capacity and acceptance assessment

Assessment date: 2026-09-12 UTC. This is a pre-submission review and does not
represent approval by Harvard Dataverse.

## Conclusion

The proposed Preservation Epoch II is technically within the ordinary Harvard
Dataverse service envelope. Harvard's current researcher guidance allows all
researchers, including non-Harvard researchers, to deposit files up to 2.5 GB each
and store up to 1 TB. The 26-file Polygon/Base Finality set totals 17,551,241,826
bytes; its largest file is 943,718,400 bytes. No Finality file needs to be transformed
or split further to meet that limit.

The verified public research-content selection is 4,931,812,359 unique bytes. The
concrete researcher-readable and recovery layout is approximately 23.11 GB and about
420 files, including the approximately 0.52 GB source/review capsule, all 26 Finality
files and all 48 computationally delayed witness files. Together with the old
approximately 1.95 GB Harvard v1.0 Dataset, the known project total is approximately
25.1 GB, far below 1 TB. The exact manifest is regenerated from the final fixed
commit. The actual remaining account quota must still be read from the authenticated
account before upload.

The fee-based Large Data service is aimed at collections over 2.5 TB, very large
file counts and special storage/access requirements. Epoch II has neither condition.
Its roughly 420 planned files also remain far below the examples of tens of thousands
or millions of files used by Harvard to describe Large Data cases.

## Acceptance fit

Harvard Dataverse describes itself as a research data repository open to researchers
from all disciplines. Its curation page welcomes research replication datasets, data
for related publications, and all file types and domains. The Terms define Content to
include information, data, text, software, scripts, graphics and interactive features.

Epoch II must therefore be presented positively as fixed, citable and independently
inspectable research data documenting a human-led, generative-AI-assisted digital
art/protocol project, its evidence relationships, physical-anchor documentation,
175-work Chronicle corpus, verification software and preservation provenance. It
must not be described merely as a website backup or a bulk mirror.

The Polygon/Base files fit this purpose as a fixed, machine-verifiable, noncanonical
cross-chain evidence dataset. They support independent recovery and verification of
published observations. Their inclusion supplies a real second-institution copy;
links to GitHub or Zenodo alone do not.

The three computationally delayed witness archives are also deposit-ready research
data: 48 public files totalling 2,798,199,225 bytes. Their ciphertext, recovery code,
format documentation, checksums, attack-cost benchmarks and verification/destruction
receipts are the complete current public object. The intentionally absent plaintext
is not a missing Dataset file.

## Conditions that remain mandatory

- The depositor must have authority to license every deposited byte for Harvard's
  archiving, preservation and access operations.
- License, Custom Terms and Terms of Use must be complete and mutually consistent.
- The AI-assistance disclosure and the human depositor's responsibility must be
  explicit.
- The 2026-09-12 owner decision authorizes public access to recoverable project
  materials, including historically nonpublic-labelled physical-anchor originals.
  There is no owner-asserted privacy exclusion. Component and third-party rights
  remain controlling, and live credentials or third-party secrets are not research
  payloads.
- The former scope blocker is resolved: the 23 unresolved public commitments and 116
  historically nonpublic-labelled commitments may be published if their exact bytes
  are recovered. They remain commitment-only today; their absence cannot be hidden
  or represented by substitute files.
- The three Bitcoin Originals remain the only Canon; Harvard is a non-amending
  institutional preservation mirror.
- The old DOI `10.7910/DVN/YUCG12` and its released v1.0 files remain unchanged. Epoch
  II must be a separate Dataset/DOI.
- An `InReview` Dataset must not be mutated or automatically resubmitted. Under the
  depositor-provided Ticket 423683 arrangement, the curator publishes after approval
  without another submission.
- After publication, every public Harvard file must be downloaded anonymously and
  checked against the frozen filename, byte count and SHA-256 manifest.

## Remaining uncertainty

Technical fit does not guarantee curator acceptance. Harvard reserves discretion
under its Terms, and the present account's unused quota is not visible to this
read-only audit. The remaining acceptance risk is documentary and legal rather than
capacity-related: clear research-data framing, complete metadata and terms, and
rights-compatible handling of every selected object. The owner's public-access scope
decision is complete, but it does not create rights in third-party material.

## Official sources

- Harvard Dataverse, [For Researchers](https://support.dataverse.harvard.edu/researchers)
  — 2.5 GB per file and up to 1 TB for researchers inside and outside Harvard.
- Harvard Dataverse, [Large Data Support](https://support.dataverse.harvard.edu/large-data-support)
  — ordinary free support up to 1 TB for non-Harvard researchers and groups; Large
  Data services address larger or operationally unusual collections.
- Harvard Dataverse, [Large Data Services and Pricing, updated 2026-03-23](https://support.dataverse.harvard.edu/sites/g/files/omnuum821/files/2026-05/Harvard%20Dataverse%20Repository%20Large%20Data%20Services.pdf)
  — service thresholds, storage choices and file-count/file-size characteristics.
- Harvard Dataverse, [Curation and Data Management Services](https://support.dataverse.harvard.edu/curation-services)
  — research datasets, related publication data, all file types and domains welcomed.
- Harvard Dataverse, [General Terms of Use](https://support.dataverse.harvard.edu/harvard-dataverse-general-terms-use)
  — content scope, depositor rights, privacy and licensing responsibilities.
- Harvard Dataverse, [Preservation Policy](https://support.dataverse.harvard.edu/harvard-dataverse-preservation-policy)
  — multiple storage copies and permanent bit-level preservation of directly
  deposited materials.
