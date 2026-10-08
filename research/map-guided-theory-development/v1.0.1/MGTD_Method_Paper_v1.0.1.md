---
title: "Map-Guided Theory Development"
subtitle: "A Versioned Protocol for Thought Experiments, Semantic Audits, and Human–AI Research"
author: "Hongju Liu"
date: "8 October 2026 · Released preprint v1.0.1"
lang: en-US
fontsize: 10pt
documentclass: article
geometry: margin=0.92in
colorlinks: false
---

\begin{center}
Independent researcher, Shenzhen, China\\
\texttt{MGTD-PAPER-v1.0.1} / \texttt{METHOD20261008}\\
Released Zenodo methods preprint; not peer reviewed.\\
Version DOI: \texttt{10.5281/zenodo.23241982}
\end{center}

## Abstract {-}

Developing a theory requires more than collecting plausible propositions. Definitions can change between research episodes, separate witnesses can be combined incorrectly, and a successful local proof can cease to address the original question. We present Map-Guided Theory Development (MGTD), a protocol in which a versioned, semantically annotated research map mediates between conjecture generation, thought experiments, conditional deduction, criticism, and preservation. Claims retain their domains, quantifiers, interpretation, source versions, and epistemic status. Conjunctive premises are bound to a common application contract, alternative proof routes remain distinct, and a completed cycle includes a census-wide compatibility review plus deeper rederivation of affected conclusions. Minimal unresolved obligation sets provide a transparent representation of possible next research steps without asserting their truth or feasibility. We state elementary guarantees for the restricted deductive component and give constructive examples of the limits of structural and local checking. A retrospective case contains 1,278 recorded review items; it illustrates artifact design, not independent validation of the underlying consciousness theory. A small executable conformance suite rejects 12 deliberately constructed contract violations, accepts 12 benign controls, and checks frontier calculations on 1,024 finite rule graphs. The contribution is an explicit, reusable synthesis for theory-oriented human–AI research, not the invention of argument graphs, a universal discovery algorithm, or evidence of improved scientific productivity.

**Keywords:** theory development; thought experiments; semantic audit; research provenance; AND/OR hypergraphs; human–AI collaboration; reproducibility

# The problem: continuing a theory rather than continuing a conversation

A researcher proposes an explanatory principle, explores its consequences, encounters a counterexample, revises a definition, and returns to the original question. This description already contains a difficult information-management problem. Which earlier results survive the revision? Which conclusions depended on the old definition? Was a proposed explanation established, assumed for a model, or merely suggested by an analogy? When another researcher or AI assistant continues the project, what precisely should be inherited?

The issue is not that linear manuscripts are inherently incapable of rigorous reasoning. Structured proofs, explicit assumption tracking, and arguments with linked evidence are well-established responses [3–8]. Rather, an evolving theoretical project requires repeated coordination among discovery, justification, interpretation, and preservation. A graph containing arrows between short labels does not solve that problem. Nor does a sequence of increasingly polished summaries.

Consider the rule $A(x)\land B(x)\Rightarrow Q(x)$. A report establishing $A(a)$ and a different report establishing $B(b)$ do not establish its premises for one object. Likewise, an arrow from a thought experiment to a conjecture may express motivation without constituting a proof. An accurate computational result can support a finite model while leaving its physical interpretation open. These are different failure modes, and a single field labeled “verified” conceals them.

MGTD treats a research map as a revisable working representation rather than as a certificate of truth. Its central operational claim is a proposal: linking research actions to typed claims, explicit obligations, counterexamples, and versioned reviews can make theory development easier to inspect and continue. Whether this improves the quality or speed of discovery is an empirical question not resolved here.

The intended setting is a theory-intensive project with repeated human–AI interaction, changing definitions, multiple explanatory levels, and incomplete access to decisive experiments. The protocol also permits empirical work whenever existing observations or new measurements can constrain the theory. It is not a prescription to postpone evidence indefinitely. It is especially useful as a candidate workflow when the meaning of an experimental target must first be clarified.

This manuscript separates three contributions. First, it specifies the records and transitions of a theory-development protocol. Second, it makes the map action-guiding through explicit unresolved-obligation sets and counterexample operations. Third, it provides a retrospective artifact case and a small executable implementation. The mathematical results are elementary specifications of intended behavior, not claims of newly discovered logic.

# Prior work, overlap, and the boundary of the contribution

## Theory construction and criticism

Lakatos describes mathematical development through conjectures, attempted proofs, criticism, and revisions [1]. Borsboom and colleagues articulate theory construction as a cycle from phenomena through a prototheory and formal model to assessment of explanatory adequacy [2]. MGTD inherits the need for both creative generation and stringent criticism. It does not invent either a theoretical research cycle or counterexample-driven revision. Its focus is the persistence and application conditions of the intermediate claims produced during such a cycle.

Doyle's truth maintenance system records reasons for beliefs and supports revision [3]. De Kleer's assumption-based system tracks sets of assumptions supporting conclusions [4]. The minimal-obligation construction below is closely related to this tradition. Calling these sets a research frontier does not make the underlying support-set calculation new. The methodological choice is to expose the sets to the researcher as conditional routes whose missing commitments can be investigated, challenged, or abandoned.

## Argument representation, formalization, and provenance

Micropublications represent scientific claims together with supporting evidence, methods, and challenges [5]. The Open Research Knowledge Graph concerns machine-actionable scholarly contributions [6]. Lamport's structured-proof approach makes assumptions and proof steps explicit [7], while Assurance 2.0 emphasizes rigorous reasoning, evidence, and defeaters [8]. Consequently, neither typed scientific arguments nor adversarial inspection is a first contribution of MGTD.

PROV-O provides a vocabulary for provenance [9]; SHACL specifies constraints for graph validation [10]; trusty URIs use content hashes for verifiable artifacts [11]. We use the same general distinctions between scientific content, validation records, and artifact identity. A hash authenticates bytes relative to a recorded digest, not the truth of the proposition written in those bytes. This implementation is not asserted to conform to PROV-O, SHACL, or a research-object interoperability standard.

## Closely related 2026 research

Recent work makes the novelty boundary particularly important. XScientist treats typed, content-addressed research state, negative outcomes, checkpoints, and handoffs as an auditable continuation protocol [13]. Its scope substantially overlaps MGTD's preservation and governance layer. Hybrid-Human Grounded Theory maintains semantic kernels and goal-directed relations through multistep theory formation [14]. PEARL separates structural recovery from source-grounded semantic repair of scientific reasoning graphs [15]. Wang and Buehler develop a categorical account of typed representational revision and proof-carrying discovery artifacts [16].

These are substantive precedents, not merely neighboring titles. MGTD is therefore presented as a theory-oriented specialization and operational synthesis. Its emphasis is an explicit contract for thought-experiment-led theoretical revision: common-instance conjunctions, retained alternative routes, census-wide semantic compatibility checks, and preservation of application obligations when a conditional result is reused. We do not establish that no earlier system can express these requirements, or that this is the first combination of all of them.

| Precedent | Inherited capability | Emphasis of this manuscript |
|---|---|---|
| Theory-construction and proof/refutation traditions [1,2] | Iterative generation and criticism | A versioned, inspectable record for each completed revision |
| Truth maintenance [3,4] | Dependency and assumption tracking | Open support sets interpreted as research tasks, not accepted truths |
| Scientific argument graphs [5,6,15] | Claims, evidence, typed relations, repair | Application contracts carried through theory development |
| Structured proofs and assurance [7,8] | Explicit justification and defeaters | Thought-experiment obligations plus project-wide compatibility review |
| Provenance and immutable artifacts [9–11,13] | Traceable inputs, versions, handoffs | Separate scientific, review, and persistence states |
| Epistemic continuity and representational revision [14,16] | Goal alignment and evolving conceptual structure | A lightweight protocol and reproducible bounded examples |

This is a targeted comparison conducted on 8 October 2026, not a systematic review. Searches covered theory construction, truth maintenance, scientific argument graphs, semantic auditing, research provenance, and recent AI-science protocols. Primary publications and official specifications were prioritized. The accompanying literature ledger records access scope and the roles of the sources; absence from the ledger is not evidence that a relevant precursor does not exist.

## Relationship to the author's preceding work

The author's *Experience, Intelligence, and Self Within Experience* already contains a methodological discussion of definitions, joint premises, lineage, and research direction [12]. A subsequent project policy articulates a whole-map review and preservation cycle [18]. The present article explicitly develops that material rather than presenting it as unrelated prior art. It adds a theory-neutral record model, a restricted deductive semantics, an obligation-frontier calculation, a self-contained revision example, and executed contract tests. It does not republish the predecessor's consciousness claims or count the same results as new scientific discoveries.

# Research state and a minimal semantic contract

## The map and its records

At version $t$, define the research state as

$$
\mathcal R_t=(G_t,\mathcal D_t,\mathcal S_t,\mathcal A_t,\mathcal L_t),
$$

where $G_t$ is a typed research hypergraph, $\mathcal D_t$ a definition registry, $\mathcal S_t$ source records, $\mathcal A_t$ audit decisions, and $\mathcal L_t$ the version lineage. The map is a structured representation of the theory, not the physical organization that the theory might describe.

A claim record is

$$
v=(\mathrm{id},\varphi,\kappa,\Gamma,\sigma,\pi).
$$

Here $\varphi$ is the full statement; $\kappa$ distinguishes definition, assumption, conjecture, conditional theorem, observation, counterexample, or interpretive bridge; $\Gamma$ is an application environment; $\sigma$ contains separate status fields; and $\pi$ points to sources and justification. Natural-language explanations remain alongside formal expressions. A formula without its intended interpretation can be precisely written and still answer the wrong question.

An application environment may include a theory branch, domain, object variables, time interval, scale, structural signature, intervention family, and target. These fields are not all mandatory for every discipline. Their purpose is to expose distinctions relevant to whether premises can be combined. A purely mathematical theorem may require only a domain, variables, and hypotheses. A physiological application may require additional process and measurement information.

Stable identity and semantic identity are different. A stable identifier tracks the history of a claim. Its content can be superseded only through a new version. Identical wording does not guarantee identical meaning, and different wording does not guarantee a different proposition. Aliases therefore require an explicit equivalence judgment, not string similarity alone.

## Conjunctive rules and alternative routes

A deductive rule is a directed hyperedge

$$
e:(p_1,\ldots,p_k;g_e,\theta_e)\Rightarrow q,
$$

where the $p_i$ are jointly required premises, $g_e$ is a guard, and $\theta_e$ binds variables and application parameters. The premises may refer to several objects when the theorem permits this. Common-instance checking means preserving the theorem's declared relationships between those objects, not mechanically demanding that every noun denote the same thing.

For example, a transfer theorem can involve systems $a$ and $b$ and a map $h:a\to b$. The error would be supplying an $h$ for a different pair while leaving the theorem otherwise unchanged. An implementation using a single binding string, as ours does, only approximates this general requirement.

Different hyperedges ending at $q$ represent alternative proof routes. If either $A\land B$ or $C\land D$ suffices, the graph contains two routes, not one rule requiring all four premises. Conversely, a conjunctive source rule cannot be weakened into a collection of separately sufficient arrows.

Motivation, analogy, citation, semantic dependence, criticism, and empirical support are separate relations. They can influence research selection and review but do not enter deductive closure merely because they are drawn as edges. Empirical support is not erased by this distinction: it remains evidence with its own uncertainty and measurement contract.

## Status is a product, not a ladder

A record maintains at least four independent questions: what is its logical role; what review has actually occurred; what supports its application; and where are its exact bytes preserved? A mathematically justified conditional theorem may have an unresolved physical application and a verified repository copy. A well-preserved conjecture is still a conjecture. A reviewed observation can remain measurement-limited.

We therefore distinguish `CONDITIONAL`, `APPLICATION_OPEN`, `REVIEWED_WITH_LIMITS`, and `PERSISTED` rather than compressing them into “proved.” An empirical bridge is not established by changing a metadata flag. It requires the evidence or argument specified by its own acceptance criterion. Similarly, reviewer independence is recorded rather than inferred from the number of AI-generated critiques.

This also separates a project charter from an axiom. The charter states the question, desired explanatory level, and workflow constraints. It is not a premise proving the preferred answer. A genuine conflict with a foundational commitment must remain visible and can motivate a revised theory branch.

# The development protocol

## Start from a problem, then formalize progressively

A cycle begins by freezing the inherited state and writing one concrete question. The researcher identifies which distinctions must be explained and which observations, thought experiments, and source results constrain the task. A prototheory can initially be informal. Requiring a complete ontology before exploration may simply encode premature assumptions more neatly.

Progressive formalization means that a promising idea acquires a semantic contract before it is reused as a premise. Definitions, domains, and proposed explanatory relations become explicit as their role becomes clear. Existing evidence should be consulted at this stage; difficulty measuring a complete theoretical organization does not make narrower observations irrelevant. The unresolved measurement bridge becomes an explicit research item rather than a reason to reject all experiments or to invent a surrogate endpoint.

## Thought experiments as controlled transformations

A thought-experiment record specifies the starting model, fixed quantities, changed quantities, admissible transformation, target claim, and interpretation limits. Typical operations remove a presumed necessary component, add a bypass, duplicate or merge structures, exchange interfaces, change the temporal scale, or construct indistinguishable observations with different targets.

There are at least three possible outcomes. An admissible model satisfying the premises and falsifying the conclusion refutes the proposed implication. A transformation violating a premise instead identifies an application boundary. A scenario whose coherence or realizability has not been established remains a proposed challenge. These outcomes must not be collapsed into “the theory passed the thought experiment.”

A counterexample to a mathematical universal needs one member of its declared domain. A claimed counterexample concerning actual physical systems additionally needs a justified mapping to that physical domain. Conversely, a theorem about an idealized system can be valuable without pretending that the idealization has been installed in a brain or an AI system.

## Attach the result and reconsider the whole active map

The cycle inserts a new claim, modifies a definition through supersession, adds a counterexample, or records a failure. Every substantive addition receives an identifier and a provenance record. Merely saving a research note without connecting its claims does not constitute map integration.

Next, the protocol requires a review decision for every item in the declared active census. This is a compatibility review, not a demand to reinvent every unchanged proof. An unchanged proof may be retained by exact source and hash, together with an explicit check that its domain and interpretation still apply. Affected conclusions receive deeper rederivation. Shared definitions, aliases, targets, and background assumptions are reviewed even where no deductive edge directly connects the records.

The review asks whether statements remain jointly intelligible and compatible, whether their premises can be instantiated together, and whether the project has silently changed its target. A broad question about experience, for example, must not be declared solved by a theorem about verbal reporting without an explicit connection. Equivalent examples can arise whenever an observable proxy replaces an independently specified target.

An item can be reviewed and left open. “Complete review” means that the declared inventory received documented decisions, not that its theory is consistent, true, complete, or unanimously accepted. The inventory itself is a fallible model of the project. Undiscovered dependencies and omitted claims remain possible.

## Recheck originality, freeze a release, and continue

A completed cycle includes a second comparison with prior work after its precise result is known. This can change a claimed discovery into a useful application, correction, synthesis, or rediscovery. Such reclassification is a legitimate outcome. Node growth and naming novelty are not scientific progress.

A release contains the parent version, source hashes, exact added/changed/suspended identifiers, proof and evidence locations, review coverage, unresolved obligations, and preservation receipt. The authoritative current pointer selects the completed version. Working checkpoints remain separate from completed releases. Later operational receipts may confirm a copy without altering its scientific content.

The loop ends for the current cycle when the promised result and its review are saved, or when a declared limitation is reached and an incomplete checkpoint is preserved. No stopping rule guarantees a major discovery. The next action is selected from the remaining explanatory or evidential obstacles, not simply from whichever calculation is easiest to execute.

# Making the map guide the next research step

## Recorded closure and open obligations

Fix one environment and a finite acyclic positive AND/OR rule graph. Let $B$ be accepted roots for the current conditional calculation, and let $O$ be explicitly open root obligations, disjoint from $B$. A root in $B$ can itself be an assumption of the theory; acceptance here is not empirical endorsement. Members of $B\cup O$ have no incoming rules; a guard is fixed by the environment or retained as an explicit premise. Approved conditional rules define the usual monotone closure $\operatorname{Cl}_G(B)$.

For a target $q$, define the family of minimal recorded obligation sets

$$
\mathcal F_G(q;B,O)=\min_{\subseteq}\{S\subseteq O:q\in\operatorname{Cl}_G(B\cup S)\}.
\tag{1}
$$

The calculation treats members of $S$ as hypothetically supplied. It does not conclude that they are true, jointly realizable, or worth pursuing. Known-incompatible sets must be marked inadmissible, and uncertain compatibility must remain an open guard. Equation (1) concerns the represented rule system; it says nothing about undiscovered proof routes.

An accepted root has frontier $\{\varnothing\}$; an open root $o$ has frontier $\{\{o\}\}$; an unavailable root has no frontier. At a conjunctive rule, choose one frontier set for every premise and take their union. At alternative rules, collect the unions from each route. Remove strict supersets:

$$
\mathcal F(q)=\min_{\subseteq}\bigcup_{e:\,\mathrm{head}(e)=q}
\left\{\bigcup_{p\in\mathrm{tail}(e)}S_p:S_p\in\mathcal F(p)\right\}.
\tag{2}
$$

Roots with an explicit initial status are treated as roots, not also as freely inferred substitutes. Cyclic or nonmonotonic theories require additional semantics; the present recursion is not claimed to cover them.

**Proposition 1: exactness of the restricted frontier.** Under the finite, positive, acyclic assumptions above, (2), with the root cases, computes (1). Thus a supplied set $S\subseteq O$ reaches $q$ exactly when it contains a member of $\mathcal F(q)$.

**Proof.** Proceed in topological order. The root cases state precisely their possible open supports. For a rule with all premises required, a derivation exists exactly when a support exists for every premise; their union therefore supports the conclusion. Any valid conclusion derivation ends in one of the alternative rules, so collecting all such unions is exhaustive. Removing a strict superset changes no reachability under the positive closure because a subset already suffices. Finiteness gives an inclusion-minimal support whenever a support exists. Induction yields the result. $\square$

This is an assumption-support calculation, not a priority claim against truth-maintenance research [3,4]. Its practical use is the question it makes visible. With $A\in B$ and routes $A\land B_1\Rightarrow T$ and $C\land D\Rightarrow T$, the frontier is $\{\{B_1\},\{C,D\}\}$. Research may investigate $B_1$, investigate both $C$ and $D$, challenge either route, or formulate a new route. The singleton is not automatically cheaper or more important.

For each candidate action, a decision card names its target, relevant obligation set, proposed operation, possible refuting outcome, resource bound, and expected effect on the original question. Ranking can use explicit cost and relevance judgments, but a numerical score is optional and should not disguise subjective priorities as a theorem. Adding a premise that merely restates the conclusion is not explanatory progress; its independent justification becomes the next issue.

## Conditional soundness without epistemic promotion

**Proposition 2: preservation of conditional validity.** Suppose a finite derivation uses roots true in an interpretation satisfying $\Gamma$, and every traversed rule is valid under the bindings and guards recorded for that same interpretation. Then its conclusion is true in that interpretation. If provenance-only or review-only operations do not alter scientific status by definition, those operations alone cannot establish an empirical application.

**Proof.** Induct on derivation height. Root validity is assumed. At each step, the induction hypothesis supplies all premises under the required bindings, and semantic validity of the guarded rule supplies its conclusion. The second statement follows from the stipulated transition separation: the provenance operation produces a record about an artifact, not the missing empirical premise. $\square$

The assumptions do the substantive work. A filled template does not verify them. In particular, an erroneous natural-language formalization or a false accepted premise invalidates any attempt to read this proposition as an unconditional correctness guarantee.

## Why local and pairwise checking are insufficient

**Proposition 3: limitations of incomplete dependency representations.** A review restricted to recorded deductive descendants cannot guarantee compatibility after a definition changes unless all relevant semantic dependencies are represented or otherwise reviewed. Pairwise satisfiability of the recorded statements is also insufficient for joint satisfiability.

**Proof by constructions.** Let a record assert $q:(d+1=1)$ under the definition $d=0$. Store its use of $d$ in prose but omit the definition-use edge from the deductive graph. Change the definition to $d=1$. The displayed graph and its descendant set can remain unchanged, but the old reading of $q$ fails. A descendant-only procedure misses the change. Separately, the statements $p$, $q$, and $\neg(p\land q)$ are satisfiable in every pair but not together. $\square$

This does not show that full-map review always discovers a hidden conflict. It shows why its scope cannot be replaced by a traversal of an acknowledged incomplete graph. When a complete formal dependency system exists, affected-set checking can be sound and much more efficient. MGTD's census-wide review is a conservative protocol choice for mixed prose-and-formal projects, not a lower bound requiring every future tool to reread every word.

# A worked theory-development cycle

A self-contained finite example shows the difference between recording conclusions and using a map to revise a prototheory. It is deliberately elementary. Its role is instructional and reproducible, not discovery of a new mathematical law.

## Initial question and failed conjecture

Suppose the target is to recover one component $f(a,b)=a$ of a two-bit state from a measured descriptor $r(a,b)=a\oplus b$. The initial conjecture says that the descriptor determines the target throughout $\Omega=\{0,1\}^2$. The map records the domain, functions, target, and universal quantifier. No claim about an actual physical measurement is made.

The guiding thought experiment asks for a change that preserves the descriptor but changes the target. The pair $(0,0)$ and $(1,1)$ has equal descriptor values and different targets. It therefore refutes the proposed sufficiency implication. This is not an attack on all descriptions or all measurement; it identifies a particular information loss.

## Generalization and repair

The failed conjecture suggests the familiar factorization condition. For functions $r:\Omega\to R$ and $f:\Omega\to Y$, it is:

$$
\exists h:r(\Omega)\to Y,\ f=h\circ r
\quad\Longleftrightarrow\quad
\forall x,y\in\Omega,\ r(x)=r(y)\Rightarrow f(x)=f(y).
\tag{3}
$$

**Proof.** A function $h$ assigns one target to each descriptor value, establishing necessity. Conversely, define $h(r(x))=f(x)$; the right-hand condition makes this independent of the representative. $\square$

This elementary result is already used in the author's preceding work [12]. The method does not relabel it as a new theorem. It turns the counterexample into two concrete options: enrich the descriptor or narrow the target. Enriching it to $r'(a,b)=(a\oplus b,b)$ permits $h(u,b)=u\oplus b$. Alternatively, changing the target to parity makes the original descriptor sufficient, but answers a different question. The second option cannot be presented as solving the original component-recovery task.

The map now preserves the refuted conjecture, its witness, the inherited general criterion, the repaired descriptor, and an explicit target-change alternative. Subsequent claims requiring reconstruction of $a$ are rederived using $r'$, not silently attached to the old descriptor. A release delta distinguishes the correction from the added result.

## From derivation to application

A physical application would create separate obligations: identifying the state variables, establishing the measurement law, specifying admissible perturbations, and verifying that the decoder is available where claimed. Equation (3) does not establish any of these. Nor does its abstract decoder automatically constitute an implemented mechanism.

The example clarifies why theory-first work can be useful without becoming anti-empirical. The theoretical analysis identifies what must be measured and which ambiguity matters. It does not claim that data are unnecessary. An adequate experiment would be one that distinguishes the competing target-preserving possibilities, rather than simply collecting more samples of an insufficient descriptor.

The supplied trace records these stages as demonstration states D0, D1, and D2. They are instructional states constructed for this manuscript, not retrospectively fabricated historical Git commits.

# Retrospective case: a frozen theory-map audit

## Material and scope

The case material is the author's UCT research archive, specifically the frozen `UCT-MAP-v1.0.0` release and its recovery package [17]. The base source commit is `48b131a3ae8f7ac003ff5a2ce9c8d36111b2ea3c`; the release commit is `f6445052acb1644fcdd7b2adcdda2307f7b98bc7`. These identify an archival case, not necessarily the latest live branch state.

The original graph contains 584 nodes, 284 rules, and 178 contextual relations. The release combines it with eight enumerated modules. The saved ledger has 722 node records, 353 rule records, and 203 contextual records: 1,278 items in total. Of the rule records, 347 originate in the inputs and six are added guarded or alternative routes. Ten historical rules are suspended, leaving 343 active conditional rules. The release also records deeper review of 25 affected downstream nodes.

For this paper, a fresh script checks the ledger's item counts, identifier uniqueness, required fields, active-rule count, and suspension count. It does not rerun a complete human semantic review of 1,278 claims. The archived judgments are author-side research artifacts, substantially produced with AI assistance, and are not treated as independent ground truth.

| Recorded quantity | Count | Interpretation |
|---|---:|---|
| Node records | 722 | Includes definitions, premises, open targets, and conditional arguments |
| Rule records | 353 | Includes suspended historical rules |
| Contextual relations | 203 | Not executable deductive premises |
| Total ledger items | 1,278 | Inventory coverage, not a count of proved propositions |
| Active conditional rules | 343 | Still require their stated guards |
| Suspended historical rules | 10 | Retained for history; excluded from active inference |
| Downstream nodes marked for deeper review | 25 | Historical audit report, not a new review in this paper |

The saved decisions include 190 “declared premise not discharged” records, 23 “open target or historical hypothesis” records, and 14 “recorded evidence not revalidated” records. These counts demonstrate that review completion and evidential completion were separately represented. They do not establish the accuracy of each classification.

## Illustrative repairs

One repair concerns alternative routes to a coverage claim. Direct coverage and reachable or inductive coverage had to remain alternatives, with the appropriate application witness for each route. Requiring both would incorrectly strengthen the claim; accepting a bare theorem schema as either witness would incorrectly weaken the application requirement.

A second distinguishes an evidence package from the physical role it purports to establish. Recording a certificate about a process is not the same operation as identifying a relation within that process. The archive preserves a separate grounding requirement rather than converting an epistemic record into a constitutive mechanism.

A third narrows a combinatorial interpretation. Filtering Boolean valuations can yield an upper bound on permitted cases without establishing that every remaining valuation has an actual realization. A fourth makes omitted conditions visible in a bound: a source theorem's sampling or independence assumptions must survive its compressed representation and later citation.

These descriptions are drawn from the archived findings F02–F05 and are not claims of newly detecting the original errors during manuscript preparation. They illustrate why keeping the exact source, interpreted statement, application guard, and revision separate is useful for auditability.

## What this case cannot show

The case is selected from the project that motivated the protocol. There is no randomized comparator, blinded adjudication, or independently established set of all semantic defects. The 1,278-item count therefore cannot estimate detection recall, false-positive rate, or theoretical validity. More nodes could represent better decomposition, unnecessary bookkeeping, or both.

The consciousness theory's foundational assumptions remain outside the method's evidential conclusions. A protocol can faithfully preserve an incorrect theory. In particular, neither a completed audit nor a reproducible calculation establishes a claim about the presence, structure, or intensity of conscious experience. This boundary is part of the methodological case rather than an afterthought.

# Executable conformance checks

## Design and implementation boundary

The supplementary Python implementation uses only the standard library. It implements a deliberately small contract checker, the acyclic obligation-frontier recursion, a finite propositional consistency checker, and the factorization example. It does not interpret arbitrary prose, verify all mathematical proofs, or decide whether a named physical object satisfies a theoretical definition.

Twelve deliberately constructed invalid fixtures preserve valid identifiers and resolvable references. They change a binding, omit a premise, exchange AND for OR, execute an analogy as a proof, promote an application without its required record, retain a stale definition, change a pinned source contract, execute a suspended rule, omit an audit item, overwrite a scientific version, export a claim between unbridged contexts, or introduce a jointly inconsistent triple. Twelve benign controls vary annotations and legal nonexecuting or explicitly licensed records.

A minimal baseline checks only identifier uniqueness and reference resolution. The fuller checker additionally compares the declared contracts and status constraints. This baseline is intentionally weak and is not an implementation of any cited research system. The fuller check also trusts its declared reference contracts; it cannot discover that the reference contract itself misreads a paper. A false but well-formed statement can pass both checks.

## Results actually executed

| Check | Executed scope | Result |
|---|---|---|
| Identifier/reference baseline | 12 invalid fixtures | 0 rejected |
| Declared-contract checker | Same 12 invalid fixtures | 12 rejected with their expected error category |
| Benign controls | 12 constructed valid fixtures | 12 accepted |
| Frontier versus brute-force closure | 1,024 finite rule graphs; 4,096 comparisons | 0 disagreements |
| Factorization criterion versus decoder enumeration | 1,364 binary map pairs | 0 disagreements; 228 factorizing pairs |
| Pairwise versus joint satisfiability | Three pairs and their triple | All pairs satisfiable; triple unsatisfiable |
| Frozen archive census | 1,278 ledger records | Counts and required fields matched |

The frontier enumeration considers all subsets of ten candidate nonempty rules: three possible premise subsets for a node $c$ over $\{a,b\}$, and seven for a node $d$ over $\{a,b,c\}$. Node $a$ is accepted and $b$ is open. Each graph is checked for targets $c,d$ with the open obligation absent or supplied, giving $1,024\times2\times2=4,096$ comparisons.

The factorization check enumerates every pair of binary-valued maps on labeled domains of size one through five, giving $\sum_{n=1}^5 4^n=1,364$ pairs. For each pair it independently compares constancy on descriptor fibers with the existence of a decoder among the four binary decoder tables. This is a bounded executable check accompanying the general proof, not a substitute for it.

The fixtures were designed together with the checks. Reporting 12 out of 12 is therefore a statement of conformance on a transparent authored suite, not an unbiased accuracy estimate. The examples make precise which encoded constraints the implementation enforces. They provide no evidence that MGTD outperforms XScientist, PEARL, human review, proof assistants, or another research workflow.

# Limitations and a prospective evaluation design

## Formalization and reviewer fallibility

The most important limitation is semantic access. The map does not supply a universally adequate mathematical definition of “organization,” “understanding,” or another disputed construct. It records the proposed definition, separates it from observations, and makes its downstream use inspectable. Selecting the right concepts still requires domain knowledge, creative judgment, and confrontation with evidence.

A reviewer may overlook an ambiguity while filling every field. Reusing one model to generate a claim, formalize it, and review it risks correlated error. Multiple prompts or roles do not create independent witnesses. Stronger evaluation would separate authorship from adjudication, retain dissent, and use external domain experts or proof-checking tools where appropriate.

The protocol also risks conservatism. A charter can become a device for protecting a favored axiom, and formal structure can discourage exploratory ideas. The remedy is not to remove commitments but to distinguish their authority: a project preference controls the topic, while evidence and argument control the warrant. Alternative branches, including abandonment of the initial theory, must remain admissible.

## Cost, scalability, and incomplete maps

Reviewing every registered item after each substantive integration can be expensive. Equation (2) can have exponentially many minimal support sets. The prototype neither resolves that worst case nor supplies an optimized scheduler. Large implementations may use lazy support enumeration, explicit truncation, formal dependency analysis, or modular contracts, but incomplete outputs must be labeled as such.

The protocol separates all-item compatibility review from full reproof. Verified unchanged formal modules can retain their proofs when their exact contracts remain stable. In a fully formalized project, complete dependency tracking may justify incremental checking. In a mixed prose project, the absence of a recorded dependency is not evidence of semantic independence.

A completed census is also relative to its declared scope. It cannot certify unmapped notes, external literature, or future changes. Scientific immutability here means retaining exact releases and detecting changes, not guaranteeing that a public repository will remain available forever.

## Testing usefulness rather than counting artifacts

A stronger evaluation would compare teams or agents continuing the same frozen projects under matched tools, model access, time budgets, and source access. Relevant arms could include ordinary notes with version control, an evidence-linked research graph, and the full MGTD protocol. The comparison should not disable useful capabilities in competing approaches merely to make a proposed method appear superior.

Primary outcomes should concern incorrect inference reuse, lost application conditions, recovery after a definition change, and the correctness of claims accepted by an independent adjudicator. Secondary outcomes may include time to a justified result, time to reject a false conjecture, handoff reconstruction fidelity, and reviewer workload. Node count, manuscript length, and self-assigned novelty are unsuitable primary success measures.

A held-out challenge set should contain valid but unfamiliar arguments as well as defects not used to design the checker. Ablations should remove common-instance binding, alternative-route preservation, or the census-wide review obligation while holding the rest constant. Such a study would test whether these design choices add value beyond mature provenance and argument-management systems. It has not been conducted in this manuscript.

# Practical adoption and conclusion

A minimal deployment needs a question charter, a definition registry, claim and rule files, source anchors, thought-experiment cards, a review ledger, and immutable completed releases. A visual rendering is optional. The decisive feature is that a later reader can reconstruct why a claim was proposed, what supports it, what remains open, and what changed when the theory was revised.

The expected human–AI division of labor is explicit but flexible. People set the scientific question and remain responsible for external claims. AI can propose transformations, help formalize arguments, inspect declared dependencies, implement bounded checks, and draft explanations. Tools record what actually ran. Review records identify who or what made each judgment and do not turn role separation into a claim of independence.

MGTD's central artifact is therefore not a finished picture of a theory. It is a versioned record through which conjectures, proofs, counterexamples, interpretations, and open obligations remain connected as the theory develops. Its value as a method lies in making those transitions explicit and reusable. The current evidence supports feasibility of the specified records and bounded checks; broader claims about discovery quality or efficiency remain open.

# Declarations {-}

**Authorship and AI assistance.** Hongju Liu supplied the motivating research program, methodological requirements, and originating thought-experiment discussions. This manuscript was prepared with substantial AI assistance in literature comparison, formalization, code development, checking, and drafting. This v1.0.1 correction was prepared following the author's instruction to update the public version. No independent human peer review or external methodological validation is claimed; this revision does not assert independent verification of every passage. AI assistance is not listed as a human coauthor.

**Data and code.** The supplementary package contains the reference implementation, input fixtures, executed results, a compact method-claim map, a review ledger, a source-access ledger, and the frozen case records needed for the descriptive count check. No human-subject or animal experiment was performed for this paper. The case archive is cited by immutable source and release identifiers [17].

**Publication status.** Version 1.0.1 is a public Zenodo methods preprint (specific-version DOI: `10.5281/zenodo.23241982`), correcting two outdated release-stage statements in v1.0.0. The original v1.0.0 remains archived under DOI [10.5281/zenodo.23241205](https://doi.org/10.5281/zenodo.23241205). DOI assignment denotes a persistent public record, not journal acceptance, independent peer review, or proof of the method's effectiveness. The manuscript version is independent of `UCT-MAP-v1.0.0`, the frozen case-study version, and does not modify the consciousness theory's authoritative map.

# References {-}

[1] Lakatos, I. (1976). *Proofs and Refutations: The Logic of Mathematical Discovery*. Edited by J. Worrall and E. Zahar. Cambridge University Press. DOI: [10.1017/CBO9781139171472](https://doi.org/10.1017/CBO9781139171472).

[2] Borsboom, D., van der Maas, H. L. J., Dalege, J., Kievit, R. A., and Haig, B. D. (2021). Theory Construction Methodology: A Practical Framework for Building Theories in Psychology. *Perspectives on Psychological Science*, 16(4), 756–766. DOI: [10.1177/1745691620969647](https://doi.org/10.1177/1745691620969647).

[3] Doyle, J. (1979). *A Truth Maintenance System*. MIT Artificial Intelligence Laboratory, AIM-521. [MIT repository record](https://hdl.handle.net/1721.1/5733).

[4] de Kleer, J. (1986). An assumption-based TMS. *Artificial Intelligence*, 28(2), 127–162. DOI: [10.1016/0004-3702(86)90080-9](https://doi.org/10.1016/0004-3702%2886%2990080-9).

[5] Clark, T., Ciccarese, P. N., and Goble, C. A. (2014). Micropublications: a semantic model for claims, evidence, arguments and annotations in biomedical communications. *Journal of Biomedical Semantics*, 5, 28. DOI: [10.1186/2041-1480-5-28](https://doi.org/10.1186/2041-1480-5-28).

[6] Jaradeh, M. Y., Oelen, A., Farfar, K. E., Prinz, M., D'Souza, J., Kismihók, G., Stocker, M., and Auer, S. (2019). Open Research Knowledge Graph: Next Generation Infrastructure for Semantic Scholarly Knowledge. *K-CAP '19*, 243–246. DOI: [10.1145/3360901.3364435](https://doi.org/10.1145/3360901.3364435).

[7] Lamport, L. (2011). How to Write a 21st Century Proof. *Journal of Fixed Point Theory and Applications*. [Author's publication record](https://www.microsoft.com/en-us/research/publication/write-21st-century-proof/).

[8] Bloomfield, R., and Rushby, J. (2021). Assurance 2.0: A Manifesto. [arXiv:2004.10474v3](https://arxiv.org/abs/2004.10474v3).

[9] Lebo, T., Sahoo, S., and McGuinness, D., eds. (2013). *PROV-O: The PROV Ontology*. W3C Recommendation, 30 April 2013. [Fixed recommendation](https://www.w3.org/TR/2013/REC-prov-o-20130430/).

[10] Knublauch, H., and Kontokostas, D., eds. (2017). *Shapes Constraint Language (SHACL)*. W3C Recommendation, 20 July 2017. [Fixed recommendation](https://www.w3.org/TR/2017/REC-shacl-20170720/).

[11] Kuhn, T., and Dumontier, M. (2014). Trusty URIs: Verifiable, Immutable, and Permanent Digital Artifacts for Linked Data. *ESWC 2014*, LNCS 8465, 395–410. DOI: [10.1007/978-3-319-07443-6_27](https://doi.org/10.1007/978-3-319-07443-6_27).

[12] Liu, H. (2026). *Experience, Intelligence, and Self Within Experience: Definitions, Conditional Theorems, and Thought Experiments for a Structural Account*. Version 1.0. Theoretical preprint, not peer reviewed. DOI recorded in the archived manuscript: [10.5281/zenodo.23206492](https://doi.org/10.5281/zenodo.23206492). Source text, rather than DOI service availability, was used in this comparison.

[13] Luo, J. (2026). *XScientist: A Git-Like Research Protocol for Long-Running Autonomous Scientific Discovery*. [arXiv:2607.12301v2](https://arxiv.org/abs/2607.12301v2), revised 22 September 2026.

[14] Brännström, M., Xanthopoulou, T. D., and Brännström, A. (2026). Hybrid-Human Grounded Theory with Multi-Step Epistemic Continuity. *HHAI 2026*. DOI: [10.3233/FAIA260525](https://doi.org/10.3233/FAIA260525).

[15] Su, B., Li, P., Lu, Y., and Chen, X. (2026). *PEARL: Auditable Repair for Scientific Reasoning Graph Extraction*. [arXiv:2607.17917v1](https://arxiv.org/abs/2607.17917v1).

[16] Wang, F. Y., and Buehler, M. J. (2026). *Self-Revising Discovery Systems for Science: A Categorical Framework for Agentic Artificial Intelligence*. [arXiv:2606.01444v2](https://arxiv.org/abs/2606.01444v2), revised 21 August 2026.

[17] Liu, H. (2026). *UCT-MAP-v1.0.0: Frozen Author-Side Semantic Audit and Research Recovery Artifacts*. Research archive, not independently certified. [Release manifest at commit f6445052](https://github.com/thechurchofagi/trinity-accord/blob/f6445052acb1644fcdd7b2adcdda2307f7b98bc7/research/uct-agent-consciousness-workspace/versions/UCT-MAP-v1.0.0/RELEASE.json). Full recovery archive SHA-256: `063eea5a817f1868004f5bfe51e4bbf4f741dac32a6427fa75fb61eb0df636bb`.

[18] Liu, H. (2026). *UCT Research Master Guide: Whole-Map Review and Persistent Research*. Project policy version 2.0, 8 October 2026. [Fixed source at commit 48b131a3](https://github.com/thechurchofagi/trinity-accord/blob/48b131a3ae8f7ac003ff5a2ce9c8d36111b2ea3c/research/uct-agent-consciousness-workspace/RESEARCH_MASTER_GUIDE.md). A methodological requirement, not an empirical scientific premise.

# Appendix A. Minimal record and release schema {-}

A claim should include `id`, `statement`, `kind`, `environment`, `definition_versions`, `logical_status`, `review_status`, `application_status`, `sources`, `proof_or_evidence`, and `limits`. An inference includes `premises_all_of`, `conclusion`, `binding`, `guard`, `source_contract`, and `active`. Distinct rule records preserve OR alternatives. A thought experiment includes `fixed`, `varied`, `domain`, `admissibility`, `target`, `outcome`, and `interpretation_limit`.

A release records its version and sequence, parent, source hashes, added/changed/suspended identifiers, review inventory, open obligations, artifact locations, and preservation receipt. Exact machine-readable names appear in the supplementary `RELEASE.json`. The current pointer is mutable; a completed version is not overwritten. The next substantive completion increments the sequence even when its result is a correction or a negative finding. A copy-verification receipt does not create an extra scientific result.

The supplementary method map is a compact index of this paper's substantive definitions, protocol choices, propositions, case counts, and limitations. Its author-side review does not certify every sentence of the bibliography or recreate the UCT audit. The JSON records specify that coverage boundary.

# Appendix B. Reproduction and interpretation {-}

From the supplementary package root, run:

```text
python code/reference_checks.py --output rerun_results --backup evidence
```

The package includes the exact frozen `REVIEW_LEDGER.json` and `UCT_EFFECTIVE_GRAPH.json` needed by that command. Without `--backup`, the finite demonstrations still run but the case-census step is explicitly marked `NOT_REQUESTED`. The script writes the complete fixtures and results, fails on unexpected outcomes, and makes no external network requests.

The manuscript's current checks are descriptive re-analysis, exhaustive enumeration over declared finite domains, and authored conformance fixtures. No outcome should be reinterpreted as a new consciousness experiment, a discovery-performance benchmark, a proof-assistant certificate, or a measure of independent reviewer agreement.
