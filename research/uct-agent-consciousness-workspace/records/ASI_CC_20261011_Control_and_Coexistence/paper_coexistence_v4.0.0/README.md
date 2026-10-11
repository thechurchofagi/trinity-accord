# PR-v4.0.0 Research Package — Coexistence Without Presupposed Subjecthood

**Manuscript:** paper/manuscript.pdf — 14 A4 pages (the earlier 16-page progress note was inaccurate).
**Source:** paper/manuscript.tex — LaTeX self-contained.
**Programs:** src/revocation_frontier.py, src/service_handoff.py.
**Data:** data/frontier_v4.json, data/service_results.json.
**Review:** audit/ includes prior art, critical audit, failure corrections, work log, baseline regression and publication coverage.
**Status:** Complete research revision for independent critical review, not peer reviewed, not registered as DOI, not a formal UCT graph theorem.
**Scope:** All live evaluations are local deterministic backends and simulated logical reserve slots; no frontier LLMs or consciousness experiments.

## Rerun commands from package root

```
python src/revocation_frontier.py --out data/frontier_v4_rerun.json
python src/service_handoff.py --out data/service_results_rerun.json
cd paper && pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
```

Original generated data are retained. The quantitative rules have strong restrictive assumptions: precommitted fallback, trusted timely evidence, and no secret adaptive router. See the paper, handoff, and internal critical review. This package does not certify real-world AI safety.
