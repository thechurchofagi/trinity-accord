# Novelty audit: proportional and ordinal cross-task width constraints

**Audit date:** 10 October 2026.  
**Status:** scoped internal and primary-literature review; no worldwide priority claim.  
**Decision:** the defensible contribution is a **new, explicitly restricted secondary analysis of a published intervention dataset**, supported by transparent sharp discrepancy calculations. It is not a new general measurement theory, a first demonstration that two bodily endpoints covary, a first causal perturbation of body ownership, or a validation of UCT C1.

## 1. The contribution that remains available

For one participant, two positive psychometric widths measured under several stimulation conditions are hypothesized to satisfy

\[
W_{tf}=c_t\tau_f,\qquad c_t>0.
\]

The task multiplier must remain fixed across conditions. The strict hypothesis implies equal within-task log changes and constant cross-task width ratios. With two tasks and three conditions it imposes two independent restrictions. The proposed analysis contrasts this proportional model with the weaker state-trace model \(W_{tf}=h_t(\tau_f)\), where the task maps are stable and positively monotone.

The two sharp discrepancy quantities in `theory/THEORETICAL_RESULTS.md` are:

\[
\varepsilon_{\rm prop}=\tfrac14\operatorname{range}_f[\log W_{Of}-\log W_{Sf}],
\]

and

\[
\varepsilon_{\rm mon}=\min_\pi\tfrac12\max_{t,j<k}
[\log W_{t,\pi_j}-\log W_{t,\pi_k}]_+.
\]

These formulas respectively measure the minimum uniform log-cell correction required for proportionality and for a shared nondecreasing order. They make a useful application-specific sensitivity summary. Their ingredients are classical log-additive separability, Chebyshev approximation, and isotonic/state-trace analysis. The word “sharp” describes an attained optimum in the declared information class; it does not establish historical mathematical priority or physiological validity.

The narrow empirical question was not found reported in the inspected D’Angelo main article or supplement, or in the inspected UCT published corpus. That supports recording this as an unreported analysis in the inspected sources. It does not establish that no earlier researcher has ever tested the same restriction.

## 2. Exact external predecessors that constrain the claim

| Source | Existing result or method | Required reuse decision |
|---|---|---|
| D’Angelo, Lanfranco, Chancel & Ehrsson (2026), Nature Communications 17:53, DOI `10.1038/s41467-025-67657-w` | Same 30 participants, 8 Hz / 13 Hz / sham, ownership and simultaneity endpoints; intervention effects in both tasks; BCI uncertainty-versus-prior model comparison; cross-task individual intervention-effect correlations in Supplement Fig. S7. | The experiment, participants, stimulation effects, mechanistic interpretation, and correlations are inherited. The new analysis must credit them explicitly. |
| Chancel, Ehrsson & Ma (2022), *Uncertainty-based inference of a common cause for body ownership*, eLife 11:e77221, DOI `10.7554/eLife.77221` | Individual psychophysics and BCI fitting of ownership; comparison with synchrony judgments; cross-task differences and correlations in common-cause prior. | Joint task comparison and model-indexed psychophysical explanation are not new. A common BCI uncertainty parameter does not automatically imply proportional descriptive Gaussian widths. |
| Bamber (1979), *State-trace analysis: A method of testing simple theories of causation*, Journal of Mathematical Psychology 19:137–181, DOI `10.1016/0022-2496(79)90016-6` | State-trace causal-dimension reasoning under measurement assumptions. | Do not claim invention of the common scalar / monotone endpoint test. |
| Prince, Brown & Heathcote (2012), *The design and analysis of state-trace experiments*, Psychological Methods 17:78–99, DOI `10.1037/a0025809` | Design and statistical analysis of state-trace experiments. | Appropriate design and uncertainty treatment have established precedents. |
| Kalish, Dunn, Burdakov & Sysoev (2016), *A statistical test of the equality of latent orders*, Journal of Mathematical Psychology 70:1–11, DOI `10.1016/j.jmp.2015.10.004` | Coupled monotonic regression, a test statistic, bootstrap calibration, partial-order restrictions, and binomial-data applications. | Especially close antecedent. “We create a method to test shared latent order” would be an incorrect novelty claim. |
| Loftus (1978), *On interpretation of interactions*, Memory & Cognition 6:312–319, DOI `10.3758/BF03197461`; Dunn & Anderson (2026; online 2024), *The monotonic linear model: Testing for removable interactions*, Psychological Methods 31:585–606, DOI `10.1037/met0000626` | Interaction interpretation depends on the theoretical-to-observed map; monotonic transformations and removable interactions are studied explicitly. | Proportional failure is not automatically multidimensional mechanism evidence. |
| Stout (2015; revised 2017), *L infinity isotonic regression for linear, multidimensional, and tree orders*, DOI `10.48550/arXiv.1507.02226` | General uniform-error isotonic regression. | The finite three-condition formula is an elementary specialization, not a new optimization field. |

### D’Angelo’s already published within-person result

Supplement pp. 16–17, Fig. S7 already relates each participant’s ownership and simultaneity intervention effects. For sham-minus-low-alpha effects it reports Pearson \(r=.728\), \(p<.001\), and Spearman \(.702\); for high-alpha-minus-sham effects it reports Pearson \(r=.547\), \(p=.002\), and Spearman \(.545\). Thus it is **incorrect to say the source study only compared group means**. The proposed proportional restriction is stronger than a positive correlation and was not found tested there.

Main article: https://www.nature.com/articles/s41467-025-67657-w  
Supplement: https://media.springernature.com/original/springer-static/esm/art%3A10.1038%2Fs41467-025-67657-w/MediaObjects/41467_2025_67657_MOESM1_ESM.pdf  
Data: https://osf.io/ytga5  
Retrieval handles: `turn31view0`, `turn32view0`, `turn32view2` (supplement); `turn30view0`, `turn30view1` (main). Publication date is 12 January 2026, despite the DOI’s 2025 component.

## 3. Measurement precedents the manuscript should cite

### Yarrow et al. is directly relevant to the width estimand

**Full metadata:** Yarrow, K., Solomon, J. A., Arnold, D. H., & Roseboom, W. (2023). *The best fitting of three contemporary observer models reveals how participants’ strategy influences the window of subjective synchrony*. **Journal of Experimental Psychology: Human Perception and Performance, 49**(12), 1534–1563. https://doi.org/10.1037/xhp0001154.

Author accepted manuscript: https://openaccess.city.ac.uk/id/eprint/30958/1/BayesMLM_SJ%20V7%20APA.pdf  
Repository metadata: https://openaccess.city.ac.uk/id/eprint/30958/  
Retrieval handles: `turn43view2`, `turn47view3`.

Precise locators refer to the **82-page repository PDF**, whose first page is a repository cover; these are not claimed as final publisher page numbers:

- PDF p. 3, manuscript numbered p. 2, lines 30–44: abstract; strategy changes the width of the simultaneity function and motivates distinguishing width from sensitivity or multisensory binding.
- PDF pp. 6–7, manuscript pp. 5–6, lines 123–149: critique of descriptive Gaussian fitting and unqualified temporal-binding interpretations.
- PDF pp. 16–17, manuscript pp. 15–16, lines 333–368: strategy manipulation, competing criterion versus response-scaling explanations, and sample provenance. Twenty observers were recruited; one was excluded, leaving **19 analyzed**, not 20 analyzed.
- PDF p. 64, manuscript p. 63, lines 1335–1346: additive midpoint versus positive multiplicative criterion-width parameter changes. This is a direct precedent for modeling positive parameters on a log scale, although not the present cross-task common-width hypothesis.

The present manuscript should use **psychometric response width** as its empirical estimand and identify a latent temporal coordinate only as an additional hypothesis. A width discrepancy cannot uniquely identify a neural oscillator, an efference-copy route, or an experiential change.

**Correction status checked:** the journal published an erratum in December 2025, *Journal of Experimental Psychology: Human Perception and Performance, 51*(12), 1708, DOI `10.1037/xhp0001226`, PMID 41325147: https://pubmed.ncbi.nlm.nih.gov/41325147/ (`turn54view0`). It reports a missing factor 2 before `l` in four equations. The present paper cites the empirical strategy/width limitation and does not reproduce those equations. Any reuse of the detailed observer likelihoods must use the corrected version.

### Further relevant current primary evidence

Lanfranco, R. C., Katyal, S., Hägerdal, A., Luan, X., Nos, V., & Ehrsson, H. H. (2025). *Conscious awareness, sensory integration, and evidence accumulation in bodily self-perception*. **PNAS, 122**(49), e2503629122. https://doi.org/10.1073/pnas.2503629122. Full text: https://pmc.ncbi.nlm.nih.gov/articles/PMC12704745/ (`turn46view0`). It already compares ownership discrimination with perceptual-awareness sensitivity and reports a stable meta-d′/d′ relation across asynchronies, with a simultaneity control. Its ratio is a different estimand. Both ownership choice and awareness judgments remain measured responses; this is not independent ontic access to experience.

Lanfranco, R. C., Chancel, M., Hasenack, B., & Ehrsson, H. H. (2026). *Disentangling visually driven tactile predictions from multisensory integration in body ownership*. **Royal Society Open Science, 13**(4), 252132. https://doi.org/10.1098/rsos.252132. Author institutional record and article: https://research-portal.uu.nl/en/publications/disentangling-visually-driven-tactile-predictions-from-multisenso/ (`turn48search4`). Occluding predictive visual information changes perceptual bias while sensitivity is retained under the studied conditions. Thus experimentally separating prediction-related information from psychophysical sensitivity is already an active empirical research line.

These sources reinforce the specific measurement limitation. They do not license extending the current data analysis into a comparison of whole consciousness theories.

## 4. Internal published and checkpoint precedents

The local published corpus was searched across 207 text files and text members of four ZIPs. The actual MGTD v1.0.1 archived effective graph was inspected, including relevant node statements, source anchors, and correction status. Its SHA-256 is `943b136a48c40e44a976867604cbb76df5cdf9efcad2975c647970a0f23e7830`, with 722 nodes, 343 active rules and 203 contexts. This is disclosure within a published formal attachment, even when the antecedent record had once been called “pending.”

| Exact antecedent | Already disclosed content | Relationship to this analysis |
|---|---|---|
| UCT I v1.2, DOI `10.5281/zenodo.23131575`, especially complete organization / finite views and C1 interpretation | Experience is associated by C1 with complete token-relative organization; a finite view or fitted estimate is not that organization. Independent endpoint interpretation is required. | Entire ontology/view/measurement separation is inherited. |
| TA15, *Cross-Substrate Phenomenal Comparison*, DOI `10.5281/zenodo.22934654`, §§4–6, 8–9 | Typed transport, semantic calibration distinct from causal correspondence, Lipschitz error propagation, held-out failures, and nonindependent evidence accounting. | Do not recast a “bridge certificate” or held-out test as newly invented here. |
| MGTD v1.0.1, DOI `10.5281/zenodo.23241982` | Typed premise binding, disabled/open application obligations, provenance, map review. | All map discipline is inherited. Candidate status does not establish actual premises. |
| `R168:SHARP_METRIC_ENVELOPE` | \(E(z)=\min\{M,\inf_i[U_i+Ld(z,s_i)]\}\), attained sharp upper envelope for bounded Lipschitz effect functions. | Sharp finite-calibration envelopes are already in the project. The new two-row distance has a different target and geometry; its general extremal method is not new. |
| `R169:METRIC_SCALE_GAUGE_NONENTAILMENT` | Rescaling \(d\) and inversely rescaling \(L\) leaves the envelope unchanged. | Numerical fits do not fix a unique physical/phenomenal scale. |
| `R169:HELDOUT_CALIBRATION_FALSIFIER`; `R169:ROUTE_CALIBRATION_TRIAGE` | Valid lower evidence can refute a calibrated upper budget; invalid protocol, calibration-refuted, certified and unresolved remain distinct. | The present prospective discrepancy tests must retain the same validity/uncertainty separation. |
| `TO20261008:GLOBAL_CLOCK_COMPATIBILITY` | Additive edge-reference cycle sums vanish iff a global temporal potential exists. | A distinct notion of clock compatibility, not a two-task psychometric multiplicative model. No exact result overlap found. |
| `R174:SHARED_TEMPORAL_COORDINATE` | Actual same-episode reference/comparison information used by two named consumers. | A statistical shared width coordinate does not discharge this actual-use relation. |
| `R175:ORIENTATION_ANCHOR_PACKAGE`; `R175:HELD_OUT_ORDER_PREDICTION`, as narrowed by R176 | Two independently admitted endpoint correspondences select increasing versus decreasing chain correspondence; **full-chain correspondence completion**, not independently named held-out content prediction. | Independent orientation anchors and their limitations are inherited. Do not claim the first two-anchor result. |
| R197 (`RESEARCH_NOTE.md`, §§1–4) | Unsigned latent-label symmetry; independently signed fallible endpoint can orient evidence; verbal/nonverbal modality alone is irrelevant; conditional transport required. | Monotonicity’s sign is an additional assumption, not generated by C1 or a width fit. |
| R200 (`RESEARCH_NOTE.md`, §3) | Multiple proxies do not self-anchor latent semantics; report, target, actual use, use evidence and transport remain distinct; interaction is nonidentifying alone. | Same firewall applies to both task endpoints and their stimulation interaction. |
| R201 (`RESEARCH_NOTE.md`, §§1–4) | Binary marker sign certificate \(\delta_C>\beta+\epsilon_0+\epsilon_1\), conditional on positive semantic reliability and actual use. | The proposed continuous monotone calibration gap has a different finite function class; it does not replace or empirically discharge R201’s semantic/drift premises. |
| SCU-PAPER-v1.0.1, *Matched Behavior and Source Use*, DOI `10.5281/zenodo.23272690`, §§2, 5–7, 9–10 and `SCU20261010:C1`–`C8` | Source equality costs under pure/OR consumer classes; source dependence does not identify internal consumption, intake identity or prediction chronology; actual complete binding and separate phenomenal bridge remain open. | Source identification itself is inherited. The present tACS data do not instantiate the independently controlled ports, fixed consumer law or actual route-binding premises. |

R197/R200/R201 describe themselves as unpublished/disabled checkpoints. They are antecedent project results regardless of whether they have a separate DOI. This audit does not upgrade their status.

**Effective-correction qualification.** The subsequently inspected SCU reproducibility archive contains `corrections/R201_R202_CORRECTIONS.md` and `R201_EFFECTIVE_CORRECTION_OVERLAY.json`. R201’s sufficient inequality remains valid, but its original displayed tuples with \(\rho=1,b=1/10\) cannot arise from the stated joint probability model: \(\rho=1\) forces \(H=J\) on supported strata and hence \(b=0\). The correction replaces them with coherent existential witnesses and explicitly withdraws arbitrary-budget sharpness. The present sharp-width calculation must not cite that defective witness as an inherited proof. No new result here depends on it. The correct same-instance rule also separates strict-margin instances from equality/below-margin counterexample instances.

The additional SCU baseline inspected for compatibility is `source_archives/UCT_DVC_SCU_DOI_Increment_20261010/reproduction_baseline/UCT_EFFECTIVE_GRAPH.json`, SHA-256 `0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612`. It contains 913 nodes, 424 active rules, 261 context links and 10 suspended historical rules (1,608 records including those suspended IDs). This extends the older-corpus search described above; its relevant antecedents and archived corrections were read directly rather than inferred from the older MGTD index.

## 5. Optional calibration appendix: specific residual scope

For a feasible common nondecreasing function \(h\) with calibration intervals \(h(a_j)\in[L_j,U_j]\), define \(L(z)=\max_{a_j\le z}L_j\) and \(U(z)=\min_{a_j\ge z}U_j\). For \(x<y\), the proposed exact interval for \(h(y)-h(x)\) is

\[
[\max\{0,L(y)-U(x)\},\; U(y)-L(x)].
\]

This is an elementary monotone partial-identification specialization. The closest inspected internal result R175 fixes orientation between already supplied finite chains; it does not provide this interval-valued monotone effect-gap formula. R168 supplies a sharp Lipschitz envelope with different assumptions and target. R201 supplies a binary semantic reliability/drift margin. The exact interval formula was not found in those sources.

A positive lower gap requires separated constraints inside the target interval; merely fixing an overall range or one internal anchor does not bound local compression away from zero. This is a useful, narrow calibration observation. It should be cited as an extension/application of established monotone bounding, **kept in an optional appendix**, and not counted as a second empirical discovery. The present stimulation dataset does not by itself supply independently calibrated experiential anchors.

## 6. Recommended claims and prohibited inflation

**Defensible:** “We reanalyze a published within-participant intervention dataset using an explicitly stronger proportional psychometric-width hypothesis, compare it with a positively monotone common-coordinate model, and report exact sensitivity distances and uncertainty under stated models.”

**Not defensible:** “We first show that ownership and simultaneity changes covary”; “we invent shared-latent-order testing”; “matching widths identifies a common neural source”; “nonzero individual fitted discrepancy proves separate physical mechanisms”; “the data validate UCT”; “a null test establishes a universal shared clock”; or “the method settles whether AI has consciousness.”

The quality of the empirical analysis, source-data reconciliation, uncertainty propagation and transparent negative result determines the scientific increment. The mathematical formulas and corpus audit support that increment; they are not independent evidence for C1.

## 7. Audit limits and artifacts

- `NOVELTY_SEARCH_RECEIPT.json` records the exact local search patterns and hits. The narrow strict-clock search had no substantive match; one broad regex matched unrelated wording in UCT III.
- `PRIMARY_LITERATURE_AUDIT.md` records the earlier sensorimotor and theory-comparison review. The Yarrow/Chancel/Lanfranco additions above materially update it for the chosen width-analysis direction.
- The inspected formal statements were read semantically for the named predecessors. No complete new semantic proof review or graph promotion was conducted.
- Bibliographic prior art for state-trace/optimization was also independently supplied by the theoretical branch. Root must open a source itself before using subagent retrieval handles in user-facing web citations.
- External searches were focused, not an exhaustive systematic review. Absence of an exact formula in the inspected corpus is a bounded reuse decision, not proof of worldwide originality.
