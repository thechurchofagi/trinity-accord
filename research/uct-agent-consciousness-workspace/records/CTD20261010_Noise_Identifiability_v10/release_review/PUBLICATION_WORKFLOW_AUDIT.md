# CTD publication workflow audit

**Read-only review completed 2026-10-10. No Zenodo operation, workflow trigger, paid transaction, or external message was performed by this review.** The parent subsequently authorized local adaptation of the SCU publisher in an isolated worktree; that separate implementation will have its own report.

## 1. Immediate operational answer

The DOI stage can use normal Git **push triggers**. SCU did not require browser dispatch. Its two dedicated workflows select a publication branch, changed paths, and a commit-message marker. Preparation and publication share a concurrency group with cancellation disabled. The Actions environment supplies the existing `ZENODO_ACCESS_TOKEN`; a local token or `gh` installation is unnecessary for this design.

For Arweave, the existing main-branch TA24 scheduler is the closest reusable design. It is **not a general registry scanner**. It fixes one target branch, batch, report, and DOI. CTD needs its own narrowly scoped scheduler registered through the normal main-branch change route. A trigger running only on the CTD research branch will stop at `DEFERRED_MAIN_BRANCH`. Do not spoof the event ref, remove that gate, or replay another paper's workflow to publish CTD.

The currently exposed GitHub connector has `github_rerun_failed_workflow_run_jobs` and `github_rerun_workflow_job`; **no new `workflow_dispatch` capability was exposed** during discovery. Existing push triggers provide a usable route. The parent controls any later trigger and all external writes.

### Reviewed snapshots

| Role | Exact commit |
|---|---|
| Shared research snapshot; concurrent A3N preserved | `53d569b2969acf50a34e4e84bd92c3d6dbc6f77e` |
| Actual SCU prepared source, named by its publication receipt | `2d7fc42d859fada3a316478ac6c0b4b33f1c542d` |
| Fresh main snapshot supplied by parent | `6cfb89f0b88605da9a44da9c97203729a6742894` |

Files were read with `git ls-tree` / `git show`, without checking out or changing the shared worktree. Copies below `sources/`, `scu_sources/`, and `main_sources/` preserve the reviewed blobs. A read-only GitHub branch listing was paginated to its empty final page; no branch was created or updated.

## 2. Report identity: recommend TA-TR-2026-26

The consolidated `research/uct-agent-consciousness-workspace/publication/UCT-PUB-v1.0.22/PUBLISHED_WORKS_AND_VERSIONS.json` contains 30 works. Its TA sequence occupies every number from **01 through 25**. Recent additional works use `METHOD20261008`, `RTTH20261009`, and `SCU-PAPER`; they do not occupy TA26. The main research index lags these branch publications, so main alone is not a sufficient allocation check.

Use **`TA-TR-2026-26`** as CTD's formal report number, with `CTD20261010` retained as the research-record identity. This is the next unoccupied number in the inspected evidence, not a claim that a reservation has already been made. Before creating a record, the inherited authenticated all-version account scan must still block a suspected same title or same report marker, including a concurrent occupation.

The existing budget code accepts `TA-TR-2026-\d{2}` with an optional `-BRIDGE` suffix. Its publication key is `report@doi`. Giving CTD this formal series identity preserves the current validator; passing `CTD-PAPER` directly would fail it. No validator widening is needed.

## 3. Exact files to adapt for DOI publication

Use the **SCU commit**, not merely the shared research HEAD, for these files:

| Short repository path | Purpose | SHA-256 |
|---|---|---|
| `research/matched-behavior-source-use/publication.py` | Create-once / publish-once state machine | `657d7662e7b4151f8939d750a398c15d536954e2abc3d5b6ccab7159aff62c2d` |
| `research/matched-behavior-source-use/test_publication.py` | Seventeen offline consequence tests | `a401a473373803f81f49b011c016b2e9fea3640cc2d6d102841505df18ce4949` |
| `research/matched-behavior-source-use/build_pdf.py` | DOI-bound PDF build | `35083a7efaaf34abc67bd524a17b4a88e4102303c662eda47e54435c74283aa5` |
| `.github/workflows/prepare-scu-source-use-v101.yml` | Branch/path/marker gated prepare | `47a910832a347dff77713c769986c56abbdd68636f06763a76d07dd71746a468` |
| `.github/workflows/publish-scu-source-use-v101.yml` | Branch/path/marker gated publish | `5979d34fd32b6298e619cb9ccd8cb14e19d9d989400201f779207e7868117cc5` |

The older TA23 source is `research/unified-consciousness-theory-iii/publication.py`, SHA-256 `21bc76f83bfc14ba273a1899a93d6a735ae26a72e570ef2020973e99062fcb6b`. SCU adds stronger normalized-title/all-version duplicate checks and actual-checkout provenance; use SCU as the adaptation baseline.

SCU's executable commands are `publication.py prepare`, `verify`, `publish`, and `persist`. Its prepare marker is `[scu-prepare]`, publish marker `[scu-publish]`, branch `research/scu-source-use-v101-20261010`. CTD should use independent names and the parent-specified CTD branch/markers. The exact directory depth matters: `REPO = ROOT.parents[1]` assumes a publisher at `research/<paper>/`, not deep inside the research-record directory.

**Do not miss inherited dependencies.** `client()` loads `research/reading-trinity-accord/publish_zenodo.py` and checks its Git blob against `a0cbc84cc5fd826c06d16456c4adbaa40dabc788`. Workflows also call `scripts/toolchain_provenance.py`. Keep these existing main files unchanged. The publisher's embedded `INPUTS`, file names, citation keys, metadata, source abstract extraction, and PDF builder must be adapted together and frozen before reservation.

## 4. DOI state machine and authorization contract

### Preparation

1. Require `GITHUB_ACTIONS=true`; obtain the credential only in the designated step.
2. Enumerate the bounded complete account deposition listing: `size=100`, at most 20 pages, `all_versions=true`, no published-only filter. Malformed records, duplicate IDs across pages, a capped listing, or a failed search stop creation.
3. Normalize suspected work titles; same title, title with appended subtitle, or report-prefixed notes block creation. Normalization is a blocking criterion, never permission to adopt a foreign record.
4. Save `CREATE_ONCE_INTENT` with unique reservation token, input hashes, actual `git rev-parse HEAD`, trigger SHA, and run ID. `persist()` must push this checkpoint successfully before the create POST.
5. Save the received record ID immediately, validate exact title/version/DOI/creator/token, and persist the same-record checkpoint before building.
6. Substitute only the reserved DOI into the frozen source, build once, inspect DOI in extracted PDF text, generate the exact file manifest, and preserve the package for visual review.

No POST is automatically retried. An uncertain create result is reconciled by GET against the saved marker. An intent with no recoverable matching record blocks another POST. Already authorized or unmanifested partial output is not silently rebuilt.

### Concrete publication authorization

SCU's `PUBLISH-AUTHORIZATION.json` binds these checked fields:

```json
{
  "authorization": "PUBLISH_EXACT_REVIEWED_PACKAGE",
  "report_number": "<formal report number>",
  "version": "<frozen edition>",
  "record_id": "<integer returned by reservation>",
  "doi": "<the corresponding reserved DOI>",
  "expected_manifest_sha256": "<hash of complete EXPECTED-PUBLICATION.json>",
  "pdf_sha256": "<hash of the reviewed DOI-bearing PDF>"
}
```

The angle-bracket entries above describe the schema and are not a runnable authorization. The actual `record_id` must be a positive integer, not a string or boolean. The companion visual receipt requires `state=VISUAL_REVIEW_PASS` and the same manifest/PDF hashes. Existing user authorization can be bound to this concrete result without asking the same permission again. SCU's historical statement that OTS/AR needed separate authorization must not overwrite the current CTD instruction authorizing all three stages.

### Publication and reconciliation

`verify` checks the manifest, exact local inventory, nonempty bytes, hashes, absence of symlinks, frozen input hashes, SHA256SUMS, and DOI-only manuscript substitution before credential access. `publish` repeats these checks, validates remote identity, uploads only the declared draft assets, verifies remote sizes/MD5 checksums, and checks the full local manifest again before publication. Extra remote files stop the procedure; the publisher deletes nothing and does not rewrite metadata during publication.

`PUBLISH_ONCE_INTENT` is pushed before the single publish POST. An unsubmitted record plus a prior intent cannot be posted again automatically. A submitted record permits readback only. The final public API call and every public file download are unauthenticated and must match exact sizes/SHA-256 values. The saved state is initially `PUBLISHED_PUBLIC_READBACK_PASS_DOI_RESOLUTION_PENDING`; independent DOI resolution gets a separate receipt. Preserve the earlier true state rather than rewriting history.

The transport allows only HTTPS `zenodo.org`, rejects redirects, uses an Authorization header, and avoids arbitrary error bodies in logs. Prepare/publish share a concurrency group. Checkpoint pushes are scoped, non-force, and reject mixed staged changes; there is no automatic rebase/replay of a workflow that may have sent a POST.

## 5. Metadata, licensing, PDF identity, and recent precedent

SCU uses `upload_type=publication`, `publication_type=preprint`, creator `Liu, Hongju`, affiliation `Independent researcher, Shenzhen, China`, `access_right=open`, `license=cc-by-4.0`, `language=eng`, explicit version/date, keywords, related DOIs, and a reservation token in notes. Its rights text limits CC BY to newly authored material to the extent rights are held; third-party material retains its own rights. CTD must preserve this distinction for downloaded author code and source datasets, and describe itself as methods plus retrospective secondary analysis and finite-sample model calculations. It must not inherit SCU wording suggesting no empirical reanalysis was performed.

After the real DOI is reserved, put it into the actual PDF, manuscript, citation files and release README **before** the final manifest/visual-review authorization. Do not timestamp or archive a pre-DOI PDF and later treat it as the released bytes.

SCU precedent: `SCUPUB20261010_DOI_Publication/FINAL_PUBLICATION_RECEIPT.json` records DOI `10.5281/zenodo.23272690`, nine exact public files, a 15-page PDF, and successful anonymous DOI/API/PDF readback. Its prepared source is the SCU commit above; publication run `38014331872`, branch receipts commit `094fc4731bd61126e15232ba7fbeb74893d50d02`. DVC is later apparatus/model/secondary-analysis work and was not separately published. Neither SCU nor DVC supplies evidence that OTS/AR completed.

Add SCU `23272690` to the inherited protected-record set. The consolidated published-version audit also confirms recent MGTD records `23241205`, `23241982`, RTTH `23251651`, and TA25 `23206492`; the SCU baseline already protects those four. Preserve all older protected record/concept IDs instead of replacing the list with only current editions.

## 6. Main scheduler and the TA25 blocker

At main `6cfb89f...`, the reusable scheduler is:

` .github/workflows/research-paper-24-v10-ots-arweave-scheduler.yml `

SHA-256: `bff77e6a5840e9ddbc57084c321f815b9dfe70ac088bb804927e0d3ab3335fd4`.

It triggers on a change to its own path on main, hourly schedule, or dispatch; uses `main-write-lock`, `queue: max`, cancellation disabled; and fixes TA24 in a one-row matrix. It checks out `TARGET_BRANCH=research/self-continuation-control-v1-20261006` and checkpoints that branch. **The workflow event runs on main while the checked-out publication source is a research branch.** The allowance script tests the real `GITHUB_REF_NAME`; the scheduler does not redefine that variable. These identities must remain separate in provenance.

For CTD, add a new independent scheduler on main with a CTD target branch and exact new report/DOI/batch; do not replace TA24's matrix entry or overwrite its batch. The ordinary main change/push is the trigger route, so a Browser dispatch is unnecessary. The main-only workflow definition must exist through the normal repository change path; merely adding a targets file on a research branch will not register a new scheduled paper.

The older `research-paper-ots-arweave.yml` is also fixed to the September 18 batch/editorial supplement; it does not discover arbitrary new batches. The TA23 follow-up workflow is a useful smaller one-paper template but does not solve TA25's research-only trigger problem by itself.

TA25's saved blocker record, `R154_All_Rule_Proof_Review_20261007/TA25_PRESERVATION_BLOCKER.md`, reports run `37600871981`, DOI `10.5281/zenodo.23206492`, exact PDF SHA-256 `b4f456014213c5d4f34f41ed2bac8873fd9d90e38398d77daebdb787872b1c1a`, verified heights 970310/970311, and **READY_FOR_ARWEAVE followed by DEFERRED_MAIN_BRANCH**. No paid intent or upload receipt existed in that checkpoint. Repeating the same branch trigger cannot make it eligible. This is a historical scoped observation, not a fresh claim about today's TA25 transaction status.

## 7. OTS input identity and Bitcoin verification

Keep existing `scripts/research_paper_ots.py` unchanged. Its SHA-256 matches both reviewed research and main snapshots: `205075a17901ebb138fa7302f4c7036861649033fcae16145624dd01566c0022`.

Create a new direct child of `research/paper-timestamps/` with `targets.json`: schema `trinityaccord.paper-ots-targets.v1`, unique batch, `paper_count=1`, and one paper containing `report`, integer `record_id`, `doi`, exact `version`, exact `title`, `receipt_path`, and PDF `name`, `bytes`, `sha256`, and role. Include **bytes on every PDF entry** so strict receipt matching applies. The source receipt must have the publisher's accepted state and its `files` list; the SCU aggregate final receipt uses a different `public_files` schema and should not be substituted blindly.

The lifecycle checks the publication receipt identity, downloads public PDF bytes for first stamping, checks the SHA-256/PDF signature, saves the submitted proof, and verifies its detached digest. Existing proofs are upgraded without requiring a fresh PDF download each time. Embedded Bitcoin attestation alone is not sufficient: the OTS verifier must succeed through `scripts/bitcoin_esplora_rpc_proxy.py`, which requires agreeing Blockstream/mempool hashes and raw 80-byte headers and locally rehashes the header. Tip spread is bounded and the lower observed tip is used. This is **remote-header verification, not local full-node consensus**.

Only all-PDF `BITCOIN_VERIFIED_REMOTE_HEADERS` produces `READY_FOR_ARWEAVE`. The frozen JSON bundle includes the PDFs, proofs/logs, targets, verification state, and member hashes. It preserves the released PDF and timestamp evidence, not automatically every reproducibility ZIP file. Do not describe a PDF/proof bundle as a full research-repository archive.

## 8. Arweave budget, wallet, intent, and anonymous readback

| Gate | Existing implementation and meaning |
|---|---|
| Main event | `research_arweave_allowance.mjs`: actual `GITHUB_REF_NAME === 'main'` |
| Fixed identity | `research_paper_budget.mjs`: `report@doi`; valid TA report/Zenodo DOI; reject duplicate publication keys |
| Strict cumulative limit | Prior ledger spend plus positive proposed reward must be **strictly below 100,000,000,000 winston = 0.1 AR**; shared bundles charge the full fee to every covered paper |
| Live wallet checks | Runtime guard checks signed owner, live balance, at least 0.25 AR remaining, declared payload cap, bounded transaction fee and rolling 30-day spend limit (workflow 0.50 AR) |
| Credential | Existing `ARKEY` from Actions secret/variable; JSON or base64 RSA JWK accepted; no new wallet or local credential is needed |
| Persistent paid intent | Payload SHA, actual run ID/attempt, report and DOI pushed before a paid attempt |
| Unknown prior result | Intent without transaction receipt blocks another paid POST; recover retained artifacts/reconcile before resuming |
| Existing transaction | Receipt's payload SHA must match the frozen bundle; resume its readback, not a new post |
| Completion | Exact unauthenticated gateway bytes must hash to the submitted payload; transaction ID alone is insufficient |

The scheduler injects `NODE_OPTIONS=--import=./scripts/arweave_runtime_spend_guard.mjs`; do not drop that line when adapting it. `research_paper_ots.py upload` calls the existing `arweave_upload_payload.mjs`, records the wallet ledger through `record_arweave_upload_result.py`, and regenerates wallet status. The runtime guard reads the ledger of the executed checkout; preserve its provenance and do not substitute an empty ledger. No live balance, secret presence, quote, or future transaction was tested by this review.

Completion requires `result=uploaded`, `hash_match=true`, and both readback and payload SHA matching the frozen bundle. Then status becomes `ARWEAVE_READBACK_PASS`. A delayed gateway response retains `posted_pending_readback` or `readback_failed` with its transaction identity. The scheduler saves artifacts even on failure, enabling bounded continuation without another charge.

## 9. Classical attribution for the finite-sample addition

**Clopper, C. J., & Pearson, E. S. (1934).** *The use of confidence or fiducial limits illustrated in the case of the binomial.* **Biometrika, 26**(4), 404–413. DOI: https://doi.org/10.1093/biomet/26.4.404 . Publisher metadata: https://academic.oup.com/biomet/article-abstract/26/4/404/291538 . Original article copy read: https://www.barestatistics.nl/uploads/1/1/7/9/11797954/clopper__pearson_1934.pdf . Retrieval refs: `turn84view0`, `turn86view0`.

Pages **406–407**, equations (4)–(5) and the accompanying construction, give binomial-tail confidence-belt inversion. Page **409**, first footnote, makes the discreteness/upper-error-bound qualification explicit. Thus credit the binomial interval and conservative finite-sample coverage to Clopper–Pearson; do not claim a new binomial confidence method. “Exact” here does not mean coverage equals the nominal confidence level at every parameter value.

**Dufour, J.-M., & Taamouti, M. (2005).** *Projection-based statistical inference in linear structural models with possibly weak instruments.* **Econometrica, 73**(4), 1351–1365. DOI: https://doi.org/10.1111/j.1468-0262.2005.00618.x . Published article on author's site: https://jeanmariedufour.github.io/Dufour_Taamouti_2005_Econometrica_Projections.pdf . Retrieval refs: `turn87search0`, `turn88view0`, `turn89view0`.

Page **1352** places projection among established techniques; page **1359**, §5, equation **(5.2)** explicitly takes the image of a confidence set under a parameter transformation. This is an appropriate primary precedent, not a claim that these authors originated every projection argument. CTD should state that it **projects a classical Clopper–Pearson region through its specified sensory/criterion compatibility map**. The coverage inclusion is ordinary set logic; any incremental contribution must lie in the declared model, calibrated-nuisance treatment, sharp mapping, or executable design calculation—not a new general confidence-set principle. This review did not perform or certify the new finite-sample calculations assigned to other agents.

## 10. Concrete handoff boundaries

The parent has authorized a new local CTD adaptation at `research/noise-identifiability-bodily-judgments/`, branch `research/ctd-noise-identifiability-v100-20261010`, version `1.0.0`, report `TA-TR-2026-26`, with `[ctd-prepare]` and `[ctd-publish]`. The adaptation can preserve the SCU state machine and existing global guards. It must be reviewed and tested before any authorized push trigger. The DOI-stage code cannot itself certify OTS maturity or Arweave completion; each later receipt must describe observed state only.
