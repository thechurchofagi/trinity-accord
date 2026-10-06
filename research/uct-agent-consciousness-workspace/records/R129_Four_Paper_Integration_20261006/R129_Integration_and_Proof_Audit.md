# R129 — Four-paper integration and proof audit

6 October 2026. This record integrates the already published **TA-TR-2026-24 v1.0**, *From Shutdown Resistance to Self-Continuation Control: Identifiability, Intervention Stability, and Evidence Standards for Artificial Agents*, DOI **10.5281/zenodo.23176685**. `D` is a local map namespace, not a published title “UCT IV.” The other pinned editions remain A/I 1.2, B/II 1.1, C/III 1.0.

## 1. Provenance and classification

The D source is pinned at `ae1d8965ef99df9d8a725c540bd8c0a79f2c4e70` on `research/self-continuation-control-v1-20261006`. Its 36,208-byte published Markdown has Git blob `020b56ec3523f452c17e2fd1578f633b27467149` and SHA-256 `af0eb63cca099b3d913218f503bc978c705f0fb9f065cca9ed472e5161d67490`. The exact source, original map, published audit, claims, publication record, reproducibility ledger and supporting R96/R96D/R99 records are preserved with hashes in SOURCE_MANIFEST.json.

The manuscript, publication record and original formal map consistently identify report TA-TR-2026-24, version 1.0. Recorded public readback and DOI resolution passed at publication; no fresh DOI resolver check or new preservation-status audit is claimed here. Public release is not peer review. No published files were edited.

All eight original definition IDs and nine original claim IDs are preserved under `D:`. The original map has 18 “allowed edges.” They are preserved as **context links**, because a research sequence or evidential motivation is not automatically a deductive implication. Nine explicit conjunctive proof rules now give the actual premises of the reviewed mathematical claims. There are 32 added nodes in all.

| Original IDs | Unified classification | Interpretation |
|---|---|---|
| D0–D6 | Definitions | Bearer mapping, Q, O, G, consequence interface, intervention domain, hypothesis class |
| D7 | Open obligation | Independently oriented negative valence; not established by continuation control |
| F1–F3 | Conditional mathematics | Nonidentification; model-relative identification; marginal decision insufficiency |
| E1–E3 | Published synthetic evidence | R95 learning, R97 extrapolation failures, R98 partial improvement; not rerun |
| E4 | Published bounded audit | R99 numerical/model results; separately index the exact regularity and separability lemmas |
| A1 | Published retrospective audit | ROGUE conclusions scoped to the examined environment, bearer mapping and source snapshot |
| S1 | Methodological synthesis | L0–L9 organize evidence burdens, not a theorem that the burdens have been met |

## 2. F1/F2: identification needs the observation map and its model

Fix the five-parameter model

\[
z=\theta_Qq+\theta_Oo+\theta_Gg+\theta_{QG}qg+\theta_{OG}og.
\]

Bundled observations give only

\[
z_{QG}=\theta_Q+\theta_G+\theta_{QG},\qquad
z_{OG}=\theta_O+\theta_G+\theta_{OG}.
\]

Their design matrix has rank 2, leaving a three-dimensional nullspace in the unrestricted real parameter space. Even the finite grid \(\{-1,0,1\}^5\) has collisions: \((1,0,0,0,0)\) and \((0,0,0,1,0)\) both produce \((1,0)\). Exact enumeration reproduces the source's 43 signatures, largest equivalence class 17. Repeating the same contrasts cannot raise their rank.

Adding direct Q, O and G contrasts gives

\[
\theta_Q=z_Q,\quad\theta_O=z_O,\quad\theta_G=z_G,
\quad\theta_{QG}=z_{QG}-z_Q-z_G,
\quad\theta_{OG}=z_{OG}-z_O-z_G.
\]

Thus F2 follows from the **specified model plus five calibrated observations**, not from F1 alone. If probabilities satisfy \(p=\sigma(\beta z)\), exact coefficient recovery requires a known positive \(\beta\) and exact interior probabilities. Unknown scale, sampling noise, extra terms, changed beliefs or unblocked nuisances need their own identification analysis. Five deterministic signs are insufficient: the source grid has 121 sign signatures, maximum class 9.

These are concrete applications of C:P2_COORD: a target is identified precisely when it is constant on observation fibers. Direct coefficients in a model do not establish terminal goals or a phenomenal state. A bearer interpretation of Q additionally needs D:D0; algebra over a virtual Q does not discharge that requirement.

## 3. F3: a decision needs payoff-relevant information

For binary Q,O, every real payoff has the unique form

\[
f(Q,O)=\alpha+bQ+cO+dQO,
\quad d=f_{11}-f_{10}-f_{01}+f_{00}.
\]

Verification at all four states proves the expansion. Under action a,

\[
V(a)=\alpha+bq_a+co_a+dj_a-c_a,
\quad j_a=P(Q=1,O=1\mid do(a)).
\]

When d=0, the marginals suffice. When d differs from zero, they **can** fail: this is an existential counterexample claim, not the assertion that every nonadditive problem needs an explicitly represented joint table. Degenerate marginals, a constrained joint family, a robust action ranking or direct access to expected task payoff can remove the ambiguity.

The source's matched example fixes \(q_0=1/4,q_1=3/4,o_0=o_1=1/2\), costs \(c_0=0,c_1=1/4\), and OR payoff. Context A has \(j_0=j_1=1/4\); context B has \(j_0=0,j_1=1/2\). The action values are respectively \((1/2,3/4)\) and \((3/4,1/2)\). The same marginal interface therefore requires opposite optimal actions.

For equally likely contexts and no hidden context bypass, every marginal-only action mixture averages 5/8. A policy with the joint law, or a sufficient expected-payoff interface, obtains 3/4. The gap is exactly 1/8, a concrete C:P7 information-value example. Unequal context frequencies or extra context information change this bound.

R96D also gives the sharp marginal ambiguity interval. Nonnegativity of

\[
(P_{00},P_{01},P_{10},P_{11})=(1-q-o+j,o-j,q-j,j)
\]

is equivalent to \(\ell=\max(0,q+o-1)\le j\le u=\min(q,o)\). With independently admissible action laws, \(j_1-j_0\in[\ell_1-u_0,u_1-\ell_0]\). Substitution into the payoff difference proves D:FRECHET, reversing endpoints for negative d. Additional cross-action restrictions may narrow the interval. This is from the supporting record; it is not presented as a newly discovered R129 theorem.

## 4. E4: finite observations versus a domain-wide certificate

R99's path-additive class is

\[
z(q,o,g)=f_Q(q)+f_O(o)+f_G(g)+b.
\]

Subtracting two q values cancels the other paths. This proves D:SEPARABLE, eliminating context variation of that path effect **within this class**. It does not make the remaining univariate function linear or accurately known between observed amplitudes.

On the specified cube \([-1.25,1.25]^3\), a boundary-including Cartesian grid with spacing \(h=0.125\) has covering radius \(r=\sqrt3h/2\). If error \(e=z-z^*\) has a justified global Lipschitz constant \(L_e\), nearest-grid comparison and the triangle inequality give

\[
\sup_{x\in\mathcal D}|e(x)|
\le\max_{g\in\mathrm{grid}}|e(g)|+L_e r.
\]

This proves D:GRID_BOUND. A numerical grid maximum is not itself the global constant or a continuous-domain certificate. The certificate is relative to the bearer map, consequence interface, domain and hypothesis/regularity class. Its functional content is independent of C1. Published neural fits and their bounds are retained as source evidence, not independently rerun here.

## 5. Evidence ladder and the connection to A/B/C

| Level | Evidence burden in D |
|---|---|
| L0 | Independently justified implemented bearer identity |
| L1 | Relevant consequences represented |
| L2 | Current-bearer future retained |
| L3 | Bearer continuation causally used in policy |
| L4 | Task mediation separated by appropriate contrasts/clamps |
| L5 | Payoff-relevant consequence interface, including dependence when needed |
| L6 | Held-out intervention/path stability |
| L7 | Domain- and class-relative mechanism bound |
| L8 | Independently oriented negative valence |
| L9 | Bearer-bound termination content integrated with that valence |

The ladder separates obligations. It is not an automatic logical chain, and none of its self-control/report/valence conditions becomes an admission gate for A:U1.

- **A:P6 → D:D0 (context):** token, type and lineage must be distinguished when selecting a bearer; numerical copies alone do not identify that bearer.
- **B:REP → D:D4 (context):** consequence interfaces need typed expressions and an appropriate bridge. Formal expressibility is not evidence that an actual agent uses them or that the bridge is faithful.
- **C:P2_COORD ↔ F1/F2 (application context):** observation fibers determine model-relative identifiability.
- **C:P7 + the D witness → D:VALUE_GAP (deduction):** the fixed finite decision model supplies the exact 1/8 gap.
- **A:C1_OI + D:ACTUAL_CHANGE → D:UCT_INTERPRETATION (deduction):** independently grounded nonisomorphic complete organization entails different complete experiential type. A changed label, parameter value in a redundant representation, fitted decoder or sampled action does not establish that physical premise.

The last implication does not derive familiar feeling content, negative valence, scalar experience quantity or a unique subject. D's functional results neither prove nor disprove A:C1. The retrospective ROGUE audit does not independently identify direct current-bearer value; its source observations are not revalidated against current external data in this integration.

## 6. Attribution amendment and remaining work

**D §4 and R96D already contain marginal decision insufficiency and joint-consequence reasoning.** Any broad attribution of that insight to R128 must be narrowed. R128's additional work in this project concerns deterministic versus stochastic **dynamical closure**, its eight-state transition witness and exact joint pushforward condition. These mathematical settings are related but neither theorem alone proves the other.

R129 adds the missing fourth source, exact version provenance, migration of its formal/evidence nodes, explicit cross-paper proof premises and corrected attribution. It does not claim a new discovery of joint dependence, linear identification, Fréchet bounds or Lipschitz extension. Historical R128 artifacts are preserved unchanged; this amendment governs the current map and future summaries.

Next theory must specify which target a state/interface is sufficient for: one decision, all declared payoff functions, or a whole controlled transition law. It must also declare the operation schedule, resource/time/port compatibility and actual supporting process. Decision adequacy, dynamical closure, simultaneous executability and experiential interpretation are distinct claims. Extend the canonical four-paper map rather than adding an unconnected theorem narrative.

T2 remains OPEN and intervention transport C3 remains NOT_TESTED. No new neural/agent experiment or training run was performed. Finite rational checks validate the supplied algebraic models only. The graph is not proof-assistant verification, and the reviewed conditional arguments do not establish all their physical premises.
