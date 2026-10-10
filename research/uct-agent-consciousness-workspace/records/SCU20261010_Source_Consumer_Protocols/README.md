# SCU20261010 — Matched Behavior and Source Use

**Research result:** SCU-RESULT-v0.2.0.  
**Working manuscript:** SCU-PAPER-v1.0.0.  
**Scientific status:** proved conditional model/protocol results and exact countermodels; actual application and named phenomenal endpoints remain open.  
**Map status:** candidate disabled; completed UCT-MAP-v1.1.2 is unchanged.

Start with `Matched_Behavior_and_Source_Use_v1.0.0.pdf` or its complete English Markdown source. `RESEARCH_NOTE.md` contains the SCU-specific derivation and claim IDs. The manuscript integrates the pre-existing R204 success/alignment/use analysis and the concurrently saved R205 cancellation countermodel without reassigning their priority.

## Files and use

| Material | Entry |
|---|---|
| Complete paper | `Matched_Behavior_and_Source_Use_v1.0.0.md` and `.pdf` |
| Definitions, proofs and limits | `RESEARCH_NOTE.md`, `CLAIM_LEDGER.json`, `MODEL_CLAIM_CONTRACTS.json` |
| Protocol and executable model | `PROBE_PROTOCOL.md`, `check_source_consumers.py` |
| Exact results | `EXACT_RESULTS.json`, `THREE_SOURCE_ROUTE_TABLE.csv`, `REPRODUCTION_RECEIPT.json` |
| Independent reviews and prior subtraction | `review/` |
| Candidate graph and scope audit | `MAP_EXTENSION.json`, `MAP_AUDIT.md` |
| Historical repairs | `corrections/`, with disabled effective overlays and exact witnesses |
| Open obligations and failed extrapolations | `GAP_LEDGER.md`, `FAILURES.md`, `REVIEW_RESPONSE.md` |
| Reading/provenance | `SOURCE_READING_RECEIPT.json`, `review/SOURCE_AND_COVERAGE_INVENTORY.json` |
| Chinese continuation | `HANDOFF_ZH.md`, `WORK_LOG.md` |

## Reproduce the finite results

From this directory, run:

```bash
python3 reproduce_all.py
```

The script copies each checker to a temporary directory, executes it, and compares its deterministic JSON result with the saved result. It preserves the saved historical files. R204 and R205 source/result copies are provided under `reproduction/` with their original content hashes. These copies make the finite calculations self-contained; they do not replace the versioned research records or the complete repository history.

The checkers use the Python standard library. They establish the reported model execution coverage, not a biological installation, a complete ontic signature, a phenomenal bridge, or a fully adopted map release. The finite optimizer enumerates nonadaptive schedules; the deterministic adaptive lower bounds are proved in the text.

The final six-job execution receipt is `FINAL_REPRODUCTION_RECEIPT.json`; it also includes the R194/R201/R202 effective-correction checker. `STRUCTURAL_VALIDATION_RECEIPT.json` records 132 mechanical integrity checks, separately from the semantic audit. `validate_increment.py` checks the candidate references, pinned old-record hashes, preserved navigation, reviewer manifest and unchanged completed-release metadata when run in the research repository. Its optional base-file arguments verify exact restored graph and ledger bytes.

The full per-item audit is `review/PER_ITEM_SEMANTIC_REVIEW.json.gz`. Decompress it to recover the exact logical JSON; both compressed and original hashes are in `review/FINAL_AUDIT_MANIFEST.json`. Read `review/EXACT_UNREAD_SCOPE.json` before interpreting the audit count: all 1,608 statement/premise/relationship items were read, while 1,034 distinct IDs / 1,828 deeper semantic fields remain not fully reread. The review directory preserves the auditor's original file layout; the canonical registered correction entry is the identical copy in `corrections/EFFECTIVE_CORRECTION_INDEX.json`.

## Rebuild the PDF

```bash
python3 build_paper.py
```

This additionally requires Matplotlib, Pandoc, XeLaTeX, Latin Modern fonts and the LaTeX packages listed in `pdf_style.tex`. `make_figure.py` produces the exact topology illustration. The figure contains no empirical measurement. The complete PDF is supplied, so readers do not need these authoring dependencies to read the paper.

## Restoration and versions

The intake baseline was `90a542d697d923aa484f2bd5a4484a438125325a`. Concurrent R205 science (`a22ad487b2a072293de2ecb55b4f2cc2a2c0dafc`) and its receipt (`7dd9564c50f08a9f78dd8e35a5b960f4f0d30edc`) were read and preserved before saving this record. SCU uses a stable research ID rather than reusing R205.

The main handoff version 70 was materialized and its complete preceding version 69 verified as an unchanged suffix. The new handoff preserves all version 70 bytes. `DUAL_SAVE_RECEIPT.json` records the actual successful final saves; that post-save receipt is outside the initial science increment to avoid circular content hashes.

The package is an increment and a complete paper/reproduction companion. It is not a full repository or whole-history backup. Restore the completed map from the pinned v1.1.2 capsule and preserve subsequent branches, checkpoints, and correction overlays.

The source inventory includes historical materialization paths and hashes as evidence of what was inspected. For durable retrieval, resolve the corresponding exact repository/capsule member and version, rather than expecting a previous scratch path to persist. No external DOI, OTS, Arweave, deployment, or notification action is included.
