# DVC20261010 apparatus evidence component

This component selects a real, published active/passive movement apparatus, checks primary sources, actually reanalyses the author's public human dataset, and specifies the additional device evidence required for a source–consumer claim.

Start with `MAIN_FINDINGS.json` for the compact exact summary and affected-premise ledger. Read `DATA_REANALYSIS_REPORT.md` for methods and results, `TIMING_PARSE_REVIEW.md` for raw-row ambiguities, and `APPARATUS_CONTRACT.md` for the proposed external-consumer installation.

The 2026 journal articles are date-verified. The attention study's public data were downloaded and reanalysed, not simulated. The independent analysis uses 18 original participants and 108 participant-condition cells. The 216 numerical fits are two specifications per cell. No new human data or hardware measurement was collected. PSE is a future protocol's selected primary target; this retrospective analysis was not preregistered.

The archive is supplied unchanged under its author's CC BY 4.0 declaration. Attribution: Pierangelo D’Onofrio Pacheco, *Effects of prediction and attention on tactile precision in somatosensory gating--DATASET*, DOI [10.5281/zenodo.18877381](https://doi.org/10.5281/zenodo.18877381), 2026. License: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The accompanying Python analysis and reports are new work; they do not alter or impersonate the source archive.

The published fitting repository and vendor manuals were inspected as source material. Their local caches are excluded from the copy manifest; official URLs, version information and captured hashes remain in `SOURCE_SCOPE.json`. All delivered raw data can also be reacquired with `code/fetch_public_dataset.py`.

## Reproduction

The executed runtime was Python 3.12.14, NumPy 2.3.5 and SciPy 1.17.0. From this component directory, extract the supplied unchanged archive and run:

```bash
python -m zipfile -e sources/Zenodo18877381_Data.zip sources/Zenodo18877381
python code/reanalyse_apparatus_data.py
python code/build_timing_witnesses.py
```

The first command uses the delivered bytes without another network retrieval. The optional `code/fetch_public_dataset.py` retrieves the official source again and checks the fixed archive size, MD5 and SHA256 before extraction; it preserves a changed metadata capture under a separate name. It was provided as a reproducible acquisition script, while the actual initial retrieval was performed separately through the same public API. The component identifier `APPARATUS20261010` in the executed numerical result is subordinate to the parent DVC record.

Map and publication decisions belong to the parent DVC workflow. This component changes no completed-map version and does not publish a DOI.

`RESPONSE_CODING_CORRECTION.json` corrects one provenance sentence in the frozen numerical result: the physical-key to CSV-response conversion was not directly verified. The executed code and numerical output bytes remain preserved; the effective interpretation is conditional and documented in the updated analysis report.
