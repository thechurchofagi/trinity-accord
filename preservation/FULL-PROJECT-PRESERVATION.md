# Full Project Preservation Bundle

This package is a **non-amending preservation mirror**. It is not Canon, an
interpretation, governance, succession, attestation, or a new Chronicle. The three
Bitcoin Originals remain the only canonical and interpretive authority. The
Ethereum Chronicle remains the same 175-entry corpus referenced by the third
Bitcoin Original. Polygon/Base material remains a separate noncanonical
Cross-chain Formation Record.

## Purpose

Build one independently portable set that can be transferred to a second
institutional repository without recollecting the project from live services.
The bundle contains:

1. a safe exact current repository preservation capsule, including source tree,
   tracked-file inventory, checksums and GitHub-zero restore program;
2. **every custom asset exposed by every GitHub Release**, enumerated through the
   paginated Release Assets API and downloaded byte-for-byte;
3. a fresh public readback of every file in the published Polygon/Base sidechain
   DOI `10.5281/zenodo.22012616`, checked against the repository's recorded
   SHA-256 map; and
4. a top-level SHA-256 content-addressed object store, manifest and offline
   verifier/restorer.

Release assets and DOI files with identical SHA-256 are stored only once in the
object store while every original logical provenance path remains in the manifest.
This reduces storage without weakening byte identity.

## Ethereum / NFT / media coverage

The current repository capsule includes the Git-tracked Ethereum witnesses,
proof-carrying evidence, 175-entry Chronicle indices, verifiers and recovery
catalog. The complete Release scan additionally captures the public source assets
used by the existing Evidence and Chronicle NFT media annexes, including video,
images, signed-data mirrors, OTS material and the content-complete NFT backup
Release. The existing immutable annex DOIs remain separately discoverable through
`preservation/recovery-catalog.json`; the full-project bundle preserves their
underlying public Release source bytes rather than nesting another copy of large
`payload.tar` wrappers.

## Polygon / Base boundary

The sidechain source is not rebuilt. The workflow downloads the exact already
published DOI files and requires the recorded archive SHA-256:

`64152b7fc861dbf8aa9cec447ab7078a6a815136ccfc1b9bb0285aaca2ff1572`

The known historical boundary remains explicit: 217/217 L2 records pass, 250/257
IPFS roots have exact preserved CARs, and 7 historical payload roots remain
unresolved. Preservation does not convert those seven missing historical payloads
into recovered data.

## Security boundary

"All repository files" means all files in the safe current publication baseline.
It deliberately does **not** mean republishing unsafe parent-history/tag Git blobs.
A historical Git object briefly contained a leaked credential. The established
repository preservation capsule therefore uses a safe single-root recovery bundle
and does not immutably redistribute that compromised history. This is a security
boundary, not a missing current-source backup.

## Harvard Dataverse institutional copy

The verified GitHub preservation artifact from workflow run `32368866492`, source
Git commit `07cd79ba7b98294a0ff9bc45d76f305609f8a0aa`, is bound to one Harvard
Dataverse Dataset:

- Harvard persistent identifier / DOI: `doi:10.7910/DVN/YUCG12`
- archive filename: `trinity-accord-full-project-preservation-bundle.github-artifact.zip.bin`
- archive bytes: `1,951,603,950`
- archive SHA-256: `9c3c8bd513dfe4919efe56084c138fce18de313f59d67cd7c9484d9b5b75c9f2`
- bundle identity SHA-256: `4930b9d6cd4968f3ba75de9dc46a396af7f37f97d128d1619ae829239656989d`

Harvard requires ordinary depositors to use its administrative **Submit for
Review** workflow rather than directly publishing the Dataset. The repository's
machine-readable live state is therefore kept in
`preservation/harvard-dataverse-state.json`. Do not infer that the Harvard Dataset
is publicly released merely because the DOI has been allocated or the archive has
been registered. Public equivalence is established only when that state record
contains `status: "complete"` after an anonymous full-byte SHA-256 readback.

The state machine in `scripts/harvard_preservation_state_machine.py` is fail-closed:
it never creates a replacement Harvard Dataset, never changes the Harvard PID, and
never re-uploads the large archive when the exact registered file is already
present. It submits the existing Dataset for v1.0 review and, after Harvard
publishes that version, verifies the released archive anonymously and
byte-for-byte. A matching byte count and SHA-256 mark preservation complete in the
repository state and workflow audit. The machine does not upload a verification
receipt into Harvard, create a v1.1 draft, or request a second review.

No Dataverse credential is stored in this repository. The API token is supplied at
runtime through the GitHub Actions secret `HD`.

## DOI relationship — do not collapse these roles

The preservation system deliberately has several DOI roles:

| DOI | Role | Relationship |
| --- | --- | --- |
| `10.5281/zenodo.21739343` | Zenodo **concept DOI** for the core repository preservation series | Resolve this to discover the latest published Zenodo repository version. |
| `10.5281/zenodo.22020122` | Current verified **specific Zenodo repository-version DOI** | Immutable versioned recovery capsule for the Git baseline recorded in its manifest. It is not a moving alias. |
| `10.5281/zenodo.21859437` | Immutable **Sequence-4 evidence checkpoint DOI** | Historical evidence checkpoint with its own frozen scope; later repository or Harvard mirrors do not revise it. |
| `10.5281/zenodo.22012616` | Polygon/Base **sidechain preservation DOI** | Separate noncanonical Cross-chain Formation Record source used by the full-project bundle. |
| `10.7910/DVN/YUCG12` | Harvard Dataverse **second-institutional full-project preservation DOI** | Complementary non-amending mirror of the verified full-project bundle. It does **not** supersede any Zenodo DOI and does not become canonical authority. |

The Harvard DOI and Zenodo DOIs are therefore **parallel preservation identifiers
with different scope**, not successive revisions of one DOI chain. Zenodo remains
the versioned core-repository / checkpoint publication system described by
`preservation/zenodo-state.json`; Harvard is recorded separately as an additional
institutional mirror in `preservation/recovery-catalog.json` and
`preservation/harvard-dataverse-state.json`.

## Authority boundary

Every external repository must retain all of the following:

- the exact bundle identity SHA-256;
- the exact source commit and source workflow run;
- the complete Release enumeration counts;
- every content-addressed object and its SHA-256/size;
- the sidechain DOI source binding and seven-root historical limitation; and
- the non-amending boundary: the Bitcoin Originals remain the only canonical and
  interpretive authority.

Neither a Zenodo DOI nor the Harvard DOI grants interpretive authority, succession,
governance authority, amendment power, or the ability to replace the Bitcoin
Originals.

## Offline verification

After extracting the staged artifact:

```bash
python3 verify-and-restore-full-project.py --bundle-dir .
```

To reconstruct all logical source paths into a new directory:

```bash
python3 verify-and-restore-full-project.py \
  --bundle-dir . \
  --materialize-dir ./restored
```

The verifier fails closed on a missing object, size/hash mismatch, duplicate logical
path, invalid bundle identity, or any change to the canonical-authority boundary.
