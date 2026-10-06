# From target sufficiency to controlled-law closure

R131, 6 October 2026. Research derivation, not a released paper. Basis: A/I 1.2, B/II 1.1, C/III 1.0, D/TA-TR-2026-24 1.0; R130 reviewed map.

## 1. Question and contribution

C:P2_COORD identifies a coordinate exactly when it is constant on observational fibers. D:PAYOFF makes this target-relative: some payoffs require joint information and others do not. N128:JOINT_CRITERION requires the whole pushed-forward transition law to be constant on each present-state fiber. These are different targets. This note connects them through an explicit finite test interface.

The contribution is a project-level synthesis and generalization, with a positive certificate and sharp failure construction. The mathematics is elementary finite-dimensional linear algebra, probability and strong lumpability, not claimed as historically new. D §4/R96D already gives the binary payoff decomposition; PLT ledger §§753–755 already gives high-order marginal blindness. The present argument does not rediscover those results or establish consciousness from observations.

## 2. Declared interface

Let Z be a finite outcome set of size n >= 2. Let f_1,...,f_m:Z -> R be fixed real-valued probes. For a probability column vector mu on Z define

\[
A=\begin{pmatrix}\mathbf 1^T\\ f_1^T\\\vdots\\ f_m^T\end{pmatrix},\qquad
y(\mu)=A\mu=(1,E_\mu f_1,\ldots,E_\mu f_m)^T.
\]

The admissible law class in the universal results is the **entire probability simplex** Delta(Z). Probe values are exact expectations under a common protocol, rather than estimates from one realization. The constant row represents normalization and is not an additional measured probe. The probes, outcome labels, action meanings and time grain are fixed across comparisons.

## 3. Theorem 1: target-span criterion — R131:TARGET_SPAN

For a fixed target payoff g:Z -> R, the following are equivalent:

1. E_mu g is determined by y(mu) for every mu in Delta(Z), allowing any recovery function.
2. g belongs to the real row span of A.

**Proof.** If g=A^T c, then E_mu g=c^T y(mu). Conversely, if g is outside the row span, the finite-dimensional identity row(A)=(ker A)^perp gives a nonzero d with Ad=0 and g^T d != 0. Normalization gives sum_z d_z=0. Hence the positive and negative parts d^+,d^- have the same strictly positive mass alpha. Set u=d^+/alpha and v=d^-/alpha. Then u,v are probability laws, Au=Av, but g^T u-g^T v=(g^T d)/alpha != 0. The target is not constant on the probe fiber; by C:P2_COORD it is not identified. QED.

This applies simultaneously to a payoff family by requiring every member to lie in row(A). For two action payoffs evaluated under the **same** outcome law, identifying their score difference requires their difference to lie in row(A). For action-dependent laws, apply the criterion separately or specify the allowed cross-action constraints. Failure to identify a numerical score does not necessarily leave its sign or the optimal action unidentified; a robust ranking can survive score ambiguity. This theorem is not an iff test for identifying the argmax in every decision problem.

**D as a special case.** On Z={(0,0),(0,1),(1,0),(1,1)}, probes Q and O span the additive payoffs together with the constant. QO is outside that span. Adding QO spans all four-outcome payoffs. This recovers D:PAYOFF and its dependence qualification rather than creating a new binary result.

## 4. Theorem 2: complete-law criterion and sharp blindness — R131:COMPLETE_LAW

The interface y identifies every probability law on Z iff rank(A)=n. If rank(A)<n, there exist u,v with

\[
Au=Av,\qquad \operatorname{TV}(u,v)=1.
\]

Consequently a universally law-identifying interface of this specified scalar-expectation form needs at least n-1 probes in addition to normalization. This is a worst-case requirement over the unrestricted simplex, not a lower bound for every restricted model family, nonlinear observation oracle or particular kernel.

**Proof.** Full column rank makes A injective. If rank is deficient, choose nonzero d in ker A and normalize d^+,d^- as above. Their supports are disjoint, so TV(u,v)=1. Since rank(A)<=m+1, full rank implies m>=n-1. Conversely the n-1 singleton indicator probes, together with normalization, achieve rank n. QED.

The theorem does not assert that every observed fiber has diameter one. It asserts existence of a maximally ambiguous fiber for every deficient linear interface. Some individual fibers can be singletons even when A is deficient.

**Recovered special case.** Uniform laws on even- and odd-parity binary strings have the same every-proper-subset marginal and disjoint support. PLT §§753–755 already contains this construction and its q-ary extension. Its many local indicators lie in a proper subspace; sheer test count does not repair missing directions.

## 5. Theorem 3: controlled closure certificate — R131:CLOSURE

Fix a finite state set S, a surjective summary p:S -> Z, and a family of total Markov kernels K_a for declared operations a. Put mu_{s,a}=p_*K_a(s,·). Suppose rank(A)=n. Then the following are equivalent:

\[
p(s)=p(t)\Longrightarrow E_{\mu_{s,a}}f_i=E_{\mu_{t,a}}f_i
\quad\text{for every }s,t,a,i;
\]

\[
\exists\bar K_a:\quad p_*K_a(s,\cdot)=\bar K_a(p(s),\cdot)
\quad\text{for every }s,a.
\]

**Proof.** Probe agreement gives A mu_{s,a}=A mu_{t,a}, since both laws normalize. Theorem 2 gives equality of these laws. Define bar K_a at z using any representative in p^{-1}(z); this is well-defined. Conversely, a common law implies equality of all probe expectations. This is precisely N128:JOINT_CRITERION in a separating-test basis. QED.

The quantifier over all allowed operations matters: passive matching is not an intervention certificate. For partial operations, preservation of enabledness is an extra obligation; here operations are total. Exact closure supports abstract dynamics under policies depending on the abstract state/history. It does not certify the same controlled law under arbitrary hidden-state-dependent policies, identify full physical organization, transport biological interventions, or select a subject.

**Universal necessity — R131:BLIND_KERNEL.** Full rank is necessary for the test implication to hold for all such finite kernels. Given deficient A and the disjoint laws u,v from Theorem 2, use S=Z x {0,1}, p(z,b)=z and

\[
K_a((z,b),(z',b'))=\mathbf1\{b'=b\}\,u_b(z'),\qquad u_0=u,\ u_1=v,
\]

identically for every declared a. All next-probe expectations agree, even across all current states. But states (z,0),(z,1) have the same present summary and different, indeed disjoint, next-summary laws. Thus the summary is not closed on the full state domain. This does not mean rank deficiency prevents every particular model from closing: an identity or constant kernel can close with a deficient test family. Closure on a restricted reachable domain is a separate question.

## 6. Decision corollary — R131:DECISION_GAP

Let a fair hidden context b select u or v from Theorem 2. The observer receives only their identical probe vector before choosing one of two actions. Let H=supp(u), and fix action payoffs h_0=1_H and h_1=1_{Z\H}; the action does not change the outcome law in this construction. Both observers have the same action set and payoff table. A context-informed observer chooses 0 for b=0 and 1 for b=1 and earns expected payoff 1. Any probe-only observer, including a randomized one, earns 1/2. The exact value gap is 1/2.

**Proof.** With an action-0 probability r independent of hidden b, the average payoff is (r+(1-r))/2=1/2. Disjoint support gives the informed score 1. This instantiates C:P7 with no common optimal action across the two hidden contexts. QED.

The witness establishes possible decision loss under a specified missing payoff direction, prior and action interface. It is not a universal loss in all tasks, nor a new estimate of D's different 1/8 example. A probe suffices for a task if that task's relevant score information is preserved, even when it cannot identify the entire law.

## 7. Stability corollary — R131:ROBUST

Assume A has full column rank and fix a left inverse L, LA=I_n. Let B be L with its first column removed. If |E_mu f_i-E_nu f_i|<=epsilon for each i, then

\[
\operatorname{TV}(\mu,\nu)
\le \min\{1,\tfrac12\|B\|_{\infty\to1}\,\epsilon\}.
\]

**Proof.** With d=mu-nu, Ad=(0,r)^T and ||r||_infty<=epsilon. Thus d=LAd=Br, and TV=||d||_1/2. QED. A convenient conservative upper bound for this operator norm is the sum of absolute entries of B. For finite m its exact norm is the maximum of ||Bv||_1 over sign vectors v in {-1,1}^m.

Poor conditioning can make an exact certificate practically weak. Statistical confidence intervals require an independently justified sampling/error analysis; if each of two estimates has error at most eta, their true expectation difference is bounded by their observed difference plus 2 eta. No empirical confidence level is supplied here.

## 8. What follows for the four-paper program

The logical chain is now explicit: choose the target; establish its probe sufficiency; certify full transition-law separation if dynamics is the target; establish closure for every admitted operation; separately ground the states, time, ports and outputs in actual processes. A:C1-OI applies only after complete actual-organizational premises are independently warranted. These finite results do not discharge that last step, do not orient valence, and do not close T2 or intervention transport C3.

Recovered X05 concerns counterfactual channel repertoire versus one-use accessible information, not just linear probe rank. X21–X24 concern which interventions are actually in the family. X07 concerns time grain. These cannot all be renamed instances of one theorem without adding their own operational assumptions. The crosswalk deliberately records this limitation.

## 9. Prior art and verification scope

- C §5.2/§6.3/§7.3; D §4 and R96D; R126–R128 supply the project premises and special cases.
- Givan, Dean and Greig (2003), *Equivalence notions and model minimization in Markov decision processes*, DOI 10.1016/S0004-3702(02)00376-4: publisher abstract consulted; existing MDP equivalence/minimization literature.
- Li, Walsh and Littman (2006), *Towards a Unified Theory of State Abstraction for MDPs*: author-uploaded article consulted, particularly the distinctions between model, value and policy abstractions. Those distinctions are not claimed as a new hierarchy here.
- Abel et al. (2020), *Value Preserving State-Action Abstractions*, AISTATS/PMLR 108:1639–1650, https://proceedings.mlr.press/v108/abel20a.html: primary abstract consulted; previous value-preserving abstraction results.

The general statements above have explicit manual proofs. check_probe_theorems.py checks representative exact rational witnesses, the binary spanning repair, controlled nonclosure, the decision gap and the norm envelope. Finite checks do not prove the general theorems; no proof assistant or exhaustive historical-priority review was performed.
