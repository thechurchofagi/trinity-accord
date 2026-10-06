# R127 — From a capability requirement to actual organizational support

Hongju Liu / UCT research checkpoint, 6 October 2026.

**Status:** theoretical working note under published UCT I v1.2, II v1.1 and III v1.0. Hand-derived proofs and counterexamples; no proof-assistant verification, empirical fitting, simulation, experience measurement, or publication release. General automata, information-theoretic and isomorphism results are established mathematics, not claimed here as historical discoveries.

## 1. The question and the advance over R126

R126 separated arbitrary coordinates, operation-closed causal descriptions, and physically justified constitutive interpretation. It left the positive question: what can a capability require of actual organization, rather than merely of a mathematical summary?

This note gives a conditional chain for delayed discrimination:

1. The task determines distinctions that any exact implementation must preserve.
2. Every complete causal cut between acquisition and response must carry sufficient distinctions, jointly with declared external resources.
3. The distinctions can reside in relations among carriers, and can move between carriers over time.
4. Membership in an actual process is established by physically grounded events, inherited relations and accounted boundaries, using UCT I's existing token criterion.
5. C1 then preserves those identified structural relations in the intrinsic presentation of that actual token. It does not supply a familiar feeling label or an exclusive subject.

The contribution is this explicit connection, including where each premise enters. We do not derive a unique physical implementation from behavior. We also correct a possible ambiguity in the prior queue: UCT already supplies a process-domain criterion. What remains is its application to a specified support, not a new admission threshold for experience.

## 2. Fixed objects and assumptions

There are three different domains:

- A **task family**, specifying histories, later queries, required answers, accuracy, timing and resources.
- A **supplied implementation model**, describing possible runs and all relevant physical channels. Its counterfactual states and operation laws are not all actual occurrences.
- An **actual process token** P, with complete token-relative structure K(P), a declared interval and accountable boundary. C1 concerns this token, not a bare task table.

For the exact task results, let H, Q and Y be finite nonempty sets. A history x in H is presented before a temporal cut; q in Q is supplied later. The prescribed answer is

\[
f:H\times Q\to Y.
\]

All pairs in this Cartesian product are admitted. The query is not supplied to the encoder in advance. In the noisy deferred-query claims it is externally set, or sampled independently of the pre-query encoding and its noise; it cannot secretly correlate with an encoder seed and thereby supply missing information. If availability depends on x, use an explicit availability marker and a new specification; do not apply the theorem unchanged. If a task admits several acceptable answers rather than one f(x,q), the equivalence and minimality result below also needs revision.

The cut state C includes every state, signal in transit, clock distinction and boundary memory on which the later computation can depend, except declared side information B. A clock encoding x is a memory channel for this purpose. A pre-trained constant independent of the particular trial's x is a resource, not a source of that trial's missing information.

For noisy results, the decisive mediation assumption is

\[
P(y\mid x,c,b,q)=W_q(y\mid c,b).\tag{M}
\]

It must follow from the supplied causal model, rather than from a regression fit. One sufficient finite-model construction is a time-unrolled acyclic structural model in which every past-to-answer path meets C or B, and subsequent exogenous noise is independent of (X,C) conditional on B and the exogenously supplied query. Correlated noise, an external archive, a timing channel or a later re-presentation of x must be included if it defeats (M). A directed-path drawing alone is insufficient when shared exogenous causes are omitted.

These are conditions for attributing a capability to specified resources. They are not conditions for the existence of experience.

## 3. Proposition 1 — The task determines a minimum distinction structure

Define the response profile and task equivalence by

\[
\rho(x)=(f(x,q))_{q\in Q},\qquad
x\equiv_Q x'\ \Longleftrightarrow\ \rho(x)=\rho(x').
\]

Let z:H→Z be a deterministic encoding at the cut, with no additional history-bearing input available later. There is an exact decoder d satisfying

\[
f(x,q)=d(z(x),q)\quad\text{for all }x,q
\]

if and only if

\[
z(x)=z(x')\Rightarrow x\equiv_Q x'.\tag{1}
\]

Equivalently, there is a well-defined map g on z(H) with rho=g∘z. Consequently

\[
|z(H)|\ge |H/{\equiv_Q}|.\tag{2}
\]

**Proof.** If z(x)=z(x'), the decoder has the same arguments for each q and hence gives the same answer. Conversely, if (1) holds, define d(z(x),q)=f(x,q); the value is independent of the chosen representative x. Each distinct response profile requires a distinct code value, proving (2). Choosing z=rho attains the bound at the abstract encoding level. QED.

The sufficiency is logical representability, not physical feasibility under arbitrary time, energy, locality or noise limits. A minimum abstract code does not identify its actual carrier.

### Query-family refinement

If Q1⊆Q2 under a common f, then equivalence under Q2 refines equivalence under Q1. Proof: equality of all Q2 answers entails equality on its subset. Thus expanding the capability requirement can force more retained distinctions without fixing how those distinctions are realized. Strict growth is not guaranteed.

For x=(x1,...,xn) in {0,1}^n, asking only parity requires two response classes. Asking any indexed bit q=i requires 2^n classes: two different strings differ at some queried position. Asking a known index before encoding requires only the selected bit; this changes the task and cannot be used to refute the delayed-query bound. These are symbolic examples, not new simulations.

### Relation to R126's dynamical refinement

In R126's deterministic model, let o(s)=(p(s),r(s)). Define

\[
s\equiv_\infty t\ \Longleftrightarrow\
o(F_w(s))=o(F_w(t))\ \text{for every finite operation word }w,
\]

including the empty word. This is exactly R126's stabilized equivalence. It is stable, because a first operation followed by any word is another word; it refines the initial observation equivalence. Conversely any stable equivalence refining o preserves o after every word by induction. Hence it is the coarsest such equivalence, the same object characterized by R126's refinement proof.

This identifies *which future distinctions* that refinement retains. It is the familiar automata/predictive-equivalence idea, not a new automata theorem. Passive predictive equivalence and intervention-preserving equivalence must still use their respective declared query/operation families.

## 4. Proposition 2 — Every complete causal cut must retain the required distinction

In a deterministic implementation satisfying (M), fix common side information b and take two admissible histories x,x' requiring different answers to the same query q. Their full cut states cannot be equal. Otherwise the common downstream computation Wq, supplied with equal cut states and b, would give equal answers.

For stochastic cut states, let mu_x and mu_x' be their distributions under these two preparations, at common b and q. The same downstream kernel implies

\[
\operatorname{TV}(P_{Y|x,b,q},P_{Y|x',b,q})
\le\operatorname{TV}(\mu_x,\mu_{x'}).\tag{3}
\]

If the correct outputs differ and their respective error probabilities are at most epsilon_x and epsilon_x', then

\[
\operatorname{TV}(\mu_x,\mu_{x'})\ge
1-\epsilon_x-\epsilon_{x'}.\tag{4}
\]

The right side is informative when positive; for equal error epsilon it is 1−2epsilon.

**Proof.** In finite spaces, for any output event A,

\[
P_x(A)-P_{x'}(A)=\sum_c(\mu_x(c)-\mu_{x'}(c))W_q(A|c,b).
\]

Since 0≤Wq(A|c,b)≤1, the absolute value is bounded by the total variation of the cut distributions. Maximize over A to obtain (3). For (4), take A to be the correct-answer singleton for x. Its probability is at least 1−epsilon_x under x and at most epsilon_x' under x', since x' has a different correct answer. Combine the inequalities. QED.

In the zero-error finite case, distinct response profiles require disjoint supports of cut states. Any shared positive-probability state would require a single downstream kernel to produce two different answers with probability one. Thus randomized encoding cannot evade the exact distinction count by overlapping its supports.

### Temporal persistence without a privileged carrier

The argument applies at **each** complete cut during the delay, provided (M) holds there. Information sufficient for the later discrimination cannot disappear from the complete carrier-plus-boundary state at one cut and be recreated from independent inputs later. It can, however, move from one carrier to another. A finite chain of relays can preserve the distinction without a recurrent loop, a stable dedicated neuron, or a verbal self-report.

This is a necessity for the selected memory capability. It is not an experience-onset criterion, a requirement that one subject persists throughout the interval, or a claim that every current carrier has positive individual information about x.

## 5. Proposition 3 — External support changes the internal requirement quantitatively

Let X have m≥2 possible values; let C be the declared internal cut state and B all admitted external side information. Suppose a later output estimates X through (C,B), with error epsilon. All logarithms here are base two. Then

\[
I(X;C\mid B)\ge H(X\mid B)-h_2(\epsilon)
-\epsilon\log_2(m-1),\tag{5}
\]

and for a finite internal state space

\[
\log_2|\mathcal C|\ge H(C\mid B)\ge I(X;C\mid B).\tag{6}
\]

Use zero as a trivial lower bound when the right side of (5) is negative.

**Proof.** Conditional mediation gives H(X|C,B)≤H(X|Xhat,B): this is conditional data processing. To see the required entropy bound directly, introduce the error indicator E. Given Xhat and B, specifying E costs at most h2(epsilon) bits. If E=0, X is determined; if E=1, at most m−1 possibilities remain. Thus

\[
H(X\mid\widehat X,B)\le h_2(\epsilon)+\epsilon\log_2(m-1).
\]

Subtract from H(X|B) to obtain (5). Finally I(X;C|B)≤H(C|B)≤log2|C|. QED.

The error epsilon is the actual average error of the specified estimator. This is a Fano/data-processing application, not a novel information inequality. It does not turn information in bits into an amount of experience or a count of physical components. A noiseless real-valued variable with unbounded precision has no finite alphabet bound; any physical precision/noise restriction must be stated.

### Delayed indexed recall

Let X be n independent fair bits. Select query i independently of the encoding after the cut. Suppose the answer to each query has error epsilon_i≤1/2 and depends only on S=(C,B) and the query. For each i, binary error accounting and mediation give H(Xi|S)≤h2(epsilon_i). Therefore

\[
I(X;S)=n-H(X\mid S)
\ge n-\sum_i h_2(\epsilon_i)
\ge n[1-h_2(\bar\epsilon)],\tag{7}
\]

where the first inequality uses conditional entropy subadditivity and the second concavity of h2. Hence a finite joint state S needs at least that many bits of logarithmic alphabet capacity. This does not assert that every bit can be read simultaneously without disturbing the state; it compares each admitted query from the same pre-query state distribution.

Equation (7) bounds the **joint** support. It cannot be assigned entirely to C when B is available. Equation (5) makes the corresponding internal attribution explicit for full-X recovery. Perfect indexed recovery also implies H(X|C,B)=0, hence I(X;C|B)=H(X|B).

### A relation can retain information absent from every individual marginal

Let X and N be independent fair bits, C=X XOR N, and B=N. Then

\[
I(X;C)=I(X;B)=0,\qquad I(X;C,B)=I(X;C\mid B)=1.
\]

Each carrier alone is uninformative, while their joint relation determines X by XOR. This does not create information from nothing; a decoder using only C is missing the key channel. It extends the published Paper C §7.2 distinction between masked storage and accessible task information by making the formerly unavailable mask an explicit available resource.

If instead B=X is an external archive, the same perfect answer is compatible with C being constant at the cut. Equation (5) correctly gives no positive internal information requirement because H(X|B)=0. The archive retrieval and boundary signal still have to be physically implemented and accounted for.

These examples show why neither single-site decodability nor successful final behavior identifies where the required organization resides.

## 6. A localization obstruction and the limits of lesion reasoning

Consider two ideal delayed-recall implementations with identical exposed input, query, output, timing and permitted interface operations. In A, an internal register retains X. In B, an external register retains X and delivers it through a declared boundary port; the internal cut state before retrieval can be constant. Both return the same X for every admitted interface history. Such ideal implementations are possible in a model family allowing both placements and matched latency.

Any identification rule whose complete input is only that interface law must return the same result for A and B. It therefore cannot correctly infer different internal storage locations in both. This proves a scoped non-identifiability claim. Exposing the archive port, imposing locality/latency restrictions, or permitting location-specific interventions changes the available evidence and can break the equivalence.

Similarly, a necessary intervention target need not be inside a predeclared token boundary. Removing an external power input may stop a local computation. Conversely, an actual internal contributor may be replaceable by a redundant route, so removing it need not change the selected output. A component may also be constitutive of the whole chosen episode while irrelevant to the selected task.

Accordingly these predicates must not be collapsed:

| Predicate | What it says |
|---|---|
| Constitutive of P | The event/relation belongs to this physically identified token's organization. |
| Required by task family | Every implementation in the declared family needs the specified distinction or some support satisfying a condition. |
| Necessary in a manipulation context | The selected capability fails under the specified removal with other conditions fixed. |
| Used in this occurrence | The relation is instantiated in the actual execution path or interaction. |
| Sufficient in context | Together with stated background resources it supports the capability. |

A task necessity often has the form “some support across this complete cut,” not “this particular constituent in every implementation.” R111's alternative-support hypergraph already captures that disjunction. The present results constrain those support alternatives; they do not make their intersection a unique intelligence organ.

## 7. Proposition 4 — A positive, finite route to actual-process membership

UCT I v1.2 §2.5 already supplies a finite actual-process criterion. Apply it explicitly instead of treating a predictive variable as a new process.

Assume a **physically grounded** finite event graph G over an actual episode: vertices are actual occurrences, edges are actual inherited causal relations, and times and materially relevant boundary connections are represented. Take a nonempty vertex set V_H, connected through the inherited causal links over the declared interval. Retain all G-edges between its vertices, record materially relevant crossing edges as ports, and preserve the physically traceable occurrence/continuation history.

Then the resulting subhistory H is an admissible actual process under that existing finite criterion. Each retained internal relation belongs to H's organization, independently of whether it is necessary for a chosen task.

**Proof.** Vertices witness actual support. Induced edges witness relation fidelity. Inherited connected causal history witnesses continuity. Recorded crossing edges witness boundary accountability. The recorded occurrence history gives traceability, while coordinate renaming does not alter the selected occurrences. These are the stipulated token conditions, rather than an inference from prediction accuracy. QED.

This proposition is an application of the published definition, **not** a newly discovered empirical test or a derived universal boundary selector. The graph's physical grounding remains a substantive premise. Connectivity here does not impose recurrent dynamics, mutual influence among every pair, maximality or an autonomous Markov state.

### Applying the construction to support

For an actual routed episode, physically established input-to-output paths can supply candidate vertices. Take their union and the inherited graph on those vertices; if it is connected, preserve its boundary ports and traceability as above. This produces a candidate support subhistory without assuming an anatomical boundary in advance. If the union is disconnected, do not invent edges: consider the components or independently establish actual connecting activity in a larger episode.

The graph of actual events must not be replaced by the union of all counterfactual routes the architecture could have taken. Likewise, a path in a statistical graph, a computationally decoded feature or a possible future operation is not automatically an actual event or physical interaction.

A causal cut C need not itself be connected; it can intersect several parallel paths. Its informational sufficiency therefore need not make C an additional process token. The connecting history and its ports do the physical work. Conversely an open local process remains an actual process while receiving external inputs: boundary accountability permits representing an external contributor as a port without forcing it inside that local token. A larger interaction token may also be admitted. No unique boundary or subject partition follows.

## 8. Proposition 5 — What the identified support licenses under C1

Let P be an independently established actual token. Write its complete common-signature organization as D(P), and the C1 isomorphism as

\[
h_P:D(P)\cong\Phi(P).
\]

Let a selected support contain actual carrier occurrences and typed relational facts of D(P), identified by physical grounding rather than by transporting an arbitrary numerical summary. Restrict attention to a relational reduct if the selected carriers are not closed under every operation of D(P).

For every retained relation R and admitted tuple a in its physical support,

\[
R^{D(P)}(a)\Longleftrightarrow R^{\Phi(P)}(h_P(a)).\tag{8}
\]

Thus the selected physically identified relation structure has an isomorphic image within the intrinsic organization of P.

**Proof.** This is the relation-preserving and relation-reflecting property of a structural isomorphism. Restricting the carrier and inherited relations preserves that property. If operation structure is claimed as well, the selected domains/codomains and outputs must be retained or represented as ports; a restriction not closed under operations must not be called an operation-preserving subalgebra. QED.

Unlike R126's arbitrary transported numerical projection, this statement has a separately supplied actual-support witness. Its physical premise is stronger. The C1 step itself remains a conditional structural consequence, not independent evidence for C1 and not a method of discovering a feeling label.

Three limits are essential:

1. A task-equivalence class is a counterfactual response description. It is not automatically a constituent slot of D(P). The physically realized carriers and relations, not the mere number of classes, receive the conclusion (8).
2. A relation's image in Phi(P) does not make that relation an independent subject. If an actual subhistory H is also a token, C1 applies to H separately; identifying Phi(H) with a particular phenomenological “part of” Phi(P) requires the relevant inclusion and boundary maps to be specified and preserved. Independently chosen type labels alone do not provide that relation. When constituent maps are part of the common signature, their commutation follows by preservation of those maps.
3. Identical task quotients across two implementations do not identify their complete D or Phi. Nor does a lower bound on physical information capacity produce a scalar ordering of experiential richness, human-likeness, valence or fear.

There is no extra E-variable that can be changed while complete D(P) is held fixed under C1. The causal explanation runs through the actual organization; its intrinsic presentation does not supply a second force.

## 9. Combined conclusion: capability-conditioned organizational constraints

For delayed discrimination, suppose the task law and implementation mediation assumptions hold. Suppose further that physical grounding identifies the relevant carriers, routes and boundaries in an actual token P. Then:

- Proposition 1 specifies the distinctions an exact implementation cannot collapse.
- Propositions 2–3 constrain their preservation across complete cuts, including error and external-resource qualifications.
- Proposition 4 establishes membership for a physically witnessed finite subhistory using the already published ontology.
- Proposition 5 carries the actual identified relational structure into P's intrinsic organization under C1.

This is more informative than merely saying “unequal capability implies unequal complete type.” It identifies a family of required preservation/access relations under a specified capability. It remains **disjunctive over physical realizations** and **conditional on actual support identification**.

The argument has different conclusions for three cases:

| Physical case | Theoretical conclusion |
|---|---|
| History is retained internally and used through grounded internal relations | Those identified relations are part of the chosen token's organization, with the C1 interpretation in (8). |
| History is retained externally and later supplied through a port | Capability belongs to the admitted resource arrangement; internal retention cannot be inferred from success alone. The actual local input/use process and any justified larger interaction remain within UCT's domain. |
| Joint relations carry the history but individual marginals do not | The complete support must be analyzed jointly; failure of individual decoders does not erase relational retention. |

No rat or AI result has been used to verify these premises in this round. R125's failed scalar decoder does not test this entire family. Nor is the relational example offered as an explanation of those rats without evidence.

## 10. Counterexample and assumption audit

| Tempting inference | Why it fails or what is needed |
|---|---|
| Every task history needs its own state | Only distinct response profiles do; parity collapses many histories. |
| Correct delayed answers imply internal storage | External B may already contain X. |
| Zero information at every individual site means no stored information | XOR/key support has zero marginals and one bit jointly. |
| A more accurate predictor can recover an erased distinction | Not under the same mediation kernel; (3) is a contraction bound. |
| Task memory requires recurrence or a fixed carrier | A relay chain preserves it across successive complete cuts. |
| A successful quotient is automatically an actual process | A cut may be disconnected; a computed coordinate need not name occurrences. |
| Every necessary enabler is inside the chosen process | External power or side information can be represented at its boundary. |
| Every constituent is individually necessary | Redundancy and task-irrelevant constituents defeat this. |
| An abstract minimum code can be implemented within any budget | Logical sufficiency does not guarantee time, energy or physical feasibility. |
| The theorem bounds a noisy observed decoder's capacity directly | It concerns specified states and channel laws; measurement noise and latent support need their own model. |
| Task distinctions count moments of experience | The quotient is a task-relative counterfactual object, not an experiential unit count. |
| C1 alone identifies a selected familiar feeling or unified subject | Neither label nor exclusive subject criterion is supplied here. |

## 11. What remains theoretical work

The next question is **compositional reuse**: when several capabilities use overlapping supports, what additional routing, temporal coordination and conflict-resolution relations are required to exercise them jointly? Two capabilities available separately need not be jointly exercisable under one resource budget. The XOR example also shows why summing individual information contributions is unreliable.

A useful next derivation should therefore distinguish alternative supports, shared supports and simultaneous use; fix resource and operation compatibility; and determine which added coordination relations survive changes of implementation. This advances R111's support hypergraph beyond a monotone availability table without declaring a universal scalar intelligence measure. The selected experiential interpretation can follow the same actual-support/C1 sequence.

Universal phenomenal labels, exclusive subject boundaries, complete cross-substrate identity and empirical model identification remain open. No new experiment is queued. The point is to finish the local theoretical object and its discriminating alternatives before choosing a measurement.

## 12. Sources and reading scope

Published project sources, preserved unchanged:

- **UCT I v1.2**, DOI [10.5281/zenodo.23131575](https://doi.org/10.5281/zenodo.23131575), fixed source ref f8750d32afeea9209e6d53ad3cfbd5bbde7a8126: §2.1–2.5, §3.1 and C1 were re-read in this round. Its finite actual-event criterion directly supplies Proposition 4; C1 supplies Proposition 5.
- **UCT III v1.0**, DOI [10.5281/zenodo.23137088](https://doi.org/10.5281/zenodo.23137088): §2 and §7 re-read, including the existing masked-memory example and value-of-information result. Neither is counted as newly discovered.
- UCT II v1.1 remains a fixed foundation; no fresh full reread is claimed.
- R111 support hypergraph, R115 anchored causal content geometry, R126 theory note, HANDOFF and MASTER_INDEX read at the R126 parent. R111 and R115 were fetched in full; the sections used concern alternative support, constitutive membership premises and G3/G4 separation.

External antecedents, with limited claims:

- Cornell CS 4120, [Automating Lexical Analysis](https://courses.cs.cornell.edu/cs4120/2023sp/notes/leximpl/index.html), “DFA minimization”: inspected the suffix-distinguishability and refinement argument. This establishes an explicit automata antecedent for the response-profile argument; our delayed-query physical application is not a new minimization theorem.
- Shalizi and Crutchfield, [Computational Mechanics: Pattern and Prediction, Structure and Simplicity](https://arxiv.org/abs/cond-mat/9907176), published 2001: author abstract and metadata checked, not the full proof. Predictive-state minimality is established prior art; no claim to reproduce all of that theory.
- Muriel Médard, MIT 6.441 Spring 2010, [Lecture 2](https://ocw.mit.edu/courses/6-441-information-theory-spring-2010/5c0b5a8a544cb2320778e4c9e5dea64f_MIT6_441S10_lec02.pdf): text extraction checked, especially PDF pages 11–14 for data processing and error-entropy arguments. The noisy support bounds use standard information theory. Extraction has damaged inequality/error symbols; the displayed proofs above are derived explicitly rather than copied from OCR.
- Craver, Glennan and Povich (2021), [Constitutive relevance & mutual manipulability revisited](https://digitalcommons.butler.edu/facsch_papers/1201/), DOI 10.1007/s11229-021-03183-8: institutional abstract read. It distinguishes metaphysical, semantic and epistemic aspects and proposes matched interlevel experiments. This note does not claim to settle that debate or to have read the full article.
- Mckilliam (2024), [A mechanistic alternative to minimal sufficiency as the guiding principle for NCC research](https://pmc.ncbi.nlm.nih.gov/articles/PMC11013376/), DOI 10.1093/nc/niae014: abstract, introduction and opening discussion retrieved; later targeted retrieval hit a bot challenge. Used only to acknowledge existing criticism of minimal-sufficiency reasoning, not to endorse an empirical prefrontal-consciousness conclusion.

The literature check is targeted, not an exhaustive originality review. The research increment is the connected conditional argument and its attribution limits inside this UCT program.
