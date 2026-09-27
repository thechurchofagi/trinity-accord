# Supplementary Material: Selecting and Tracking Conscious Subjects

**Version:** Final Preprint Supplement v1.0  
**Date:** 28 September 2026  
**Author:** Hongju Liu  
**Status:** Supplement to TA-TR-2026-19; English theory preprint; not peer reviewed.  

---

## Supplementary Methods S1. Formal assumptions

The main text uses a regular candidate region \(X^\circ\) where \(\pi:E^\circ\to X^\circ\) is a finite covering. This assumption is local: it does not apply automatically at branch birth/death, merger, split, scale changes, or other singular states.

A relevant symmetry \(g\) is an automorphism of the complete physical description admitted by the theory. If an apparently symmetric state contains an additional physical feature that distinguishes candidate branches, the state description must be enlarged and the stabilizer recomputed.

## Supplementary Proposition S1. Orbit-valued repair

Let a finite stabilizer group \(H\) act transitively on a top-tier orbit \(\mathcal O\). If \(R\subseteq\mathcal O\) is nonempty and \(H\)-invariant, then \(R=\mathcal O\).

**Proof.** Choose \(P\in R\). Invariance gives \(hP\in R\) for all \(h\in H\). Transitivity gives \(H\cdot P=\mathcal O\), so \(\mathcal O\subseteq R\). Since \(R\subseteq\mathcal O\), equality follows. \(\square\)

## Supplementary Proposition S2. Invariant lottery

Let \(H\) act transitively on a finite orbit \(\mathcal O=\{P_1,\dots,P_n\}\). The unique \(H\)-invariant probability measure is uniform: \(\mu(P_i)=1/n\).

## Supplementary Proposition S3. Top-tier probability continuity obstruction

Suppose \(T(\lambda)=\{Q\}\) for \(\lambda<0\), \(T(0)=\{P,Q\}\), and \(T(\lambda)=\{P\}\) for \(\lambda>0\). If probability support is restricted to the exact top tier and the tie distribution is symmetry invariant, then no probability-valued rule is continuous at zero.

## Supplementary Proposition S4. Closed-graph top-tier completion

If the unique side winners are \(Q\) and \(P\), a set-valued extension restricted to \(\{P,Q\}\) has closed graph only if it contains both \(P\) and \(Q\) at the tie.

## Supplementary Example S1. Double-cover monodromy

Let \(\pi:S^1\to S^1\), \(\pi(z)=z^2\). The loop \(\gamma(t)=e^{2\pi it}\) lifts from \(+1\) to \(e^{\pi it}\), ending at \(-1\). Thus the two locally regular sheets exchange after one circuit and no global continuous single-valued section exists.

## Supplementary Methods S2. Exact IIT model parameters

State: \((A,B,C)=(1,1,1)\).

Parameters:

\[
\begin{aligned}
b_A&=-3.3817613395604793,\\
w_A&=-0.8884306235600699,\\
w_{BA}&=3.764183299002207,\\
w_{\rm far}&=5.399411767064731,\\
b_B&=-2.330666926538962,\\
w_B&=4.112049126654821,\\
w_{\rm side}&=-1.3994639599679264.
\end{aligned}
\]

TPM row order: \(A+2B+4C\). Columns: \(A,B,C\). All three next-state units are conditionally independent given the current state. Connectivity matrix: all ones.

Official PyPhi source commit:
`e2cb2812daa71501d1edfe1862ca004d684fc380`.

Formalism: `pyphi.iit4_2026`.

## Supplementary Table S1. Center candidate values

| Candidate | \(\phi_s\) |
|---|---:|
| A | 0.00228630205089240 |
| B | 0.000764925239030639 |
| C | 0.00228630205089240 |
| AB | 0.395109130115104 |
| AC | 0.00829222984087624 |
| BC | 0.395109130115104 |
| ABC | 0 |

Composition:
\[
\Phi(AB)=\Phi(BC)=0.23405618533677028,
\]
\[
\Phi(AC)=3.909980177943.
\]

Official failed clique at center:
`[[AB, BC]]`.

Official accepted center family:
`[AC, B]`.

## Supplementary Table S2. Main parameter sweep

| \(\lambda\) | \(\phi_s(AB)\) | \(\phi_s(BC)\) | \(\phi_s(AC)\) | \(\phi_s(ABC)\) |
|---:|---:|---:|---:|---:|
| -0.050 | 0.389867 | 0.400861 | 0.008302 | 0 |
| -0.020 | 0.392954 | 0.397346 | 0.008294 | 0 |
| -0.010 | 0.394021 | 0.396217 | 0.008293 | 0 |
| -0.005 | 0.394563 | 0.395661 | 0.008292 | 0 |
| 0 | 0.395109 | 0.395109 | 0.008292 | 0 |
| +0.005 | 0.395661 | 0.394563 | 0.008292 | 0 |
| +0.010 | 0.396217 | 0.394021 | 0.008293 | 0 |
| +0.020 | 0.397346 | 0.392954 | 0.008294 | 0 |
| +0.050 | 0.400861 | 0.389867 | 0.008302 | 0 |

## Supplementary Table S3. Official full complex output

| \(\lambda\) | Accepted complexes |
|---:|---|
| -0.01 | BC: 0.396217300611; A: 0.002307764474 |
| 0 | AC: 0.008292229841; B: 0.000764925239 |
| +0.01 | AB: 0.396217300611; C: 0.002307764474 |

## Supplementary Methods S3. Numerical precision and relabeling audit

At precision settings 10, 12, 13, and 14, the points \(-10^{-6},0,+10^{-6}\) all produced maximal-complex pattern \(BC\to AC\to AB\).

All six permutations of node labels were recomputed. After mapping results back to original labels, every center calculation returned accepted family `[AC, B]`.

At the center, the \(AB/BC\) state specification has a positive margin and the MIP margin is approximately 0.007691308454.

## Supplementary Methods S4. Robustness protocol

Random generator: NumPy `default_rng`, PCG64.  
Seed: 20260927.

Each base parameter \(\theta_j\) was perturbed as:
\[
\theta_j'=\theta_j(1+\mathrm{SD}\,Z_j),
\]
with independent \(Z_j\sim N(0,1)\).

Four SD levels were used: 1%, 3%, 5%, 10%; 250 samples per level. Shared parameter perturbations preserved the central mirror symmetry. Every sample was evaluated at \(\lambda=-0.01,0,+0.01\), all seven nonempty subsystems were evaluated, and official `Substrate.complexes()` was called.

Total:
- 1000 parameter sets;
- 21,000 subsystem evaluations;
- 3000 official complex searches.

Official and independent values differed by at most:
\[
4.440892098500626\times10^{-16}.
\]

### Directional criterion

| SD | \(BC\to\) fallback \(\to AB\) |
|---:|---:|
| 1% | 250/250 |
| 3% | 204/250 |
| 5% | 168/250 |
| 10% | 123/250 |

### Post hoc orientation-free description

All 1000/1000 records retained exchange of the symmetry-related overlapping pair across the two sampled sides when left/right orientation was ignored. This was a post hoc descriptive reclassification, not a preregistered success criterion.

At 10% SD, center maximal fallback identities were:
- AC: 223/250;
- B: 5/250;
- nonoverlapping A/C tie at leading fallback level: 22/250.

## Supplementary Methods S5. Version specificity

Old v0.13 model:
- IIT 4.0 (2023): maximal complex \(AB\to ABC\to BC\); center \(AB=BC=0.925482306487\), \(ABC=0.900887034154\).
- IIT 4.0 (2026): \(ABC\) maximal at all sampled points.

Current v0.14.1 model:
- IIT 4.0 (2023): \(AC\) maximal at all sampled points.
- IIT 4.0 (2026): \(BC\to AC\to AB\).

Formalism versions must not be mixed.

## Supplementary Methods S6. Landscape continuity

Let \(Z=\bigsqcup_{P\in\mathcal C}(\{P\}\times Z_P)\) be the finite topological sum of branch spaces. If each \(z_P:X\to Z_P\) is continuous and \(\mathcal C\) is locally fixed and finite, then the landscape \(\mathscr L(x)=\{(P,z_P(x))\}\) is continuous in the Vietoris hyperspace topology.

In metrizable components, one convenient metric is:
\[
d_Z((P,u),(Q,v))=
\begin{cases}
\min\{1,d_P(u,v)\}, & P=Q,\\
2, & P\ne Q.
\end{cases}
\]
The metric is representational; cross-label distance 2 is not interpreted as a physical magnitude.

## Supplementary Note S1. Claim boundaries

The study does not establish:
- that IIT is inconsistent;
- that brains instantiate the model;
- that \(\phi_s\) is a measure of phenomenal intensity;
- that the v0.14.1 crossing persists for every nonzero \(\lambda\) in an analytically proven punctured neighborhood;
- that the landscape ontology is empirically correct;
- historical first priority for symmetry, tracking, complex switching, or multiple subjecthood.