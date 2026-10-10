# Independent internal review of the SCU manuscript

Review ID: `SCU-MANUSCRIPT-REVIEW-v0.1.0`  
Manuscript: `Matched_Behavior_and_Source_Use_v1.0.0.md`  
Reviewed SHA-256: `fbe3f19b68d0067df8a7781fd039ca920bc5449ab6ca146085d2277e0f52d0d3`  
Scope: complete 379-line manuscript, including all proofs, interpretation, bibliography, and declarations. The original model-instance counts were not recomputed for this review. Source verification and the preceding coverage audit are separate from external peer review.

## Recommendation

**Complete the manuscript after the narrow revisions below.** The article is sufficient as one coherent theoretical methods/application paper under the master guide's §0. The proofs of the declared pure-source and unrestricted-OR problems are sound; the cumulative R204/R205/SCU contribution is correctly presented as an application and synthesis of established principles. I found no new fatal mathematical error and no conclusion that turns the probe into an experience-existence gate.

The paper's value is a precise reusable sequence: select a source relation, state the mechanism and observation class, choose a provably adequate probe schedule, and stop at the resolution actually identified. A positive phenomenal bridge or a new general coding theorem is not a prerequisite for that contribution. The current manuscript appropriately does not claim either. Its absence of biological data limits application, not the validity of the finite formal result.

## A. Revisions that should be made before freezing this edition

### MR-01 — State the unrestricted OR class unambiguously in the abstract

**Location:** Abstract, sentence beginning “Allowing either consumer ...”.  
**Severity:** Scope precision; required small correction.

The proved linear lower bound allows **both consumers independently** to use arbitrary nonempty OR source sets. “Either consumer” can be read as relaxing only one consumer while the other remains pure. That is a different problem and does not generally require n probes. For example, five distinct weight-two binary columns of length four distinguish an unknown pure source from every unequal nonempty OR set: every other column has a one outside the pure source's column. Thus four probes can suffice in that one-sided class when n=5.

Suggested replacement:

> Allowing both consumers to aggregate independently chosen arbitrary nonempty source sets by OR changes the exact worst-case requirement to n probes.

Theorem 6 and §6 already have the correct quantifiers; no proof change is required. There is no need to add the one-sided problem to this paper.

### MR-02 — Cite the published RT-TH predecessor directly and distinguish its target

**Location:** §1 prior-coverage paragraphs; reference 10.  
**Severity:** Attribution and self-contained source access; recommended before completion.

RTTH20261009 is a formally published preprint with DOI `10.5281/zenodo.23251651`, not merely another unnamed research record. Its theorem R3 gives the minimum supplied route-tag alphabet for task recovery; that is a close predecessor to the present information-cost discussion. Grouping it with IA/R147/R174/R182 under one changing branch URL makes this overlap unnecessarily hard for a reader to assess.

Give the full RT-TH title/version/DOI a separate reference and add a brief distinction in §1 or §5.2. For example:

> The author's Task-Relative Continuity paper already characterizes the minimum alphabet of a supplied route tag for task recovery. Here the investigator instead chooses source assignments and observes only the discrepancy between two consumers; the target is source equality, rather than recovery using delivered route metadata.

The exact work is *Task-Relative Continuity Through Changing Representations: Reversible Handoffs, Route Ambiguity, and the Limits of Stable Readout*, v1.0.0, DOI [10.5281/zenodo.23251651](https://doi.org/10.5281/zenodo.23251651). This metadata is receipt-backed in the frozen publication census and its exact manuscript was directly read in the preceding audit. No fresh live-DOI readback is claimed here.

TA18 is also worth citing directly for the already published actual-participation/trajectory distinction: DOI [10.5281/zenodo.22991126](https://doi.org/10.5281/zenodo.22991126), *Actual Participation Before Counterfactual Capacity*, v1.0. This is supporting attribution, not a demand to expand the argument. It makes the source of §§3.2–3.3 and 7's general distinction clearer than the bundled record citation alone.

### MR-03 — Synchronize the ancillary audit description with the R194 finding

**Location:** §10, paragraph beginning “Independent review also found two errors ...”.  
**Severity:** Provenance completeness; small correction if this paragraph summarizes the completed companion audit.

The R201/R202 statements are accurate, but the companion audit now also records R194's omitted multi-anchor consistency condition. The graph count is `2^c` only when the edge constraints and all anchors are jointly consistent; inconsistent anchors can give zero solutions on an acyclic graph. This does not affect any source-probe proof.

Either explicitly call R201/R202 “two probability-record errors” without implying an exhaustive audit inventory, or add one sentence about the R194 correction. Keep these ancillary repairs out of the main contribution claim. Preserving the original records and applying effective overlays is correct.

## B. Optional wording improvements

### MR-04 — Narrow the Zaadnoordijk paraphrase to causal self-attribution

**Location:** §1, third paragraph, “causal and ownership relations needed in an account of a sense of agency”.

The direct predecessor is correctly cited and its insufficiency argument is fairly credited. A cleaner paraphrase is “causal self-attribution involved in a sense of agency.” The inspected paper's central argument is about what a match can explain about agency; the phrase “ownership relations needed” risks sliding between agency and body ownership just before this manuscript carefully distinguishes those targets. This is a precision improvement, not a finding that the entire attribution is false.

### MR-05 — Include the known-root OR extension only if useful

**Location:** §5.3 after Theorem 5.

The current theorem is correct for a pure predictor. The SCU source note also proves that the complement probe works for an unknown nonempty OR predictor set B: with the known motor root a set to zero and every other source set to one, agreement occurs exactly for `B={a}`. A single sentence could connect §5.3 to §6 and make the role of prior source knowledge clearer. This is optional; its omission does not invalidate the article. If included, retain nonemptiness and independently known pure motor source.

### MR-06 — Avoid symbol reuse if doing a final clarity pass

**Location:** §§2.1–2.3 and §6.

P denotes an actual process token and then a predictor consumer in the contract tuple; B denotes the bearer and later an OR source set. Their local meanings are recoverable, but using named consumer symbols or a subscript would reduce friction. This is not a semantic contradiction and does not require a new model.

## C. Bibliographic verification requested by the parent

### Bollobás–Scott: verified, including pages

The University of Memphis official faculty-publication record confirms 2007, *European Journal of Combinatorics* **28(4), 1068–1071**, DOI **10.1016/j.ejc.2006.04.003**:

[Official institutional record](https://digitalcommons.memphis.edu/facpubs/5309/)

The author manuscript dated 18 April 2006 remains the directly read six-page mathematical source. The printed page numbers need not match the author-PDF pagination. Reference 6's current pages are correct; adding issue 4 and the DOI is optional but useful. A DOI follow-through encountered an Elsevier redirect error; the official institutional metadata was successfully read, so no inference was made from that failure.

### Ganesh and colleagues: verified eight authors and article number

The official PubMed record confirms *Science Advances* **4(5):eaaq0183**, 9 May 2018, DOI **10.1126/sciadv.aaq0183**. The ordered full author names are:

1. Gowrishankar Ganesh
2. Keigo Nakamura
3. Supat Saetia
4. Alejandra Mejia Tobar
5. Eiichi Yoshida
6. Hideyuki Ando
7. Natsue Yoshimura
8. Yasuharu Koike

[Official PubMed record](https://pubmed.ncbi.nlm.nih.gov/29750195/)

Reference 9's `eaaq0183` is correct, including the initial “e”; it is an article identifier rather than a page number. “Ganesh et al.” is a permissible abbreviated author form if used consistently. Adding `(5)` makes the citation complete. The source-reading declaration should remain abstract/indexed-description level: this review read that official page, including its displayed figures, but the linked PMC full article again returned an access interstitial. No full experimental-methods audit should be inferred from verification of all authors.

### Shanmugam and colleagues: venue and authors verified

The official proceedings page confirms the title, the four listed authors, and *Advances in Neural Information Processing Systems 28*, NIPS 2015:

[Official NIPS 2015 publication page](https://papers.nips.cc/paper_files/paper/2015/hash/b865367fc4c0845c0682bd466e6ebf4c-Abstract.html)

Reference 7 is accurate. An official proceedings link is slightly more direct than the arXiv link for this citation; the arXiv full proof and Appendix 6.3 remain valid directly read sources. The formal graph-learning target differs from SCU's comparator-only source predicate, and the manuscript states that difference honestly.

### Remaining bibliography

The foundation version/DOI pairs, TA25 identifier, Zaadnoordijk DOI, arXiv v1 citation for D'yachkov et al., and the two exact-commit R204/R205 links match the inspected source records. R205's concurrent contribution is explicitly and correctly retained. Reference 10 is the principal retrieval-quality weakness because it bundles several documents and a published work behind a live branch; MR-02 addresses that issue. No invented TA26/TA27 label appears.

## D. Checks that passed in this bounded manuscript review

- Theorem 3 identifies the equality predicate, not the ordered source allocation. The nonzero-transcript collision example is correct.
- Theorem 4's deterministic adaptive lower bound follows the all-zero branch and preserves the same response history. It is not falsely inferred from the finite nonadaptive optimizer.
- Theorem 5 correctly states its prior-knowledge requirement, n≥2 scope, and zero-probe ambiguity.
- Theorem 6 correctly assumes two arbitrary nonempty sets; its `N` versus `N minus {i}` witnesses and unit-probe necessity/sufficiency are valid.
- Nominal matching is explicitly separated from diagnostic perturbation. The paper does not claim every probe preserves task success or prediction alignment.
- R204's reflex/comparator result concerns projected predictor states and allows different write events. No experience-free reflex assumption is introduced.
- R205's cancellation countermodel is attributed to the concurrent record and is not counted as a fresh SCU discovery.
- Installed OR sets, actual event ancestry after intervention, and numbers of short-circuit reads are distinguished.
- Root dependence, actual branch consumption, shared intake occurrence, predictive chronology, numerical continuity, and selected phenomenal targets are not collapsed.
- Complete organizational clones are treated in accordance with C1; partial observational twins are not smuggled in as complete twins.
- Task success is not a complete intelligence measure. Conceptual self, report, agency, ownership, intensity, sensitivity and H retain separate roles.
- C1/U1 are conditional framework commitments. Actual local processes are not denied status because a larger comparison fails; neither report nor memory nor source correspondence becomes a basal-experience gate.
- The paper explicitly preserves the difference between source-compatible derivations, candidate registration, numerical checks, whole-map compatibility and an adopted map release.
- Reproducibility counts are scoped and are not summed into human sample size or a number of discoveries. I did not repeat their numerical verification here, as requested.

## Final disposition

`READY_AFTER_SCOPED_MINOR_REVISIONS` for the complete working manuscript. MR-01 should be fixed; MR-02 materially improves publication attribution; MR-03 aligns the accompanying audit description. MR-04–MR-06 are optional clarity improvements. No additional round of broad research or larger enumeration is needed to address these findings.

This review does not authorize external release, certify human phenomenal claims, close QC10/IA-QC11/QC12/QC13, or replace the separately documented map review. It approves the modest, explicitly stated kind of contribution that this manuscript actually offers.
