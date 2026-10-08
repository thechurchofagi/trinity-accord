# Coupling, retained distinctions, and relative time in UCT
## A theory-first continuation through two-system and mechanical-brain thought experiments

**Record:** TF20261008, v0.1, 8 October 2026.  
**Status:** Unpublished conditional research note; not a numbered R round, not a new consciousness law, and not publication authorization.  
**Baseline read:** R180 plus EX20261008 and METHOD_20261008; UCT I v1.2 §§6–7,9; BR20261008 §§1–6.  
**Method:** Thought experiments and analytic derivations first; small numerical checks verify equations only. No human, animal, or language-model experiment was performed.

## 1. What changes relative to the previous round

The preceding method note separated complete actual organization, mathematical models, observations and named experiential targets. This continuation makes one organizational contrast explicit: **coupling can increase cross-component influence while compressing previously independent distinctions, but another coupling mechanism can redistribute the distinctions without that extra compression.** The relevant comparison needs a physical constituent split, a time horizon, actual transition laws and an independently grounded metric. A graph or a coupling-strength number is insufficient.

The statement that transformation need not be enrichment is already published in UCT I §9. Non-summative combination is already in §6, and graph-role discontinuity versus continuous dynamics is in BR20261008. The present project-level application is an exact *paired* continuous-time construction, a relative-timescale test for the mechanical-brain experiment, and a concrete warning against deriving subject number from coupling or asymptotic consensus. The mathematics uses established linear systems and consensus tools; historical novelty is not claimed.

## 2. The fixed comparison

Consider two explicitly stipulated state carriers, with real states x and y, independently grounded local preparation ports, an elapsed physical time T, and a common leakage rate mu >= 0. Initial-state perturbations are model probes, not new experience tokens or consciousness labels. Fix Euclidean amplitude geometry in the calibrated x/y units. Under a change of coordinates the metric and physical intervention ports must be transported, not silently reset.

These are exact *models*. No claim is made that they exhaust a real brain, that x/y mean red/blue or self/other, or that an abstract state trajectory is automatically an actual physical bearer. At g=0 the independent pair is a product comparison object; it need not constitute a single causally continuous actual token. C1/U1 is not applied to an imaginary aggregate.

The thought experiment asks what follows **if** two memory-bearing subsystems are connected through one of the following mechanisms. An actual substrate application additionally requires physical anchoring, boundary/time agreement, and correspondence of the relevant actual mechanisms and response relations.

## 3. Averaging coupling: cross-influence versus contrast retention

Let g >= 0 and define

    dx/dt = -mu*x + g*(y-x)
    dy/dt = -mu*y + g*(x-y).

Set m=(x+y)/2 and d=(x-y)/2. Direct addition and subtraction give

    dm/dt = -mu*m
    dd/dt = -(mu+2g)*d.

Consequently,

    m(T) = exp(-mu*T)*m(0)
    d(T) = exp(-(mu+2g)*T)*d(0).

Writing q=exp(-2gT), the response matrix is

    S_D(T) = exp(-mu*T)/2 * [[1+q, 1-q], [1-q, 1+q]].

Define two deliberately limited descriptors:

    C_D = exp(mu*T) * d x(T)/d y(0) = (1-q)/2
    Q_D = exp(mu*T) * d(T)/d(0) = q,

where the second expression denotes the linear response coefficient even when d(0)=0. C_D is normalized cross-port response, not channel capacity or experienced unity. Q_D is normalized differential-mode retention, not a consciousness score. The normalization removes common leakage for comparison; raw amplitudes still decay.

**Local result TF-1.** For fixed T>0, C_D increases strictly with g and Q_D decreases strictly with g, with

    2*C_D + Q_D = 1.

**Proof.** Substitute q=exp(-2gT), or differentiate: dC_D/dg=T*q>0 and dQ_D/dg=-2T*q<0. This identity is specific to the stipulated averaging mechanism. It is not a universal physical or experiential trade-off.

Thus a link can make one initial source affect the other carrier more strongly while making their initial difference less robustly recoverable. “More cross-influence” and “more preserved differentiation” are separate claims.

### 3.1 The finite-time precision trap

For every finite g,T, det S_D(T)=exp(-2mu*T-2gT)>0. Therefore this ideal real-valued map is injective: it does **not** exactly erase initial information at finite time. Its singular values are exp(-mu*T) and exp(-(mu+2g)*T). Recovery in the most contracted direction amplifies bounded observation errors by exp((mu+2g)*T).

Small amplitude is not zero information. Statements about effective loss require a specified accuracy, noise model, accessible readout and horizon. None of these is a basal-experience threshold. In the mu=0, T-to-infinity limit, the map converges to a rank-one averaging projection; that limit is not a finite conscious episode.

## 4. Mixing without extra contraction: a countercase to a universal trade-off

Consider instead

    dx/dt = -mu*x + g*y
    dy/dt = -mu*y - g*x.

Its response is

    S_R(T) = exp(-mu*T) * [[cos(gT), sin(gT)], [-sin(gT), cos(gT)]].

**Local result TF-2.** This mechanism has the same unsigned bidirectional cross-link graph and the same absolute cross-link rate g as the averaging mechanism, but both singular values equal exp(-mu*T). Increasing g rotates the joint state rather than adding differential contraction.

**Proof.** The bracketed matrix is orthogonal, so S_R(T)^T S_R(T)=exp(-2mu*T)*I. The cross-response is exp(-mu*T)*sin(gT); for 0<gT<pi/2 it increases with g while normalized worst-direction retention remains one.

The mechanisms deliberately differ in sign and self-dynamics. We do not claim they have identical complete organization or identical signed weighted graphs. This is precisely why bare adjacency plus an absolute connection-strength number does not determine the result.

At gT=pi/4, both outputs mix the two input states, but their joint pair still preserves all Euclidean distinctions up to common leakage. A particular old coordinate may become zero while the distinction survives in another coordinate. This is a positive example of *redistribution* rather than disappearance.

The pair supports a useful research question: **does a proposed organizational change preserve differentiated relations while making them jointly consequential, or does it produce agreement by contracting them?** Neither alternative alone determines a subject, intelligence or a named feeling.

### 4.1 Endpoint versus episode

At gT=pi, the rotation's endpoint cross-response is zero, but at time T/2 it has magnitude exp(-mu*T/2). Zero endpoint cross-response is not absence of communication during the episode. For a window-sensitive comparison use the full family S(t), 0<=t<=T, or an explicitly declared window functional, not only S(T).

## 5. Boundaries depend on relations and timescales, not an observer's label

For every g>0, the averaging family has cross-dependence relative to the original x|y physical split at every T>0. That is a positive nonproduct relation for this stipulated comparison, not a proof of one exclusive subject.

At mu=0,

    lim[T -> infinity] lim[g -> 0+] exp(-2gT) = 1,
    lim[g -> 0+] lim[T -> infinity] exp(-2gT) = 0.

**Local result TF-3.** Weak coupling and arbitrarily long waiting are not interchangeable limits. For a finite interval the controlling parameter is gT, not the yes/no existence of an edge.

For example, a freely declared approximation tolerance 0<eta<1/2 makes the criterion C_D<=eta equivalent to

    g <= -log(1-2eta)/(2T).

This is an operational criterion for a selected response approximation. Its dependence on eta and T blocks interpreting it as a universal physical point at which two subjects become one. Changing an observer's tolerance changes the classification, not the actual process. Real constitutive timescales may be physically grounded, but this example does not derive a unique phenomenal integration window.

### 5.1 A diagonalization is not a new physical partition

The m,d coordinates diagonalize averaging dynamics. It would be a mistake to conclude that the original two carriers are physically independent because this basis makes the matrix diagonal. A local perturbation to x changes both m and d. The physical x|y intervention split must be carried through the coordinate transformation.

Within-part invertible recodings preserve whether the cross-response block is zero: under such recodings R_yx becomes B*R_yx*A^(-1). A global mixing of x and y is not a within-part recoding. This supplies a concrete version of UCT I's existing port-aware organization requirement, not a new universal subject criterion.

### 5.2 A macrostate need not exhaust the whole

The mean m obeys an autonomous scalar equation in this model, but states (1,-1) and (-1,1) share m=0 while retaining different d at every finite time. Modeling the mean may be valid for a selected task, yet it discards whole-system distinctions. A newly useful macro-description does not by itself delete the actual constituent processes or establish one experiential owner. UCT I §6.4 already distinguishes independently realized macroprocesses from arbitrary statistics; that qualification remains necessary here.

## 6. The giant mechanical brain: relative slowing is the critical fork

Suppose all rates in the stipulated system are divided by c>0, and compare its state at cT with the original at T. Then

    S_(mu/c,g/c)(cT) = S_(mu,g)(T).

**Local result TF-4.** Uniform rate scaling preserves the displayed dimensionless response trajectory under compensated time indexing. This equality holds for both mechanisms above.

It does not establish identical complete experiential type. A signature retaining absolute physical durations distinguishes T from cT. Noise, delays, constitutive material properties, external inputs, environment dynamics and allowed interventions have not been proved equivalent by this calculation. Pure coordinate reindexing and physically slowing a machine remain different operations.

Contrast slowing only the cross-links: g -> g/c while mu and the environmental clock remain fixed. At the memory timescale T_mem=1/mu, mu>0,

    Q_D(T_mem) = exp(-2g/mu).

The ratio g/mu now changes. A system can lose memory substantially before weak cross-influence has accumulated. For g=0.5, mu=0.1, the normalized cross-gain at T_mem is approximately 0.499977; after a 1000-fold cross-link-only slowdown it is approximately 0.004975. No claim is made that these numbers measure experience.

For a geometrically enlarged mechanical brain, preserved wiring alone therefore leaves open whether communication delays, local update rates, memory decay and environment timescales preserve their ratios. In delay models, tau_link/tau_memory is an additional dimensionless quantity. The current ODE has no explicit propagation delay, so it does not prove a delay theorem or a bound for real spatially extended brains.

## 7. How these results attach to UCT

The physical mathematics does not use C1. To obtain its conditional UCT interpretation, independently admit an actual token P, interval I, physical constituent split, a common signature K and a grounded interpretation of these response/time relations in its complete organization. C1 then transports those relations to experiential organization. A calibrated metric must be included or appropriately transported before assigning numerical distance meaning.

This yields a *structural*, conditional statement: the two kinds of coupling instantiate different patterns of relation-preservation and relation-contraction, and those grounded patterns are not discarded in C1's experiential description. It is not a calculation of redness, pain, felt agency, experienced duration, intelligence or subject number. A named experiential interpretation and real physical realization are still open.

The complete-type comparison and selected-relation claim must not be confused. Differing finite model parameters do not automatically prove different complete real brain types. Conversely, identifying a selected macro-mean does not establish equality of complete organization. C1 remains a substantive axiom, not a conclusion of our numerical checks.

No basal-experience gate is added. Continuing actual constituents remain covered by U1/P3; we do not insist their experiential organizations remain unchanged under coupling. No exclusive owner is introduced. At g=0 an abstract disjoint product is not silently promoted to an actual whole token. Nonproduct relative to x|y does not mean irreducible under every conceivable split.

## 8. Verification and the limits of the calculation

The accompanying standard-library Python file implements both closed forms and independently integrates their ODEs by RK4. Forty-eight parameter/model cases give maximum absolute matrix error 9.829914660031136e-13. Eleven named checks cover eigenmodes, the averaging-only identity, rotation retention, finite-time invertibility, uniform versus link-only slowing, macro-hidden contrast, endpoint versus window and tolerance/horizon dependence. A limited grid is not a proof of universal claims; the proofs are the displayed algebra.

Selected dimensionless averaging results:

| gT | Normalized cross-gain C_D | Differential retention Q_D |
|---:|---:|---:|
| 0.01 | 0.0099006633 | 0.9801986733 |
| 0.1 | 0.0906346235 | 0.8187307531 |
| 1 | 0.4323323584 | 0.1353352832 |
| 3 | 0.4987606239 | 0.0024787522 |

The statement “averaging erases information at finite time” is explicitly rejected. The link-only slowdown comparison uses the same memory horizon on both sides. Negative findings and this scope audit are part of the result.

## 9. Prior-work and source audit

Internal primary sources, scoped-read rather than a complete repository census:

1. `records/R128_Unified_Formal_Map_Audit_20261006/sources/A_UCT_I_v1_2.md`, §§6–7 and §9, blob `7a980c86b8f94ce787d358dab3529903eb822f8f`. Inherited: non-summative combination, port-aware products, macro/whole distinction and transformation versus enrichment. The finite XOR edge family already separates retention, recurrence and output.
2. `records/BR20261008_Relational_Differentiation/Relational_Differentiation_and_Joint_Experiential_Constraints_v0_1.md`, §§1–6. Inherited: exact role counts versus continuous response, finite propagation, and conditional transport of grounded relations rather than named qualia.
3. `records/METHOD_20261008_Theory_First_Organization/METHOD_NOTE.md`, full note, blob `bdfbc62879a7d6a02954e5e70e29740f5ea40ee8`. Binding theory-first policy and complete/model/measurement distinction.
4. `HANDOFF.md`, current heading through R180/EX20261008, blob at read `94893e7921c3eaa56dc378cab01042d27028dd7e`. Existing empirical audit preserved. This continuation does not claim to have reread or replicated its human/animal papers.

External primary sources consulted for provenance, not as independent UCT confirmation:

- Olfati-Saber and Murray, *Consensus problems in networks of agents with switching topology and time-delays*, IEEE TAC 49(9), 1520–1533 (2004), DOI 10.1109/TAC.2004.834113. Author-hosted summary read: https://murray.cds.caltech.edu/Consensus_problems_in_networks_of_agents_with_switching_topology_and_time-delays . Consensus dynamics, disagreement decay and topology/speed relations are established antecedents. The full article was not reread for this note.
- Beckers and Halpern, *Abstracting Causal Models*, arXiv:1812.03789, publication associated with AAAI 2019. Abstract and introductory/formal sections read: https://arxiv.org/abs/1812.03789 . State abstraction must account for intervention semantics; this is prior causal-model methodology, not UCT novelty.
- Barnett, Buckley and Bullock, *Neural complexity and structural connectivity*, Physical Review E 79, 051914 (2009), DOI 10.1103/PhysRevE.79.051914. Publisher abstract only: https://journals.aps.org/pre/abstract/10.1103/PhysRevE.79.051914 . Connectivity/complexity modeling has explicit precedents; no uninspected theorem or empirical claim is attributed to this source.

There is no exhaustive novelty claim, no demonstrated UCT-exclusive observable prediction, and no basis here for saying IIT, GNWT, HOT or biological theories have been experimentally refuted.

## 10. Local proof map and handoff

| Claim | Premises | Result | Does not establish |
|---|---|---|---|
| TF-1 | Averaging equations, fixed metric/time/ports | 2C_D+Q_D=1; cross-gain and contrast retention move oppositely | Universal coupling law or experience amount |
| TF-2 | Rotation equations, transported metric | Mixing without extra singular-value contraction | Felt unity or identity with averaging |
| TF-3 | Finite horizon versus asymptotic limits | Boundary approximations depend on gT and tolerance | A subject-merger threshold |
| TF-4 | All rates rescaled, compensated horizon | Equality of the selected dimensionless responses | Complete cross-substrate phenomenal equivalence |
| TF-C1 | Actual common P/I/K, grounded relation interpretation, C1 | Conditional experiential structural counterparts | Named feelings, unique subject, C1 validation |

No canonical graph objects or published manuscripts were modified. This table is a local dependency attachment, not an audit of the entire graph. R179 nonduplication rules, R180's source/uptake distinction and QC10/IA-QC11/QC12 application gaps remain open.

**Next substantive question:** formulate a target-relative, physically grounded account of *coordination that retains differentiated roles*. Test it against a master that merely forces copies, a reversible distributed code, two communicating memory systems, and a human-operated mechanical implementation. Do not identify retained dimensionality with subjecthood. A decisive next step must constrain one experiential relation under C1 without naming a functional register after the feeling to be explained; otherwise retain the result as organization theory, not a solved consciousness bridge.

**Storage:** local research package plus the persistent research branch. README receives a discoverable pointer. Do not overwrite concurrent numbered rounds, initiate DOI/OTS/Arweave, or change scheduled tasks. The later source-audit instruction to acquire data does not override the author's explicit current theory-first instruction.
