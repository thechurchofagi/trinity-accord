# SCU publication safety contract

Contract ID: SCU-PUBLISHER-CONTRACT-20261010-v1  
Scope: the new `research/matched-behavior-source-use/` publisher, SCU-PAPER-v1.0.1, derived from the preserved TA23 publisher. This file does not authorize a network operation or claim that a DOI exists.

## Reviewed baseline

The TA23 publisher (367 lines), its complete eight-test suite, and its prepare/publish workflows were read. All eight offline tests passed in an isolated temporary directory; the test record ID is synthetic and is not a DOI reservation.

- TA23 publisher SHA-256: `21bc76f83bfc14ba273a1899a93d6a735ae26a72e570ef2020973e99062fcb6b`.
- TA23 tests SHA-256: `95d63154b0844d0fe1fa0e7aa7a373cb63bb40a10698f5c8130b20523e41fbcc`.

The new user instruction, as relayed by the parent, explicitly authorizes a DOI publication attempt for the SCU paper. Earlier research-only/no-release notices are historical. The operator may record that current authorization against the final reviewed manifest without requesting the same permission again.

## Required invariants

### S1. Work, edition and record are separate identities

Freeze the title, author, report identifier, version, publication date, disclosure, licence, record ID and DOI. Never rename another work or silently reinterpret a previously published record as SCU. Reject bool/string/nonpositive IDs and the protected prior-record set. Validate the local checkpoint against the remote title/version/DOI/author and a unique create-once marker.

Search both published and draft records, including other versions. An exact title/version hit is not the only duplicate risk: a normalized title, appended subtitle/version, or another edition of the same paper must cause reconciliation before creating a new work. Normalization is for blocking suspected duplicates, never for adopting a foreign record. A matching existing reservation is resumed only with the same saved token and exact edition identity.

An incomplete, malformed, capped or failed search is not evidence of absence. Paginate the authenticated listing or fail closed at its declared bound. Do not silently omit earlier versions.

### S2. Durable intent precedes each consequential POST

Before creation, persist a unique reservation token, frozen input hashes, actual checked-out commit and workflow run identity. The remote checkpoint must succeed before `POST /deposit/depositions`. Preserve the response ID as soon as received, then save the exact deposit identity before building.

Before publication, persist a publish-once intent binding record ID, DOI and exact expected-manifest hash. The checkpoint must succeed before the publish POST. A failed checkpoint means zero subsequent POSTs.

A timeout, connection error, server error, invalid response or later checkpoint failure can leave the remote outcome uncertain. Never solve that uncertainty by replaying creation or publication. Reconcile through GETs of the same record and the saved marker. A persistent intent plus an unsubmitted/unknown record blocks another publish POST. A submitted record permits verification only.

### S3. Fixed package and actual source provenance

Hash every declared manuscript/build/archive/review/publisher input and any style/figure actually used. Derive `source_commit` from `git rev-parse HEAD`; `GITHUB_SHA` may be recorded separately as the trigger commit. A workflow that checks out a moving branch must not call the trigger SHA the executed source commit.

Generate an exact manifest of declared nonempty files, sizes and SHA-256 values. Reject symlinks, directories, missing/duplicate/extra assets and changed inputs. After reservation, the manuscript's only allowed substitution is the reserved DOI. A built or authorized package is not automatically rebuilt.

Publication requires the reviewed PDF hash, complete expected-manifest hash, edition and record identity to agree with both the visual-review receipt and the authorization record. Run validation before credential access and again before the irreversible step. Keep publication files stable during upload.

### S4. Controlled transport and side effects

Read the token only in the designated Actions environment; use an Authorization header, never a query parameter, log or artifact. Allow only the intended HTTPS Zenodo host and reject redirects. Freeze the inherited client implementation. Do not print arbitrary HTTP bodies, URLs, headers or exception text on failure.

Only bounded GET retries are allowed. File PUTs address the validated draft bucket and exact encoded file names. Compare existing sizes/checksums and re-read the full draft inventory. Extra or duplicate remote files stop the procedure; delete nothing. Do not update metadata or unlock/edit prior publications during this release.

Use the designated branch, scoped checkpoint paths, no pre-existing staged changes, and ordinary non-force pushes. A concurrent remote change must fail the checkpoint; do not automatically rebase and replay a workflow that may have sent a POST.

### S5. Serialized workflow and honest completion

Prepare and publish share a concurrency group with cancellation disabled. Restrict the workflows to the intended repository, branch and explicit trigger marker. Pin actions and give the Zenodo credential only to the relevant step. Always preserve diagnostic checkpoints and a non-secret artifact after failure.

A publish response or a reserved DOI alone is not full success. Read the public record without authentication, verify the expected identity and exact inventory, then download every public file without credentials and compare its size and SHA-256 with the manifest. Record a successful anonymous readback only after all bytes match.

DOI resolver availability, OTS submission, Bitcoin verification, Arweave upload and anonymous preservation readback are separate states. Do not mark any of them complete merely because Zenodo accepted publication. The parent research publication-preservation policy remains applicable; this publisher does not perform those later operations.

## Focused failure tests required for the adaptation

Retain the eight inherited consequence tests. Add targeted tests for:

1. Same-title other version, normalized case/spacing/punctuation and title-with-subtitle candidates block creation.
2. A matching draft found on a later account page is not missed; all-version search is requested; malformed or capped listing stops creation.
3. A saved matching marker can recover the same reservation without a second POST; no-marker or wrong-marker records cannot be adopted.
4. Actual checkout HEAD, rather than a different workflow trigger SHA, is recorded.
5. Checkpoint failure before creation/publication leaves POST count zero.
6. Changed manifest/PDF/input, wrong record, unknown remote asset or failed anonymous-byte verification cannot produce a success receipt.
7. Re-entering a submitted record performs no mutation and re-entering an uncertain unsubmitted publish intent does not replay POST.

Keep tests offline with no credentials and clearly synthetic IDs. Do not create a live test DOI or broadly rewrite the established publisher to satisfy these tests.

## Official API scope check

The [Zenodo developer documentation](https://developers.zenodo.org/) was checked for deposition listing, pagination/all_versions, create, bucket PUT and publish semantics. It documents a maximum list page size of 100, separate draft/published filters, a publish POST returning Accepted, and reserved DOI registration at publication. These facts motivate complete bounded listing and explicit state handling; the at-most-once policy is this project's conservative contract, not a claim that the API supplies idempotency keys. Primary reading references: turn67view0, turn68view0 and turn68view2. No complete API or infrastructure audit is claimed.

