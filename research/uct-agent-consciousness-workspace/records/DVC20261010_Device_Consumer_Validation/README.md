# DVC20261010 — Device consumer validation

This record combines retrospective public tactile-data analysis, a review of a published apparatus and its documented interfaces, and a finite digital model of source arrival, latching and consumption. It is a subsequent supplement to SCU v1.0.1, [DOI 10.5281/zenodo.23272690](https://doi.org/10.5281/zenodo.23272690), and does not modify that published paper. The DVC candidate remains disabled and a standalone paper is held.

## Read first

- [RESEARCH_NOTE.md](RESEARCH_NOTE.md): integrated findings, evidence classes, limits and UCT interpretation.
- [PROBE_PROTOCOL.md](PROBE_PROTOCOL.md): the proposed acceptance package for one actual installation.
- [apparatus_evidence/MAIN_FINDINGS.json](apparatus_evidence/MAIN_FINDINGS.json): exact public-data results and unresolved application premises.
- [apparatus_evidence/RESPONSE_CODING_CORRECTION.json](apparatus_evidence/RESPONSE_CODING_CORRECTION.json): effective coding-provenance qualification; numerical outputs are unchanged.
- [device_model/RESEARCH_NOTE.md](device_model/RESEARCH_NOTE.md): detailed proofs, event semantics and counterexamples.

## What was completed

The [public-data component](apparatus_evidence/README.md) includes 18 participants, 9,704 command-range records and 108 participant-condition cells fitted under two analysis specifications. The [digital component](device_model/EXACT_RESULTS.json) exhausts 720 event orders, partitioned into six intended-current-pair executions, 360 premature-consume attempts and 354 matching-output executions with an unintended source token. Numerical fits, model schedules and people have different denominators.

No new human observations or hardware deployment occurred. The archive does not establish a motor-only `10` branch at a human neural consumer. PSE is a future endpoint choice, not retrospective preregistration; fitted sigma and source-labelled JND remain separate. Agency, ownership, familiar H and actual RetBind are not established.

## Preservation and reproduction

The original model package is retained under `device_model/`; its [manifest](device_model/ARTIFACT_MANIFEST.json) binds those bytes. The selected evidence package is under `apparatus_evidence/`; its [copy manifest](apparatus_evidence/COPY_MANIFEST.json) identifies the supplied files and source provenance. Each component contains its own code, run/audit results and reading scope. Consult their reproduction instructions and run scripts in a working copy when preserving the frozen receipts.

The root map and combined result record integrate these scoped components. A local PASS does not establish hardware support, complete historical semantic proof or an additional experience-existence criterion. Those obligations remain explicit in the component contracts and the parent research audit.

## Integration and review records

- [MAP_AUDIT.md](MAP_AUDIT.md) and [ALL_MAP_CORE_REVIEW_SUMMARY.json](ALL_MAP_CORE_REVIEW_SUMMARY.json) define the actual core-layer coverage and remaining depth.
- [FAILURES.md](FAILURES.md), [GAP_LEDGER.md](GAP_LEDGER.md), and [REVIEW_RESPONSE.md](REVIEW_RESPONSE.md) preserve failed inferences and uncompleted scope.
- [HANDOFF_ZH.md](HANDOFF_ZH.md), [WORK_LOG.md](WORK_LOG.md), [SOURCE_READING_RECEIPT.json](SOURCE_READING_RECEIPT.json), and [DUAL_SAVE_RECEIPT.json](DUAL_SAVE_RECEIPT.json) support continuation.
- [CONCURRENT_CBI_RECONCILIATION.md](CONCURRENT_CBI_RECONCILIATION.md) deducts concurrent results and corrects citation metadata without rewriting their history.

## Concurrent EIP reconciliation

The last pre-save ref check found EIP at d8c94faa846fc4d459628c9bc896adfb4a038d7e. Its exact files and disabled 6/3/5 candidate are preserved. The arrival/read and redundant-writer boundary is additionally deducted from DVC novelty; no frozen DVC component claim or public SCU file changes. See [CONCURRENT_EIP_RECONCILIATION.md](CONCURRENT_EIP_RECONCILIATION.md). Current coverage is UCT-PUB-v1.0.22, following EIP v1.0.21.
