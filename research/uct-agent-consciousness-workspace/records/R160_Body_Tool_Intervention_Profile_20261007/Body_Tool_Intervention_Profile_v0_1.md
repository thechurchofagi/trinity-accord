# Protocol-Relative Body and Tool Slots

## Interventions, overlap, and a finite nonidentification limit

Version 0.1, 7 October 2026. Research checkpoint, not a published edition.

## 1. Question and bounded contribution

R159 left one precise gap: an internal body-frame relation can be actually installed even when its external referent is anatomically wrong, but the weak words *binding* and *use* could equally describe a tracked or controlled tool. The present note asks what a finite human upper-limb/tool-use protocol can discriminate without turning a behavioral marker into anatomical membership or phenomenal ownership.

The contribution is deliberately bounded:

1. a typed intervention/readout contract separates biological-body perturbations, tool-transformation perturbations, body-only readouts after tool removal, and tool-specific readouts during use;
2. a four-way classifier permits body dominance, tool dominance, overlap, and neither, so it does not search for a uniquely exclusive extra owner;
3. an exact coupled witness shows that both dominance relations can hold while both cross-effects remain positive;
4. a standard latent-label theorem shows why no finite input/output profile alone determines the meanings *body slot*, *tool slot*, anatomical membership, or familiar felt ownership;
5. C1 is applied only tokenwise: cross-trial intervention contrasts require their own comparison/measurement bridge and are not automatically experiential relations under one common isomorphism.

This advances the physical-witness side of the selected body/tool application. It does not close `B_min`, identify complete neural organization, prove C1, or introduce a new condition for basal experience.

## 2. Types, actual domain, and preregistration

Fix a declared protocol `Pi` over a finite family of actual human trial tokens `P_omega` with intervals `I_omega`. A participant lineage may be retained across trials, but distinct trials are not silently treated as one identical complete organization. For each admitted trial, R159's internal frame token `r_omega`, internal representation token `k_omega`, external referent map `psi_omega`, and actual installed relations remain correctly sorted.

The protocol declares two independently grounded intervention families before inspecting target outcomes:

- `J_B`: a physically verified perturbation of biological somatosensory/proprioceptive input or its task-relevant routing, while the declared tool transformation and distal task are held fixed to the stated tolerance;
- `J_T`: a physically verified perturbation of the tool's motor-to-mechanical transformation, end-effector mapping, or distal feedback contingency, while the declared biological manipulation is held fixed to the stated tolerance.

The names do not do the grounding. A manipulation belongs to `J_B` or `J_T` only through an independently documented physical intervention and fidelity check. Unsafe or destructive interventions are outside this research note; it specifies a theoretical protocol contract rather than executing a human experiment.

Declare two readout families:

- `Y_B`: tool-absent, body-only readouts obtained after the tool is removed, such as preregistered free-hand transport kinematics or tactile/proprioceptive localization on the biological limb;
- `Y_T`: tool-present readouts tied to the functional end-effector or tool-relative multisensory relation, such as endpoint adaptation/error or a distal visuotactile interference contrast.

Questionnaires, confidence and ownership reports may be collected as separate fallible target evidence, but they do not define either family and do not enter the profile classifier below. Every outcome metric, normalization, equivalence tolerance, exclusion rule and multiplicity correction must be frozen before target unblinding. UCT I's no-post-hoc-rescue requirement therefore applies directly.

For one candidate internal slot family `k`, let the normalized causal-effect magnitudes be

\[
S_\Pi(k)=
\begin{pmatrix}
a & x\\
b & y
\end{pmatrix}
=
\begin{pmatrix}
\delta(Y_B;J_B) & \delta(Y_B;J_T)\\
\delta(Y_T;J_B) & \delta(Y_T;J_T)
\end{pmatrix},
\qquad 0\le a,x,b,y\le 1.
\]

The actual study must estimate error-bounded effects. Write lower and upper bounds as `L(.)` and `U(.)`, and fix a positive margin `epsilon` in advance. The exact finite verifier later uses point values on a rational grid only to check the classifier's logical possibilities.

Define

\[
\begin{aligned}
B_\Pi(k)&\iff L(a)>\epsilon\;\land\;L(a)-U(x)>\epsilon,\\
T_\Pi(k)&\iff L(y)>\epsilon\;\land\;L(y)-U(b)>\epsilon.
\end{aligned}
\]

`B_Pi` means **body-dominant under this protocol**; `T_Pi` means **tool-dominant under this protocol**. Neither predicate means anatomical membership, external-reference correctness, a complete constitutive boundary, or felt ownership. Effects in different units are not compared until the normalization and error model have been declared; otherwise the inequalities are undefined rather than false.

## 3. Four outcomes and cross-modulation

The pair `(B_Pi(k),T_Pi(k))` has four exhaustive Boolean cases:

| Profile | Interpretation permitted by the contract |
|---|---|
| `(1,0)` | body-dominant only in `Pi` |
| `(0,1)` | tool-dominant only in `Pi` |
| `(1,1)` | overlapping body- and tool-dominant roles in `Pi` |
| `(0,0)` | neither dominance relation established in `Pi` |

This is a protocol-relative classification, not a metaphysical partition of the organism. In particular, overlap is allowed. With point estimates, `epsilon=1/4`, and

\[
S_\Pi(k)=
\begin{pmatrix}
3/4 & 1/4\\
1/4 & 3/4
\end{pmatrix},
\]

both dominance margins equal `1/2`, while both off-diagonal cross-effects are positive. Thus role dominance does not entail quantitative independence, reproducing R159's correction in an intervention-typed form.

The exact script enumerated all `5^4=625` matrices on the grid `{0,1/4,1/2,3/4,1}`. At the fixed strict margin it found 114 body-only, 114 tool-only, 36 overlap and 361 neither profiles. Restricting to matrices with both off-diagonals positive still leaves all four classes nonempty (51, 51, 9 and 289 respectively). These counts check the definitions; they are not frequencies expected in humans.

## 4. What the profile rules out—and what it cannot name

### 4.1 Conditional evidential use

If the intervention fidelity checks, readout measurement model and error bounds all hold, `B_Pi` and `T_Pi` distinguish two causal-dominance patterns. A pure tracking descriptor that has no verified sensitivity to the body-pathway manipulation cannot satisfy `B_Pi` merely because an analyst calls its target a hand. Conversely, successful tool control cannot satisfy `T_Pi` when tool-transformation changes have no verified tool-family effect beyond the error margin.

This is stronger than an untyped claim that a candidate was *used*. It remains weaker than a complete mechanistic or constitutive identification. An unmeasured common cause, an omitted intervention, or a different admissible normalization can remain relevant; these are protocol failures or scope changes, not zero-valued facts.

### 4.2 Latent-label nonidentification

Let a finite latent model have states `z in Z`, intervention inputs `u`, transition kernels `K_u`, initial law `p`, and output kernel `E`. For any bijection `pi:Z->Z`, define

\[
p^\pi(\pi z)=p(z),\quad
K_u^\pi(\pi z,\pi z')=K_u(z,z'),\quad
E^\pi(o\mid \pi z)=E(o\mid z).
\]

Summing over latent paths and changing variables from `z_t` to `pi(z_t)` gives the same output law for every finite input sequence. Therefore observations identify at most a latent structure up to such relabeling. Calling one ungrounded latent state *body* and the other *tool* adds no evidence.

The verifier checked this equality for every pair of deterministic two-state transition functions under two inputs, every deterministic binary emission, both point-mass initial states and every length-three input sequence: 1,024 exact trace equalities. This is an instance of standard latent-state label symmetry, not a new general mathematical theorem.

Independent physical grounding of `J_B`, `J_T`, `Y_B`, and `Y_T` breaks the *intervention/readout-role* ambiguity enough to support the protocol-relative predicates. It still does not identify:

- anatomical membership `M(O(P),psi(k))`;
- whether the external referent is correctly represented;
- complete neural organization;
- familiar felt ownership `F_O`;
- a unique or exclusive subject.

Those claims require additional, separately justified bridges or evidence. The finite classifier must not be renamed into them.

## 5. Tokenwise C1 application boundary

For each actual admitted trial `omega`, if R159's grounded internal relation is present in the complete signature `K_omega`, its structural counterpart follows under that trial's C1 isomorphism `h_omega`. But `S_Pi(k)` compares effects across multiple actual trials and interventions. It is not generally a formula evaluated inside one unchanged `D(P)` and one unchanged `Phi(P)`.

Therefore:

\[
\bigl[\forall\omega:\ D_\omega\models\theta_\omega
\leftrightarrow \Phi_\omega\models\theta_\omega^{h_\omega}\bigr]
\not\Rightarrow
\text{a cross-trial phenomenal ownership contrast}.
\]

A cross-trial conclusion additionally needs a declared correspondence across trial tokens, stable readout semantics, measurement assumptions and a fixed selected target. Different trials in one participant do not supply one common complete `K,D,Phi,h` by identity. This blocks an object/time/signature switch that would otherwise turn an empirical effect matrix into a direct C1 theorem.

Positive UCT interpretation remains available but conditional: an actually installed body/tool causal profile is part of actual organization, and C1 interprets each admitted actual organization intrinsically. Which intrinsic organization is the familiar human experience of bodily ownership remains the `B_min` application question, not a new general-quality gap and not an experience-existence gate.

## 6. Primary evidence and competing explanations

The sources below motivate readout families and failure modes; none implements the entire `Pi` contract.

1. **Cardinali et al. (2009), DOI 10.1016/j.cub.2009.05.009.** The study is the cited origin of tool-use-dependent changes in subsequent free-hand kinematics consistent with a longer represented arm. The accessible PubMed record had metadata but no abstract in this run; detailed design claims were therefore taken only where later full primary papers explicitly described the paradigm.
2. **Cardinali et al. (2011), DOI 10.1016/j.neuropsychologia.2011.09.033.** In healthy participants, tool use affected localization when body position was supplied tactually; motor output alone was not a sufficient access condition. Only the PubMed abstract was retrieved, not raw data or full methods.
3. **Martel et al. (2019), DOI 10.1038/s41598-019-41928-1.** In a full primary report, blindfolded tool use altered later tool-free transport kinematics without a significant grip-component change, and the paper documents control conditions from the experimental programme. This motivates a tool-absent `Y_B` family but does not prove that every such effect is a body slot.
4. **Maravita et al. (2002), PMID 11869727.** The primary abstract reports tool-position-dependent reversal of visual-tactile interference, motivating a distal `Y_T` family. The full article was not retrieved here.
5. **Holmes et al. (2007), PMCID PMC1885399.** This primary report and analysis found results incompatible with a simple peripersonal-space-extension interpretation and raised spatial-attention confounds. It is retained as a direct counterpressure: distal crossmodal effects are not self-interpreting body incorporation.
6. **Weser et al. (2017), DOI 10.1016/j.concog.2017.07.002.** A modified rubber-hand protocol reported tool-dependent embodiment for chopsticks but not a teacup, with skill/recent use modulation. This prevents an anatomical body/tool dichotomy from being assumed, while its perceptual/subjective measures still do not define the present causal classifier.
7. **Martel et al. (2016), DOI 10.3389/fnhum.2016.00272.** A deafferented-patient study reported abnormal/unspecific post-tool kinematic changes and argued for a key proprioceptive role. It is a single-case longitudinal result, not a universal necessity theorem.

The source review therefore supports a plural readout contract and an explicit alternative-explanation ledger. It does not license the claim that one behavioral number reveals the complete body schema, the subject, or a phenomenal quality.

## 7. Four retained thought-experiment families

### Ancestor and formation

Consider an ancestral sequence in which biological afferent routing, distal object manipulation and tool-specific transformation learning emerge at different times. Holding the final behavior fixed does not show that `B_Pi` and `T_Pi` formed together. Role: formation question and counterexample to treating one late tool skill as a basal experience condition.

### Abacus and calculator

An abacus operator and a calculator user can produce the same answer while their body-only aftereffects and tool-transformation sensitivities differ. Equal task output is therefore outside the classifier's sufficient data. Role: definition test for actual installed pathways versus external result equivalence.

### Human-realized agent

A human formation can implement a tool controller whose distal endpoint is tracked precisely while the humans' biological body readouts remain separately anchored. Calling the endpoint *the agent's hand* does not install a biological intervention relation. Role: physical-witness test and warning against semantic inflation.

### Copy, swap, and memory

Copy a controller, swap its tool-transform tables, or transfer its memories while retaining biological pathway grounding. The same report history may accompany a changed `T_Pi` profile, and a relabeled latent state may leave every finite output unchanged. Role: counterexample to report/history sufficiency and illustration of the label theorem. It does not prove phenomenal transfer or absence.

## 8. Formal-map and inference audit

- **Concepts and quantifiers:** `Pi`, each `P_omega,I_omega`, internal `r_omega,k_omega`, external `psi_omega`, two intervention families, two readout families, effect bounds and `epsilon` are fixed before application. Undefined effects block classification.
- **All-of premises:** the classifier requires intervention fidelity, measurement semantics, normalization, error bounds and both dominance inequalities simultaneously. The C1 scope conclusion requires R159 tokenwise transport and the full profile contract on the same declared trial family.
- **Joint satisfiability:** the rational overlap matrix witnesses nonempty simultaneous body/tool dominance with positive cross-effects. It is abstract consistency, not a human observation.
- **Object/time/signature:** no trial-family contrast is substituted for one token's complete organization; no external referent is placed in `h_omega` without a declared carrier.
- **Evidence level:** exact enumeration verifies definitions and label symmetry. Primary studies motivate candidate readouts and countermodels. Neither is complete physical realization or subjective evidence.
- **Direction:** reports, kinematics, drift, distal interference and profile class do not prove C1; C1 does not make the profile a basal gate or supply `B_min`.
- **Unlinked consistency:** actual anatomical membership, internal attribution, conceptual I, autobiographical memory, language report, agency and ownership remain distinct even when correlated.
- **Purpose:** the result answers the R159 grounding question by replacing an untyped body/tool label with a falsifiable relative causal profile, while proving the profile's semantic limit.

Direction check after result formation: **PASS WITH OPEN BRIDGE**. The result is a sharper physical/organizational discriminant, not a declaration that the selected target has been phenomenally identified.

## 9. Failures and next exact question

The round does not provide an actual dataset that jointly manipulates `J_B` and `J_T` while recording both `Y_B` and `Y_T`. It does not prove that the proposed intervention families can be made perfectly selective, or that their normalized effects are commensurable. It does not solve no-report ownership measurement, complete neural realization, or `B_min`.

Next exact question: for one concrete, ethically admissible human protocol, specify fidelity tests and a shared error model for a proprioceptive/tactile `J_B` manipulation and a tool-transformation `J_T` manipulation, then determine whether the four effect bounds are jointly estimable without using ownership reports to define either readout. Predeclare what observed pattern would falsify the body-dominant candidate. Do not repeat R155 Bayesian formation, R159's algebra, or relabel generic tool performance as self-experience.

## 10. Attribution and limits

Boolean case analysis, causal contrasts, latent-state label symmetry and change-of-variables proofs are established methods. The project contribution is their typed placement into the current UCT body/tool application and the resulting repair of an explicit map gap. No claim of a historically new mathematical theorem, neural mechanism, experiment, or ownership measurement is made.
