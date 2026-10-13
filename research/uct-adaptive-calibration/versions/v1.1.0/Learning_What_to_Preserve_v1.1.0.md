---
title: "Learning What to Preserve Without Silencing the Body"
subtitle: "Adaptive Organization, Mutable Evaluation, and Reference-Calibrated Regulation"
author: "Hongju Liu"
date: "13 October 2026 · UCT-GD-2026-01 · v1.1.0"
lang: en
---

\begin{center}
Independent researcher, Shenzhen, China\\
\texttt{trinityaccord@gmail.com}
\end{center}

**Research status.** Final author-directed theoretical and computational preprint prepared for DOI deposition. No DOI has been assigned to this manuscript. It has not undergone independent peer review. The results concern declared stochastic models and measuring arrangements, not a consciousness assay, a biological evolutionary history, or a guarantee of survival.

**AI assistance.** Substantial literature retrieval, mathematical derivation, coding, execution, adversarial review, drafting and preparation were performed with ChatGPT / GPT-6 Astra Pro under the human author's research direction. Repeated runs by the same computational pipeline are reproducibility checks, not independent corroborations. The human author of record is responsible for the theory commitments and publication decision. This revision preserves the predecessor v1.0.0 unchanged and records its additional scope checks separately.

# Abstract

An adaptive system can reduce its error signal by improving its condition or by changing how that condition is measured. We analyze this ambiguity in a two-compartment stochastic regulator with adjustable sensory routing and a mutable binary evaluator. Identical complete baseline observation laws can support opposite effects of a subsequent routing change; a sensory-activity objective can favor muting rather than regulation. For a held, centered two-dimensional Gaussian body measured in a fixed quadratic geometry, two reference modes and two body-reading modes exactly recover total squared deviation from population no-alarm probabilities despite unknown scalar sensitivity and background. For known dimension $n$, $n$ distinct positive body gains suffice and fewer predetermined gains fail universally within this radial Gaussian query family. We derive finite-data enclosures and explicit failure cases for reference bypass, non-Gaussian tails, and directional sensitivity changes. In particular, even knowing an anisotropic sensor metric does not generally recover Euclidean bodily deviation from an arbitrarily dense radial gain sweep. Directional reference calibration followed by a physically implemented equalizer restores the stated recovery contract, or yields a range when the equalizer is imperfect. Fixed-calibration online adaptation and mutable-calibration finite-grid selection are executed as separate studies. A joint-confidence reanalysis of all candidate settings confirms substantially fewer changes than point-estimate selection, exposing the distinction between actual model improvement and available statistical evidence. The contribution is a bounded mechanism, recovery and failure analysis, not new foundations for calibration, a universal anti-tampering system, or a consciousness assay. It makes explicit the physical relations under which a gradually changing organization can continue evaluating its own consequences.

**Keywords:** adaptive organization; homeostatic regulation; sensor calibration; mutable feedback; causal identification; Gaussian quadratic forms; organizational continuity; UCT.

# 1. The explanatory problem

Suppose two parts of a system continually exchange information. Their states may become more similar as communication increases. Similarity, however, can conceal a loss: the system may no longer distinguish a local disturbance from a common condition. Conversely, preserving every local fluctuation can amplify noise into inappropriate action. Neither maximal separation nor maximal mixing is an adequate general principle.

A second difficulty appears when the routing itself learns. What consequence makes one organization persist and another change? If a numerical objective is supplied by an analyst, optimization only shows what that objective favors. If an internal alarm is supplied, its physical relation to the body must still be examined. An alarm can become quieter because regulation improves; because its input is averaged away; because its sensitivity falls; or because an upstream connection no longer carries the condition of interest. These possibilities are not interchangeable.

The paper asks a concrete question: **when a system changes both its signal routing and its evaluator, what observations and physical invariances suffice to keep the learned ordering tied to actual bodily deviation?** We do not require the evaluator to be an immutable, perfectly known oracle. We do require a declared physical reference relation, and we show exactly what is lost when that relation is absent or bypassed.

The word *body* denotes the controlled compartments in our model. Their squared deviations are a specified regulation target. The compartments are not human participants, alarms are not reports of pain, and lower deviation is not a measure of phenomenal richness. In UCT, the motivating distinction is between the existence of experience and the organization of an already actual process [1]. The present task concerns a possible transformation of organization. It does not add a sensing, calibration, homeostasis or learning requirement for basal experience.

This distinction also prevents a false evolutionary narrative. A continuous path of model parameters is not a reconstructed phylogeny. Within-organism learning is not natural selection. A modern person's bodily ownership and conceptual self cannot be projected backward onto every modeled distinction. What can be advanced is more modest and more specific: an installed distinction can participate in a sensing–action–body loop, its consequence can alter a routing parameter, and the relation between that consequence and the evaluator can itself be tested rather than merely named.

# 2. Relation to earlier work and contribution boundary

Several foundations are inherited. Integration with differentiation is a longstanding topic in neuroscience [2]. Spatial sharing can improve sensing by reducing noise even while weakening a local contrast, as the REGI model demonstrates [3]. Homeostatic reinforcement learning explicitly connects rewards to physiological regulation [4]. Causal analyses of reward tampering distinguish changing an intended outcome from changing the reward process [5]. Extremum seeking supplies established tools for improving performance by perturbing parameters [6]. Work on semantic information already connects information to its causal role in maintaining a system [7]. None of these general ideas is claimed as new here.

The measurement literature supplies equally important precedents. Coarse one-bit observations can lose scale information; known dithering can restore covariance information under appropriate conditions [8,9]. Self-test signals are used in actual closed-loop sensors [10]. Gaussian integration and polynomial interpolation are classical mathematics [11]. The new monitor below is not a replacement for the covariance estimators in [8,9], and we claim no minimax efficiency improvement over them. It observes a radial quadratic quantity, not one sign bit per coordinate, and includes mutable monitor gain and background probability. Recovery from quadratic measurements has a substantial literature [16]; the polarization identities and matrix equalization used in this revision are classical. Our additional result is their scoped role, including their limitations, in the mutable-evaluator contract rather than a new covariance-estimation paradigm.

The internal GD v0.1–v0.3 checkpoints progressively developed selective communication, embodied regulation and binary-alarm learning [12]. This paper consolidates their relevant results rather than presenting each checkpoint as a different publication. It adds the variable-calibration identification construction, its finite-query boundary, and explicit failures of a supposedly self-authenticating evaluator. The previous UCT-RC preprint fixes separate local laws in an overlapping discrete process and varies joint memory structure [13]. Here the regulator's local laws can change; the issue is the relationship between adaptive routing, physiological consequences and their measurement. The two models must not be conflated.

The reusable contributions are therefore an integrated family, with three levels. First are exact regulatory and muting results, previously disclosed in the working checkpoints. Second is a reference-calibrated consequence estimator that permits evaluator change, with a finite-dimensional probe-count result. Third are scope tests: finite precision, temporal dependence, reference bypass, and exact non-Gaussian ambiguity. The resulting method can be used without accepting UCT. Its UCT interpretation remains conditional on the theory's constitutive premises and does not close the separate problem of identifying a named phenomenal target [14]. The prior-art search was targeted, not a certificate of global priority.

# 3. A continuous organization family with an actual regulatory role

## 3.1 Physical compartments, routing and regulator

Let $x=(x_1,x_2)$ denote two bodily deviations, expressed in fixed dimensionless physical units, from installed reference values and let $m=(m_1,m_2)$ denote finite-bandwidth regulatory states. A sensory mixing matrix is

$$
P(p)=\frac12\begin{pmatrix}1+p&1-p\\1-p&1+p\end{pmatrix},
\qquad 0\leq p\leq1. \tag{1}
$$

The common component passes unchanged. The difference component is attenuated by $p$. At $p=1$ the sensory mixer preserves local contrast; this does not imply that the physical body compartments are disconnected. Passive bodily coupling remains in the dynamics.

In a fixed orthogonal common/difference basis, the differential body coordinate $z$ and regulator $w$ obey

$$
\begin{aligned}
dz&=(-az-kw)\,dt+\sqrt{2D}\,dW,\\
dw&=(bpz-bw)\,dt+\sqrt{2b^2(Np^2+M)}\,dV,
\end{aligned} \tag{2}
$$

where $a,b,k,D>0$, $N,M\geq0$, and the Wiener drivers are independent. The $N$ term enters before mixing and the $M$ term after mixing. The common sector has the same form with $p_+=1$ and fixed coefficients. Together the sectors are a four-dimensional continuous-state process. “Four-dimensional” is not “four-state.”

The drift matrix for (2) is $A_p=\left(\begin{smallmatrix}-a&-k\\bp&-b\end{smallmatrix}\right)$. Its characteristic polynomial has positive coefficients $a+b$ and $b(a+kp)$, so the fixed-$p$ process is stable. The stationary law is centered Gaussian around those fixed reference values. Changing the reference zero or the relative physical units would change the target, not merely calibrate the sensor; Section 10.3 separates a nonzero physical offset from covariance. This law is a small-signal idealization, not a distributional claim about arbitrary organisms. In particular, an unbounded Gaussian state cannot support a literal zero-failure survival guarantee.

## 3.2 Stationary bodily variance and optimal routing

Let $V=\mathbb E[z^2]$, $Z=\mathbb E[zw]$, and $T_w=\mathbb E[w^2]$. The Lyapunov equations are

$$
aV+kZ=D,\quad bpV-(a+b)Z-kT_w=0,\quad
T_w=pZ+b(Np^2+M). \tag{3}
$$

Eliminating $Z,T_w$ gives the inherited exact formula

$$
V(p)=\frac{D}{a+b}+\frac{b}{a+b}
\frac{D+k^2(Np^2+M)}{a+kp}. \tag{4}
$$

Differentiation gives

$$
V'(p)=\frac{bk}{a+b}\left[N-
\frac{D+k^2M+a^2N}{(a+kp)^2}\right]. \tag{5}
$$

For $N>0$ the unconstrained minimizer is

$$
p_*^{\rm free}=\frac{\sqrt{a^2+(D+k^2M)/N}-a}{k}; \tag{6}
$$

clipping to $[0,1]$ gives the unique constrained minimum. For $N=0$, $V'<0$ and the minimum is $p=1$. These are optima for a fixed regulator, fixed noise conditions and the stated physical objective, not universal organizational or experiential optima. They do not imply that evolution maximizes a single scalar.

Changes of finite parameters change finite-time transition laws continuously. The optimum may meet a constraint boundary without a discontinuous change in experience existence. Likewise a discrete report label can change although physical quantities change gradually. UCT I's continuity and fine-chain claims distinguish these issues [1]; none is inferred from (4) alone.

## 3.3 Identical baseline histories, different intervention effects

At $p=1$, the noise splits $(N,M)=(S,0)$ and $(0,S)$ give the same drift and diffusion in the whole observed $(x,m)$ process. Matched initial laws therefore yield identical complete observation laws at that setting, not merely identical means or one-step tables. A monitor generated by the same conditional kernel from $x$ also has the same history law.

At $p<1$ their diffusion terms differ. Hence the best routing may differ even though passive baseline recordings agree. This is a scoped causal-identification example: the unobserved physical source arrangement differs, so no claim of complete physical equivalence is made. A learner that probes routing can obtain information unavailable at the baseline. Such exploration can worsen regulation in one of the twins; the paper promises neither harmless experiments nor cost-free learning.

## 3.4 Why minimizing sensory activity can favor muting

Set $M=0$, $A_0=D+a(a+b)N>0$, and $B_0=bkN\geq0$. Solving (3) gives

$$
T_w(p)=\frac{bp^2(A_0+B_0p)}{(a+b)(a+kp)}. \tag{7}
$$

\Needspace{6\baselineskip}
For $p>0$,

$$
T_w'(p)=\frac{bp\{2aA_0+(kA_0+3aB_0)p+2kB_0p^2\}}
{(a+b)(a+kp)^2}>0. \tag{8}
$$

Thus the sensory-activity objective has its unique minimum at $p=0$, regardless of whether that choice regulates the body well. For $a=.2,b=2,k=1,D=1,N=.01$, the bodily optimum is $p=1$, where $V=1.21969697$, while $V(0)=5$. Adding the fixed common-sector sensory activity does not change the wrong optimum. This is an explicit realization of a known evaluator-input failure [5], not a refutation of all active-inference or homeostatic-learning accounts.

# 4. From an analyst's optimum to consequence-driven adjustment

## 4.1 Fixed calibration is sufficient, but not an explanation of its permanence

Install a binary alarm $A$ with

$$
\Pr(A=0\mid x)=s\exp[-r\|x\|^2],\qquad r>0,\quad0<s\leq1. \tag{9}
$$

Here $1-s$ is an independent background-alarm probability. An exponential threshold and a background Bernoulli event realize this conditional rule. The squared input can be computed by a transducer, but the state values are not supplied to the learner. Equation (9) is a specified measuring mechanism, not a pain model.

For fixed $p$, with independent common and difference coordinates of variances $V_+$ and $V(p)$,

$$
J(p)=\mathbb E[A]=1-
\frac{s}{\sqrt{(1+2rV_+)(1+2rV(p))}}. \tag{10}
$$

If $r,s$ remain fixed and $V_+$ does not change, $J$ is strictly increasing in $V$. The monitor can be numerically unknown yet preserve the ordering. The reference states, physical input path and monitor family are still installed assumptions.

For an interior paired perturbation $p\pm\delta$, the sign of $J(p+\delta)-J(p-\delta)$ equals that of the variance difference. Writing $C_0=D+k^2M+a^2N$ gives

$$
\frac{V(p+\delta)-V(p-\delta)}{2\delta}
=\frac{bk}{a+b}\left[N-
\frac{C_0}{(a+kp)^2-k^2\delta^2}\right]. \tag{11}
$$

The stationary-evaluation root is

$$
p_\delta=\frac{\sqrt{C_0/N+k^2\delta^2}-a}{k} \tag{12}
$$

when $N>0$, clipped to the permitted probe interval. Its difference from an interior $p_*$ is $O(\delta^2)$. A tangent-projected scalar descent has a unique attracting target because the comparison changes sign only once. This is an expected stationary-feedback statement, not a proof of convergence for arbitrary finite noisy adaptive trajectories.

## 4.2 Previously executed finite learning

The GD v0.3 experiment uses the complete four-dimensional process, exact fixed-gate Gaussian transitions, carried physical state, two finite probe blocks per round, and randomized block order [12]. The learner receives only its settings, timing and two alarm fractions. It does not receive $a,b,k,D,N,M$, body states, modal labels, $V$, or $p_*$. The reference values, gate, timing apparatus and update rule are supplied organizational resources.

Each of five conditions has 32 fixed seeds and 100 rounds. The final 20 center settings are averaged, held fixed and evaluated separately. The following values are medians of the GD v0.3 run, re-executed during v1.0 preparation; they exclude total exploration cost. The current v1.1 revision preserves those trajectories and their prior receipt rather than claiming another fresh execution of this ancestor study.

| Plant and monitor | Learned $p$ | Held differential variance | Best fixed variance |
|:--|--:|--:|--:|
| Upstream noise, bodily alarm | 0.18138 | 0.36257 | 0.36212 |
| Downstream twin, bodily alarm | 0.98764 | 0.88746 | 0.87879 |
| Low upstream noise, bodily alarm | 0.98360 | 1.23005 | 1.21970 |
| Low upstream noise, sensory alarm | 0.000067 | 4.99847 | 1.21970 |
| Gradually relocated noise, bodily alarm | 0.98203 | 0.89146 | 0.87879 |

The common bodily variance is $1/7$ in these fixed-setting comparisons. The gradual-noise condition is adaptation to a specified environmental change, not a simulation of natural selection. That v1.0 re-execution reproduced six main GD v0.3 result files byte for byte. It establishes that the code and recorded results agree; it is not independent scientific confirmation.

## 4.3 The remaining gap

If the gate can change $r$ as well as the body, (10) is no longer an increasing transform of $V$ across settings. For example, $r(p)=r_0p^2$ and $s=1$ give $J(0)=0$ whatever bodily variance remains. More subtly, a positive but changing gain can reverse an ordering without complete muting. Calling the monitor “bodily” or “intrinsic” does not exclude this failure.

We now allow $r=r(p)$ and $s=s(p)$ and ask what finite readings can recover. Calibration does not explain where all reference relations came from. Its purpose is to replace one overly strong premise—an immutable evaluator—with a weaker, explicit set of shared-path and reference premises.

# 5. What an uncalibrated radial monitor cannot identify

**Proposition 1 (scale ambiguity).** In the centered Gaussian family, body readings at any set of known relative gains cannot distinguish $(\Sigma,r)$ from $(c\Sigma,r/c)$ for $c>0$, while $\operatorname{tr}\Sigma$ changes by $c$.

**Proof.** At relative gain $t>0$ the no-alarm probability is

$$
q(t)=s\det(I+2tr\Sigma)^{-1/2}. \tag{13}
$$

The product $r\Sigma$ is unchanged by the stated transformation. The same observation ambiguity can be extended to temporal records by scaling a Gaussian process $X_t$ to $\sqrt c X_t$ and using $r/c$ with identical comparator randomness. Every radial alarm probability conditional on the scaled path is then unchanged. This is an existence construction in the declared observation class, not a theorem that all physical sensors are powerless. $\square$

The general lesson that coarse, scale-invariant measurements do not identify scale is established [8]. Here the ambiguity is relevant because the gain can change with the organization being evaluated. A richer relative-gain sweep cannot, by itself, fix the absolute bodily scale. If only an ordering is needed, an unknown but fixed scale is harmless; an independently changing scale is not.

# 6. Exact recovery with a mutable evaluator

## 6.1 The four-mode contract

At a held organizational setting, assume the following. The body is centered Gaussian in two dimensions, with arbitrary positive semidefinite covariance $\Sigma$. Its target is the fixed Euclidean squared deviation $\|x\|^2$ in the declared physical units. The monitor must act as a scalar gain on that same quadratic quantity, not an unknown direction-dependent weighting. This is the isotropic transduction premise of (9); sharing a path alone does not establish it, as Section 8.2 shows. A nonzero reference squared input $C>0$ and a zero input can enter the same adjustable path as the body's squared input. The same $r>0$ and $s>0$ apply during the four-mode acquisition. A known relative gain of two can be applied to the exponent without changing $s$ or the body's distribution. Comparator randomness is conditionally independent for different reads. The calibration monitor is the evaluator, not the regulator's continuously used sensing channel; its zero/reference modes do not replace regulatory input with a test value. Parameter updates are suspended during each calibration block. A physical implementation in which probes alter the body or its controller must instead model and compensate those effects.

The four population no-alarm probabilities are

$$
\begin{aligned}
q_0&=s, & q_C&=s e^{-rC},\\
q_1&=\frac{s}{\sqrt{\det(I+2r\Sigma)}}, &
q_2&=\frac{s}{\sqrt{\det(I+4r\Sigma)}}.
\end{aligned} \tag{14}
$$

The modes are experimental or internal circuit modes, not four observations sufficient without repeated sampling. Neither an exact probability nor an independently repeated stationary preparation is available for free. The reference can be a maintained internal physical standard; it need not be an external numerical oracle. Its coupling must nevertheless be real, and a reference inserted after an adjustable corruption does not test that corruption.

## 6.2 Two-dimensional reconstruction

**Theorem 2 (reference-calibrated trace).** Under the four-mode contract, define

$$
\widehat r=\frac{\log(q_0/q_C)}{C},\qquad
F_1=(q_0/q_1)^2,\qquad F_2=(q_0/q_2)^2.
$$

At population probabilities, the hats denote reconstruction, not sampling estimates. Then

$$
\boxed{\operatorname{tr}\Sigma=
\frac{4F_1-F_2-3}{4\widehat r}},\qquad
\boxed{\det\Sigma=\frac{F_2-2F_1+1}{8\widehat r^2}}. \tag{15}
$$

These values are invariant to allowed changes of $r(p)$ and $s(p)$ between held settings.

**Proof.** Diagonalizing a centered Gaussian covariance, or directly integrating its density, gives (13). In dimension two,

$$
\det(I+2t r\Sigma)=1+2tr\operatorname{tr}\Sigma+4t^2r^2\det\Sigma.
$$

The two references give $\widehat r=r$. Evaluations at $t=1,2$ yield two linear equations in the trace and determinant. Solving them gives (15). No knowledge of a preferred body mode, $V_+$, an eigenbasis, or the plant coefficients is used. $\square$

This reconstruction does not identify the covariance's orientation. Rotating the physical basis leaves all radial readings unchanged. It also does not identify the whole regulator, hidden temporal states, an experiential type or a subject boundary.

In the regulator of Section 3, the trace is $V_++V(p)$. Since $V_+$ is fixed in the comparison, minimizing the recovered trace gives the same population optimum as minimizing $V$. Crucially, a change in monitor sensitivity alone no longer supplies an apparent improvement.

## 6.3 A fixed relative reference can suffice

Suppose the actual reference input is an unknown constant $C_*$, while the arithmetic uses a nominal $C$. Equation (15) returns $(C/C_*)\operatorname{tr}\Sigma$. If $C_*$ is the same at all settings, this positive multiplier preserves the ordering. The learner therefore need not know an absolute physical unit to compare settings.

If $C_*$ can itself vary with $p$, the score becomes $C\operatorname{tr}\Sigma(p)/C_*(p)$ and can again be made favorable by changing the reference. This is a physical change, not a harmless change of units. At least one stable relation is needed in this observation family; the theorem does not claim that all agency requires this particular reference device.

## 6.4 When the two gains or backgrounds are not shared

A label “double gain” is not evidence that the factor is exactly two. One can instead calibrate each of two distinct gains separately, using zero, reference and body readings at each gain. This gives six modes and permits different backgrounds $s_1,s_2$. Let the individually calibrated gains be $r_1\ne r_2$ and

$$
B_i=\frac{(q_{0i}/q_{bi})^2-1}{2r_i}.
$$

Then $B_i=T+2r_iD_\Sigma$, where $T=\operatorname{tr}\Sigma$ and $D_\Sigma=\det\Sigma$, and

$$
T=\frac{r_2B_1-r_1B_2}{r_2-r_1},\qquad
D_\Sigma=\frac{B_2-B_1}{2(r_2-r_1)}. \tag{16}
$$

This relaxes an electronics premise at the cost of more modes. It does not remove the shared body/reference path within each calibration or the requirement that both modes sample the same held body distribution.

# 7. How many positive body gains are needed?

Let the centered Gaussian body have known finite dimension $n$ and no further covariance restriction. After calibration of $r,s$, define

$$
F(t)=(s/q(t))^2=\det(I+2tr\Sigma). \tag{17}
$$

This is a polynomial of degree at most $n$, with $F(0)=1$. Its derivative at zero is $2r\operatorname{tr}\Sigma$.

\Needspace{9\baselineskip}
**Theorem 3 (sufficiency and fixed-query necessity).** In this family, $n$ distinct positive body gains suffice to recover the trace. For arbitrary positive-definite covariances, fewer than $n$ distinct predetermined positive body gains do not suffice to recover it universally, even when $r,s$ are known exactly.

**Sufficiency proof.** Interpolate the degree-at-most-$n$ polynomial using its known value at zero and the $n$ observed positive values. For gains $1,\ldots,n$, differentiation of the Lagrange polynomial gives the classical weights

$$
\operatorname{tr}\Sigma=\frac{1}{2r}\left[
-H_n+\sum_{j=1}^n\frac{(-1)^{j+1}}{j}\binom nj F(j)\right],
\quad H_n=\sum_{j=1}^n\frac1j. \tag{18}
$$

Polynomial differentiation and such weights are inherited mathematics [11].

**Necessity proof.** Suppose $m<n$ distinct positive gains $t_1,\ldots,t_m$ are fixed. Choose a positive-definite covariance with distinct eigenvalues, so its determinant polynomial $F$ has $n$ distinct strictly negative roots. Perturb it by

$$
F_\epsilon(t)=F(t)+\epsilon\,t\prod_{j=1}^m(t-t_j). \tag{19}
$$

Its degree remains at most $n$, its value at zero stays one, and it agrees at every measured gain. For sufficiently small nonzero real $\epsilon$, all roots remain real, simple and negative: simple real roots persist under a sufficiently small real coefficient perturbation, and disjoint negative neighborhoods can be maintained. Its degree stays $n$. Hence $F_\epsilon$ is again a product $\prod_i(1+2r\lambda_i' t)$ with $\lambda_i'>0$. Its derivative at zero changes by $\epsilon\prod_j(-t_j)\ne0$, so the trace differs. $\square$

The result concerns distinct gain values and exact population readings, not the number of finite bits, computational complexity or an unrestricted information-theoretic optimum over all possible experiments. Directional measurements, prior covariance restrictions or known rank can change the requirement. An unknown ambient dimension prevents this particular finite guarantee.

For $n=2$ a simple witness is $r=1/2$ with eigenvalues $(1,1)$ versus $(1/2,5/3)$. Both give $F(1)=4$, yet their traces are $2$ and $13/6$. A second positive gain separates them. The determinant formula does not become more informative because its single reading is measured to more decimal places.

# 8. Reference transport and preserved measurement geometry

## 8.1 A common path must actually include the changing gain

**Proposition 4 (body/reference mismatch).** Suppose reference probes calibrate $r_C$, but the body actually enters with effective gain $r_B$ at both relative gains. Applying (15) reconstructs

$$
\widehat T=(r_B/r_C)\operatorname{tr}\Sigma. \tag{20}
$$

**Proof.** The body determinant polynomial is formed with $r_B\Sigma$, while the denominator in (15) uses $r_C$. Its linear coefficient is therefore divided by the wrong gain. $\square$

A concrete failure doubles the amplitude of body deviations, multiplying $\Sigma$ by four, while attenuating only the body-input squared signal by one quarter. The references remain intact. All four no-alarm probabilities then match those of the original well-regulated body, and the reconstructed score is unchanged although the actual squared deviation is four times larger. The reference is functioning; it is testing the wrong part of the path.

If independent physical evidence bounds $r_B/r_C$ in $[1-\varepsilon,1+\varepsilon]$ with $\varepsilon<1$, then $\widehat T/(1+\varepsilon)\leq T\leq\widehat T/(1-\varepsilon)$. Similar multiplicative bounds apply to bounded reference drift. Such evidence cannot be supplied merely by asking the same compromised channel to certify itself.

Randomly interleaving modes can reduce ordinary drift, but it does not prove that a mode-dependent manipulator cannot distinguish calibration from use. Arbitrary changes of the input mapping, reference source, comparator rule and observation record are outside the theorem. This calibration does not authenticate arbitrary alterations of its own input and reference conditions. The demonstrated non-identification is the explicit family in Proposition 4, not a universal impossibility theorem about all self-evaluation.

## 8.2 Shared-path directional sensitivity can still conceal change

A scalar reference calibrates (9), not every sensor attached to the same wires. To expose the difference, allow the vector transducer to have a positive-definite metric $G$:

$$
\Pr(A=0\mid x,t)=s e^{-t x^T Gx},\qquad
q(t)=s\det(I+2t\Sigma G)^{-1/2}. \tag{20a}
$$

For a reference vector $v$, $\log(q_0/q_v)=v^TGv$. The matrix $G$ incorporates the total sensitivity. The body objective remains $T=\operatorname{tr}\Sigma$ in the original fixed physical units. Defining the objective to be $\operatorname{tr}(G\Sigma)$ instead would change the question whenever $G$ changes.

**Proposition 5 (two directional ambiguities).** A common reference path need not identify $T$ if directional sensitivity is free to change. Even exactly known anisotropic $G$ need not identify $T$ from all population body probabilities $q(t)$, $t>0$.

**Proof by two exact constructions.** First compare

$$
(\Sigma_1,G_1)=(I,I),\qquad
(\Sigma_2,G_2)=\left(\operatorname{diag}(1,4),\operatorname{diag}(1,1/4)\right).
$$

Both use the same physical body/reference input plane, with the fixed reference $v=(1,0)^T$. The reference response is identical and $\Sigma_iG_i=I$, so every body gain gives the same probability, while $T_1=2$ and $T_2=5$. The original four-mode formula, misapplied as a scalar model, returns two for both. This is outside the isotropic premise, not a counterexample to Theorem 2.

Second hold $G=\operatorname{diag}(1,4)$ fixed and known. The covariances $\Sigma_a=\operatorname{diag}(1,2)$ and $\Sigma_b=\operatorname{diag}(8,1/4)$ have the same weighted eigenvalues $\{1,8\}$, in opposite directions. All body gains therefore match, as do all reference measurements of this identical $G$, but $T_a=3$ and $T_b=33/4$. Radial data determine a weighted spectrum without its orientation relative to the sensor metric. $\square$

Consequently, merely adding more relative body gains or calibrating $G$ more accurately cannot repair the second ambiguity without an additional operation or measurement. This is an eigenvalue/orientation obstruction, not a generic assertion that full covariance estimation is impossible. Directional measurements [8,9,16], known covariance restrictions, or the following physical equalization can change the observation family.

## 8.3 A constructive repair, and what it additionally requires

**Theorem 6 (metric calibration and implemented equalization).** For held positive-definite $G$ in known dimension $n$, exact zero and reference probabilities determine $G$ if and only if the reference matrices $vv^T$ span the real symmetric matrices, when universal identification over that open metric family is required. Once $G$ is determined, an independently implemented linear input transform $H=G^{-1/2}$ makes the effective metric $H^TGH=I$, restoring the centered-Gaussian radial trace construction in the fixed physical body coordinates.

**Proof.** Each reference supplies the linear measurement $\ell(v)=v^TGv=\operatorname{tr}(Gvv^T)$. Spanning gives injectivity. If the span is deficient, choose a nonzero symmetric $K$ orthogonal to it. For small enough $\epsilon$, $G+\epsilon K$ stays positive definite and gives every same reference value, establishing necessity. In particular, the $n(n+1)/2$ vectors $e_i$ and $e_i+e_j$, $i<j$, give

$$
G_{ii}=\ell(e_i),\qquad
G_{ij}=\frac{\ell(e_i+e_j)-\ell(e_i)-\ell(e_j)}2. \tag{20b}
$$

An eigendecomposition of $G$ defines $H$ and directly verifies $H^TGH=I$. A body sample actually transformed to $Hx$ before entering this transducer therefore has exponent $t\|x\|^2$, so (17)--(18) apply with unit calibrated exponent gain. $\square$

The reference count is for reconstructing an unrestricted symmetric metric from quadratic reference readings, not a claim about the fewest measurements needed for every possible body objective. Diagonal references alone do not suffice: metrics with unit diagonal and off-diagonal $+1/4$ or $-1/4$ agree on $e_1,e_2$ but disagree on $e_1+e_2$. Polarization, linear rank and matrix inverse square roots are established mathematics, not foundational inventions of this paper [16].

Equalization is an additional physical intervention on the evaluation input, not an arithmetic correction of already stored radial bits. It must not alter the body distribution or the continuously used regulator, and $G$ must remain stable during calibration and use. Known reference directions and their relative amplitudes are stronger resources than the scalar squared-input standard of Theorem 2. Singular metrics lose directions and admit no such inverse. Finite or ill-conditioned metric reconstruction requires uncertainty control; the present verification demonstrates exact-population recovery, not noise-optimal matrix estimation.

A bounded-error alternative does not require perfect equalization. Let $K=H^TGH$ be the actual effective metric and let $0<k_L I\preceq K\preceq k_U I$ be independently supported bounds. The gain polynomial in (20a) determines $J=\operatorname{tr}(K\Sigma)$, without needing its orientation, and

$$
\frac{J}{k_U}\leq\operatorname{tr}\Sigma\leq\frac{J}{k_L}. \tag{20c}
$$

Indeed, multiplying the positive-semidefinite inequalities by $\Sigma$ and taking traces gives $k_LT\leq J\leq k_UT$. A simultaneous sampling interval for $J$ can replace $J$ by its lower and upper endpoints. If there is no positive $k_L$, this gives no finite upper bound. The bounds themselves are not certified by a single unrepresentative reference. In this way, the repair retains directional calibration error rather than hiding it under the phrase "same path."

# 9. Finite precision, abstention and temporal dependence

## 9.1 A deterministic score enclosure

Population identities must not be substituted for finite measurements. Suppose simultaneous probability intervals $q_j\in[\ell_j,u_j]$ are available for $j\in\{0,C,1,2\}$. If all lower endpoints are positive and $\ell_0>u_C$, set

$$
r_L=\frac{\log(\ell_0/u_C)}C,
\quad r_U=\frac{\log(u_0/\ell_C)}C,
$$

$$
F_{jL}=(\ell_0/u_j)^2,\qquad F_{jU}=(u_0/\ell_j)^2,
\quad j=1,2.
$$

Then let $N_L=4F_{1L}-F_{2U}-3$ and $N_U=4F_{1U}-F_{2L}-3$. The minimum and maximum of $N/(4r)$ over the four endpoint combinations enclose the trace. The lower endpoint can be intersected with zero under the covariance premise. This is conservative because it ignores dependencies among the ratios, but follows directly from interval arithmetic.

If the intervals do not separate a positive gain from zero, the result is *not identified at the stated precision*. It must not be entered into an optimizer as zero bodily cost. Invalid or contradictory model intervals likewise call for rejection, not convenient clipping that manufactures a favorable score.

For independently repeated stationary preparations, each column is binomial, even if columns share the same body sample. Exact binomial intervals [15], with a union-bound allocation across four columns, provide simultaneous coverage. For selection among $K$ settings the allocation must cover all $4K$ columns, not only the ultimately selected one. Repeated sequential tests require a corresponding time-uniform method or an explicit error budget. The point-estimate selection experiment below is not advertised as a confidence-certified adaptive safety policy.

If simultaneous trace enclosures satisfy $T_L(p)\leq T(p)\leq T_U(p)$, replacing a setting $p$ with $p'$ is certified as a fixed-setting mean improvement only when $T_U(p')<T_L(p)$. Overlap means the proposed improvement is unresolved. This certificate excludes transient adaptation costs and says nothing about rare-event safety or ethical desirability.

## 9.2 Near muting there is no uniform finite-data rescue

At $r=0$, all body modes in (14) are Bernoulli with no-alarm probability $s$, independent of $\Sigma$. As $r$ approaches zero, a fixed finite acquisition design with bounded predetermined relative gains produces distributions of readings that approach one another for different fixed bounded covariance choices. There can be no covariance-discriminating procedure with a fixed finite number of these reads and a uniform nontrivial guarantee down to zero gain.

For fixed $0<s<1$ and fixed relative gain, the leading change in a body probability is $-sr\,\Delta T$. The one-read Bernoulli divergence between close alternatives is of order $r^2(\Delta T)^2$, illustrating the growing data burden. The rate changes at the boundary $s=1$, where events become rare; we do not claim a single minimax rate covering all nuisance parameters. Calibration corrects an identifiable distortion, not erased information.

## 9.3 Correlated bodily records

For two stationary times with body covariance $\Sigma$ and cross-covariance $C_\tau$, define $\Sigma_\tau=\left(\begin{smallmatrix}\Sigma&C_\tau\\C_\tau^T&\Sigma\end{smallmatrix}\right)$. Fresh comparator randomization at distinct times gives

$$
\operatorname{Cov}(B_0,B_\tau)=s^2\left[
\det(I+2r\Sigma_\tau)^{-1/2}
-\det(I+2r\Sigma)^{-1}\right], \tag{21}
$$

where $B=1-A$ is the no-alarm bit. For $m$ evenly spaced reads,

$$
\operatorname{Var}(\bar B)=\frac{q(1-q)}m+
\frac2{m^2}\sum_{j=1}^{m-1}(m-j)\operatorname{Cov}(B_0,B_{j\Delta}). \tag{22}
$$

This follows from the Gaussian quadratic integral and expansion of the variance of a sum. It is a fixed-setting stationary formula. During arbitrary adaptive changes, Gaussian independence or stationarity cannot simply be presumed. More rapid sampling can add highly redundant observations. The finite test in Section 11 evaluates (21)–(22) with the complete regulator, not only a scalar correlation surrogate.

# 10. Beyond the Gaussian contract

## 10.1 Exact non-Gaussian ambiguity, not just a warning

The reconstruction does not certify its own distributional assumption. Let $E=\|X\|^2$ and $U=e^{-E}$ for $r=1$. Body readings at gains one and two reveal $\mathbb E U$ and $\mathbb E U^2$. A centered Gaussian $\Sigma=I/2$ has these values $1/2$ and $1/3$, and trace one.

**Theorem 7 (non-Gaussian moment twin).** There are centered, non-Gaussian two-dimensional distributions with the same four population probabilities as this Gaussian and arbitrarily large $\mathbb E\|X\|^2$.

**Construction and proof.** Assign probability $\epsilon=1/1000$ to $U=d$, where $0<d\leq1/16$, and probabilities $w_1,w_2,w_3$ to $1/10,1/2,9/10$. Set

$$
\begin{aligned}
w_1&=(4973+84d-60d^2)/19200,\\
w_2&=(23027-300d+300d^2)/48000,\\
w_3&=(4997+36d-60d^2)/19200.
\end{aligned} \tag{23}
$$

These weights are positive on the stated interval. Direct substitution gives total probability one, $\mathbb E U=1/2$ and $\mathbb E U^2=1/3$. Let the vector $X$ have squared radius $-\log U$ and an independent uniform angle. It is centered. Its expected squared radius is

$$
-\sum_{i=1}^3w_i\log u_i-\epsilon\log d,
$$

which tends to infinity as $d$ tends to zero. Zero and reference modes are unchanged. Both Gaussian reconstruction equations therefore return trace one and determinant $1/4$ for every member of this family. Even the elementary positivity and eigenvalue-consistency checks pass. $\square$

This is a finite-moment non-identification construction, not a novel foundation of moment problems. It shows why passing the monitor's internal algebra is insufficient evidence of Gaussianity. Rare large deviations are precisely what bounded no-alarm probabilities can underrepresent. Nonzero means, nonlinear response laws, or undisclosed saturation also require different models.

## 10.2 A distribution-relaxed positive bound

A useful alternative is available when a physical moment bound is independently justified. For arbitrary nonnegative $E$ with $\mathbb E[E^2]\leq M_2<\infty$, define

$$
L(r)=\frac{1-\mathbb E[e^{-rE}]}r
=\frac{1-q_b/q_0}{r}.
$$

The elementary inequalities $1-y\leq e^{-y}\leq1-y+y^2/2$ give

$$
\boxed{L(r)\leq\mathbb E E\leq L(r)+\frac r2M_2.} \tag{24}
$$

Thus one body gain plus zero and reference modes can yield a valid interval without a Gaussian shape hypothesis. A known bound $E\leq B$ gives the sharper multiplicative inequality $L(r)\leq\mathbb E E\leq rB L(r)/(1-e^{-rB})$. These inequalities are classical; their use here is to make the calibration alternative and its required physical assumptions explicit.

For finite probability intervals, combine the gain interval from Section 9 with

$$
U_L=\max(0,1-u_b/\ell_0),\quad
U_U=\max(0,1-\ell_b/u_0)
$$

to obtain $U_L/r_U\leq\mathbb E E\leq U_U/r_L+r_U M_2/2$. A smaller gain reduces the moment-truncation error but increases measurement difficulty. Neither side of this tradeoff can be removed by writing a more precise decimal. The moment bound is substantive: Theorem 7 escapes it by allowing an arbitrarily large second moment.

The regulatory Gaussian experiments do not themselves establish a bounded-moment contract for a real organism. The alternative is included as a transferable measurement rule with an independently testable premise, not a claim that every physiological distribution meets it.

## 10.3 A shifted body is not merely a different covariance

Centering is a physical premise relative to the installed reference, not an instruction to subtract an unobserved sample mean and forget it. If $X\sim\mathcal N(\mu,\Sigma)$, completing the Gaussian square yields

$$
q(t)=\frac{s\exp[-tr\,\mu^T(I+2tr\Sigma)^{-1}\mu]}
{\sqrt{\det(I+2tr\Sigma)}}. \tag{24a}
$$

The physical target is now $\mathbb E\|X\|^2=\operatorname{tr}\Sigma+\|\mu\|^2$. The extra factor destroys the determinant-polynomial identity. For $\mu=(1,0)^T$, $\Sigma=\operatorname{diag}(.2,.4)$, $r=.5$ and $s=.8$, the true total deviation is $1.6$, while applying the centered four-mode formula gives approximately $.97363$. Exact arithmetic on finite modes cannot repair an omitted mean model. The distribution-relaxed bound of Section 10.2 applies to this total deviation whenever its independent energy-moment bound is supplied; unlike Theorem 2, it does not require zero mean.

A physical revision of the target zero may be justified in a particular application. It must be distinguished from improvement relative to the old target, with both changes recorded. This paper does not infer a correct physiological reference merely from whichever reference gives the smallest subsequent score.

# 11. Executed studies and reproducibility

## 11.1 Algebraic and model checks

The research package contains explicit proofs and executable checks. New verification includes 80 rational two-dimensional identities; 24 rational general-dimensional reconstructions for dimensions one through eight; 1,000 rotated positive-definite covariance examples; 1,000 deterministic interval checks; five explicit fewer-gain polynomial witnesses; five non-Gaussian exact moment matches; 400 arbitrary-gain six-mode reconstructions; and 1,000 non-Gaussian second-moment-bound examples. Ninety full regulator Lyapunov equations also agree with (4).

The maximum absolute discrepancy in the rotated-covariance recovery checks was $1.30\times10^{-13}$; in the regulator variance checks it was $8.89\times10^{-15}$. These numerical tolerances are not error bounds on nature or substitutes for the general proofs. All assertions passed. The spectral witnesses use floating-point root checks only as illustrations; the lower-bound proof is the perturbation argument in Theorem 3.

## 11.2 Finite-sample calibration-mediated routing selection

The new experiment uses 21 candidate settings $p=0,.05,\ldots,1$. The environment changes monitor sensitivity and background with the setting:

$$
r(p)=.2+1.8p^2,\qquad s(p)=.85-.1p. \tag{25}
$$

Neither function is provided to the selector. At each setting, it receives four empirical no-alarm fractions from 65,536 independently prepared stationary samples per mode. Body modes share the same squared-body sample within each draw, with fresh comparator randomness; samples across draws are independent. Reference draws are generated by the same declared monitor law. The selector receives the grid, these fractions, the reference input $C=1$, and the known factor two. It never receives the state values, noise split, variance formula or optimum.

One selector minimizes the raw alarm fraction; the other minimizes the reconstructed trace from (15). The latter rejects nonfinite or negative trace estimates. The raw selector deliberately ignores the extra reference and body-gain information, so this is a mechanism comparison, not proof of measurement-budget-optimality or superiority over advanced competing estimators. The calibrated method uses four mode counts; one cannot describe it as obtaining the repair at no measurement cost.

Every environment has 32 declared seeds. The retained decision is evaluated by the actual fixed-setting body variance, not by the noisy quantity that selected it. This avoids presenting winner-biased fitted scores as true performance.

| Noise arrangement | Median raw-choice $p$ | Median calibrated $p$ | Raw-choice $V$ | Calibrated-choice $V$ |
|:--|--:|--:|--:|--:|
| Upstream | 0.05 | 0.20 | 0.41818 | 0.36364 |
| Downstream | 0.15 | 1.00 | 2.90260 | 0.87879 |
| Low upstream | 0.15 | 1.00 | 3.05253 | 1.21970 |

These are medians over all seeds. The exact best differential variances are respectively .36212, .87879 and 1.21970. No invalid estimates occurred in these runs. Calibrated choices were better than raw choices in every reported seed, but this finite outcome is not a universal dominance theorem. The gain functions, Gaussian model and large sample counts make this a controlled proof-of-concept rather than a claim of practical physiological deployment.

This study is deliberately distinct from the online carried-state experiment of Section 4. It supplies independently repeated stationary preparations, which remove temporal bias at a cost. It is finite-grid selection, not a new proof of stochastic convergence for a fully mutable continuous-time organism. Existing v0.3 trajectories demonstrate installed adaptation with fixed monitor calibration; the new experiment tests whether variable-calibration readouts can guide parameter choice. A combined carried-state, confidence-certified adaptive protocol remains a future implementation task.

## 11.3 Precision and a retained failure regime

We evaluated the deterministic enclosure using binomial intervals with an overall four-column confidence allocation of 95%. For each of seven gains, 1,000 trials used 65,536 samples per mode. The tested covariance was $\operatorname{diag}(1/7,.9)$ and $s=.8$.

At gains $10^{-4}$ and $10^{-3}$, all 1,000 trials failed to certify a positive gain. The correct output was no score. At gain .01, 467 trials returned no score; finite intervals in the remainder had a median width of approximately 19.61. At .5 the median width was about .421. All finite intervals in this particular test covered the true trace; this empirical 100% is not asserted as a universal confidence level. The intervals are conservative. A point estimate alone would conceal the severe near-muting uncertainty. These tests address a single four-mode setting, not the simultaneous choice among all 21 settings; Section 11.5 audits that larger family separately.

For a separate stationary, temporally sampled four-dimensional regulator with 128 reads at spacing .2, $r=.5$ and $s=.8$, (22) gives alarm-fraction variance .00311870. Treating the reads as independent gives .00181175, an underestimate by a factor 1.72137. An independent Monte Carlo check over 16,000 complete records gave .00314923. Its finite discrepancy is expected. This check validates one specified stationary covariance calculation, not the use of independent binomial intervals on arbitrary adaptive records.

## 11.4 Reproduction and version discipline

The new code was executed twice with fixed seeds. The main JSON and CSV outputs matched byte for byte. During v1.0 preparation, the six primary GD v0.3 outputs were also regenerated and matched their supplied originals; their receipt is preserved as prior execution evidence, not relabeled as a v1.1 run. Two algorithmic comparisons are independent in a limited computational sense: rational polynomial identities are checked separately from determinant recovery, and stationary analytic covariance is compared with full process propagation. Neither is an independent laboratory or author replication.

The package includes source, exact outputs, all finite-selection records, the predecessor archives, a source-access ledger, claim-level coverage, an adversarial review and a reproduction receipt. Software versions are fixed in the environment record. Original published manuscripts and predecessor checkpoints are not overwritten.

## 11.5 Joint-confidence decision audit of the archived selection data

The point-estimate results in Section 11.2 do not show that the sampled evidence certifies an improvement. We therefore reanalyzed the same archived counts, without drawing new samples. For each environment and seed, all 21 settings and all four mode columns form one decision family. We assign two-sided Clopper--Pearson intervals with tail probability $.05/(2\times84)$ to each column and propagate them using Section 9.1. The union bound gives at least 95% simultaneous coverage per decision family under the stated independent-trials-per-column model; correlations between columns are allowed. The 96 validation families are not claimed to have a single joint 95% guarantee.

The fixed incumbent is $p=1$. A change is accepted only if the candidate's upper trace bound is below the incumbent's lower trace bound. When multiple candidates qualify we choose the smallest upper bound; otherwise we retain the incumbent. The acceptance condition is inherited from Section 9.1, not a new statistical theorem.

| Environment | Families | Certified improvement over incumbent | Retained incumbent |
|:--|--:|--:|--:|
| Upstream noise | 32 | 4 | 28 |
| Downstream noise | 32 | 0 | 32 |
| Low upstream noise | 32 | 0 | 32 |

All 2,016 propagated intervals were finite and contained their model's true trace in this particular audit; no accepted change had a worse true held-setting trace. These observed counts are not an assertion of 100% coverage. The downstream and low-noise incumbents are already population-optimal in this model, so withholding an improvement certificate there is appropriate. In the upstream condition many genuine point-estimate improvements remain unresolved because the joint intervals overlap.

This retained limitation is essential: calibration can correct a scale distortion, yet current data may remain insufficient to warrant a change. The audit is neither a new online adaptive experiment nor a proof that the chosen interval construction is statistically efficient. A sharper joint likelihood or better acquisition design may certify more changes, but is not represented as implemented. Exploration costs, correlated online sampling and rare-event harm remain outside this certificate.

## 11.6 Revision-specific verification and input handling

The three original programs were freshly rerun in the final-revision environment; all five primary v1.0.0 outputs matched their archived bytes. The additional program `verify_final_revision.py` checks the two directional ambiguity constructions symbolically for arbitrary relative gain, 400 metric reconstructions in dimensions two through six, 1,200 equalized body-probability comparisons, 400 nonideal metric bounds, five spanning reference designs and 500 valid score boxes. Maximum numerical errors were $3.33\times10^{-16}$ for metric entries, $3.33\times10^{-15}$ for equalization, and $2.67\times10^{-15}$ for the two-dimensional trace examples. The known-metric twin is not claimed to be resolved by calibration without the additional transform.

The companion `calibration_safeguards.py` rejects malformed probability boxes, invalid physical scales and non-positive-definite metrics. Thirteen malformed-input cases and two explicit abstention/inconsistency cases were checked. These screens reject selected algebraic failures; passing them does not certify a distribution, correctly shared wiring, or complete physical validity. The original point-estimate pipeline is retained as the historically executed comparison, while the new familywise audit uses the guarded enclosure interface. Both source and exact outputs are included, and final-repeat results are recorded in the reproduction receipt.

# 12. Thought experiments and conditional implications for UCT

## 12.1 Two gradually communicating mechanical bodies

Imagine two mechanical compartments whose temperatures or concentrations affect each other and whose actions continuously regulate local deviations. Increasing exchange can reduce noise or erase an important difference. Section 3 states which effect wins in one family; Section 4 lets the system adjust the route from finite events. Section 6 makes changes to its evaluator visible through a reference relation. None of these transformations requires inserting an experience-existence switch.

The model nevertheless does not show that bodily ownership is the value of $p$, that two subjects fuse at an optimum, or that every useful discrimination is phenomenal. Under UCT's C1, *actual complete constitutive* changes correspond to experiential organizational changes [1]. A finite model is not automatically that complete description. This is a candidate explanation of organizational formation that a constitutive theory may use, not independent proof of C1 or identification of a selected experiential quality [14].

## 12.2 The thermometer that improves its score

A thermometer attached to a regulator can lower displayed variation by helping correct temperature or by reducing sensitivity. A fixed calibration blocks the second route by stipulation. A reference-calibrated construction need not freeze sensitivity: it can permit change while tracking what that change does to the meaning of the reading. But a reference connected after the faulty input can continue to pass self-tests. This thought experiment separates changing a process, changing its representation, and changing the relation between the two.

No psychological deception is needed. The counterexample therefore cannot establish intentional denial, pain relief or a human symptom mechanism. Those interpretations would add premises absent here.

## 12.3 An evolving internal standard

A biological or artificial system might retain an internal comparison through turnover, use multiple references, or change units as its body changes. The fixed-reference result allows unknown scale: what must persist is a usable relation across the changes being compared. If all bodily scales and all references are allowed to vary independently without evidence, the scale ambiguity returns. Saying “the value is intrinsic” does not supply the missing relation.

This is not an argument that all standards must be externally commanded. The reference can be maintained by the same extended process. But explaining that maintenance is an additional scientific task. Continuity also does not decide which reference changes preserve the intended relation: a smooth loss of sensitivity in one direction can follow the counterexample in Section 8.2. No subjective threshold is needed for either a genuine adjustment or an increasingly misleading one. The present paper installs the standard, evaluator family and adjustable route. It does not derive their origin from an organism with no organization or no experience.

## 12.4 Slow realizations and finite windows

Rescaling all rates and observation times consistently can preserve dimensionless regulatory behavior. Actual slowing can introduce unscaled leaks and noise; it must not be treated as an automatic exact equivalence. A slow process can also yield too little evidence within an observer's available window. That is a limitation of identification, not a proof that the process lacks experience. Conversely, idealized precision cannot recover a distinction erased by the observation mapping, as Proposition 1 illustrates.

## 12.5 Why this is not another scalar theory of selfhood

The paper separates source distinctions, regulatory role, evaluative calibration, learning history and phenomenal interpretation. These are not successive thresholds on one consciousness scale. A system may retain a distinction without using it; use it without a conceptual self-report; change its report without changing the tracked bodily outcome; or preserve a reliable measure while becoming worse at another task. The work therefore supports a plural description of gradually constructed relations rather than a universal developmental ladder.

Local processes that actually persist are not removed to make the whole exist. Local persistence is also not unchanged local content. Which physical process is being described, at what time and boundary, remains necessary to apply the UCT claims. The official UCT map is not promoted on the basis of these finite calculations; the separate all-history semantic audit remains incomplete.

# 13. Limitations and next empirical use

The results rely on physical assumptions that can fail: the adjustable family, the body–reference path, held calibration, stationary centered Gaussian states and a fixed or physically equalized quadratic metric for exact trace recovery, and a supported moment bound for the distribution-relaxed alternative. An arbitrary adaptive observer can also change its reference or its input mapping; we provide counterexamples rather than a universal defense against that possibility.

The mathematical trace is an explicitly chosen small-signal regulation objective. Minimizing it need not minimize energy use, transient harm, tail risk, discomfort, or every component's individual loss. A physically meaningful survival objective would require a different model. The paper does not derive ethics from covariance.

The minimal-gain theorem is an algebraic statement for exact radial Gaussian queries. It is not a lower bound on all sensor designs. Finite probabilities require repeated measurements, and high-dimensional interpolation can be ill-conditioned. The experiment uses a two-dimensional body and does not demonstrate scalable high-dimensional estimation. Known rank, symmetry or directional measurements may permit better designs.

A direct engineering test would use two coupled, continuously regulated physical compartments, an independently audited adjustable mixing path, a comparator with controllable gain and background, and a reference entering before all mutable signal scalings. The primary endpoints would be calibration error, held-state regulation and the predicted failure when the reference bypasses a change. Such a test would evaluate the organizational mechanism without labeling an alarm as experience. Biological or brain applications would additionally require a defensible mapping of variables, independent physiological measurements, appropriate ethics, and a separate account of the intended experiential comparison. No new human, animal, neural or hardware experiment is reported here.

# 14. Conclusion

Gradual organizational development cannot be represented merely by increasing communication, reducing internal activity, or improving a self-produced score. Those changes can alter both the system and the means by which it evaluates the alteration. In the declared regulator, consequence-driven adjustment is possible without giving the learner the optimum, but a mutable evaluator creates an additional identification problem.

A same-path physical reference, together with a preserved or independently equalized measurement geometry, can make a changing evaluator informative rather than immutable. The centered Gaussian construction gives an exact recovered bodily trace from finite mode probabilities, a general-dimensional gain-count result, and explicit uncertainty conditions. A reference bypass, anisotropic sensitivity, a nonzero unmodeled mean, or a non-Gaussian moment twin defeats an unqualified interpretation; a supported second-moment bound permits a weaker non-Gaussian guarantee. A directionally calibrated sensor can still need a physically implemented equalizer rather than more radial samples. The joint-confidence audit also separates a genuinely improved model setting from sufficient evidence to recommend it. These positive and negative results belong together.

The work identifies neither a first experiencer nor a numerical self. It models how distinctions can retain a regulatory role as organization changes. A favorable self-evaluation matters here only insofar as its physical connection to the intended consequence is preserved.

# Data, code, authorship and disclosure

All new study data are generated by the supplied stochastic models; there are no participant, animal, clinical, proprietary-model or hardware data. The source, seeds, outputs, preceding checkpoint archives and revision review are supplied with the prepared deposit package. No external grant, institutional endorsement or independent replication is claimed. This is first-party UCT-motivated work; its model conclusions do not rely on treating that first-party origin as corroborating evidence. The author identity and AI assistance are disclosed on the first page. DOI and preservation states are recorded outside the scientific claims and must not be inferred from the existence of this PDF.

# References

[1] Liu, H. (2026). *Unified Consciousness Theory I*, v1.2. DOI: 10.5281/zenodo.23131575. Primary theory source; C1/U1, U2/E2 and evolutionary-scope claims. Repository source identified in the access ledger. A first-party preprint, not independent empirical support.

[2] Tononi, G., Sporns, O., & Edelman, G. M. (1994). A measure for brain complexity: relating functional segregation and integration in the nervous system. *PNAS*, 91, 5033–5037. DOI: 10.1073/pnas.91.11.5033.

[3] Mugler, A., Levchenko, A., & Nemenman, I. (2016). Limits to the precision of gradient sensing with spatial communication and temporal integration. *PNAS*, 113, E689–E695. DOI: 10.1073/pnas.1509597112.

[4] Keramati, M., & Gutkin, B. (2014). Homeostatic reinforcement learning for integrating reward collection and physiological stability. *eLife*, 3, e04811. DOI: 10.7554/eLife.04811.

[5] Everitt, T., Hutter, M., Kumar, R., & Krakovna, V. (2021). Reward tampering problems and solutions in reinforcement learning: a causal influence diagram perspective. *Synthese*, 198, 6435–6467. DOI: 10.1007/s11229-021-03141-4. Author preprint: arXiv:1908.04734v5.

[6] Krstić, M., & Wang, H.-H. (2000). Stability of extremum seeking feedback for general nonlinear dynamic systems. *Automatica*, 36, 595–601. DOI: 10.1016/S0005-1098(99)00183-1.

[7] Kolchinsky, A., & Wolpert, D. H. (2018). Semantic information, autonomous agency and non-equilibrium statistical physics. *Interface Focus*, 8, 20180041. DOI: 10.1098/rsfs.2018.0041.

[8] Dirksen, S., Maly, J., & Rauhut, H. (2022). Covariance estimation under one-bit quantization. *Annals of Statistics*, 50, 3538–3562. DOI: 10.1214/22-AOS2239. Author preprint: arXiv:2104.01280v2.

[9] Dirksen, S., & Maly, J. (2024). Tuning-free one-bit covariance estimation using data-driven dithering. *IEEE Transactions on Information Theory*, 70, 5228–5247. DOI: 10.1109/TIT.2024.3358994. Author preprint: arXiv:2307.12613.

[10] Sun, Z., & Wang, M. (2022). Self-test and self-calibration of digital closed-loop accelerometers. *Sensors*, 22, 9933. DOI: 10.3390/s22249933. Used as an engineering precedent, not validation of the present monitor.

[11] Fornberg, B. (1988). Generation of finite difference formulas on arbitrarily spaced grids. *Mathematics of Computation*, 51, 699–706. DOI: 10.1090/S0025-5718-1988-0935077-0. Cited for inherited interpolation/differentiation machinery, not a theorem copied into this model without proof.

[12] Liu, H., with ChatGPT assistance (2026). *UCT Gradual Differentiation*, v0.1.0–v0.3.0. Versioned working notes, programs and executed results supplied with this paper as unchanged predecessor archives. No independent DOI claimed for these checkpoints. v0.3 remote summary commit: 85b853079ba185f6cb5e7ddd9ec5721965a12c0d.

[13] Liu, H. (2026). *What the Whole Adds Without Erasing Its Parts*, v1.1.0. DOI reported in its publication receipt: 10.5281/zenodo.23327394. Supplied source and package reviewed; the present work does not modify the record or reverify the preservation lifecycle.

[14] UCT working record A5L20261012 (2026). *Role reversal and the semantic barrier*. Source blob f3f86c4719bd3dd48a65c99858f41b8a9a44c566. Its direct-coordinate-writer countermodel prevents equating an observed coordinate with a selected experiential target.

[15] Clopper, C. J., & Pearson, E. S. (1934). The use of confidence or fiducial limits illustrated in the case of the binomial. *Biometrika*, 26, 404–413. DOI: 10.1093/biomet/26.4.404.

[16] Chen, Y., Chi, Y., & Goldsmith, A. J. (2015). Exact and stable covariance estimation from quadratic sampling via convex programming. *IEEE Transactions on Information Theory*, 61(7), 4034–4059. DOI: 10.1109/TIT.2015.2429594. Author preprint: arXiv:1310.0807. Cited for prior quadratic-measurement recovery work, not as proof of this monitor's specific contract.

# Appendix A. Claim and dependency summary

The regulator variance, baseline twins, sensory-muting derivative, fixed-calibration ordering and finite learning data consolidate GD7–GD17. They are disclosed checkpoint results, not new results merely because they enter a manuscript.

The new layer comprises GD18 (radial scale ambiguity in the mutable-evaluator setting), GD19 (reference-calibrated trace and determinant), GD20 (finite-dimensional body-gain count), GD21 (shared-path/reference mismatch), GD22 (finite-precision enclosure and near-muting abstention), GD23 (exact non-Gaussian moment twin and moment-bounded alternative), and GD24 (finite-sample calibration-mediated selection). These are conditional mathematical results or executed finite studies. “New” here means incremental to the supplied GD checkpoints; global priority is not certified. The numerical methods and basic algebra are explicitly inherited.

The v1.1 revision adds GD25 (directional ambiguity, metric reconstruction and the additional physical equalization requirement), GD26 (joint-confidence reanalysis of archived candidates and guarded abstention), and GD27 (the explicit noncentral-Gaussian scope correction). GD19 now explicitly names fixed quadratic geometry; its original radial proof is unchanged. Classical matrix identities and simultaneous-coverage machinery are not claimed as new foundations. No preceding public work is overwritten by this unpublished revision.

The map baseline remains UCT-MAP-v1.1.2. The manuscript's finite claim layer is internally checked, but no all-node historical semantic audit is claimed. Its graph is disabled as an automatically established UCT premise set. This administrative status does not change the scope of the proofs printed here.

\clearpage

# Appendix B. Reproduction commands and source-access limits

Run from the package root without Python optimization:

```text
python code/verify_calibration.py
python code/experiment_calibrated_selection.py
python code/verify_precision.py
python code/verify_final_revision.py
```

The first program verifies identities, adversarial constructions and deterministic bounds; the second executes all stated settings and seeds; the third evaluates binomial precision and full-process temporal covariance; the fourth checks the final-revision metric results and audits the archived count families. The fourth program uses the existing `results/SELECTION_TRACE.csv` by default, or an explicitly provided `--counts` path. Files in `results/` are actual outputs. `review/REPRODUCIBILITY_RECEIPT.json` records the comparison with a second execution. The predecessor archive contains the unchanged programs for the online fixed-calibration experiments. The reproduction receipts distinguish the prior ancestor re-execution from programs freshly rerun for v1.1.

The v1.0 source-access ledger remains preserved. In the v1.1 review, the author preprint and introductory model discussion of [8], the publisher abstract and bibliographic record of [5], the author abstract of [9], the accessible primary abstract and conclusions of [10], and the author/institutional primary metadata and abstract of [16] were re-opened. The primary eLife page for [4] and its PMC mirror returned browser challenges in this round; their earlier reviewed claims were retained without pretending to obtain fresh full-text access. Other original references were not comprehensively re-audited. Source-access limitations are recorded separately from mathematical validity. The full historical UCT map was not freshly re-reviewed; the candidate layer remains disabled. No search absence establishes global originality.
