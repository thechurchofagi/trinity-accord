# Trinity Accord software-resource review guide

This guide was added in response to the Harvard Dataverse curator's request for software-research resources in reviewable formats. It is supplementary only: it does not replace, revise, or amend the preserved full-project archive or the project's three canonical Bitcoin Originals.

## Frozen source identity

- Git commit: `07cd79ba7b98294a0ff9bc45d76f305609f8a0aa`
- Reviewable source file: `trinity-accord-source-07cd79ba7b98.zip`
- Generation method: `git archive` from that exact commit
- Complete tree listing: `SOURCE-TREE-07cd79ba7b98.txt`

The source ZIP is uploaded through a one-file outer ZIP because Harvard Dataverse automatically expands an uploaded ZIP and limits that operation to 1,500 entries, while this exact source snapshot contains 5,379 tracked files. Dataverse expands only the outer transport wrapper, leaving the inner source ZIP as one downloadable and locally inspectable software resource.

## Human- and machine-readable components

- `README-07cd79ba7b98.md`: project overview and navigation from the frozen commit.
- `CITATION-07cd79ba7b98.cff`: citation metadata from the frozen commit.
- `package-07cd79ba7b98.json` and `package-lock-07cd79ba7b98.json`: Node.js direct and locked dependencies.
- `requirements-ci-07cd79ba7b98.txt`: Python dependencies used by repository verification and CI.
- `requirements-ots-07cd79ba7b98.txt`: Python dependencies used for OpenTimestamps verification.
- `harvard-software-review-manifest-v2.json`: machine-readable provenance, preserved-archive invariants, and component hashes.
- `SHA256SUMS-v2.txt`: SHA-256 checksums for the review components.

## Inspection and execution

1. Download and extract `trinity-accord-source-07cd79ba7b98.zip` locally.
2. Start with the root `README.md`, then inspect `.github/workflows/` for the exact automated verification commands and `tests/` for executable tests.
3. For Node.js verification paths, use the frozen lock file with `npm ci`.
4. For Python verification paths, create an isolated environment and install the task-appropriate frozen requirements file, for example `python -m pip install -r requirements-ci.txt` or `python -m pip install -r requirements-ots.txt`.

This repository is an archival and verification system rather than one monolithic application with a single universal start command. Expected outputs are workflow/test pass-or-fail results plus generated evidence and verification reports documented by the corresponding scripts and workflows.

## Rights and scope

The frozen source commit does not contain a repository-wide software license. The Harvard Dataset Terms of Use and component-specific copyright, license, and third-party-rights notices therefore govern. These supplementary review files grant no new license or interpretive, canonical, governance, succession, or attestation authority.
