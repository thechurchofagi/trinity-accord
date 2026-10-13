# From preserved distinctions to effective regulation
## Why longer retention need not improve a system's own feedback

**Checkpoint:** UCT-GD-20261013, version 0.2.0.  
**Research direction:** Hongju Liu.  
**Derivation, computation, review and drafting:** ChatGPT / GPT-6 Astra Pro.  
**Status:** theoretical/computational checkpoint; not a new published paper, not peer reviewed.  
**Predecessor:** GD v0.1.0, commit `2cbcf7167794c9d6a9ee4432c52a42f92802ac4c`.  
**Map status:** pending and disabled for automatic inference; UCT-MAP-v1.1.2 unchanged.

## 1. The question that changes this round

The previous checkpoint showed how selective communication can preserve a freshly written local distinction while maintaining a specified common response. Its decoder was external: preserving a bit was not yet evidence that the modeled system used it. This round inserts the retained state into an explicit feedback circuit that alters the subsequent physical deviation being sensed. The comparison is no longer solely about what an observer can read.

The principal result is a **ranking reversal**. Within a declared family, a route with more residual bench memory can regulate a noisy physical variable substantially worse than a route with less residual memory. Excessive mixing can nevertheless destroy regulation altogether. The constructive target is neither maximal preservation nor maximal agreement, but an appropriate relation among retention, sensory coupling and effective action. An exact limiting optimum depends on the body–controller gains rather than on a putative universal amount of selfhood.

This is an application of established feedback mathematics, not a discovery that feedback or forgetting can be useful. It does not derive subjective ownership, an exclusive subject boundary, endogenous norms, life, or natural evolutionary history. It advances one specific structural question needed by that larger program: how a persisting distinction becomes causally consequential for the process that generates it, and why its useful persistence cannot be ranked in isolation from that relationship.

## 2. Inherited constraints and nearest prior work

UCT I v1.2 already supplies, within its assumptions, nonempty basal experience, conditional structural continuity, and fine-grained paths that may branch, specialize, delete or reorganize relations. It does not derive C1 from evolution, require a monotonic consciousness scalar, or identify a functional threshold with experience onset [U1]. No new experience-existence rule is added here.

UCT-RC v1.1.0 distinguishes passive correlation from storage of a freshly written bit, and warns that visible one-step laws may hide slow mediators [U2]. GD v0.1.0 distinguishes selective routing from indiscriminate copying but leaves endogenous consumption open [U3]. A5L shows why an endpoint that directly reads an organizational coordinate does not independently identify a selected phenomenal target [U4]. These boundaries remain in force. The ERF index also already describes shared modulation as a candidate organization with a separate attribution bridge [U5]; endogenous regulation itself is not a newly invented UCT theme.

Kolchinsky and Wolpert [P1] formulate information's causal value for maintaining a physical system and explicitly distinguish this from arbitrary exogenous task value. Barandiaran, Di Paolo and Rohde [P2] distinguish organizational autonomy from merely satisfying externally assigned norms. Our engineering model is more modest: the feedback dependency is internal to its equations, while its carrier, equilibrium and disturbance regime are stipulated. It does not resolve the origin of its norms.

Biomolecular feedback, leaky regulation and noise/performance tradeoffs are already studied by Briat, Gupta and Khammash [P3] and Olsman and colleagues [P4]. Common/transverse mode decomposition has classic predecessors such as Pecora and Carroll [P5]. The cubic criterion, covariance equation, pulse-energy identity, state-coordinate transformations and feedback/replay contrast used below are inherited mathematics. The proposed contribution is this specific continuation of the GD model, its equal-budget/endogenous-use comparison, exact optima and explicit failure boundaries. Global priority has not been established.

## 3. A six-variable realization of the structural question

There are two physical compartments, indexed by i=1,2; j denotes the other. A compartment has a physical deviation x_i, a controller state m_i, and an interface state u_i. These are real-valued variables in an ideal linear model, not signs representing personal identity. The complete deterministic dynamics are

\[
\begin{aligned}
\dot x_i &= a x_i-bm_i,\\
\dot m_i &= s x_i-cm_i+\ell(u_i-m_i)+h(m_j-m_i),\\
\dot u_i &= -d u_i+\ell(m_i-u_i)+g(u_j-u_i).
\end{aligned}
\]

Here a,b,s,c,d,ell are positive and g,h are nonnegative. Physical perturbations can be added to the x equations. For a noise calculation, add independent Brownian increments of stated intensities. The equilibrium x=m=u=0 is stipulated, not a discovered biological optimum. The open physical deviation amplifies at rate a, while sensing s and action b can close a corrective loop. A real circuit could approximate these dynamics locally; the numerical simulation is not itself proof that an ideal modeled process has been physically realized as its own experiential bearer.

The m/u filter is a **linear analogue** of the first-moment dynamics in GD v0.1.0 when c=d=2mu. The new s*x term and the new physical x variable alter the operation. We do not claim that the full stochastic copying system, its local path laws, or its experiential contents have been preserved.

The essential new causal cycle is

\[
x_i\longrightarrow m_i\longrightarrow \dot x_i\longrightarrow x_i.
\]

At g>0 and ell>0, all compartments remain connected even if h=0. At b=0, the controller state no longer corrects x, even though it can still be observed or stored. At s=0, it is not updated by x. These are changes in the modeled dependency, not experience-existence gates.

The total nominal cross-coupling budget is G=g+h. This fixes a sum of coefficients, not energy expenditure, physical channel count, information rate or complete hardware cost.

## 4. ER1 — A common response can hide failure of local regulation

Use orthonormal common/difference variables x_+=(x_1+x_2)/sqrt(2) and x_-=(x_1-x_2)/sqrt(2), and likewise m,u. Reflection symmetry exactly decomposes the full six-dimensional matrix into two three-dimensional blocks.

The common block is independent of g and h:

\[
A_+=\begin{pmatrix}
a&-b&0\\s&-(c+\ell)&\ell\\0&\ell&-(d+\ell)
\end{pmatrix}.
\]

The difference block is

\[
A_-(g,h)=\begin{pmatrix}
a&-b&0\\s&-C&\ell\\0&\ell&-D
\end{pmatrix},\quad
C=c+\ell+2h,\quad D=d+\ell+2g.
\]

Thus identical common inputs and common initial conditions generate identical common trajectories for every route. This remains true when the difference block is unstable. Equal and opposite local deviations can grow while x_+ remains exactly zero. Common-channel data alone cannot certify local corrective competence in this symmetric family. This is not an empirical claim that all real systems possess exact reflection symmetry.

Let K=bs. The characteristic polynomial of A_- is

\[
p(z)=z^3+p_1z^2+p_2z+p_3,
\]

where

\[
\begin{aligned}
p_1&=C+D-a,\\
p_2&=CD-\ell^2-a(C+D)+K,\\
p_3&=D(K-aC)+a\ell^2.
\end{aligned}
\]

The classical strict cubic Routh–Hurwitz conditions are p_1,p_2,p_3>0 and p_1p_2>p_3. A useful factorization is

\[
p_1p_2-p_3=(C+D)[(C-a)(D-a)-\ell^2]+K(C-a).
\]

No static feedback condition is silently substituted for the full criterion outside the explicitly proved parameter region.

### Exact route boundary in a fixed example

Set

\[
a=1/10,\quad b=s=3/10,\quad c=d=1/25,\quad\ell=1/10.
\]

Then C,D>=7/50. We have p_1>=.18 and p_2=(C-a)(D-a)+.07>=.0716. At C=D=.14 the Routh margin p_1p_2-p_3 is .001248. Its derivative with respect to D is

\[
(C-a)(C+2D-a)-\ell^2\ge .0028,
\]

and its derivative with respect to C is the analogous positive expression plus K. Therefore that margin stays positive throughout this entire nonnegative g,h region. Stability is consequently equivalent here to p_3>0, or

\[
h<.38+\frac{.005}{.14+2g}.
\]

The selective route h=0 is stable for every finite g>=0. The uniform equal-budget route g=h=G/2 is stable only for

\[
G<G_{crit}=.31+\frac{\sqrt{85}}{20}\simeq .7709772229.
\]

Equality gives a zero mode and no strictly stationary finite-noise covariance; above it the difference block has a positive growth mode. The common block does not change at this boundary.

This gives an explicit reason not to infer regulatory unity from overall agreement. It neither counts subjects nor locates a first experience. A functional stability boundary can occur along a continuous structural path without changing UCT's basal-experience commitment.

## 5. ER2 — The memory ranking reverses after the state is used

### 5.1 Separate the bench test from the live regulatory test

To measure retention alone, clamp the sensory drive s*x to zero and write m_-(0)=1,u_-(0)=0. This is a bench intervention, not the controller's normal operating environment. With c=d, define z=sqrt((g-h)^2+ell^2) and B0=c+ell+g+h. Then

\[
R_{bench}(t)=\frac{1+(g-h)/z}{2}e^{-(B0-z)t}
+\frac{1-(g-h)/z}{2}e^{-(B0+z)t}.
\]

At fixed G, g=G-h and 0<=h<=G/2, this response strictly decreases as h increases for t>0 and G>0. This is the same mean-retention mechanism as GD v0.1.0, not a new theorem about human memory. The quantity is a response amplitude, not Shannon information or a decoding percentage.

To test actual regulation, restore sensing and action and perturb the physical coordinate. In the difference block use

\[
dY=A_-Y\,dt+e_x\,dW_t.
\]

For stable A_-, the stationary covariance P solves

\[
A_-P+PA_-^{T}+e_xe_x^T=0,
\]

and the physical deviation variance is J=P_xx. Equivalently,

\[
J=\int_0^\infty[e_x^Te^{A_-t}e_x]^2\,dt.
\]

Thus J can be obtained from the response to a physical impulse even without interpreting a reward or a report. It remains a chosen measure of physical disturbance rejection, not survival probability, total health or an intrinsic phenomenal value. The pulse-energy identity and covariance equation are standard.

### 5.2 Equal-budget numerical witness, with independent exact readback

Using the parameters above, G=1 and bench delay t=5:

| Route | g | h | Bench response | Physical error J | Stability |
|---|---:|---:|---:|---:|---|
| maximal retention in this family | 1 | 0 | .5078614673 | 17.6450584853 | stable |
| moderate internal mixing | .92 | .08 | .2290410393 | 6.2655982099 | stable |
| uniform mixing | .5 | .5 | .0037729975 | undefined | unstable |

The first two variances were independently recovered exactly as 501836615/28440632 and 8887325/1418432. Direct numerical pulse integration agrees with covariance solutions. No finite stationary error is assigned to the unstable model. The first two routes have precisely the same common-channel transfer function; only the disturbance-difference response changes. The common-channel variance under unit common noise is about 52.9748 in both, so the table must not be misreported as a 64.5% improvement in total independent-noise variance. The approximately 64.5% reduction concerns J for the declared differential mode only.

The moderate route remembers less in the clamped test but rejects physical disturbances better in the live test. Its increased damping reduces repeated overcorrection. Too much mixing weakens the corrective difference signal until it no longer compensates for the locally amplifying physical deviation. Which route is best is not determined by retention or coupling strength alone.

For G=.5, even the uniform route has lower J than h=0, while for G=1 the uniform route is unstable. “Always protect local records as much as possible” is therefore not a valid extension of GD1. This qualifies a proposed inference; it does not retract the predecessor's correctly scoped memory result.

## 6. ER3 — An exact useful-forgetting optimum

Hold finite h and other rates fixed and let g grow. The fast difference interface u_- decays, and the slow closed-loop block tends to

\[
A_2=\begin{pmatrix}a&-b\\s&-C\end{pmatrix}.
\]

This is a limit of finite models, not infinite-speed hardware. For a<sqrt(K), the reduced block is stable precisely on

\[
a<C<K/a.
\]

For a fixed C inside this interval, the third pole tends to -D and the other poles approach A_2's stable poles. Equivalently, the x transfer function

\[
H_D(z)=\frac{(z+C)(z+D)-\ell^2}
{(z-a)[(z+C)(z+D)-\ell^2]+K(z+D)}
\]

converges after division by z+D to (z+C)/[(z-a)(z+C)+K]. The fast residue vanishes and the slow stability margin stays positive for sufficiently large D. The stationary covariance converges to that of A_2; this also follows by eliminating the interface entries in the finite Lyapunov equations. The statement holds with fixed finite noise intensities, not noise that grows with g.

With unit body noise and no separate controller noise,

\[
J(C)=\frac{C^2-aC+K}{2(C-a)(K-aC)}.
\]

**Derivation.** Put P_xx=p, P_xm=r, P_mm=v. The three covariance equations are a*p-b*r+1/2=0, s*p+(a-C)r-b*v=0, and s*r-C*v=0. Solving gives r=(ap+1/2)/b, v=sr/C and the stated p. Written without abbreviations, the first equation is aP_xx-bP_xm+1/2=0.

Differentiation yields

\[
J'(C)=\frac{K(C^2-K)}{2(C-a)^2(K-aC)^2}.
\]

The variance diverges at both stability boundaries. It strictly decreases up to C=sqrt(K) and strictly increases thereafter. The unique unconstrained optimum is therefore

\[
\boxed{C_*=\sqrt{bs}}.
\]

This is the optimum of the stated linear model and noise criterion, not a universal law of neural forgetting. If hardware constraints exclude C_*, the feasible optimum is elsewhere. Increasing effective action gain b or sensing gain s moves this particular optimum; there is no scalar “best memory” independent of the rest of the loop. Conversely, with only body noise, changing a alone shifts stability and error but not the interior optimum, provided a<sqrt(K) still holds. This latter independence does not survive all noise models.

For the example, C_*=.3 and h_*=(.3-.14)/2=.08 in the fast-interface limit, with J_*=6.25. At finite G=1, numerical optimization gives h about .0826513, J about 6.2629251. The finite optimum is reported as a numerical optimization, not identified with the limiting formula. A small continuous adjustment toward the limiting optimum lowers J within the stable interval. This supplies an admissible graded refinement path, not evidence of an actual learning or evolutionary process.

### Independent controller noise shifts the optimum

Let the reduced physical and controller coordinates receive independent noise intensities q_x>0 and q_m>=0, respectively. Put B=b^2 q_m. The exact covariance becomes

\[
J(C)=\frac{q_x(C^2-aC+K)+B}{2(C-a)(K-aC)}.
\]

Its derivative numerator is

\[
q_xK(C^2-K)+B(2aC-K-a^2).
\]

Defining r=B/(q_xK), the unique optimum is

\[
C_*=-ar+\sqrt{K+r(K+a^2)+a^2r^2}.
\]

It lies inside (a,K/a): the derivative is negative at the lower boundary, positive at the upper one, and its numerator has positive derivative for C>0. The formula reduces to sqrt(K) when B=0. It generally moves toward greater decay as controller noise rises. Correlated or colored noise, delay, nonlinear constraints and changing readouts require separate analysis; no universal noise robustness is claimed.

## 7. ER4 — Consequence-sensitive routing, not an intrinsic “mine” bit

Suppose the physical actuators are exchanged across the two compartments, while sensing and retained signals stay attached to their original compartments. Common action is unchanged; difference action changes sign. In A_-, replace -b by +b. With the example's C,D, p_3 becomes -KD-a(CD-ell^2)<0, giving an unstable mode. The source record did not have to disappear for it to cause harmful correction.

Now exchange the corresponding sensor pathways as well. In the difference block s changes to -s. The new matrix is S A_- S^{-1} with S=diag(1,-1,-1); the x input-output law is restored. This is a paired rewiring of actual paths, not merely renaming a symbol. It preserves this regulatory law, not necessarily the complete physical/experiential organization.

The result localizes the relevant relation: signal, sensor and actuator have to be matched to the physical consequences. An independently privileged “self label” is unnecessary to define the operational match, but absence of that label does not prove subjective mineness. Source dependence, positive causal use, useful regulation and phenomenal identification remain different claims.

### Replay control: same nominal record, absent current correction

Drive a second compartment with a recording of a reference controller's output. With matched initial state and identical nominal disturbances, it can reproduce the reference x trajectory. Give only the second physical compartment an unanticipated perturbation. Because its prerecorded output does not change, its deviation from the nominal path obeys delta_dot=a delta. The genuine loop instead responds through exp(A_-t), decaying in the stable regime.

This standard feedback/replay counterexample shows why matching nominal signals is insufficient. It does not assert that the replayed machine lacks basal experience. A5L's semantic limitation survives both positive tests. At most, the present construction discharges the **within-model physical-consumption** step: perturbing the actual signal-to-action path changes the subsequent physical deviation.

## 8. ER5 — Continuity and scope under stress

1. **Continuous rates, nontrivial functional transitions.** Every finite A(g,h) and finite-time exp(tA) varies smoothly. The asymptotic covariance ceases to exist when a pole crosses zero; this does not make finite-time laws discontinuous. A stability boundary is not a first-conscious-ancestor result. Under UCT, a loss of regulation may change or terminate a chosen process token, not switch experience off in all continuing physical processes.
2. **Local, not global, regulation.** Replace the actuator by b*tanh(m). The linearization at the origin is unchanged, but at x>b/a the physical deviation increases even at maximal opposing action. For the example, x>3 escapes the linear region regardless of stored memory. Stability, stationary Gaussian variance, global safety and survival are not interchangeable.
3. **No perfect adaptation.** With a constant load w, the finite model generally leaves x_*=w/[K/(C-ell^2/D)-a]. Leaky feedback need not return exactly to the original zero. The construction is not antithetic integral control and is not claimed to inherit that motif's adaptation guarantee.
4. **State and clock conventions.** Rescaling m changes b and s reciprocally, leaving K and the physical prediction invariant. Uniform time slowing rescales all rates and noise intensity appropriately; stationary physical variance stays unchanged. Slowing only some processes or leaving noise unchanged is a different physical route.
5. **No unconditional evolutionary hierarchy.** Phylogeny, development, learning and engineering rewiring are distinct. We derived no ancestral sequence, selection law, neonatal ownership claim, or inevitability that evolution optimizes J. A physical system with open-loop damping a<0 need not require these corrective pathways at all.
6. **No new gate.** Memory, feedback, useful regulation and stable equilibria are neither necessary nor sufficient for UCT's basal experience. No score here measures intelligence, pain, fear, bodily ownership, subjective unity, or subject count. The mathematical field x is not the complete ontic organization.

## 9. Research gain and the remaining bridge

This round goes beyond preserving information for an observer: the retained variable now participates in an explicit sensor–correction–physical-return loop. The new counterexample prevents an unjustified monotone evolutionary story: better retention or stronger sharing can make regulation worse, while intermediate decay can improve it. The precise dependence on body and sensor gains supplies a prospective organizational prediction rather than another label.

The candidate hypothesis for a later broader account is **co-development of retained distinctions and their consequence-sensitive use**. It allows communication, differentiation and updating to change gradually together. It does not insist that current adult categories are present in their complete form at every stage. Under C1, actually realized constitutive relations must be reflected in experiential organization, but this simulation has not identified the particular experiential distinction to which a finite coordinate corresponds.

To move further, one needs an independently grounded actual carrier and a structural/experiential bridge, not more descriptions of a code as 'mine'. A useful near-term empirical extension would test how reconfigured sensor–actuator relations change calibrated regulator decay and physical error. Its first endpoint is the physical effect, not a phenomenal self report. Studying endogenous construction of the sensor, actuator and viability regime is also necessary before claiming autonomous agency in the stronger sense of [P2].

The mathematics has strong precedents and the global map has not been re-audited. Preserve this as one growing research program with GD v0.1.0 rather than immediately splitting it into another DOI paper. The achieved result is a bounded constructive explanation and a correction of a tempting research inference, not a solved theory of consciousness.

## 10. Actual verification and reproducibility

`code/verify_endogenous_regulation.py` performs symbolic characteristic-polynomial, Routh-factor and covariance checks; 961 exact-rational stability/modal cases; 42 independent ODE-versus-exponential comparisons; 31 full six-variable covariance comparisons; 192 two-variable noise-law comparisons; exact rational and numerical main examples; direct integration of impulse energy; finite-interface limits; sensor/actuator rewiring; replay and scaling checks. General claims rely on the proofs, not grid size. All numerical grids and arbitrary parameter choices are recorded.

The first code execution failed before numerical work because SymPy's `charpoly` generated a symbol without the supplied variable's positivity assumptions, making identically printed symbols unequal. Direct computation of det(zI-A) resolved this programming issue without changing the proposed polynomial. The failure is recorded, not treated as a mathematical refutation or hidden. Final executions and byte comparisons are documented in the reproducibility receipt. No human, animal, hardware, real-model consciousness or natural-evolution experiment was performed.

## References and access limits

[U1] Liu, H. *Unified Consciousness Theory I*, v1.2, DOI 10.5281/zenodo.23131575. This round re-read E2/8.3 and the current guide; not every proof or complete publication corpus was reviewed.

[U2] Liu, H. *What the Whole Adds Without Erasing Its Parts*, v1.1.0. Supplied manuscript and checkpoint; reported DOI 10.5281/zenodo.23327394. No new preservation-lifecycle audit was conducted here.

[U3] *Gradual coordination without indiscriminate mixing*, GD v0.1.0. Full local research note read; repository head and policy checked. Commit 2cbcf7167794c9d6a9ee4432c52a42f92802ac4c.

[U4] A5L20261012, *Role reversal and the semantic barrier*. Full working note re-read this round; semantic target-sensitivity conditions remain undischarged.

[U5] *Endogenous Reference Fields and Experiential Attribution*, repository index. Current index read; v1.2 preferred metadata and preserved v1.1 summary distinguished. No full v1.2 manuscript review claimed.

[P1] Kolchinsky, A., & Wolpert, D. H. (2018). *Semantic information, autonomous agency and non-equilibrium statistical physics*. Interface Focus 8, 20180041. DOI 10.1098/rsfs.2018.0041. Publisher full HTML conceptual framework accessed; no numerical reproduction of their models.

[P2] Barandiaran, X. E., Di Paolo, E., & Rohde, M. (2009). *Defining Agency: Individuality, Normativity, Asymmetry, and Spatio-temporality in Action*. Adaptive Behavior 17, 367–386. DOI 10.1177/1059712309343819. Publisher abstract/accessible notes and author abstract accessed; full article access restricted.

[P3] Briat, C., Gupta, A., & Khammash, M. (2016). *Antithetic Integral Feedback Ensures Robust Perfect Adaptation in Noisy Biomolecular Networks*. Cell Systems 2, 15–26. DOI 10.1016/j.cels.2016.01.004. Publisher summary and introductory material accessed. Our linear circuit is not their molecular motif.

[P4] Olsman, N., Baetica, A.-A., Xiao, F., Leong, Y. P., Murray, R. M., & Doyle, J. C. (2019). *Hard Limits and Performance Tradeoffs in a Class of Antithetic Integral Feedback Networks*. Cell Systems 9, 49–63.e16. DOI 10.1016/j.cels.2019.06.001. Publisher summary and indexed accepted-manuscript leakiness discussion accessed; full-page open attempt returned 403. Prior art, not independently audited here.

[P5] Pecora, L. M., & Carroll, T. L. (1998). *Master Stability Functions for Synchronized Coupled Systems*. Physical Review Letters 80, 2109–2112. DOI 10.1103/PhysRevLett.80.2109. Publisher abstract accessed; full text restricted. Modal stability separation is not claimed as new.
