# Theory-first UCT research discipline and the mathematical meaning of organization

**Date:** 8 October 2026 (Asia/Shanghai)  
**Status:** Author-directed research methodology, scoped formal note and finite countermodel. **Not a paper, not a discovery claim, not empirical confirmation, and not a release authorization.**  
**Project:** UCT experience–intelligence–self, branch \`uct-agent-consciousness-workspace\`.  
**Lineage:** UCT I v1.2 (TA20), UCT II v1.1 (TA21), UCT III v1.0 (TA23), Experience/Intelligence/Self (TA25), Actual Participation (TA18), R179 and R180 v0.2. Do not revise or silently supersede their axioms and review amendments.

## 1. Author's methodological instruction (persistent project policy)

The author identifies a serious epistemic bottleneck: although real brains and organisms possess actual physical organization, current measurements and mathematical models do not expose its complete token-relative composition, causal role, boundaries and temporality. Differences inferred from an fMRI signal, an animal behavior, a neural firing map or an AI report may fail to identify the complete organization and cannot automatically identify a specific experience. It is premature to design large human/animal studies before the relevant UCT ontology, formal notions and discriminating conceptual predictions are stabilized.

**Research order, effective for subsequent rounds:** (1) first principles and premise audit; (2) extreme, adversarial, contrasting thought experiments; (3) explicit mathematical definitions, conditional proofs and countermodels; (4) tiny formal/computational checks only when they test an exact derivation; (5) existing published human, animal, neuroscience and AI studies as evidence constraints, potential defeaters and prior-art checks; (6) only after a substantive theory/bridge is coherent and scope-fixed, discuss realistic experimental translation. Do not promote model-fitting or large new experiments to the primary activity. Do not reject inconvenient pre-existing evidence or claim experiments can never matter.

Every future research report should display its premise-to-conclusion argument, distinguish conditional conclusions from observations, identify failure conditions, preserve negative findings, avoid reinventing results already in TA20–TA25/R1–R180, and cite the precise prior paper where a result is inherited.

## 2. The central distinction: ontology, formal view, observations, phenomenology

Fix a physically realized process token P, its independently specified bearer/boundary, a time interval I, a grain g and a comparison signature K. Distinguish:

* **Ontic organization O(P)**: the complete *actual* token-relative physical organization posited by UCT I v1.2. Not automatically observable or finitely enumerated.
* **Scoped mathematical model M_(g,I,K)(P)**: a scientific representation of selected constituents and roles, justified by physical anchors, valid only under its declared grain, time and signature.
* **Observable record D_J(P)**: responses accessible to a specified observation/intervention family J, possibly indirect, noisy and lossy.
* **Experiential organization Φ(P)**: related to O(P) by UCT's **conditional C1 structural–experiential identity axiom**, not supplied by a fitted readout label.
* **Selected named experiential target T(P)**: such as felt trying, familiar mineness, pain or experienced temporal order. Assigning a particular name to a mathematical relation requires a separate, noncircular interpretive/empirical bridge.

The dependencies may be represented schematically as O(P) -> M_(g,I,K)(P) [scientific modeling, fallible], O(P) -> D_J(P) [measurement, lossy], and O(P) ==struct Φ(P) [C1, strong *axiom*]. A selected target T requires an independently admissible phenomenal meaning; D_J alone is not a licensed inverse map to O or T. Even an arbitrarily successful supervised decoder is not by itself a proof of the ontic organization or of C1.

This architecture is inherited in substance from TA20 v1.2, TA25 and earlier bridge/identifiability audits; this note makes the author's priority explicit and applies it to research planning.

## 3. A mathematically usable but explicitly non-unique organizational interface

For a *declared*, physically grounded grain and interval, a model of actual organization may be presented as

\[
\mathcal O_{g,I,K}(P)=
\bigl(
 V,\{X_v\}_{v\in V},
 \Theta,K_\Theta,\mathcal I^{phys},
 \mathcal H^{AP}(h),\partial P,\mathsf T,h,\mathcal R,C^{PA}
\bigr).
\]

Here V is the physically anchored constituent/event set; X_v are state spaces; Θ and K_Θ specify actual installed mechanisms and stochastic/conditional transitions; I^phys contains admissible mechanism-aware intervention operations; H^AP(h) is a *chosen admissible model* of actual token participation, potentially joint and hypergraphic; ∂P accounts for boundaries and environmental ports; T preserves physical timing and order; h records the realized history; R fixes operating regime; and C^PA records physical anchoring and admissible coordinate changes.

This is a **modeling signature**, not a discovered universal uniquely correct brain decomposition and not itself the ontically complete O(P). A physical brain is not a graph alone: directed topology can be shared by processes with different kernels, realized states, time constants, joint causal relations, boundary conditions and physical implementations.

Two such models are compared by maps that preserve **declared constituents, pointed states, admissible interventions, response kernels, actual participation, boundaries and relevant temporal relations**. Coordinate relabeling is not physical rewiring. A graph isomorphism preserving adjacency only is weaker than the required organizational comparison; equal external input/output mappings are weaker still. A comparison topology or structural distance must be fixed independently rather than picked to make one target feeling appear.

A stronger *complete-organization* equality claim cannot be inferred from equality of these finite signatures, unless completeness and admissibility are separately defended. UCT I v1.2 explicitly retains this obligation.

## 4. Formal observation-equivalence discipline

Let J be a physically meaningful, predeclared family of probes and R_M(j) the responses read from a given model M. Define

\[
M\equiv_J N\quad\Longleftrightarrow\quad R_M(j)=R_N(j)\quad \forall j\in J.
\]

When J is a strict subset of J', then M ≡_(J') N implies M ≡_J N. This elementary implication says stronger probes refine observational equivalence classes; it does **not** say an experiment recovers complete organization. If an observation map has a fiber with multiple admitted distinct ontic completions, no unique complete-experience-type conclusion follows solely from that observation under C1. This is the already published TA25 type/fiber constraint, not a new theorem.

The inference guard is:

\[
\text{same output under }J
\centernot\implies
\text{same complete ontic organization}
\centernot\implies
\text{settled named phenomenal content}.
\]

The second non-implication should **not** be interpreted as "different ontic organizations have identical phenomenology": by the strong version of C1, genuinely distinct comparable complete structural types have distinct corresponding complete structural types. Rather, limited data do not tell us which ontic type is present, and complete type does not provide a calibrated named quale by fiat.

## 5. Thought experiment T1: two machines with identical *complete external truth tables*

Fix physical boundaries and a restricted external interface with binary inputs a,b and output y.

* **Machine A:** z = a AND b; y = z.
* **Machine B:** z = a AND b; w = a AND b; y = z AND w.

For every one of the four possible external inputs (00,01,10,11), both machines output 0,0,0,1. This was exhaustively evaluated in a finite JS model (four rows; no human, animal, LLM or consciousness experiment). For a=b=1 in B, the intervention do(w=0) changes the output from y=1 to y=0, whereas A has no w constituent or intervention. B has a duplicated realized circuit whose internal causal description and part roster are not the same as A's; no arbitrary "SELF" or "FEELING" marker was introduced.

**Conditional consequence:** external behavior—even across its *entire* finite external input space—does not select an intrinsic organization. With a common physically justified signature that includes actual internal realization, a non-isomorphic organization will map under UCT C1 to a non-isomorphic complete experiential structural type. This says nothing about intensity, valence, unique owner, or named feeling. The example uses established causal/logical distinctions and is not claimed novel relative to TA20/TA18/TA25. Its present use is to justify theory-first discipline.

**Failure/qualification:** if the proposed internal units are mere mathematical encodings without corresponding physically realized constituents, or if the selected macro-target justifiably excludes them, this purported whole-token difference cannot be smuggled into the target. A physically grounded part-to-whole contract is mandatory.

## 6. Thought experiment T2: external provenance versus bearer-relative structure

Take a fixed bearer P, time I and *complete declared* relevant signature K. Imagine two different upstream external histories (e.g., spontaneous instruction and externally scripted instruction) producing exactly the same physically timed boundary input into P, with identical internal realized history, mechanism, boundary interaction and response structure through I. Provided all causally effective distinctions for P really are matched, O_K(P1) ≅ O_K(P2) and C1-W entails Φ_K(P1) ≅ Φ_K(P2). Merely changing a historical cause strictly **outside** this screened scope does not supply a phenomenal difference for this fixed P/I/K. The larger ensemble, or a bearer including the source path, may legitimately differ.

This is a scoped application of TA20's **causally screened history/no ghost history** and R178/R180's frozen-bearer/source distinction, not a new principle. In actual human movement stimulation it will be difficult to establish such exact internal equality: unnoticed efference copies, sensory updates, subthreshold constraints and boundary fields may differ. Do not claim observed human agency reports contradict C1 without first justifying complete equality. Likewise, do not use the source's informal label "voluntary" as if it settled what the person actually experiences.

## 7. Thought experiment T3: model change versus actual organization change

Observer A fits a seven-region brain network; observer B divides the same specimen into seven hundred regions. If neither manipulates the physical process, their change of representation does not by itself change the actual process's experience under C1. Different scientific network diagrams may disagree while O(P) stays fixed. Yet some recodings alter admissible intervention semantics and thus are not mere renamings; a physical measurement procedure may itself perturb the process. This separates **epistemic refinement** from **ontic transformation**.

A universal consciousness metric inferred from a graph alone must survive this distinction or specify a justified scale family, physical units, interventions and aggregation law. This reuses UCT I chart/scale covariance constraints; no new scalar or basal consciousness gate is proposed.

## 8. Existing evidence: constraint bank, not a shortcut to metaphysical identity

* **Desmurget et al., Science (2009), DOI 10.1126/science.1169896:** awake neurosurgical electrical stimulation reported dissociations between movement intention/awareness and detected movement. Supports rejecting naive equivalences of overt motion, reported intention and physical cause; does not recover a complete organization or validate C1.
* **Poldrack, Trends in Cognitive Sciences (2006), DOI 10.1016/j.tics.2005.12.004:** warns that inverse inferences from regional activation to a cognitive process lack deductive force without selectivity assumptions.
* **Friston, Harrison & Penny, NeuroImage (2003), DOI 10.1016/S1053-8119(03)00202-7:** dynamic causal modeling demonstrates an explicitly parameterized *model-based* approach to estimating effective connectivity; fitting does not automatically prove ontic completeness.
* **Cogitate Consortium, Nature (2025), DOI 10.1038/s41586-025-08888-1:** 256-person preregistered IIT–GNWT adversarial comparison, with mixed support/challenges. Their experiment tests specified theory-linked neural predictions, not the universal completeness of UCT's ontic organization. Data remain potentially useful later if a predeclared bridge gives an identifiable readout.

These are existing experiments/theory-methodology sources. No new human/animal/AI experiment or raw-data analysis was performed here.

## 9. Formal map / claim status and next research priorities

**Inherited, not new:** C1 and its conditional structural consequences; finite-view/type-fiber non-identification (TA25); actual participation and trace insufficiency (TA18); no-ghost-history/bearer scope (TA20); proposal origin/uptake/later attribution dissociation and forced/free evidence limitation (R180).

**Research-method addition:** theory-first stage order and an explicit organizational identifiability veto on claims from neural/AI readouts. The exact four-row gate demonstration illustrates the veto; it does not establish consciousness. **No canonical graph node/rule counts changed, no new theorem claimed.**

**Unresolved, retained open:** uniquely grounded grain/boundary for a real brain, complete ontic-versus-finite scientific signature, identification of a *named* phenomenal content (QC10), relation to selected self-related feeling (IA-QC11), actual human bearer/source application (QC12), and R180's action formation versus later attribution interpretation.

**Next:** (a) challenge this organization interface with neural replacement, slow mechanical brain, independently reporting half-brains, simple calculator versus a human executing the same calculation, and copied AI agents; (b) derive one *scope-fixed, theory-conditional* positive experiential relation without relabeling a functional bit as a quale; (c) adversarially compare C1, IIT, GNWT, HOT, mechanistic and biological rivals; (d) use pre-existing published data strictly as falsification/constraint searches after the claim and its evidential requirements are written. Refrain from new large empirical designs until these conceptual debts have been reduced. Retain the original UCT ambition: experience–intelligence–self across inorganic, cellular, animal, human and artificial substrates.

## 10. Publication and storage

This is a research-methodology checkpoint for future windows. Preserve it with a pointer in HANDOFF.md and MASTER_INDEX.md. **Do not** change released papers, DOI, Zenodo, OTS, Arweave or a public website. Do not treat the note as a new round number or overwrite R180. Include the author preference in later handoffs rather than relying on an unverified account-wide memory setting.
