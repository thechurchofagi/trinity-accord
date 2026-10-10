# A4A work log

## 2026-10-11 — round start

- Fetched and verified the latest remote branch head `4e38e57f7e617ba6413e70125cbfdaef74675216`.
- Read the mandatory entry sequence, A3Z handoff, persistent master handoff v106, latest review ledger and carried OPEN/ACKNOWLEDGED items before selecting the question.
- Recorded the five-field round question above. No scientific result is claimed at this checkpoint.
- Direction check: the bounded causal-design question serves the experience–organization–mineness problem; it is not a generic control or statistics detour. Return condition: finish once post-treatment matching is classified and one installable protocol/stop rule is stated.

## 2026-10-11 — exact result block

- Read the relevant UCT I v1.2 sections, R157/R173 contracts and A3Z source/anchor/gap files.
- Checked primary causal-inference antecedents for intermediate-variable adjustment, direct/indirect effects and selection/collider bias; no novelty claim is made for those methods.
- Added four exact rational models: post-treatment collider plus common-support trimming, full-overlap weighting sensitivity, formation-path overcontrol, and a pre-treatment positive control. All four checks pass.
- Result: the requested five-way residual is not currently a coherent single estimand. A randomized total formation effect is installable; a controlled direct effect additionally needs physical, route-preserving clamps and joint positivity.
- Direction check after result: PASS. The block clarifies when historical organization can be tested as a contributor to a selected judgment/experiential coordinate and preserves the open phenomenal bridge.
- First full-map validator attempt failed because it searched for the historical raw R173 boundary-rule ID. The effective completed map uses `r175_r173_target_boundary_effective`. The validator and audit were corrected to the effective route; the failure is retained here rather than hidden.

## 2026-10-11 — final audit and navigation invocation correction

- Rechecked every carried OPEN/ACKNOWLEDGED review item before save; none was self-closed.
- Re-ran the exact and scoped application validators after the final direction record and handoff were written; both passed with the application disabled and completed-map counts unchanged.
- The first invocation of the inherited navigation validator omitted its required `--root` argument and failed while looking for `UNIFIED_RESEARCH_INDEX.json` in the repository root. This was an invocation error, not a scientific or graph result. It is retained here; the corrected invocation targets `research/uct-agent-consciousness-workspace`.
- A final clean-checkout run then exposed that `check_exact_models.py` had lost its executable bit while the composed validator invokes it directly. The exact script still passed when called with Python, so this was a packaging/recovery defect rather than a failed model. The executable bit was restored, the composed validator was rerun, and the superseded increment was not treated as the final recovery package.
- A subsequent persistence-metadata edit again materialized the script as non-executable in the working filesystem despite the Git tree mode. To remove this environment-sensitive assumption, `validate_application.py` now invokes the exact checker with `sys.executable`. The validator then passes regardless of the checkout's executable-bit handling; the mode-only repair package is retained as superseded history.
