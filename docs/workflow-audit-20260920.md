# Recent workflow audit — 20 September 2026

Repository: `thechurchofagi/trinity-accord`. Read-only audit window: runs created since 18 September 2026 UTC, queried on 20 September. The failure query returned 99 failed runs across 16 workflow names; these are repeated run results, not 99 distinct bugs. There were also 64 cancellations and no timed-out runs in that query.

## Confirmed fixes

1. **Stale homepage regression expectations.** [Full Integrity run 35431139302](https://github.com/thechurchofagi/trinity-accord/actions/runs/35431139302) failed in `fast-regression`. The tests still required the retired hero wording and propositions-before-overview layout. Executing the rest of that suite exposed the same stale assumptions in the readability, terminology, version-marker and repair checks. Align the tests with the existing English reading homepage, including its triad/cross-chain sections. Retain explicit bounds on length (38,000 source characters; current source approximately 35,500), repetition, authority and overclaims. No homepage or canonical text is changed.
2. **Missing daily-allowance scheduling.** [Research Paper OTS run 35481669772](https://github.com/thechurchofagi/trinity-accord/actions/runs/35481669772) and [papers 07/08 run 35471462947](https://github.com/thechurchofagi/trinity-accord/actions/runs/35471462947) reached the existing `research_paper_ots_archive` daily limit of 1/1. Add a preflight using the existing budget helpers immediately before each upload. Defer new paid attempts when the allowance is exhausted, while allowing payload-matched transaction readback. Keep the runtime spend guard, shared main-write lock, transaction limits and actual archive status unchanged. A successful deferred iteration is not `ARWEAVE_READBACK_PASS`; its step summary and separate scheduling receipt say so explicitly.

The editorial allowance is checked after the original-paper upload, so an upload in the same job cannot leave a stale allowance decision. Scheduling receipts omit a changing wall-clock timestamp to avoid repeated identical-state commits.

## Failures that do not need another code change

| Workflow | Evidence and current interpretation |
| --- | --- |
| Deploy Pages | Run 35479899786 rejected an obsolete source after main advanced. Later [35481555417](https://github.com/thechurchofagi/trinity-accord/actions/runs/35481555417) succeeded. Keep the current-main publication guard. |
| Harvard preservation | Run 35359621344 received HTTP 504 from the dataset lookup. Later [35480572424](https://github.com/thechurchofagi/trinity-accord/actions/runs/35480572424) succeeded. |
| Deep Integrity | Run 35351019572 failed writer-provenance checks; later [35444875868](https://github.com/thechurchofagi/trinity-accord/actions/runs/35444875868) succeeded. |
| Core repository / gateway / record-chain checks | Latest observed main runs 35449875368, 35449875520, 35449875381 and 35449875391 succeeded. Earlier branch failures are not evidence that current main is broken. |
| AI Claimant v1.2 preparation | A descendant-draft identity check rejected an earlier attempt; later run 35449012073 succeeded. Keep the identity guard. |
| Coexistence paper publication | An earlier rendered-manuscript check failed; later run 35347037689 succeeded. |
| Editorial supplement publication | Historical run 35410324589 hit Zenodo HTTP 504. Current main carries `SIX_DOI_METADATA_LINKS_VERIFIED`; the remaining observed failure is the separately budgeted Arweave archive, not proof of a failed DOI publication. |
| Papers 07/08 preservation | Later run 35478750938 succeeded after the earlier allowance failure. The scheduling fix prevents recurrence of the same class of needless paid attempts. |

## Validation

- `python3 scripts/run_ci_group.py fast-regression`: passed, including the complete chained homepage suite.
- Focused paper/editorial/budget/YAML tests: 22 passed.
- Strict parsing and CI alignment: 158 workflows passed.
- Workflow permissions, writer toolchain provenance and main-write safe-push contracts: passed.
- `git diff --check`: passed.

This audit does not rerun historical DOI publication, increase paid-upload allowances, or claim that queued preservation is already complete. GitHub checks on the repair PR provide the subsequent remote verification.
