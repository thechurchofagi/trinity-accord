# Appendix A. Main changes relative to v1.0

1. Replaces the potentially ambiguous scale-indexed ontological reading with a token-relative ontic organization:
   \[
   \Phi(P)\leftrightarrow\mathbf D^{ontic}(P).
   \]

2. Separates:
   \[
   \mathbf D^{ontic}
   \neq
   D_v
   \neq
   \widehat D_v
   \neq
   Subject.
   \]

3. Separates the intended tokenwise identity A5-SI from its pairwise A5-OI and one-way A5-W consequences.

4. Marks all converse/nonisomorphism theorems as A5-OI-dependent.

5. Repairs Non-Summative Combination using explicit tokenwise identity A5-SI and the standard product in the declared common structural category.

6. Adds Probe Invariance, No Future Contamination, and Causally Screened History.

7. Adds the restricted candidate-orbit obstruction and explicitly retains possible invariant global partitions.

8. Recasts A3 primarily as process persistence under embedding.

9. Recasts A4 as Selfhood Non-Prerequisite and removes positive self-formation mechanisms from the axiomatic layer.

10. Demotes First-Person Reference Field, binary macrofield membership, H-V*, and RREP-as-universal-generator from the foundational layer.

11. Adds the structural-evolutionary synthesis from elementary physical processes to conceptual selfhood.

12. Introduces the distinction (with one-way sufficiency and two-way reflection separated in rc4):
    \[
    A5
    \neq
    B_v
    \neq
    OSC_v,
    \]
    making finite empirical bridge assumptions explicit.

13. Replaces grain-only falsifiability discipline with Physical Token/View Selection Protocol and No Post-Hoc Token/View Rescue.

14. States explicitly that finite experiments ordinarily test an operational bridge package rather than isolated full A5-OI.

15. Distinguishes internal theoretical obligations from application-level physical identification and measurement. General macro-experience gates, a universal exclusive subject selector, and a second human-quality mechanism are not added as prerequisites.
16. Adds the pointed, port-aware finite comparison signature, four-setting causal-retention proposition, noncircular bridge-failure countermodels, and a typed interface to UCT II v1.1.


# Appendix B. An exact three-register thought experiment

## B.1 Physical specification and scope

Stipulate three physically implemented binary registers \(s,a,b\), a common clock, an external input \(u\), XOR gates, buffered one-way connections from \(s\), and switchable cross-connections between \(a\) and \(b\). The switch setting is \(\lambda\in\{0,1\}\). One clock step is

\[
\begin{aligned}
s_{t+1}&=s_t\oplus u_t,\\
a_{t+1}&=s_t\oplus(\lambda b_t),\\
b_{t+1}&=s_t\oplus(\lambda a_t),\\
y_t&=s_t.
\end{aligned}
\]

\begin{figure}[htbp]
\centering
\begin{tikzpicture}[>=stealth, every node/.style={font=\small}, scale=0.9]
\foreach \dx/\label in {0/{Setting 0: cross-links absent},7/{Setting 1: cross-links present}} {
  \begin{scope}[xshift=\dx cm]
    \node at (0,1.6) {\label};
    \node[circle,draw,minimum size=7mm] (s\dx) at (0,0.7) {$s$};
    \node[circle,draw,minimum size=7mm] (a\dx) at (-1,-1) {$a$};
    \node[circle,draw,minimum size=7mm] (b\dx) at (1,-1) {$b$};
    \draw[->] (-2,0.7) node[left] {$u$} -- (s\dx);
    \draw[->] (s\dx) -- (2,0.7) node[right] {$y=s$};
    \draw[->] (s\dx) to[loop above] (s\dx);
    \draw[->] (s\dx) -- (a\dx);
    \draw[->] (s\dx) -- (b\dx);
  \end{scope}
}
\draw[->] (a7) to[bend left=22] (b7);
\draw[->] (b7) to[bend left=22] (a7);
\node at (0,-2) {Transition images: 2};
\node at (7,-2) {Transition images: 8};
\end{tikzpicture}
\caption{The two stipulated circuit settings. Arrows denote state dependencies. The added pair cross-links distinguish the settings; the external output is the same implemented state in both. Clock and buffering are specified in the text.}
\end{figure}

Multiplication and XOR act on bits. Buffering is stipulated to exclude feedback and loading from the downstream pair into the \(s\) update. In real hardware this isolation and all relevant boundary effects would require examination. The mathematics treats the finite update/intervention specification as complete within the stated idealized model. A real circuit's complete ontic structure is not established by this calculation. No circuit was built and no phenomenal observations were collected.

Before calculating any output, specify two token hypotheses: the whole implemented network \(W_\lambda\), and the continuing implemented register process \(S_\lambda\) with state \(s\), its update mechanism, clock, and declared boundary \(u\). The whole is causally connected through the outgoing \(s\) links in both settings. The cross-coupled \(a,b\) pair has boundary \(s\). These are explicit component/boundary choices, not subject assignments. A1 applies conditionally if the stipulated processes are actually instantiated and meet the token requirements; a mathematical state table is not itself proof of that instantiation.

The intervention family comprises all 27 coordinate clamps immediately before an update: each register is either unchanged, set to 0, or set to 1. The boundary input takes both bit values. The switch settings are separately compared mechanisms; they are not assumed to constitute a continuous A2 path. This is a worked theoretical specification, not a preregistered empirical study.

## B.2 Exact closure of an implemented sub-process

For \(\pi(s,a,b)=s\), the macro update is \(\bar T_u(s)=s\oplus u\). Every two physical states with the same \(s\) have the same next projected state. Projected coordinate clamps act as the same clamp on \(s\) if it is targeted and as the identity otherwise. Hence

\[
\pi(T_u^\lambda(Ix))
=\bar T_u(\omega(I)\pi(x))
\]

for every declared clamp, input, setting, and state. The implementation of \(s\) is part of the physical specification, not inferred from closure alone. The present state and future update of this sub-process do not depend on \(a\) or \(b\), even though it causally drives them. The case separates physical downstream connection from participation in this particular process's state and update.

By induction on time, for the same \(s_0\) and any input string,

\[
y_t=s_0\oplus u_0\oplus\cdots\oplus u_{t-1}
\quad(t\ge1)
\]

in both settings, independently of initial \(a,b\). This is equality of the declared output behavior, not equivalence under every conceivable additional physical experiment.

## B.3 Full structural difference is invariant to state relabeling

Fix either input value. At \(\lambda=0\), both downstream next states equal \(s\), so the eight-state transition map has exactly two images. At \(\lambda=1\), the map is bijective: from \((s',a',b')\), recover

\[
s=s'\oplus u,\qquad a=b'\oplus s,\qquad b=a'\oplus s.
\]

It therefore has eight images. Conjugating a transition map by a bijective state relabeling preserves its image cardinality. Consequently the two whole-network transition structures are not isomorphic, even before requiring isomorphisms to preserve the intervention ports.

At a fixed boundary \(s\), the \(a\mid b\) split has independent component updates at \(\lambda=0\). At \(\lambda=1\), changing \(b\) changes \(a^+\) and changing \(a\) changes \(b^+\); no product of component-local update maps reproduces this behavior relative to these physical ports. This is a statement about the specified split, not about every conceivable factorization or about one phenomenal subject. Because the boundary is explicitly conditioned, correlation from the common \(s\) drive is not mistaken for cross-coupling.

The two distinctions yield compatible conditional UCT statements:

| Fixed comparison | Mathematical result | Conditional UCT interpretation |
|---|---|---|
| Whole tokens \(W_0,W_1\) | Nonisomorphic full modeled dynamics | A5-OI gives different complete experiential types if the stipulated organization is complete and the tokens actual |
| Implemented processes \(S_0,S_1\) | Same state/update and represented interfaces | A5-W gives equivalent experiential types under the same completeness and actuality qualifications |
| Output \(y\) | Same trajectory for common \(s_0,u\) | Output equality does not settle whole-token experiential equivalence |
| Downstream split \(a\mid b\), boundary \(s\) fixed | Cross-dependence appears at setting 1 | A compositional interpretation uses A5-SI and the specified constituent product; it does not determine one subject |

The coexistence of these conclusions is the point of token-relative completeness. Replacing a whole-process claim by the sub-process claim after a failed test would still violate the freeze protocol. Here both comparisons are specified in advance and are reported together.

## B.4 Two checks against arbitrary coarse-graining

The feature \(q=a\oplus b\) obeys \(q^+=\lambda q\). Its exact algebraic closure does not establish a separate actual \(q\)-token. No separate parity register is stipulated. A distributed realization could still be proposed and independently examined; absence of a literal register is not a proof of absence of such a process. This example demonstrates a limit of the certificate: algebra alone does not finish the realization argument.

The feature \(r=s\oplus a\oplus b\) fails even the deterministic closure test at \(\lambda=0\). With \(u=0\), states \((0,0,0)\) and \((1,1,0)\) both have \(r=0\), but their next \(r\) values are respectively 0 and 1. Thus no deterministic one-state update for \(r\) alone exists in that scope. This is a model failure, not a no-experience conclusion.

## B.5 What the example does and does not distinguish

An output-sufficiency hypothesis assigning whole-token experiential equivalence whenever every declared \(u\)-to-\(y\) response agrees conflicts with A5-OI on this model, conditional on the stated actuality/completeness premises. This comparator is deliberately narrow. It is not all functionalism: theories that include internal counterfactual organization need not identify the two whole networks. No IIT 4.0 quantity or GNWT neural model is calculated here; this construction is not reported as an empirical victory over either theory.

The example is a finite specialization and audit of the project's earlier behaviorally silent internal-change argument. Its value is to put output equality, full nonisomorphism, fixed token boundaries, intervention closure, and the limits of coarse descriptions in one independently checkable specification. It does not claim that the general phenomenon or the underlying mathematics is new.

## B.6 Exact verification record

The accompanying standard-library Python script `verification/check_rc4.py` checks 13 scoped properties. It enumerates all 32 state/input/setting transitions, 128 same-projection closure comparisons, and 864 state-reset intervention cases. It also verifies the finite-set compositional counterexample, the restricted symmetry orbit and invariant global counterpartitions, the lossy-target counterexample, the transition-image invariant, and the coarse-projection examples. Full transition data and results are supplied in `transition_table.csv` and `verification_results.json`.

The original 13-check script is preserved and rerun in the v1.1 package. A separate `verification/check_transformations.py` checks the four-setting extension, port covariance, and bridge countermodels. General statements rely on the analytic proofs above; finite enumeration is not a proof about arbitrary physical systems and is not empirical validation of any consciousness axiom.


# Appendix C. Revision-specific dependency ledger

| Result | Required premises | Scope boundary |
|---|---|---|
| Pairwise type equivalence | Tokenwise A5-SI in the common signature | Weaker A5-OI alone does not establish A5-SI |
| Repaired combination | Actual whole/parts; tokenwise A5-SI; standard constituent product | Relative nonproduct structure, not a subject count |
| Restricted selection obstruction | One symmetry orbit with overlap; equivariance; nonempty exclusive output | Does not exclude other invariant partitions |
| Actual finite process criterion | Actual events; inherited causal links; connected subhistory; represented boundary | Describes the domain; no new experience threshold |
| Finite closure lemma | Surjective projection; representative-independent projected next state | Optional scientific model consistency |
| One-way measured correspondence | Frozen view/target; sufficiency; measurement assumptions | Not necessarily injective after projection |
| Two-way measured correspondence | One-way package plus finite reflection | Does not isolate the identity axiom from all auxiliaries |
| Whole-model divergence | Specified actual realization/completeness; image-cardinality invariant; A5-OI | No independently measured phenomenal difference |
| Sub-process invariance | Same complete implemented sub-process; A5-W | Does not assert whole-network invariance |
| Human and cellular quality | The same A1 and A5-SI principles | Concrete biological identification is a separate application |
| Pointed, port-aware isomorphism | Declared signature; fixed point, ports, operations and temporal relations | A finite model is not a certificate of complete ontic organization |
| Four-setting retention partition | Stated binary updates; held common boundary; initial perturbation; rank-nullity | Counts response distinctions, not consciousness or subjects |
| Finite bridge failure does not isolate A5 | Explicit lossy-view and lossy-target countermodels | No preservation of a falsified implication as a secure premise |
| UCT-II operational reconstruction | Frozen physical view, shared operators, applicable fixed bridge | Does not alone establish A1/A5 or sensitive phenomenal measurement |

The earlier static dependency-map audit checked the presence and direction of encoded dependencies. It did not verify that the displayed weak formula expressed all of the intended strong identity. Rc4 makes that difference explicit. The old freeze candidate should not be reused as a semantic proof certificate without updating the identity and composition nodes.

# Appendix D. Optional checks on a finite coarse description

These checks concern a proposed scientific model, not the existence of experience. Actual processes need not admit autonomous, closed coarse descriptions. The finite process criterion in Section 2.4 does not depend on the checks below.

A useful model dossier identifies the actual referent and its physical state carriers or distributed organization; declares the time horizon, boundary, and omitted feedback; and distinguishes implemented relations from a calculated summary. Predictive success alone does not create a new token. A literal register is not required for a distributed realization.

For a deterministic lower-level update \(x^+=T_e(x)\) and a surjective coarse map \(\pi:X\to M\), a closed deterministic update \(\bar T_e\) exists exactly when

\[
\pi(x)=\pi(x')\ \Longrightarrow\
\pi(T_e x)=\pi(T_e x').
\]

**Proof.** If \(\pi T_e=\bar T_e\pi\), equal coarse states have equal coarse successors. Conversely, define \(\bar T_e(m)=\pi(T_e x)\) using any representative of \(m\). The displayed condition makes the definition representative-independent, and surjectivity supplies a representative. \(\square\)

For a declared state-reset intervention \(I\), an additional intervention correspondence \(\omega\) can be checked by

\[
\pi(T_e(Ix))=\bar T_e(\omega(I)\pi(x)).
\]

The reset is applied before the transition. Mechanism-changing interventions require separately indexed update maps; the reset equation does not automatically cover them. Approximate, probabilistic, or history-dependent models need their own error and sufficiency conditions. Failure of a closed deterministic description is a failure of that model, not absence of experience in the actual process.

This mathematics belongs to established lumpability and causal-abstraction methodology (Buchholz, 1994; Rubenstein et al., 2017; Beckers & Halpern, 2019). UCT claims no mathematical priority. Appendix B supplies both an implemented closed process and examples illustrating why a closed calculated feature is not automatically another token, and why an arbitrary feature can fail closure. These distinctions keep optional modeling requirements separate from the common explanatory principle for elementary, cellular, and human experience.
