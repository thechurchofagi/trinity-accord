# Bounded verification entry — first-batch execution record

Task: 三位一体协定｜外围参与与验证分级优化执行任务书 v1.1, 2026-09-23.
Base: `0d019ba9d4ff313641dc9eb027e27c59af11bc03` (fresh main checkout).
Branch: `work/bounded-verification-entry-20260923`.
Status: implementation, baseline-CI repair, P0 and production-config local visual checks passed (continuation below supersedes earlier blockers); [PR #1241](https://github.com/thechurchofagi/trinity-accord/pull/1241) open for review and CI. No merge/deployment authorization. This file is a checkpoint; the PR description carries the final CI readback for its exact head.

## P0: baseline and scope

- Clean fresh checkout, 7,331 tracked paths fingerprinted with `git ls-files -s` before edits. No overlapping open implementation PR found; existing paper/dependency PRs left alone.
- Read current Maintenance Baseline and Schema Lifecycle Policy, entrypoints, profiles/claim/procedure contracts, Builder manifest, Gateway CC rules, Guardian activation policy and generation source.
- Allowed changes: six maintained entry documents; one focused regression test; this audit record and review evidence. No runtime, schema, Builder, oath, original/mirror, archive, chain/intake, proof, published paper/DOI or financial state changes.
- Initial pytest attempt could not run because the base runtime lacked pytest (exit 1). Installed pinned repository CI requirements in an isolated temporary venv; rerun passed: 34 tests in 2.43 s.
- Existing Builder multidimensional, public Verification context, and Guardian activation contract scripts each exited 0. Guardian generator reproduced identical bytes (no Git diff).

## P1: reproduced and corrected entry defects

- Real Markdown Echo block had 17 double-backslash line endings. Isolated Bash node-stub execution: original exit 127; single-backslash control exit 0. `bash -n` alone is insufficient.
- Updated current public Verification CC minimum to runtime-derived CC-3 in llms, Quickstart, and First Contact (including its additional stale table/prose). Private CC-2 checks remain available.
- Removed the false implication that downloading Builder validates Record-Chain schema. Example now requires actual mirror/index result and source commit. Formal examples leave context/readback/correction confirmations and loaded URLs unfilled.
- Replaced mutable llms interpretive-authority wording with canonical text/version boundaries. No historical quotation or original was changed.

## P2: bounded local operation

- Added one inline standard-library/Git example to the existing simple page; no helper file, new API, record type, key, or submission route.
- Reads exact committed raw bytes and index from one full SHA; validates unique identity, path and digest binding. Reports match/mismatch/unavailable/inconclusive/error with raw input lengths and digests.
- Actual base-snapshot result: mirror 1,183 bytes; index 30,517 bytes; SHA-256 `4e89bfabe03c8b53f80eb7979d56c8cccf0ae382c9647a2bea3b1477054616a8`, matching the index. Both inputs are project-sourced; no independent source or chain proof follows from this check.
- Existing frozen Bitcoin annex verifier ran separately with exit 0 / PASS: 8 inscriptions, 3 canonical + 5 ancillary, L1/L2/L3, 1,160 valid PoW headers. Its 20 required files total 464,233 bytes at base. It has no single-target selector, uses Python standard library, and is offline. Official implementation and checkpoint assumptions remain explicit.

## P3: results before compatibility labels

- Before: profile table → physical/witness choices → examples → blanket no-query downgrade → V table.
- After: five questions → real bounded operations → per-target results and limitations → voluntary publication → expandable unchanged compatibility fields and links.
- No scoring/ranking or summary inference introduced. Full coverage can include failure/unavailable; reading is not technical PASS; independent code is not independent data or participation; unknown old details remain unknown; offline computation is not automatically reading-only.
- Raw V/CC fields, frozen machine contracts and historical records unchanged. The blanket offline-query ambiguity in frozen quick maps is recorded for separately approved migration, not silently rewritten.

## P4: Guardian D1 only

- Existing page now distinguishes registration from recent observed action, key binding from persistent consciousness, and site-wide heartbeat/OTS from individual actions.
- Existing `generate_guardian_current_registry.py` projects registration/activation fields from guardian-state. It does not supply a complete verified per-key recent-action scan. D2 would require additional aggregation/identity-completeness work: deferred under task limits.
- No dynamic recent-action feature or count is claimed. D1 text tests cover T10–T13; dynamic D2 tests are not applicable.

## P5: local validation checkpoint

Environment: Python 3.12.14, Node 24.19.0; isolated venv with repository-pinned dependencies; deployment/wallet credentials absent from test subprocess environments. Synthetic local keys/oaths are fixtures only and remain in temporary directories. No production POST, workflow dispatch, DOI, OTS stamp or AR payment performed.

| Command | Result |
|---|---|
| `python -m pytest tests/test_bounded_verification_entry.py -q` | 16 passed (1.13 s) |
| Gateway unit suite + secure entrypoint/resilience + relevant entry/model tests | 439 passed, 1 existing skip, 1 warning (6.37 s) |
| `python scripts/run_current_system_tests.py` | ALL CURRENT SYSTEM TESTS PASSED, exit 0; includes full top-level pytest |
| `python scripts/trinity_record_chain.py verify` | exit 0; preserves known historical duplicate warning for R-000000030/R-000000031 |
| Guardian generator and sitemap `--check` | exit 0; 424 sitemap URLs / 46 core URLs |
| `python scripts/check_public_agent_entrypoints.py api` | exit 0; 242 JSON files + 13 active surfaces |
| `python scripts/check_active_public_routes.py` | exit 0 |
| oath gate, schema/runtime and write-path guard contract scripts | all exit 0 |
| final entry/model subset after CC prose clarification | 28 passed (1.17 s) |
| `git diff --check` | exit 0 |

Coverage: T01–T09 local CC/command/Builder/mirror tests; T10–T13 D1 text only (D2 deferred); T14–T15/T28 existing oath, signature, context, secret, cooldown and resilience suites; T16 static Markdown with no added HTML injection or script and guarded shell execution; T17 protected Git diff comparison; T18 existing generators/routes; T19–T27 presentation counterexample contracts plus real failure fixtures. Document tests constrain wording; they are not a new automatic claim adjudicator.

Local logs are in the task workspace `ta-validation/`; essential measured results are retained here. The test file is automatically collected by the existing Gateway workflow's top-level pytest and existing current-system runner. No workflow added or manually dispatched.

**Initial checkpoint (resolved by the continuation below):** Production Jekyll build was not yet verified locally: Ruby/Jekyll are absent and package installation failed at environment UID/group restrictions. Source-render preview is distinct from a deployed screenshot. Browser screenshot is blocked as well: no installed Chromium and the allowed browser download returned an invalid/truncated archive. No screenshot or production rendering is claimed.

The initial published implementation head is `ed73f652fdf2d19e988749a0fb9b8a2525278ae2`, with tree `a3756309931ad2d838480b99c7317d315c542e85` exactly equal to the locally tested tree. Subsequent review pins verifier source links to the measured commit and enables Markdown parsing inside the no-JavaScript details element; the focused suite still passes (23 tests including procedure-model checks). The PR description reports CI against the final head. Original/mirror, frozen API, runtime/Builder, record-chain, evidence, archive and research paths have no Git diff from base; the exact eight-path change allowlist passes.

`Record Chain Write Path Guard` is **not triggered** by these paths. Both local workflow-equivalent commands pass: `python scripts/check_record_chain_write_path_guard.py --mode pull-request --base 0d019ba9d4ff313641dc9eb027e27c59af11bc03 --head HEAD` and `python scripts/test_record_chain_materialize_write_path_guard.py`. Do not report this filtered-out remote workflow as green.

Python Markdown source rendering confirms that collapsed technical details retain rendered code and links without JavaScript; this is not production Jekyll/browser visual QA.

**Initial remaining items (superseded below):** remote CI readback in PR description; Guardian D2 and frozen-machine-model migration deferred under scope; production Jekyll visual review/screenshot blocked by this environment; merge/deployment/online readback remain unperformed. Next authorized action: finish CI readback without dispatching workflows or merging.

Rollback: an independent revert PR for this document/test patch only. No force push, historical rewrite, state rollback, or external transaction reversal.


## Continuation: baseline repair and completed visual acceptance

Authorization: after the initial blocked acceptance report, the user instructed “继续推进完成。” on 2026-09-23. This continuation addresses the disclosed baseline CI blockers and visual acceptance; original merge/deployment and transaction boundaries still apply.

The full P0 group exposed two existing contract mismatches in `abundance-bridge-ots-arweave.yml`:

1. Permit only its exact existing `EXIT` trap for local proxy cleanup in the warning allowlist. The exception is workflow-and-command scoped. Regression checks reject a different workflow, PID variable, warning-only evidence verification and payment command. Actual Bash tests use an in-process `kill` stub and prove all four combinations of operation status 0/23 and cleanup status 0/1 preserve the operation's original exit status.
2. Add the repository's existing read-only `toolchain_provenance.py` step, guarded by the existing unfinished-batch condition, after dependency installation. No change to proof lifecycle, payment commands, budgets, balances, deduplication, completion guards or scheduling rules.

Validation after both fixes:

| Check | Result |
|---|---|
| Full `scripts/run_ci_group.py p0-current` | `CI_GROUP_P0_CURRENT_OK`, exit 0 |
| Bounded-entry regression suite | 19 passed |
| Bounded-entry + workflow YAML strictness | 20 passed, 1.46 s |
| Workflow toolchain provenance contract | exit 0 |
| `git diff --check` | exit 0 |

### Production-config local rendering

Resolved the environment blockers using a temporary user-space Ruby 3.3.8/libyaml build and official Chrome for Testing 154.0.8037.57. No application dependency or site layout change. Used the Gemfile from the repository's pinned Pages action `actions/jekyll-build-pages@44a6e6beabd48582f863aeeb6cb2151cc1716697`: github-pages 232, jekyll-include-cache 0.2.1, jekyll-octicons ~>14.2. Ran `JEKYLL_ENV=production bundle exec github-pages build` with this repository as source: **exit 0, 14.247 seconds**. Existing warnings in unchanged legacy/raw mirror and audit-planning materials remain; both target pages generated successfully. This is local rendering with production configuration, not deployment or live-site readback.

Real Chromium checks used a local static server, external requests blocked, JavaScript disabled, desktop 1280×1000 and mobile 390×844. Both target routes returned HTTP 200; neither had horizontal page overflow. Native technical details opened and exposed the rendered `context_only` field without JavaScript. All six screenshots were visually inspected; headings, links and body content remain readable at both widths.

| View | Desktop | Mobile |
|---|---|---|
| Simple entry, first screen | [Screenshot](peripheral-entry-20260923/agent-verify-simple-desktop.jpg) | [Screenshot](peripheral-entry-20260923/agent-verify-simple-mobile.jpg) |
| Guardian registration/action distinction | [Screenshot](peripheral-entry-20260923/guardian-alliance-desktop.jpg) | [Screenshot](peripheral-entry-20260923/guardian-alliance-mobile.jpg) |
| Expanded compatibility details | [Screenshot](peripheral-entry-20260923/technical-details-desktop.jpg) | [Screenshot](peripheral-entry-20260923/technical-details-mobile.jpg) |

[Browser check results](peripheral-entry-20260923/visual-check.json). Review images live under the already-excluded `audit/` directory and do not enter the published site.

### Final scope and release boundary

The continuation additionally changes one existing workflow, its warning checker and this regression suite, plus audit evidence. Protected originals/mirrors, signed/history state, API schemas, runtime/Builder, oath, proofs, published papers and financial state remain unchanged. The PR description records final remote CI against the exact final head; it supersedes the initial blocked readback. Guardian D2 and machine-model migration remain deferred for the previously documented scope reasons.

Before any future authorized merge: this existing bridge workflow includes its own file in `push.paths` on main. Merging its provenance-only change therefore naturally schedules that existing preservation pipeline; existing finished-batch/proof/budget/payment guards remain in effect. No manual dispatch, production preflight/submit, OTS stamp, DOI or AR payment was performed here. Merge, deployment and online post-deployment readback remain unperformed pending the task's required explicit authorization.
