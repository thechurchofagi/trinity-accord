# When Revocation Does Not Restore Safety

Hongju Liu · ASI-CC-v1.1.0 · 11 October 2026 · 12-page English research draft.

This is a revision of the unpublished `endogenous_coexistence_v1.0.0` manuscript, not a new public DOI. Already published PR-v6.0.0 (10.5281/zenodo.23295776) is unchanged. The paper separates current authority, historical authority and durable effects, applies a classical backlog bound to continued protected service, and tests policy-epoch resets and recovery-backed admission.

## Source and reproduction
The full typesetting source is split into three byte-preserving sequential parts. `paper/manuscript.tex` inputs them. Concatenating part01.tex, part02.tex and part03.tex produces the single-file source delivered in the conversation archive.

```sh
python -S src/recovery_frontier.py --out data/recovery_results.json
python -S src/effect_escrow_demo.py --out data/effect_demo_results.json
cd paper
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
```

The two scripts use only the Python standard library; the process demo needs Unix pipe readiness. They modify only their temporary SQLite files and child processes. No model API, real service account or administrator rights are required.

## Actual preservation scope
This repository entry contains the entire editable manuscript, both actual executed scripts, results summary, run receipt, claim index, Chinese handoff, work log, prior-art/critical review and disabled map/coverage records. Full raw result JSON, predecessor source archive and rerun data, compiled PDF, final file manifest and build receipts are supplied in the downloadable research ZIP attached to the author conversation. Data paths named in INDEX.json are reproduced by the commands above; the raw JSON and binary PDF are not asserted to have been uploaded to this repository entry.

## Status and limits
All 119 stale-token replays were rejected, yet some variants lost the modeled service. Positive escrow variants do not create missing recovery capacity, and deferral is not counted as complete on-schedule admission. The database capacity and recovery model are controlled software objects, not physical electricity, human wellbeing or consciousness. The network-calculus bound and reservation techniques are inherited; exact combined application priority is unverified.

`audit/WORK_LOG.md`, `audit/PRIOR_ART_REVIEW.md`, `audit/CRITICAL_REVIEW.md`, `audit/MAP_EXTENSION.json` and `audit/PUBLICATION_COVERAGE_UPDATE.json` record the scoped review. Full historical UCT semantics are not reverified. Formal UCT-MAP-v1.1.2 and coverage baseline UCT-PUB-v1.0.33 stay unchanged. The candidate remains PENDING_MAP and is not peer reviewed. No DOI/OTS/Arweave action or Library write is claimed in this revision.
