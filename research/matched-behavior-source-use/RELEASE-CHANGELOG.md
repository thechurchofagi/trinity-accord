# SCU-PAPER-v1.0.1 release change log

Base: 8bac31cc0b9fb4c70d87f688dabbadeb6166addb. Historical manuscript SCU-PAPER-v1.0.0 is retained byte-for-byte in the research branch.

Changes: preprint status declaration; version and running-header metadata; reserved DOI substitution; fixed-commit research links; self-contained reproducibility and internal-review packaging; data-availability paragraph adjusted to describe the actual selected supplement. No theorem, proof, result count, empirical claim, or C1/U1 commitment is changed. No new hardware result is imported into this edition.

Authorization: on 10 October 2026 the author explicitly requested continued research and an attempt to publish the paper DOI. DOI release is authorized. OTS and Arweave are tracked separately and are not silently represented as complete. An ordinary research-storage commit does not trigger CI; these two narrowly named publication workflows implement the authorized publishing action.

Implementation derives from the repository's create-once TA23 publisher. Safety gates preserve fixed source hashes, account-level same-title/version duplicate search, prior-record protection, durable intent before non-retried POST, exact PDF review, exact metadata and inventory checks, and anonymous public byte readback. Credentials stay in the established GitHub Actions secret and are never exposed.
