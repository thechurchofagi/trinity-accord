# PR-v5.0.0 — Causal Independence of Evidence, Resources and Effect-Level Revocation

English 19-page major revision by Hongju Liu (2026-10-11). Same manuscript lineage as PR1–PR4, preserved separately. **Not published, not peer-reviewed, not a universal ASI theorem, not proof of AI consciousness.**

## Scientific question

A strong deterministic AI tool may be revocable by a human principal, yet doing so without disrupting protected human-dependent services requires trustworthy pre-cut routing information, independent fallback capacity, and a complete final effect barrier. Counting signed agent messages and nominal resource copies is insufficient when several have an upstream shared owner.

## Primary new claim

Under a declared one-epoch four-route, one-primary-loss, at-most-one actual root attack, prearmed universal backup slots, one-bit group diagnosis per honest root, no later adaptive routing, and two complete series veto gates, the minimum nominal slots as a function of truly independently compromisable roots is:

- 1 root: impossible;
- 2 roots: 8 slots;
- >=3 roots: 3 slots.

Proof `paper/manuscript.tex`, subsection *Four-channel root–capacity Pareto*. A richer observation, bank-failure witness, trusted adaptive router, or hidden physical bypass changes the conclusion.

## Reproduce

```bash
python src/root_frontier.py --out data/root_frontier.json
python src/root_pareto.py --out data/root_pareto.json
python src/independent_oracle.py --out data/oracle_results.json
python src/role_protocol.py --out data/role_protocol.json
python src/revocation_frontier.py --out data/frontier_v4_rerun.json
python src/service_handoff.py --out data/service_v4_rerun.json
cd paper && pdflatex -interaction=nonstopmode -halt-on-error manuscript.tex
```

Python 3.10+, standard library, Unix-like child process protocol. Never run on an important host as root needlessly. Parent owns all test processes and keys; positive results **do not independently establish** physical or privileged-root separation. No model API keys or network operations.

`HANDOFF_ZH.md` summarizes claims, validity and open tasks in Chinese. `audit/PRIOR_ART.md`, `audit/FAILURES.md`, `audit/WORK_LOG.md`, `audit/PUBLICATION_COVERAGE_UPDATE.json`, `audit/MAP_REVIEW.json`, `INDEX.json` and `MANIFEST.json` make status and provenance explicit.
