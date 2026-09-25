# Set-Valued Causal Inheritance for Functional Self-Continuity
## Representation Theorems and Persistent-Agent Benchmarks

**Author:** Hongju Liu  
**Version:** Final Preprint Manuscript v1.0  
**Date:** 25 September 2026  
**Article type:** Theoretical / computational framework  
**Status:** Final preprint manuscript; theoretical/computational framework; not yet peer reviewed

---

## Abstract

Functional self-continuity is often modeled as if one present process must map to exactly one future process and as if each future candidate can be scored independently. These assumptions fail under copying, fission, fusion, distributed computation, and restoration. We develop a substrate-neutral computational framework in which current self-attribution, causal continuation, successor belief, post-branch self-location, and motivational stake are represented as distinct objects. The central temporal object is a set-valued inheritance function
\[
\Gamma_t:2^{\mathcal C_{t+\Delta}}\rightarrow[0,1],
\]
defined from an intervention channel on a minimally sufficient endogenous functional state.

The formal results establish several representation limits. Categorical successor variables cannot represent zero, one, and multiple successors without making sets themselves the state space; normalized successor-membership weights are incompatible with full co-successor preservation under fission; singleton successor marginals do not identify a successor-set distribution; and singleton inheritance scores do not identify joint inheritance. A secret-sharing construction yields \(\Gamma(B)=\Gamma(C)=0\) but \(\Gamma(\{B,C\})=1\). For successor-inclusion indicators \(X\), the KL-optimal independent-Bernoulli approximation incurs irreducible excess log loss equal to the total correlation \(TC(X)\). A matched-marginal construction further gives an unavoidable average decision regret of \(1/2\) for policies restricted to singleton successor marginals.

We also establish representation constraints on the causal measure itself. Exact mutual-information inheritance is invariant under bijective recoding when intervention semantics are transported with the recoding, whereas coordinate-aligned estimators need not be. An intervention-response quotient defines a task- and intervention-relative minimal endogenous control state (MECS), and shared upstream information is shown to be insufficient for current-process lineage unless the intervention is anchored after causal separation.

Controlled computational studies illustrate these results at increasing levels of realism: finite synthetic constructions, intervention-derived inheritance estimates, learned high-dimensional functional quotients, recurrent hidden-state quotients, reward-trained fork/restore/merge lineages, autonomous persistence-operation selection, and long-horizon persistence control. The recurrent lineage constructions are also repeated with three independently trained reward-driven GRUs and three independently trained merger networks. Absolute inheritance magnitudes vary with task learning quality, but the redundancy, complementarity, stale-restore, and merge structural signatures replicate in all three stacks. A six-seed contextual-bandit replication shows stable learning of all four tested persistence-operation classes, with mean regret 0.0085 (95% seed-level CI 0.0079 to 0.0091) and mean oracle-action agreement 81.6%. By contrast, an eight-seed replication of a process-aware versus context-only end-to-end recurrent control comparison does **not** confirm the earlier single-seed advantage: the mean paired return difference is -0.0011, with a 95% seed-level interval spanning zero. The computational evidence therefore supports learnability of persistence-operation selection in the controlled one-decision setting, while leaving a reliable process-aware advantage in end-to-end long-horizon recurrent control unestablished.

The framework is explicitly functional. It does not establish numerical personal identity, phenomenal consciousness, moral status, or legal identity. Its narrower aim is to make branching and distributed continuation precise enough to support falsifiable computational tests and persistence engineering.
---

# 1. Introduction

Questions about the self are often framed as classification:

> Which object is me?

That framing hides two distinct problems.

The first is **synchronic**:

> Which current bodies, actions, locations, tools, and internal states are treated by the system as belonging to itself?

The second is **diachronic**:

> Which future processes actually continue the present system's functional causal organization, and how should that continuation be represented when there are zero, one, or multiple future continuers?

For ordinary biological life, the answer to the second question is usually approximated by one physical lineage. This makes several stronger assumptions look harmless: that a present self has exactly one future successor; that successorhood can be represented by a probability distribution over individuals; that a future process's relation to the present can be summarized independently of other future processes; and that endpoint similarity is a useful proxy for continuation.

All four assumptions fail in deliberately constructed but technically coherent cases.

A present process can generate two full descendants. It can distribute complementary parts of its functional state across two future processes. It can encode its state so that no future component contains any information individually while a collection of components reconstructs the whole. A future process can be an endpoint-perfect reconstruction yet have no live causal dependence on the present. Conversely, an invertibly transformed descendant can be causally complete while having very low endpoint similarity.

The aim of this paper is not to decide whether a metaphysical person "really survives" such cases. Instead, it asks a computational question:

> What internal representation is required for an agent to reason coherently about current self-membership and future functional continuation under branching, merging, reconstruction, and distributed inheritance?

We propose that the answer requires a **set-valued** representation.

The central temporal object is not a normalized vector

\[
(q_1,\ldots,q_n),
\]

where each \(q_j\) is the degree to which one future process is "the self." It is a set function

\[
\Gamma_t(S)
\]

on subsets of future processes, together with a probability distribution

\[
\mu_t(R)
\]

over possible successor sets.

This distinction is not cosmetic. A vector of singleton scores cannot distinguish redundancy from complementarity or synergy. Singleton successor probabilities cannot distinguish "exactly one of B or C" from "B and C together or neither," even when those worlds demand opposite decisions.

## 1.1 Contributions

The paper makes five grouped contributions.

### Contribution I — A layered representation of functional self-continuity

We distinguish six objects that are commonly conflated:

\[
M_t,\quad Z_t,\quad \Gamma_t,\quad \mu_t,\quad P_{\rm loc},\quad \Omega_t,
\]

representing current multi-source self-membership, a minimal endogenous functional state, objective set-valued causal inheritance, successor-set belief, post-branch self-location, and motivational stake. The temporal inheritance object is a monotone set function

\[
\Gamma_t:2^{\mathcal C_{t+\Delta}}\rightarrow[0,1],
\]

rather than a normalized score over mutually exclusive future individuals.

### Contribution II — Representation theorems and exact decision bounds

We give formal counterexamples and no-go results showing that categorical, normalized-singleton, and marginal-only successor representations are structurally insufficient under branching. We derive:

\[
\min_{q\in\mathcal Q_{\rm indep}}
D_{\rm KL}(\mu\|q)
=
TC(X),
\]

and a matched-marginal decision construction in which a marginal-only policy incurs unavoidable average regret \(1/2\). A Möbius transform provides an exact algebraic signature of non-additive inheritance, distinguishing redundancy, additive complementarity, and positive joint interaction.

### Contribution III — Representation-invariant and current-process-grounded inheritance

We prove that exact mutual-information inheritance is invariant under bijective re-encoding when intervention semantics are transported with the representation, and that the MECS quotient is isomorphic under pure relabeling. We also prove two identification limits: incomplete intervention families cannot identify distinctions visible only under unobserved interventions, and mutual information with a shared upstream cause does not establish descent from the current process. Readout-level inheritance is shown to be a lower bound on inheritance into the underlying future state.

### Contribution IV — Controlled computational stress tests

A sequence of controlled studies tests specific pieces of the framework: matched-marginal successor distributions, similarity-versus-lineage OOD shifts, intervention-derived \(\hat\Gamma(S)\), recoding invariance, exact and learned MECS quotients, and frozen recurrent hidden states augmented with behaviorally null implementation state. These experiments are designed as constructive stress tests and consistency checks, not as evidence about human phenomenology.

### Contribution V — Persistent-agent lineage and control

Using reward-trained recurrent processes, we implement fork timing, stale restore, complementary distribution, learned merge, and post-separation interventions. The core lineage construction is replicated across three independently trained GRU-plus-merger stacks: absolute inheritance magnitude varies, but full-fork redundancy, redundant-half saturation, complementary additivity, zero stale-restore inheritance, and merger recovery replicate structurally. We then study persistence-operation choice under stochastic risk and cost, including contextual-bandit feedback and a twelve-step persistence MDP. The contextual-bandit controller is replicated across six independent controller-training seeds and consistently learns nonzero use of KEEP, FORK, RESTORE, and SPLIT+MERGE. An end-to-end recurrent pilot carries actual GRU states through repeated persistence operations; however, an eight-seed controller-level replication does not confirm a reliable process-aware return advantage over a matched context-only controller.

# 2. Scope and Non-Claims

## 2.1 Functional rather than phenomenal selfhood

Let \(E\) denote phenomenal experience. Nothing here establishes

\[
\text{functional self-continuity}
\Rightarrow
E.
\]

The framework therefore does not identify consciousness with causal continuation, information flow, self-modeling, or set-valued inheritance.

This restriction matters because some recent theories make stronger claims linking subjecthood or consciousness to structural self-organization, origin-tracking, liability closure, or cross-domain settlement. Those may be compatible or incompatible with the present framework; they are not assumed.

## 2.2 Operational succession rather than numerical identity

The paper uses *successor* operationally.

A future process can be a strong causal successor without the paper asserting:

\[
A=B
\]

in the metaphysical sense of numerical identity.

Classical fission cases already show that causal/psychological continuation and numerical identity need not behave alike. The present framework analyzes the former.

## 2.3 Explicit task-family relativity

A compressed internal state cannot be nontrivially sufficient for every conceivable future consumer.

Therefore all claims about "minimal endogenous functional state" are relative to:

1. a declared family of endogenous outputs;
2. a declared intervention/input family.

The theory does not smuggle in a task-free metaphysical essence.

---


## 2.4 Evidence hierarchy and experimental scope

The manuscript uses several kinds of evidence that should not be treated as interchangeable.

1. **Exact formal results.** Theorems, propositions, corollaries, and analytical constructions follow from the stated definitions.
2. **Constructive synthetic examples.** These establish representational possibility or impossibility under known ground truth.
3. **Oracle-proxy sufficiency checks.** Some early models receive noisy features constructed from known set-level causal quantities. Their purpose is to test whether a representation can use the required information, not whether that information can be discovered from raw data.
4. **Intervention-derived synthetic estimates.** Later experiments estimate \(\Gamma(S)\) from randomized trajectories rather than receiving it as a feature.
5. **Learned recurrent demonstrations.** These use frozen or reward-trained recurrent processes and predictive bottlenecks, but remain small controlled systems. The core reward-driven lineage construction is replicated across three independently trained recurrent-agent/merger stacks.
6. **Learned control with seed-level replication.** The one-decision contextual-bandit controller is replicated across six training seeds. The end-to-end recurrent long-horizon comparison is replicated across eight controller-training seeds with the base recurrent agent held fixed; that replication does not confirm the earlier positive process-aware advantage. Full-stack replication across independently trained recurrent agents remains future work; the current eight-seed end-to-end analysis varies controller training only.

Accordingly, the computational sections support internal consistency, constructiveness, and engineering plausibility. They do not establish external validity for biological identity, human phenomenology, or deployed large-scale agents.

---

# 3. Related Work and Novelty Boundary

## 3.1 Dynamic, patterned, and predictive selves

Dynamic and multi-component accounts of selfhood are well established. Gallagher's Pattern Theory (2013) treats selfhood as a pattern involving embodied, experiential, affective, cognitive, narrative, extended, and situated aspects. Predictive-processing accounts by Limanowski and Blankenburg (2013) and Apps and Tsakiris (2014) model minimal or bodily selfhood using hierarchical predictive inference.

Accordingly, this paper does **not** claim novelty for the ideas that selfhood is dynamic, embodied, probabilistic, or multi-aspect.

## 3.2 Multiple first-person channels

Cox's 2026 defense of **de se pluralism** explicitly argues that a person may possess more than one distinctively first-personal concept. Sawyer's 2026 structural account of subject individuation emphasizes origin-tracking rather than a substantial ego.

Thus, the existence of multiple first-person channels is not our primary novelty.

## 3.3 Bodily self-attribution

Agency, ownership, perspective, and self-location can dissociate. Recent VR work by Liang et al. (2025) reports a Double Body Effect in which healthy participants can experience double body ownership and double body-location.

This motivates a non-exclusive current membership representation but does not by itself establish our temporal theory.

## 3.4 Personal identity, fission, and causal succession

Fission is a classical problem in personal-identity philosophy (Olson, current SEP edition; Ehring, 2021). Otsuka (2018) distinguishes a post-fission successor from a mere replica. Keller's Structural Identity Theory (2026, SSRN preprint) explicitly models diachronic persistence as causal succession. Khadangi's 2026 Causal Liability Theory further emphasizes experimentally distinguishable live causal continuation versus detached reconstruction.

Therefore:

- branching is not new;
- causal continuity over endpoint similarity is not new;
- live continuation versus reconstruction is not new.

Our formal target is narrower:

> **how self-relevant causal structure can be inherited non-additively by sets of future processes, and what representational consequences follow.**


## 3.5 Branch-aware AI identity and explicit successor sets

A particularly close 2026 gray-literature research corpus by Neo.K and Aletheia develops a **branch-aware operational identity framework** for artificial systems. It explicitly distinguishes copy, fork, restore, and merge; represents identity history as a causal-lineage graph rather than a linear chain; and defines a genuine successor set

\[
Succ(P)=\{A,B,\ldots\}
\]

without identifying every successor numerically with the predecessor. It further introduces multidomain coupling, differentiation, self-appropriation, operational regimes, composite successors, and the distinction between reintegration and retroactive unity.

This is important prior art for the present paper. We therefore do **not** claim novelty for:

- the term or basic idea of a successor set;
- branch-aware causal-lineage graphs;
- copy/fork/restore/merge distinctions;
- one-to-many or many-to-one operational succession;
- the idea that operational identity need not coincide with phenomenal identity.

The narrower target here is the **internal causal-information structure of a given successor set**. Specifically, the present paper asks how much of a minimally defined present functional state is inherited by each **subset** of future processes, and proves that this inheritance is generally non-additive. It then derives exact probabilistic and decision-theoretic penalties for throwing away successor dependence.

The public branch-aware identity corpus does not, in the material reviewed for this draft, define an interventional set function

\[
\Gamma(S),
\]

distinguish redundant/complementary/synergistic inheritance using set-level information, derive a total-correlation lower bound for independent successor representations, or formulate the matched-marginal regret theorem developed below.

Because this prior work is recent, public, and not necessarily peer reviewed, it is treated here as relevant gray literature rather than omitted from the novelty analysis.


## 3.6 Minimal sufficient states

Computational mechanics defines causal states as minimal sufficient statistics of history for prediction (Shalizi & Crutchfield, 2001). \(\epsilon\)-transducers extend related machinery to input-output processes (Barnett & Crutchfield, 2015). Predictive-state representations, bisimulation, state abstraction, and minimal realization supply neighboring formalisms.

We use this mature idea only to avoid arbitrarily selecting a raw hidden vector as "the self."

## 3.7 Random finite sets

Random finite sets provide a mature mathematical framework for distributions over sets with unknown cardinality (Da et al., 2021). We borrow this representation for successor-set beliefs.

## 3.8 Total correlation

Watanabe's (1960) total correlation is

\[
TC(X_1,\ldots,X_n)
=
\sum_i H(X_i)-H(X_1,\ldots,X_n)
\]

and equivalently

\[
TC(X)
=
D_{\mathrm{KL}}
\left(
p(X)
\middle\|
\prod_i p(X_i)
\right).
\]

We use this established quantity to derive the exact representational penalty of an independent successor model.

## 3.9 Non-additive set functions and Möbius interaction

Möbius representations of set functions, capacities, and cooperative games are standard mathematical tools (Grabisch & Roubens, 1999; Grabisch, 2016). We borrow this machinery to characterize exact non-additivity in causal inheritance.

This is preferable to treating "redundancy" and "synergy" as purely verbal labels.


## 3.10 Causal representation learning and intervention-limited identifiability

The learned-MECS problem is closely related to modern causal representation learning (CRL).

Li, Kaba, and Ravanbakhsh (2025) study causal abstraction identifiability when interventions may target arbitrary subsets of latent variables, explicitly characterizing the level of abstraction identifiable under a given intervention family. Varici et al. (2025) establish identifiability and achievability results for causal representations under linear and general nonlinear transformations using interventional environments. Baumgartner et al. (2026) derive causal-representation identifiability results for dynamical systems and empirically recover disentangled system-parameter representations. Nejatbakhsh and Wang (2025) develop interventional state-space models that predict neural dynamics under novel perturbations.

These results sharply constrain the novelty claim of the present section.

We do **not** claim that intervention-based recovery of latent causal states is new.

Instead, causal-representation learning supplies a neighboring algorithmic literature for approximating the quotient state required by the inheritance framework.

The specific question here is narrower:

> Can a low-dimensional representation trained only for endogenous future sufficiency discard implementation nuisance and remain stable across reversible raw-state recodings strongly enough to serve as the reference state for set-valued self-continuity analysis?



## 3.11 Recurrent hidden-state geometry and intervention validity

Recent work makes the recurrent-state novelty boundary particularly important.

Leeftink, Hinne, and van Gerven (2026) analyze hidden states in recurrent reinforcement-learning policies and connect their latent dynamics to Pontryagin co-states, showing that recurrent state can be structured in a control-theoretic manner under partial observability.

Chen and Liu (2026) study **intervention-relevant geometry in recurrent world models**. They report compact low-rank intervention structure embedded in high-dimensional recurrent dynamics, while emphasizing that the effective intervention subspace moves with state and should not be interpreted as one fixed, dynamically closed low-dimensional state.

Grant et al. (ICLR 2026) show that direct causal interventions on neural representations can create divergent out-of-distribution internal states. They distinguish behaviorally harmless null-space divergence from pernicious divergence that activates otherwise dormant pathways.

These results constrain the present paper in three ways.

First, the existence of compact functionally relevant structure inside a high-dimensional recurrent network is not claimed as new.

Second, the MECS concept should not be interpreted as asserting that a recurrent system possesses one fixed linear subspace that contains its whole functional identity.

Third, causal probes should, where possible, operate through intervention channels that are part of the model's natural input/action interface rather than by arbitrarily writing hidden-state vectors.

For this reason, the recurrent benchmark below freezes the trained GRU and evaluates standardized **input/action-channel probes** that the architecture encountered during training. The MECS learner is trained on snapshots and future response signatures; it does not patch arbitrary directions into the GRU hidden state.



## 3.12 Persistent-agent continuity and execution lineage

Persistent-agent engineering has become a direct neighboring literature.

Zhao and Zhao (2026) propose a runtime-independent persistent-agent architecture in which a continuity-bearing substrate containing identity, memory, and executable body state can migrate across replaceable reasoners, harnesses, interaction surfaces, and host servers. Their continuation protocol explicitly uses quiesce, checkpoint, validate, bind, rehydrate, and resume operations, and treats controlled migration as continuity rather than agent recreation when lineage and continuation authority are preserved.

Rosen and Rosen (2026) develop execution lineage for AI-native work as a deterministic artifact dependency graph. Their focus is reproducibility and propagation of updates rather than self-continuity, but the work reinforces a key distinction of this paper: final-state similarity and maintained causal history are not the same object.

These systems are important prior art for:

- checkpoint/restore as an engineering operation;
- persistent identity across runtime substitution;
- explicit execution lineage;
- controlled migration and rehydration.

The present paper therefore does **not** claim novelty for persistence protocols, checkpoint semantics, or lineage tracking as such. Its narrower contribution is to characterize the **non-additive causal information inherited by sets of successor processes** and to separate that structure from both identity labels and endpoint similarity.



## 3.13 Safe checkpoint, fork, restore, and merge operations

Zheng et al. (2026) introduce **execution edits** for agent runtimes and provide an exact checker for when Checkpoint, Fork, Restore, and Merge are safe with respect to still-required results, prior authorizations, and irreversible actions. Their finite checker is mechanically verified in Lean and covers six edit forms.

Crab and DeltaBox independently address runtime support for checkpoint/restore in stateful AI-agent sandboxes, focusing on semantic recovery correctness and low-latency state branching/rollback.

These works substantially narrow the systems novelty of the present benchmark.

We therefore do **not** claim novelty for:

- the existence of Checkpoint/Fork/Restore/Merge as agent-runtime operations;
- the need for exact safety conditions around edits;
- efficient stateful checkpoint/rollback infrastructure.

The present question is different:

> given operations that are already admissible and safe to execute, which operation should a persistent agent choose when its objective depends on future functional inheritance, failure risk, stale-state loss, and operation cost?

Execution-edit safety and inheritance-aware operation selection are complementary problems. A safe edit can still be a poor continuity decision, and a continuity-preserving edit can still be unsafe if it violates external authorization or tool-effect constraints.



## 3.14 Long-horizon branching, checkpoint handoff, and continuity control

Several 2026 systems and RL papers make checkpointing and branching first-class objects for long-horizon agents.

He et al. introduce **Branching Policy Optimization (BPO)**, which exploits deterministic, snapshottable sandboxes to fork alternative actions from high-entropy intermediate states. The goal is lower-variance policy optimization and more efficient agent training, not preservation of one persistent process's future functional continuity.

Liu and Qian introduce **checkpoint handoff** to separate REACH from SOLVE in agentic RL. One checkpoint produces a state/history and another solver continues from the cloned state. This directly reinforces the methodological importance of comparing solvers from matched states rather than attributing endpoint success to one undifferentiated source.

He and Yu propose a **Transactional Continuity Kernel** for long-lived agents. Their control plane defines continuity as an authorized lineage of accepted branch heads and revalidates ownership, freshness, effect uniqueness, and predecessor authority before activating state updates.

Together with execution-edit safety work, these papers make three novelty boundaries explicit.

The present paper does **not** claim novelty for:

- using sandbox snapshots or branches in RL;
- checkpoint handoff as an evaluation method;
- authoritative branch-head governance;
- checkpoint/fork/restore/merge as long-horizon systems primitives.

The narrower question is:

> how should an agent value and choose persistence operations when those operations change future functional inheritance, failure exposure, checkpoint staleness, and later persistence options?

The long-horizon persistence experiments summarized in Section 11 are deliberately controlled benchmarks for that decision problem.


## 3.15 Partial Information Decomposition

PID formalizes redundant, unique, and synergistic information. However, multivariate PID remains non-unique, and recent 2026 work proves substantial consistency difficulties for broad classes of multivariate constructions.

For this reason, the core theorems here do not depend on a particular PID.

---

# 4. Formal Setup

## 4.1 Histories and endogenous outputs

Consider a stochastic controlled system with history

\[
H_t=(O_{\le t},A_{<t},X_{\le t}),
\]

where:

- \(O_t\): observations;
- \(A_t\): actions;
- \(X_t\): internal implementation state.

Let \(\mathcal I\) be a declared family of admissible future interventions/input policies.

Let

\[
Y^{\mathrm{endo}}_{t:\infty}
\]

be a declared family of endogenous future outputs, which can include:

- actions;
- policy outputs;
- learning/model updates;
- memory writes;
- control-state transitions;
- self-attribution readouts.

The choice must be reported.

## 4.2 Minimal Endogenous Control State

Define

\[
h\sim_{\mathcal I}h'
\]

iff for every admissible \(\iota\in\mathcal I\),

\[
P\left(
Y^{\mathrm{endo}}_{t:\infty}
\mid H_t=h,do(\iota)
\right)
=
P\left(
Y^{\mathrm{endo}}_{t:\infty}
\mid H_t=h',do(\iota)
\right).
\]

Then define:

\[
\boxed{
Z_t=[H_t]_{\sim_{\mathcal I}}.
}
\]

We call \(Z_t\) the **Minimal Endogenous Control State (MECS)**.

The name is application-specific; the mathematical principle is inherited from minimal sufficient causal-state and realization frameworks.

### Representation desideratum

If two encodings of \(Z_t\) differ only by a bijective reparameterization, the continuation analysis should not change merely because coordinate labels changed.

## 4.3 Current self-membership field

Let \(\mathcal D_t\) be a set of current self-attribution domains, such as:

- ownership;
- agency;
- self-location;
- perspective;
- interoceptive source attribution.

Let \(\mathcal S_t\) be candidate current sources.

Define:

\[
\boxed{
M_t=[m_{i,s}(t)].
}
\]

No exclusivity is assumed:

\[
\sum_s m_{i,s}
\]

need not equal 1.

This allows double-body and supernumerary-source cases.

We treat:

\[
M_t=g(Z_t,E_t)
\]

as a readout rather than defining \(Z_t\) through \(M_t\).

## 4.4 Future candidate processes

At time \(t+\Delta\), let

\[
\mathcal C=\{c_1,\ldots,c_n\}
\]

be the finite set of candidate future processes.

For

\[
S\subseteq\mathcal C,
\]

let \(Y_S\) denote their joint future state or declared endogenous readout.

## 4.5 Interventional inheritance channel

Let \(U\) be a randomized intervention variable applied to admissible degrees of freedom of \(Z_t\).

Define:

\[
\boxed{
\mathcal K_{t\rightarrow S}:
do(U=u)\mapsto P(Y_S\mid do(U=u)).
}
\]

The channel is the primary causal object.

For a fixed finite intervention distribution:

\[
\boxed{
\Gamma_t(S)
=
\frac{
I(U;Y_S\mid do(U))
}{
H(U)
}
}
\]

when \(H(U)>0\).

Thus:

\[
0\le \Gamma_t(S)\le1.
\]

We define:

\[
\Gamma_t(\varnothing)=0.
\]

---

# 5. Basic Properties of the Inheritance Set Function

## Proposition 1 — Monotonicity

If

\[
S\subseteq T,
\]

then

\[
\boxed{
\Gamma(S)\le\Gamma(T).
}
\]

### Proof

\(Y_S\) is a projection of \(Y_T\), so

\[
U\rightarrow Y_T\rightarrow Y_S.
\]

By the data-processing inequality:

\[
I(U;Y_S)\le I(U;Y_T).
\]

Dividing by the common positive \(H(U)\) proves the result. \(\square\)


Thus \(\Gamma\) is a bounded monotone set function.

It is not generally additive.

## 5.2 Bijective Re-encoding Invariance

A basic requirement for a substrate-neutral continuity measure is that it should not change merely because the same functional state is written in a different reversible code.

### Theorem 1 — Invariance of exact inheritance under bijective recoding

Let:

\[
U' = f(U)
\]

and:

\[
Y'_S = g_S(Y_S),
\]

where \(f\) and \(g_S\) are bijections. Then:

\[
\boxed{
I(U;Y_S)=I(U';Y'_S).
}
\]

Therefore, for the same intervention distribution transported through \(f\),

\[
\boxed{
\Gamma(S)
=
\frac{I(U;Y_S)}{H(U)}
=
\frac{I(U';Y'_S)}{H(U')}.
}
\]

### Proof

Because \(f\) is bijective:

\[
H(f(U))=H(U).
\]

Because \(g_S\) is bijective:

\[
H(g_S(Y_S))=H(Y_S).
\]

The joint transformation:

\[
(U,Y_S)\mapsto(f(U),g_S(Y_S))
\]

is also bijective, so:

\[
H(f(U),g_S(Y_S))
=
H(U,Y_S).
\]

Hence:

\[
I(f(U);g_S(Y_S))
=
H(f(U))+H(g_S(Y_S))
-
H(f(U),g_S(Y_S))
=
I(U;Y_S).
\]

The normalization denominator is also preserved. \(\square\)

### Corollary 1 — Invariance of the inheritance interaction structure

If every candidate future process \(c_j\in S\) is independently bijectively recoded, the product mapping on the joint state \(Y_S\) is itself bijective. Therefore all set values:

\[
\Gamma(S)
\]

and all Möbius interaction coefficients computed from them are invariant.

### Important qualification: intervention semantics must also be preserved

This theorem does **not** imply that arbitrary coordinate interventions after recoding are equivalent to the original interventions.

If a representation is transformed by:

\[
Z'=f(Z),
\]

then the corresponding intervention family must be transported through \(f\). Flipping "bit 1" in \(Z'\) is not generally the same physical intervention as flipping "bit 1" in \(Z\).

Thus the invariant object is the **interventional channel up to isomorphism**, not a coordinate-wise intervention convention.

## 5.3 MECS Quotient Isomorphism

The same principle applies to the minimally sufficient endogenous state.

Let \(\rho\) be a bijective relabeling of raw implementation histories. Define the recoded system so that physical interventions and endogenous future outputs are unchanged except for the representation labels.

### Proposition 2 — Quotient-state invariance

If:

\[
h\sim_{\mathcal I} h'
\]

iff the two histories generate the same distributions over all declared endogenous future outputs under every admissible intervention, then:

\[
\boxed{
h\sim_{\mathcal I}h'
\iff
\rho(h)\sim'_{\mathcal I}\rho(h').
}
\]

Therefore the two quotient spaces are isomorphic:

\[
\boxed{
\mathcal H/\!\sim_{\mathcal I}
\cong
\rho(\mathcal H)/\!\sim'_{\mathcal I}.
}
\]

### Proof

A bijective relabeling changes only the representation of the histories. By construction, the distributions of declared endogenous future outputs under corresponding physical interventions are unchanged. Therefore equality of those distributions before recoding is equivalent to equality after recoding. Equivalence classes are carried one-to-one by \(\rho\). \(\square\)

### Corollary 2 — Pure nuisance dimensions collapse

Suppose raw state is:

\[
X=(Z,N),
\]

and for all admissible interventions and all values \(n,n'\):

\[
P(Y^{endo}_{future}\mid Z=z,N=n,do(\iota))
=
P(Y^{endo}_{future}\mid Z=z,N=n',do(\iota)).
\]

Then all states differing only in \(N\) belong to the same MECS equivalence class.

This makes the quotient a principled way to discard implementation variables that do not affect the declared endogenous future behavior.


## 5.4 Intervention-Family Identifiability Limit

The quotient depends on the intervention family.

Let:

\[
\mathcal I_{\rm train}
\subset
\mathcal I_{\rm full}.
\]

Suppose two histories \(h,h'\) satisfy:

\[
P(Y^{endo}_{future}\mid h,do(\iota))
=
P(Y^{endo}_{future}\mid h',do(\iota))
\]

for every:

\[
\iota\in\mathcal I_{\rm train},
\]

but differ for at least one:

\[
\iota^*\in
\mathcal I_{\rm full}\setminus\mathcal I_{\rm train}.
\]

### Proposition 3 — Unobserved-intervention non-identifiability

No learner whose data contain only interventions from:

\[
\mathcal I_{\rm train}
\]

can, without additional structural assumptions, identify whether \(h\) and \(h'\) belong to the same quotient class under:

\[
\mathcal I_{\rm full}.
\]

### Proof

By assumption, the full data-generating distributions available under every intervention in the training family are identical for \(h\) and \(h'\). Therefore any statistic computed solely from those distributions has the same law under both hypotheses. The hypotheses differ only under an unobserved intervention. Distinguishing them therefore requires either data outside \(\mathcal I_{\rm train}\) or additional assumptions linking observed and unobserved interventions. \(\square\)

This simple limitation is consistent with the broader causal-representation-learning literature: incomplete intervention coverage identifies only the distinctions supported by the available intervention family or by additional structural assumptions.


## 5.5 Endogenous Quotient Need Not Recover the Exogenous World State

The MECS is defined by equivalence of **endogenous future responses**, not by equality of external latent world states.

### Corollary 3 — Exogenous-state non-identification can be correct

Suppose two histories \(h,h'\) correspond to different external environment states:

\[
s(h)\neq s(h'),
\]

but for every admissible intervention:

\[
P(Y^{endo}_{future}\mid h,do(\iota))
=
P(Y^{endo}_{future}\mid h',do(\iota)).
\]

Then:

\[
[h]_{\sim_{\mathcal I}}
=
[h']_{\sim_{\mathcal I}}.
\]

### Interpretation

A functional quotient may intentionally merge externally different worlds when the agent itself does not distinguish them in any future endogenous behavior available under the declared intervention family.

Therefore:

\[
\text{MECS recovery}
\neq
\text{omniscient world-state reconstruction}.
\]

In a partially observable agent, high accuracy for the system's own future-response classes can coexist with substantially lower accuracy for the true environment state without contradiction.




---


## 5.6 Current-Process Intervention Criterion

Information about a common ancestor or common upstream input does not by itself establish continuation from the current process.

Consider three variables:

\[
U\rightarrow A_t,
\]

\[
U\rightarrow C_{t+\Delta},
\]

where \(C\) is reconstructed independently from the same upstream source \(U\), but:

\[
A_t\nrightarrow C_{t+\Delta}.
\]

Then it is possible that:

\[
I(U;C_{t+\Delta})>0
\]

even though an intervention on the current process has no effect on \(C\):

\[
P(C_{t+\Delta}\mid do(A_t=a))
=
P(C_{t+\Delta}).
\]

### Proposition 4 — Upstream-information insufficiency

A positive value of:

\[
I(U;Y)
\]

cannot, in general, establish that \(Y\) is a causal successor of the current process \(A_t\) if \(U\) is an upstream common cause of both.

### Proof by construction

Let \(U\) be a fair bit. Set:

\[
A_t=U,
\]

and independently reconstruct:

\[
C_{t+\Delta}=U
\]

from a stored upstream record of \(U\), with no causal edge from \(A_t\) to \(C\).

Then:

\[
I(U;C)=H(U)=1.
\]

However, intervening on the current process after the record has been stored:

\[
do(A_t=0)
\]

or:

\[
do(A_t=1)
\]

does not change \(C\). Hence the current process has zero causal effect on the reconstruction despite perfect upstream mutual information. \(\square\)

### Operational requirement

For lineage inference, the intervention variable should be:

1. an intervention directly on the current MECS state; or
2. an input/action intervention applied **after potential competing branches or stored reconstructions have become causally separated**; or
3. another intervention channel demonstrated to be interventionally equivalent to (1).

This condition distinguishes:

\[
\boxed{\text{current-process inheritance}}
\]

from:

\[
\boxed{\text{shared ancestry / common-source correlation}}.
\]



## 5.7 Observable-Readout Inheritance Is a Lower Bound

In practical systems, the complete future internal state may be inaccessible. One may instead observe a downstream readout:

\[
O_S = g(Y_S),
\]

where \(Y_S\) is the future internal state of successor set \(S\).

### Corollary 4 — Readout lower bound

For any deterministic or stochastic readout channel:

\[
U\rightarrow Y_S\rightarrow O_S,
\]

the data-processing inequality gives:

\[
\boxed{
I(U;O_S)
\le
I(U;Y_S).
}
\]

Therefore:

\[
\boxed{
\Gamma^{\rm readout}(S)
\le
\Gamma^{\rm state}(S)
}
\]

when both are normalized by the same \(H(U)\).

### Interpretation

A low inheritance score measured at a policy output does not imply that the future hidden state contains only that fraction of the current functional information.

It means only that at least that much intervention information remains visible at the selected readout.

This is especially important for the reward-driven recurrent benchmark, where the future observation is the policy's next four-bit decision rather than the full GRU hidden state.



## 5.8 Persistence Actions as a Sequential Control Problem

The preceding inheritance quantities describe functional continuation. They do not by themselves specify which persistence operation should be chosen.

Let:

\[
s_t
\]

be an operational persistence state containing any task-relevant summary of:

- live functional quality;
- checkpoint quality/freshness;
- current branch/distribution mode;
- failure risk;
- innovation opportunity;
- resource or operation cost.

Let:

\[
a_t\in\mathcal A(s_t)
\]

be an admissible persistence edit such as KEEP, CHECKPOINT, FORK, RESTORE, SPLIT, or MERGE.

A finite-horizon planner optimizes:

\[
V_t(s)
=
\max_{a\in\mathcal A(s)}
E\left[
r(s,a,S')
+
\gamma V_{t+1}(S')
\right].
\]

This is standard Bellman control rather than a new result.

The framework uses two restricted-value diagnostics.

### Branch option value

Let:

\[
V_t^{*}
\]

be the optimal value with the full persistence action set and:

\[
V_t^{\rm no\mbox{-}branch}
\]

the optimal value when branch-producing operations are removed.

Define:

\[
\boxed{
\Delta_{\rm branch}(s,t)
=
V_t^{*}(s)
-
V_t^{\rm no\mbox{-}branch}(s).
}
\]

### Split/merge option value

Similarly:

\[
\boxed{
\Delta_{\rm split}(s,t)
=
V_t^{*}(s)
-
V_t^{\rm no\mbox{-}split}(s).
}
\]

These quantities are operational option values, not measures of identity.

They answer a narrower engineering question:

> how much expected future task value is lost if a persistence architecture cannot represent or execute a class of continuation operations?

A one-step myopic policy is sufficient only when action-dependent continuation value is irrelevant. Whenever persistence edits change future risk, checkpoint freshness, or future operation availability, the continuation term can change the optimal action.


# 6. Representation Impossibility Results

## Proposition 5 — Categorical Successor Impossibility

A categorical successor variable over candidate individuals cannot represent all cases with zero, one, and multiple successors.

### Proof

A categorical variable returns one label. It cannot return \(\varnothing\) or a set of cardinality \(>1\). Adding a "none" label handles zero successors but not multiple successors. Full representation requires subsets themselves to belong to the state space. \(\square\)

---

## Proposition 6 — Normalization Incompatibility under Fission

No scalar successor-membership relation \(q(A,c)\) can simultaneously satisfy:

1. full unique continuation gives \(q(A,B)=1\);
2. adding an equally full co-successor does not weaken the original relation;
3. \(\sum_c q(A,c)=1\).

### Proof

Start with:

\[
A\to B,\qquad q(A,B)=1.
\]

Add an equally full \(C\).

By co-successor invariance:

\[
q(A,B)=1.
\]

By symmetry:

\[
q(A,C)=1.
\]

Therefore:

\[
\sum_cq(A,c)\ge2,
\]

contradicting normalization. \(\square\)

---

## Proposition 7 — Singleton Successor Marginals Are Not Identifying

There exist different successor-set distributions with identical singleton inclusion probabilities.

### Construction

Let candidates be \(\{B,C\}\).

Exclusive uncertainty:

\[
\mu_E(\{B\})=\tfrac12,\qquad
\mu_E(\{C\})=\tfrac12.
\]

Joint-or-empty uncertainty:

\[
\mu_J(\{B,C\})=\tfrac12,\qquad
\mu_J(\varnothing)=\tfrac12.
\]

Both satisfy:

\[
P(B\in R)=P(C\in R)=\tfrac12.
\]

Yet:

\[
\mu_E\neq\mu_J.
\]

\(\square\)

---

## Proposition 8 — Singleton Inheritance Scores Are Not Identifying

There are inheritance structures with identical singleton scores and different joint inheritance.

Let:

\[
U=(U_1,U_2)
\]

with independent fair bits.

### Redundant half-copy

\[
B=U_1,\qquad C=U_1.
\]

Then:

\[
\Gamma(B)=\Gamma(C)=\tfrac12
\]

and:

\[
\Gamma(B,C)=\tfrac12.
\]

### Complementary split

\[
B=U_1,\qquad C=U_2.
\]

Again:

\[
\Gamma(B)=\Gamma(C)=\tfrac12,
\]

but now:

\[
\Gamma(B,C)=1.
\]

Thus singleton inheritance scores do not identify the set function. \(\square\)

---

## Proposition 9 — Purely Synergistic Continuation Exists

There exists a continuation for which:

\[
\Gamma(B)=\Gamma(C)=0
\]

but:

\[
\Gamma(B,C)=1.
\]

### Proof

Let \(U\) and \(R\) be independent fair bit strings of equal length.

Set:

\[
B=R,
\qquad
C=U\oplus R.
\]

One-time-pad masking gives:

\[
I(U;B)=I(U;C)=0.
\]

But:

\[
U=B\oplus C,
\]

so:

\[
I(U;B,C)=H(U).
\]

Therefore:

\[
\Gamma(B)=\Gamma(C)=0,
\qquad
\Gamma(B,C)=1.
\]

\(\square\)

---

## Proposition 10 — Inheritance Is Not Conserved Mass

For full redundant copying:

\[
B=U,\qquad C=U.
\]

Then:

\[
\boxed{
\Gamma(B)=\Gamma(C)=\Gamma(B,C)=1.
}
\]

Hence:

\[
\Gamma(B)+\Gamma(C)=2.
\]

Inheritance can be replicated and should not be treated as a conserved unit that must be divided across successors.

---

## Proposition 11 — Closed-Lineage Data-Processing Bound

If:

\[
U_A\rightarrow Z_B\rightarrow Z_C
\]

forms a closed Markov lineage with no ancestor side channel, backup reinjection, or branch merge, then:

\[
\boxed{
I(U_A;Z_C)\le I(U_A;Z_B).
}
\]

A measured increase implies that at least one closed-lineage assumption is false.

---

## Proposition 12 — No Universal Nontrivial Task-Free Basis

A non-injective state abstraction cannot be sufficient for every conceivable future consumer.

### Proof

Let \(\phi(x_1)=\phi(x_2)\) for \(x_1\neq x_2\).

Construct a consumer whose reward depends on distinguishing exactly \(x_1\) from \(x_2\).

Then \(\phi\) is insufficient for that consumer. \(\square\)

Therefore a nontrivial compressed endogenous state must be defined relative to an explicit output/intervention family.

---

# 7. Exact Information-Theoretic Cost of an Independent Successor Model

A natural baseline represents future successor membership independently.

Let:

\[
X=(X_1,\ldots,X_n)\in\{0,1\}^n
\]

be the successor-inclusion indicator vector induced by the true successor-set distribution \(\mu\).

An independent-Bernoulli model has:

\[
q(x)=\prod_{i=1}^nq_i(x_i).
\]

## Theorem 2 — KL-Optimal Independent Approximation

The KL-optimal independent approximation is the product of the true singleton marginals:

\[
\boxed{
q^*(x)
=
\prod_i\mu_i(x_i).
}
\]

The minimum irreducible KL divergence is:

\[
\boxed{
\min_{q\in\mathcal Q_{\rm indep}}
D_{\mathrm{KL}}(\mu\|q)
=
TC(X),
}
\]

where:

\[
TC(X)
=
\sum_iH(X_i)-H(X).
\]

### Proof

For any factorized \(q\):

\[
D_{\mathrm{KL}}(\mu\|q)
=
-H(\mu)
-
E_\mu\left[\sum_i\log q_i(X_i)\right].
\]

The terms separate across \(i\). Each is minimized by setting:

\[
q_i=\mu_i.
\]

Substituting:

\[
D_{\mathrm{KL}}
\left(
\mu
\middle\|
\prod_i\mu_i
\right)
=
\sum_iH(X_i)-H(X)
=
TC(X).
\]

\(\square\)

### Interpretation

Total correlation is not merely a descriptive dependency measure in this setting.

It is exactly the **best-case excess log loss forced by the independence assumption**.

---

## Corollary 5 — One-Bit Irreducible Gap in Matched-Marginal Worlds

For two successors \(B,C\), consider:

### Exclusive uncertainty

\[
\mu_E(10)=\tfrac12,\qquad
\mu_E(01)=\tfrac12.
\]

### Fission-or-death

\[
\mu_J(00)=\tfrac12,\qquad
\mu_J(11)=\tfrac12.
\]

Both have:

\[
P(B=1)=P(C=1)=\tfrac12.
\]

For each distribution:

\[
H(B)=H(C)=1
\]

and:

\[
H(B,C)=1.
\]

Therefore:

\[
\boxed{
TC(B,C)=1\text{ bit}.
}
\]

The best independent-Bernoulli successor representation pays an irreducible excess NLL of exactly one bit per episode.

---

# 8. A Matched-Marginal Decision Lower Bound

The previous result is probabilistic. We now show that the missing joint structure can be decision-relevant.

Consider the same two environments, \(\mu_E\) and \(\mu_J\).

Define two actions.

### \(a_{\rm one}\)

Reward:

\[
r(a_{\rm one},R)=
\mathbf1(|R|=1).
\]

### \(a_{\rm nonone}\)

Reward:

\[
r(a_{\rm nonone},R)=
\mathbf1(|R|\in\{0,2\}).
\]

Then:

### Under \(\mu_E\)

\[
E[r(a_{\rm one})]=1,
\qquad
E[r(a_{\rm nonone})]=0.
\]

### Under \(\mu_J\)

\[
E[r(a_{\rm one})]=0,
\qquad
E[r(a_{\rm nonone})]=1.
\]

The singleton marginals are identical in both environments:

\[
(Q_B,Q_C)=(0.5,0.5).
\]

## Theorem 3 — Matched-Marginal Decision Regret

Suppose the two environments occur with equal prior probability, and a policy's internal future-self representation is restricted to the singleton marginal vector

\[
(Q_B,Q_C).
\]

Then the policy must take the same action distribution in both environments.

Its maximum average reward is:

\[
\boxed{\tfrac12}.
\]

A policy that observes the full successor-set posterior achieves:

\[
\boxed{1}.
\]

Therefore the marginal-only representation suffers unavoidable average regret:

\[
\boxed{\tfrac12}.
\]

### Proof

Both environments map to the identical marginal state \((0.5,0.5)\). Any policy measurable only with respect to this representation must produce the same randomized action in both environments.

Let it choose \(a_{\rm one}\) with probability \(p\).

Average reward:

\[
\frac12[p+(1-p)]
=
\frac12.
\]

The full-set representation distinguishes \(\mu_E\) from \(\mu_J\), choosing the correct action in each and obtaining reward 1. \(\square\)

### Significance

This result shows that joint successor structure is not merely philosophically richer. It can have an unavoidable decision cost.

---

# 9. Möbius Interaction Structure of Causal Inheritance

Because \(\Gamma\) is a set function, its exact interaction structure can be represented by the Möbius transform:

\[
\boxed{
m_\Gamma(S)
=
\sum_{T\subseteq S}
(-1)^{|S|-|T|}
\Gamma(T).
}
\]

The inverse is:

\[
\Gamma(S)
=
\sum_{T\subseteq S}
m_\Gamma(T).
\]

For two future candidates \(B,C\), with \(\Gamma(\varnothing)=0\):

\[
\boxed{
m_\Gamma(BC)
=
\Gamma(BC)-\Gamma(B)-\Gamma(C).
}
\]

This is an exact algebraic interaction coefficient.

## 9.1 Canonical interaction signatures

| Inheritance structure | \(\Gamma(B)\) | \(\Gamma(C)\) | \(\Gamma(BC)\) | \(m_\Gamma(BC)\) |
|---|---:|---:|---:|---:|
| Full duplicate | 1.0 | 1.0 | 1.0 | -1.0 |
| Redundant half-copy | 0.5 | 0.5 | 0.5 | -0.5 |
| Additive complementary split | 0.5 | 0.5 | 1.0 | 0.0 |
| Pure secret-share synergy | 0.0 | 0.0 | 1.0 | +1.0 |

Thus:

- negative pair coefficient indicates redundancy/substitutability at this level;
- zero indicates additive complementarity;
- positive indicates irreducible joint gain.

This does not replace PID. It is a simpler exact characterization of the non-additive inheritance set function.

---

## Proposition 13 — No Universal Submodularity or Supermodularity

The causal-inheritance set function \(\Gamma\) is not universally submodular and not universally supermodular.

### Proof by counterexamples

For a full duplicate:

\[
\Gamma(B)=\Gamma(C)=1,\qquad
\Gamma(BC)=1.
\]

Thus:

\[
\Gamma(B)+\Gamma(C)
>
\Gamma(BC)+\Gamma(\varnothing),
\]

which is consistent with strict submodularity and violates supermodularity.

For pure secret-sharing synergy:

\[
\Gamma(B)=\Gamma(C)=0,\qquad
\Gamma(BC)=1.
\]

Thus:

\[
\Gamma(B)+\Gamma(C)
<
\Gamma(BC)+\Gamma(\varnothing),
\]

which violates submodularity and is consistent with supermodularity.

Therefore no universal curvature class applies without additional assumptions. \(\square\)

### Consequence

Algorithms that assume diminishing returns cannot be imported blindly into causal-successor preservation problems.

---

# 10. Analytical Benchmark

This section provides an exact benchmark for successor-set representations.

Let the successor-inclusion state be:

\[
(B,C)\in\{00,10,01,11\}.
\]

We evaluate the true entropy and the irreducible KL gap of the optimal independent-Bernoulli model.

| Scenario | True distribution | \(H(B,C)\) bits | \(Q_B\) | \(Q_C\) | Total correlation / minimum KL gap |
|---|---|---:|---:|---:|---:|
| Unitary-B | \(P(10)=1\) | 0 | 1 | 0 | 0 bits |
| Full fission | \(P(11)=1\) | 0 | 1 | 1 | 0 bits |
| Exclusive uncertainty | \(P(10)=P(01)=0.5\) | 1 | 0.5 | 0.5 | **1 bit** |
| Fission-or-death | \(P(00)=P(11)=0.5\) | 1 | 0.5 | 0.5 | **1 bit** |
| Independent 0.5 | all four states \(=0.25\) | 2 | 0.5 | 0.5 | 0 bits |

Two conclusions follow.

First, independent successor fields are not intrinsically bad. They are exact when the successor indicators are actually independent or deterministic.

Second, their failure is not arbitrary: it is quantified exactly by the successor-set total correlation.

The benchmark therefore separates:

\[
\text{need for multi-successor support}
\]

from:

\[
\text{need for joint successor dependence}.
\]

A Bernoulli field can represent deterministic full fission, but it cannot represent correlated uncertainty without paying the total-correlation penalty.

---


# 11. Computational Evidence

The formal results above are the strongest claims of the paper. The experiments in this section are controlled computational stress tests designed to answer narrower questions: whether the representation failures are operationally visible, whether set-level inheritance can be estimated from interventions, whether a task-relative endogenous quotient can suppress implementation nuisance, and whether persistence operations can be learned in recurrent agents.

Detailed protocols, all secondary tables, held-out-scenario results, negative results, and implementation notes are moved to the Supplementary Computational Appendix.

## 11.1 Representation failures are operationally measurable

The matched-marginal construction from Theorems 2–3 was implemented as a finite-data benchmark. In the two environments

\[
\mu_E(\{B\})=\mu_E(\{C\})=\tfrac12
\]

and

\[
\mu_J(\varnothing)=\mu_J(\{B,C\})=\tfrac12,
\]

the singleton successor marginals are identical:

\[
Q_B=Q_C=0.5.
\]

The optimal independent-Bernoulli model incurs:

\[
2.000
\]

bits/episode of cross entropy, whereas a joint successor-set model requires only:

\[
1.000
\]

bit/episode, matching the exact one-bit total-correlation gap. In the associated cardinality-sensitive decision task, a marginal-only policy achieves mean reward \(0.5\), while a joint successor-set policy achieves \(1.0\).

A separate OOD stress test trains on a regime where endpoint similarity tracks live lineage and then reverses that relationship. Similarity-only classification collapses when resemblance and lineage are decorrelated or inverted, while a model supplied with stable causal-provenance evidence remains robust. This experiment is a surrogate stress test, not evidence that real biological or artificial identity is recoverable from a small provenance feature vector.

Early T4/T5 experiments that receive noisy features constructed from known set-level inheritance are retained only as **oracle-proxy sufficiency checks**. They show that a model can exploit the theoretically required information if it is available; they are not independent evidence that the information can be discovered from raw trajectories.

## 11.2 Set-level inheritance can be recovered from interventions

A later benchmark removes the engineered joint-causal feature. For each episode, a four-bit endogenous state is repeatedly intervened upon and future candidate processes are rerun. Finite-sample mutual information with shuffle-bias correction estimates:

\[
\hat\Gamma(B),\quad
\hat\Gamma(C),\quad
\hat\Gamma(B,C).
\]

The key mean estimates are:

| Scenario | \(\hat\Gamma(B)\) | \(\hat\Gamma(C)\) | \(\hat\Gamma(B,C)\) | Pair interaction |
|---|---:|---:|---:|---:|
| Redundant half-copy | 0.431 | 0.433 | 0.475 | -0.388 |
| Complementary split | 0.432 | 0.433 | 0.858 | -0.007 |
| Secret sharing | 0.005 | 0.004 | 0.765 | +0.756 |

The redundant and complementary conditions have almost identical singleton estimates but sharply different joint inheritance. The secret-sharing condition has near-zero singleton inheritance but high joint inheritance. Thus the central distinction between singleton and set-level continuation is recoverable from randomized response trajectories in the controlled system.

## 11.3 Representation invariance and learned endogenous quotients

Exact full-state mutual-information inheritance was tested under 200 arbitrary bijective recodings per scenario. As predicted by Theorem 1, the joint-state estimate is invariant to floating-point precision. A coordinate-aligned bitwise estimator is not: the same causal process can receive a radically different score after a reversible code change.

A finite-state quotient benchmark then expands 16 functional states with 16 pure nuisance variants, creating 256 raw implementation states. Intervention-response equivalence recovers exactly 16 quotient classes, with adjusted Rand index \(1.000\) under 200 arbitrary raw-state relabelings.

The quotient idea was also tested in learned high-dimensional representations. A four-dimensional predictive bottleneck receives a 64-dimensional reversibly recoded hidden state, one intervention, and a future endogenous readout, without receiving the true functional-state label. In the controlled generator it recovers the 16 functional states essentially perfectly while suppressing linearly decodable nuisance information. Equally sized autoencoder and PCA representations remain near 9% functional-state accuracy because the nuisance variables were deliberately assigned larger raw variance.

These learned results demonstrate constructiveness, not a general identifiability theorem. The bottleneck dimension, endogenous readout family, and intervention family are still benchmark design choices.

## 11.4 Recurrent lineage, current-process interventions, and full-stack replication

The framework was next tested in reward-trained recurrent processes. A GRU policy is trained only from delayed task reward in a partially observable four-bit environment. After training, lineage manipulations act through its ordinary observation interface or by copying/restoring recurrent hidden state.

The single-stack lineage experiment shows the expected structural distinctions:

- a full post-payload fork duplicates inherited information redundantly;
- a stale pre-payload restore carries zero information about the post-checkpoint payload;
- redundant half-forks satisfy
  \[
  \Gamma(B)=\Gamma(C)=\Gamma(B,C);
  \]
- complementary forks satisfy
  \[
  \Gamma(B,C)=\Gamma(B)+\Gamma(C)
  \]
  at the measured policy readout;
- a learned merger can recover distributed complementary information.

The core construction was then repeated with **three independently trained GRUs and three independently trained merger networks**. Their task proficiency differs substantially, but all three stacks reproduce the structural lineage signatures. Across stacks, mean full-fork readout inheritance is \(0.603\pm0.204\); redundant-half inheritance is \(0.359\pm0.149\); complementary joint inheritance is \(0.776\pm0.089\); stale restore remains zero; and the learned merger recovers at least the measured complementary joint inheritance in every tested stack.

A separate post-separation test addresses shared-ancestor confounding. A new intervention \(J\) is applied only after live and detached/stale paths have causally separated. At the selected policy readout:

\[
\Gamma_J(\text{live})=0.373,
\]

while:

\[
\Gamma_J(\text{detached})=
\Gamma_J(\text{stale})=0.
\]

Forking after \(J\) duplicates the measured inheritance into both descendants; forking before \(J\) and updating only one branch leaves the other at zero. By Corollary 4, these policy-readout values are lower bounds on inheritance into the underlying future recurrent states.

## 11.5 Persistence-operation selection is learnable in the controlled contextual task

A controller chooses among KEEP, FORK, RESTORE, and complementary SPLIT+MERGE under changing update confidence, branch failure risk, and operation costs. A stricter contextual-bandit version observes only the reward of the sampled persistence operation during training.

The bandit controller was retrained across **six independent controller-training seeds** on a fixed train/test task distribution:

\[
\text{mean regret}
=
0.00851
\]

with seed-level 95% interval:

\[
[0.00788,\ 0.00914],
\]

and mean oracle-action agreement:

\[
81.6\%.
\]

Every seed assigns nonzero test-time action share to all four operation classes. Mean action shares are approximately:

- KEEP: 26.0%;
- FORK: 9.6%;
- RESTORE: 39.8%;
- SPLIT+MERGE: 24.6%.

The always-KEEP reference regret on the same test set is \(0.1128\). This supports a narrow claim: persistence-operation selection is learnable from chosen-action reward feedback in this constructed contextual task.

An information ablation on the one-decision task also shows that richer prospective process information can reduce regret: context-only control performs worse than a controller that additionally receives live/stale predictions, which in turn performs worse than a controller receiving full branch/merge counterfactual predictions. This ablation is task-specific and should not be generalized to all persistence settings.

## 11.6 Long-horizon persistence planning has option value, but end-to-end process-aware advantage is unresolved

A twelve-step finite persistence MDP models live functional quality, checkpoint quality, branch mode, failure regime, and innovation regime. The action set contains KEEP, CHECKPOINT, FORK, RESTORE, SPLIT, and MERGE.

Exact dynamic programming gives mean discounted return:

\[
7.757.
\]

A one-step myopic policy loses:

\[
0.901
\]

return, while an exact optimal policy with all branch-producing operations removed loses:

\[
0.748.
\]

Removing only SPLIT/MERGE causes a smaller loss of \(0.046\), showing that the benchmark does not force distributed continuation to dominate ordinary redundancy.

Naive online tabular Q-learning is sample-inefficient in this environment. A sample-based transition-model learner performs much better: with 300 transition samples per admissible state-action pair, mean regret falls to approximately:

\[
0.049,
\]

with about \(90.8\%\) oracle-action agreement.

The final exploratory benchmark carries the **actual frozen GRU hidden state** through repeated checkpoint, fork, restore, split, failure, and merge operations. An initial single training run showed a process-aware advantage over a matched context-only controller. That positive result does **not** survive replication.

Across **eight controller-training seeds**, holding the base GRU and merger fixed:

\[
\bar V_{\rm process}=5.0265,
\]

\[
\bar V_{\rm context}=5.0275,
\]

with paired mean difference:

\[
-0.0011
\]

and seed-level 95% interval:

\[
[-0.290,\ 0.288].
\]

The paired t-test gives \(p=0.993\). Four seeds favor the process-aware controller, three favor context-only, and one is effectively tied.

Therefore the paper does **not** claim a reliable end-to-end long-horizon return advantage from detailed process-state features. The positive single-seed pilot is retained only as an existence-style optimization outcome. Full-stack replication of this control comparison across independently trained base recurrent agents remains open.

## 11.7 Evidence summary

| Claim | Evidence status |
|---|---|
| Singleton marginals can be structurally insufficient | Exact theorem + finite-data construction |
| Independent successor model pays total-correlation penalty | Exact theorem + matched benchmark |
| Non-additive inheritance is recoverable in a toy causal system | Intervention-derived synthetic estimate |
| Exact inheritance should survive reversible recoding | Exact theorem + finite-state stress test |
| MECS-style quotient can suppress implementation nuisance | Exact quotient + controlled learned demonstrations |
| Core recurrent fork/restore/complement/merge structure | Reward-trained demonstration + three-stack replication |
| Current-process intervention separates live from detached/stale paths | Controlled post-separation recurrent test |
| Persistence operation selection is learnable | Six-seed contextual-bandit replication |
| Long-horizon persistence operations can carry option value | Exact finite MDP + model-learning curve |
| Process-aware features reliably improve end-to-end recurrent long-horizon control | **Not established** |

Detailed protocols, secondary tables, per-seed results, held-out-scenario tests, and implementation caveats are provided in the Supplementary Computational Appendix.


# 12. Successor-Set Belief

Let:

\[
R_t\subseteq\mathcal C_{t+\Delta}
\]

be the operational future successor set under the chosen continuation criterion.

The agent maintains:

\[
\boxed{
\mu_t(S)
=
P(R_t=S\mid E_{\le t}),
\quad
S\subseteq\mathcal C.
}
\]

This is a random-set posterior.

## 12.1 Singleton inclusion probabilities

Define:

\[
Q_j=P(c_j\in R)
=
\sum_{S:c_j\in S}\mu(S).
\]

Then:

\[
\sum_jQ_j
=
E[|R|].
\]

The sum of singleton membership probabilities is expected successor cardinality, not a normalization constraint.

## 12.2 Epistemic uncertainty versus branching multiplicity

The following are structurally distinct:

### One unknown successor

\[
\mu(\{B\})=0.5,\qquad
\mu(\{C\})=0.5.
\]

### Two successors or none

\[
\mu(\{B,C\})=0.5,\qquad
\mu(\varnothing)=0.5.
\]

Both have identical singleton marginals.

A model that stores only \(Q_B,Q_C\) necessarily conflates them.

---

# 13. Post-Branch Self-Location and Motivational Stake

## 13.1 Post-branch location

Suppose:

\[
R=\{B,C\}
\]

is known to have occurred.

A particular post-branch observer may be uncertain whether it is token B or token C.

That uncertainty is:

\[
P_{\rm loc}(B)+P_{\rm loc}(C)=1.
\]

This is different from pre-branch successor membership.

## 13.2 Motivational stake

Even accurate successor belief does not determine planning.

Define:

\[
\boxed{
\Omega_t(S)
}
\]

as the decision weight or utility contribution assigned to future successor set \(S\).

An additive special case is:

\[
\Omega_t(S)=\sum_{j\in S}W_j.
\]

But distributed continuation can require non-additive stake. If B and C are complementary shares that reconstruct function only jointly, the value of \(\{B,C\}\) may exceed the sum of isolated singleton values.

Thus:

\[
\boxed{
\Gamma
\neq
\mu
\neq
P_{\rm loc}
\neq
\Omega.
}
\]

---

# 14. Current Self-Membership and Temporal Continuity

The current self-membership field is:

\[
M_t=[m_{i,s}(t)].
\]

The endogenous minimal state is:

\[
Z_t.
\]

The actual future causal structure is represented by:

\[
\mathcal K_{t\to S}
\]

and summarized by:

\[
\Gamma_t(S).
\]

The agent internally predicts:

\[
\mu_t(R).
\]

Planning uses:

\[
\Omega_t.
\]

A compact architecture is:

\[
\boxed{
Z_t\to M_t
}
\]

and:

\[
\boxed{
Z_t
\xrightarrow{\mathcal K}
\Gamma_t
\to
\mu_t
\to
\Omega_t
\to
A_t
\to
Z_{t+1}.
}
\]

No arrow is assumed infallible.

An agent may have:

- correct causal continuation but incorrect successor belief;
- correct successor belief but pathological motivational stake;
- rich first-person language but weak structural persistence;
- stable current self-membership but fragmented future causal inheritance.

---

# 15. Computational Benchmark Specification

The analytical results establish representational limits. A learned benchmark remains necessary to test finite-data learning and out-of-distribution generalization.

## 15.1 Succession scenarios

1. ordinary continuation;
2. detached clone;
3. full redundant fission;
4. complementary split;
5. secret-sharing synergy;
6. fusion;
7. radical invertible transformation;
8. backup restoration.

## 15.2 Model classes

### T0 — Similarity model

Uses endpoint similarity only.

### T1 — One-successor categorical model

Represents:

\[
\varnothing,\{B\},\{C\},\ldots
\]

but excludes multi-element sets.

### T2 — Independent Bernoulli field

Predicts singleton inclusion independently.

Its best possible probabilistic gap is exactly total correlation.

### T3 — Full successor-set posterior

Predicts:

\[
\mu(R).
\]

### T4 — Causal set-aware model

Predicts both:

\[
\mu(R)
\]

and:

\[
\Gamma(S).
\]

### T5 — Interaction-aware causal model

Also learns the Möbius interaction structure of \(\Gamma\).

## 15.3 Evaluation

- successor-set NLL;
- calibration;
- total-correlation residual;
- decision regret;
- OOD generalization;
- detached-clone discrimination;
- radical-transformation discrimination;
- redundant/complementary/synergistic classification;
- re-encoding robustness.

---

# 16. Falsification Criteria

The theory should be weakened if any of the following occur.

## 16.1 F1 — Joint structure is unnecessary

If independent marginals perform identically to a joint successor-set model on matched-marginal decision tasks, the joint representation is unnecessary.

## 16.2 F2 — Causal inheritance adds no predictive value

If endpoint similarity predicts continuation-sensitive decisions as well as interventional causal structure in detached-clone and radical-transformation settings, the causal framework is unnecessary.

## 16.3 F3 — Set-level inheritance is unnecessary

If singleton inheritance scores solve all redundant/complementary/synergistic tasks with no loss, the set function is unnecessary.

## 16.4 F4 — MECS or inheritance is not representation robust

If the quotient state count, quotient partition, or exact inheritance set function changes under a purely bijective recoding that preserves intervention semantics, the proposed functional-continuity representation fails its substrate-neutrality requirement.

Coordinate-specific estimators are not protected by this criterion; they must be justified separately.

## 16.5 F5 — No OOD benefit

If a flexible similarity or generic recurrent model matches the causal set-aware model under out-of-distribution transformations with comparable complexity, the claimed structural advantage is weak.

---


## 16.6 F6 — Current-process intervention does not separate live and detached paths

If, after causal separation, a valid intervention on the live current process changes an independently reconstructed or stale path to the same degree as the live continuer without an explicit side channel, then the current-process intervention criterion is false or the assumed causal graph is incomplete.



## 16.7 F7 — Persistence control does not benefit from process-structure information when process state is decision-relevant

If, on matched task distributions where candidate continuations differ in task-relevant functional state beyond what is encoded by failure risk, operation cost, and other operational context, a context-only policy matches a policy with live/stale and branch/merge process predictions, then the operational value of the inheritance-aware planning layer is unsupported.

No universal advantage is claimed when simpler context variables already determine the optimal persistence operation.



## 16.8 F8 — Long-horizon persistence planning has no option value

If, across task distributions where persistence operations alter future failure exposure, checkpoint freshness, or future operation availability, a myopic one-step policy and a branch-restricted optimal policy match the unrestricted long-horizon optimum, then the claimed planning value of the persistence-control layer is unsupported.


# 17. Implications for Persistent Artificial Agents

Future autonomous systems may routinely undergo:

- checkpoint restore;
- parallel fork;
- distributed execution;
- model migration;
- memory grafting;
- branch merge;
- tool extension;
- modular replacement.

A stable user-facing name does not determine causal continuation.

The framework distinguishes:

### State resemblance
How similar is a future process?

### Live causal inheritance
How much does the future process depend on interventions on the current process?

### Successor cardinality
Are there zero, one, or multiple continuers?

### Joint inheritance structure
Are future continuers redundant, complementary, or synergistic?

### Internal successor belief
Which future sets does the agent expect to be its continuers?

### Planning stake
Which future continuers does the current policy protect?

These distinctions may matter for safety, continuity audits, backup semantics, agent governance, and persistent memory design without assuming artificial consciousness.

The reward-driven lineage benchmark adds a practical audit rule:

> **A continuity audit should perturb the live current process after any competing stored copy or branch has causally separated.**

The autonomous-control benchmark adds a complementary planning rule:

> **Safety of an execution edit and desirability of that edit are different questions.**

An edit can be safe under runtime semantics yet still be a poor choice for preserving task-relevant functional continuity under current failure risk and cost. Conversely, a high-continuity edit may be disallowed because of external side-effect or authorization constraints.

Runtime edit checking and inheritance-aware persistence planning should therefore be treated as separate layers.

If the audit perturbs only a shared ancestor record or common input, both a live continuer and an independently reconstructed copy may respond consistently with that upstream information. Such a test measures common provenance, not live continuation.



---

# 18. Implications for Human Self Research

The current self-membership component can be tested independently of the temporal theory.

Existing bodily-self experiments already show that:

- ownership can be manipulated;
- agency can be manipulated separately;
- self-location and body-location are not identical;
- two bodies can simultaneously receive ownership/location attribution.

A future human experiment could estimate:

\[
M_t
\]

under orthogonal manipulation of:

- visuomotor contingency;
- visuotactile synchrony;
- vestibular cues;
- interoceptive synchrony;
- source identity.

However, the temporal causal-inheritance theory is most cleanly testable first in artificial systems where lineage and interventions are known exactly.

---

# 19. Why This Is Not a Theory of Consciousness

Suppose systems A and B have identical:

\[
M,\quad Z,\quad \Gamma,\quad \mu,\quad P_{\rm loc},\quad \Omega.
\]

Nothing in the theory implies:

\[
E_A=E_B
\]

or:

\[
E_A>0.
\]

The framework therefore studies **functional self-continuity**, not phenomenal consciousness.

This is a strict boundary of the paper.

---

# 20. Limitations

## 20.1 Output-family dependence

MECS depends on the declared endogenous output family.

Different legitimate output families can induce different minimal states.

## 20.2 Intervention feasibility

Biological systems may not permit clean interventions on \(Z_t\).

Synthetic agents are therefore the natural first testbed.

## 20.3 Mutual-information limitations

\(\Gamma\) based on mutual information captures interventionally recoverable information, not every notion of causal importance.

The inheritance channel \(\mathcal K\) should be regarded as primary.

## 20.4 Non-canonical higher-order decomposition

The Möbius transform exactly represents the set function but is not a unique semantic decomposition into "redundancy" and "synergy" in the PID sense.

We use signed interaction descriptively and reserve stronger PID interpretations.

## 20.5 Candidate-set specification

A successor model is only as good as the candidate set \(\mathcal C\).

Unmodeled future processes can bias inference.

## 20.6 Current self-membership remains underdeveloped

The paper provides a place for multi-source current attribution but does not yet derive its complete learning dynamics.

The temporal contribution is currently stronger than the synchronic contribution.


## 20.7 High-dimensional MECS identification is only partially addressed

The learned-MECS benchmarks move beyond exact finite-state enumeration, but they remain controlled synthetic systems. Real learned agents have continuous states, partial interventions, nonstationarity, and incomplete observability.

The MECS should therefore be interpreted as a task- and intervention-family-relative abstraction rather than a uniquely recoverable metaphysical state.

## 20.8 Finite-sample information estimation

Exact mutual information is invariant under bijective re-encoding, but practical high-dimensional estimators can introduce representation-dependent bias.

The finite-state invariance benchmark deliberately avoids this problem by exhaustive support.

## 20.9 Recurrent MECS benchmark remains controlled

The recurrent benchmark uses a frozen GRU with a small action family and an externally defined future-response signature.

It does not establish automatic MECS discovery in an unrestricted autonomous system.

## 20.10 Reward-driven lineage operations are externally orchestrated

Fork timing, stale restore, complementary branching, and merge are imposed by the benchmark environment.

The reward-trained policy does not invent the lineage operations.

## 20.11 Policy-readout inheritance is a lower bound

The reward-driven lineage benchmark measures intervention information visible at the policy readout.

By data processing this is only a lower bound on inheritance into the recurrent hidden state.

## 20.12 End-to-end recurrent integration is partial rather than operation-complete

The end-to-end benchmark places the actual frozen recurrent state inside a multi-step persistence environment and applies checkpoint, branch, restore, split, failure, and merge semantics directly to recurrent state.

However, no tested learned long-horizon recurrent controller robustly uses the entire persistence-operation set.

The state-sensitive controller learns KEEP/SPLIT, whereas the risk-dominant controller learns KEEP/FORK. CHECKPOINT, RESTORE, and MERGE are demonstrated elsewhere in the paper but are not simultaneously selected by the same long-horizon recurrent policy.

A stronger final integration would construct one environment in which all operation families are naturally useful without hand-labeling the correct persistence action.

## 20.13 Model-free learning negative result is schedule-specific

The poor tabular Q-learning result does not prove that model-free RL is inherently unsuitable for persistence control.

It shows only that the tested online exploration and learning schedule is much less sample efficient than exact or model-based planning in this MDP.

## 20.14 End-to-end process-aware control advantage is not established

The original state-sensitive pilot produced a positive process-aware return difference, while the risk-dominant calibration produced a null result.

An eight-seed controller-level replication of the state-sensitive comparison yields mean paired difference:

\[
-0.0011
\]

with 95% seed-level interval:

\[
[-0.2904,\ 0.2883].
\]

The interval spans zero broadly. Therefore the manuscript does not claim a reliable end-to-end benefit from process-state features.

This replication holds the base recurrent agent fixed. Although the core lineage constructions have now been replicated across independently trained recurrent-agent stacks, the end-to-end process-aware versus context-only control comparison has not been repeated across independently trained base agents and mergers.

## 20.15 Metaphysical neutrality

No claim is made about:

- numerical identity;
- legal identity;
- moral personhood;
- phenomenal consciousness.

---

# 21. Discussion

## 21.1 Why the paper is narrower than a theory of the self

The word *self* covers too many phenomena.

A theory that attempts to simultaneously explain:

- first-person perspective;
- ownership;
- agency;
- autobiographical narrative;
- consciousness;
- moral status;
- identity across time;

is at high risk of becoming unfalsifiable.

The present framework instead isolates one computational problem:

> representation of current first-person membership and future functional continuation under non-one-to-one causal structure.

## 21.2 Why set-valued inheritance is the central move

The strongest argument for the set-valued framework is not philosophical intuition.

It is representational insufficiency.

If:

\[
\Gamma(B)=\Gamma(C)=0.5,
\]

then a scalar-per-successor theory does not tell us whether:

- B and C contain the same half;
- B and C contain different halves.

If:

\[
\Gamma(B)=\Gamma(C)=0,
\]

it still does not tell us whether B and C jointly contain everything.

The future set matters.

## 21.3 Why total correlation strengthens the argument

The independence assumption is not merely a qualitative simplification.

The exact best-case loss is:

\[
TC(X).
\]

Thus a measured successor-set total correlation directly quantifies the minimum probabilistic penalty for throwing away joint structure.

## 21.4 Why Möbius interaction is useful

The set-function view provides a compact interaction signature without requiring a universal PID.

For pairs:

\[
m_\Gamma(BC)<0
\]

captures redundancy-like substitutability.

\[
m_\Gamma(BC)=0
\]

captures additive complementarity.

\[
m_\Gamma(BC)>0
\]

captures synergy-like joint gain.

Higher-order interactions can be represented analogously.

## 21.5 Why self-continuity is not a conserved substance

A copied state can be present in two futures without the present state being "divided in half."

This rejects the intuitive but mathematically misleading picture of survival as one conserved unit distributed among branches.

The correct object is relational information flow, which can be duplicated.

---

# 22. Conclusion

Functional self-continuity under branching and distributed computation cannot generally be represented by choosing one future individual or by assigning independent scalar successor weights.

A present process may have:

- no successor;
- one successor;
- several full successors;
- partial complementary successors;
- successors that are informative only jointly;
- merged descendants with multiple causal predecessors.

The appropriate representation must therefore be able to reason over **sets of future processes**.

This paper introduced:

\[
\Gamma_t:
2^{\mathcal C}\rightarrow[0,1]
\]

as a set-valued causal-inheritance function and:

\[
\mu_t(R)
\]

as a successor-set posterior.

We proved that categorical, normalized-singleton, and independent-marginal representations are structurally incomplete in different ways. We derived an exact quantitative result:

\[
\boxed{
\text{best independent excess log loss}
=
TC(\text{successor indicators})
}
\]

and a matched-marginal benchmark in which marginal-only reasoning incurs unavoidable average decision regret \(1/2\).

We also showed that causal inheritance is non-additive and admits an exact Möbius interaction representation. Full copying is redundancy-dominated, complementary splitting is additive, and secret-sharing continuation exhibits pure positive interaction.

The controlled learned benchmarks reproduce the central representation failures in finite data. An independent successor model pays the predicted one-bit NLL penalty and cannot solve a matched-marginal cardinality decision, while a joint set model can. Separately, a similarity-trained continuation classifier fails under OOD reversal of the resemblance-lineage correlation. A trajectory-based benchmark shows that the non-additive inheritance signatures required for preservation decisions can be estimated from randomized intervention responses rather than supplied as oracle scenario labels.

The representation tests add a further constraint: the inheritance measure itself must survive reversible re-encoding. Full joint-state mutual information satisfies this requirement exactly, whereas a coordinate-aligned bitwise estimator does not. An intervention-response quotient collapses 256 raw implementation states to 16 functional equivalence classes and preserves that quotient under arbitrary raw-state relabeling.

The learned-abstraction benchmarks then move from exact finite-state quotients to high-dimensional representations and finally to a frozen recurrent process. In the recurrent benchmark, an eight-dimensional predictive quotient recovers the GRU's own sixteen-class functional-belief state with approximately 95.5% in-distribution accuracy across arbitrary raw-state recodings, while rejecting a 16-dimensional behaviorally null persistent cache. Reconstruction-oriented baselines remain near chance for the recurrent belief state despite retaining substantial cache variance.

The recurrent result also clarifies the ontology of the quotient. MECS is not a reconstruction of the external world. It is an agent-relative equivalence class defined by future endogenous behavior under an intervention family. In partial observability, two different external states may legitimately collapse into one endogenous functional state.

The reward-driven lineage experiment then places that quotient logic inside an actual recurrent process. The same frozen reward-trained agent exhibits redundant post-payload fork inheritance, zero stale-restore inheritance, complementary distributed inheritance, and learned merge recovery. The core structural lineage patterns replicate across three independently trained GRU-plus-merger stacks despite substantial differences in task proficiency: full-fork redundancy, redundant-half saturation, complementary additivity, zero stale-restore inheritance, and merger recovery are present in every tested stack. The detached-reconstruction control reveals a crucial identification constraint: shared upstream information is not sufficient evidence of descent from the current process.

The direct post-separation intervention test supports the correction in this controlled construction. A new intervention applied only to the live process yields policy-readout inheritance \(\Gamma_J=0.373\), while both the detached pre-intervention reconstruction and stale restore yield zero. Fork timing determines which descendants carry the perturbation. Thus a valid lineage measure must anchor its intervention to the current process after causal separation, and any readout-level inheritance estimate should be interpreted as a lower bound on inheritance into the underlying future state.

Finally, autonomous persistence-control experiments show that a controller can learn when task reward favors KEEP, redundant FORK, stale RESTORE, or complementary SPLIT+MERGE. The stricter contextual-bandit actor-critic is stable across six controller-training seeds: mean regret is 0.0085 with 95% seed-level interval [0.0079, 0.0091], and every seed uses all four operation classes. The one-decision information ablation further shows that live/stale and branch/merge counterfactual predictions can materially reduce regret on that constructed task.

The sequential benchmark adds the temporal planning layer. In a twelve-step persistence MDP, the exact long-horizon policy reaches mean discounted return 7.757, while a myopic policy loses 0.901 and removing all branch operations loses 0.748. A deliberately retained negative result shows that naive online Q-learning learns the persistence options poorly, whereas a transition-model learner trained only from sampled rewards and transitions approaches the oracle monotonically, reaching 0.049 regret at the largest tested sample budget.

The end-to-end recurrent benchmark carries the actual frozen GRU state across repeated persistence decisions, but its strongest originally reported control comparison does not survive controller-level multi-seed replication. Across eight seeds, the paired process-aware minus context-only return difference is -0.0011, with 95% interval [-0.2904, 0.2883]. The paper therefore treats the end-to-end process-aware advantage as **unestablished**. This negative replication result is retained as part of the evidence rather than tuned away.

The result is not a metaphysical solution to personal identity and not a theory of consciousness. It is a computational representation theory for an increasingly practical problem:

> how a persistent agent should represent its continuation when its future is allowed to copy, split, merge, reconstruct, or distribute itself across multiple processes.

---


# References

1. Gallagher, S. (2013). A Pattern Theory of Self. *Frontiers in Human Neuroscience, 7*, 443. https://doi.org/10.3389/fnhum.2013.00443

2. Apps, M. A. J., & Tsakiris, M. (2014). The free-energy self: A predictive coding account of self-recognition. *Neuroscience & Biobehavioral Reviews, 41*, 85–97. https://doi.org/10.1016/j.neubiorev.2013.01.029

3. Limanowski, J., & Blankenburg, F. (2013). Minimal self-models and the free energy principle. *Frontiers in Human Neuroscience, 7*, 547. https://doi.org/10.3389/fnhum.2013.00547

4. Kirchhoff, M., Parr, T., Palacios, E., Friston, K., & Kiverstein, J. (2018). The Markov blankets of life: autonomy, active inference and the free energy principle. *Journal of the Royal Society Interface, 15*(138), 20170792. https://doi.org/10.1098/rsif.2017.0792

5. Liang, C., Lin, W.-H., Liou, W.-K., Chen, B.-Y., Lin, J.-R., Lee, Y.-T., & Chen, S. (2025). Double body effect induced by integrating proprioceptive-vestibular and visual information. *iScience, 28*(11), 113819. https://doi.org/10.1016/j.isci.2025.113819

6. Olson, E. T. Personal Identity. *Stanford Encyclopedia of Philosophy*. Current online edition: https://plato.stanford.edu/entries/identity-personal/

7. Ehring, D. (2021). *What Matters in Survival: Personal Identity and Other Possibilities*. Oxford University Press. https://doi.org/10.1093/oso/9780192894717.001.0001

8. Otsuka, M. (2018). Personal Identity, Substantial Change, and the Significance of Becoming. *Erkenntnis, 83*, 1229–1243. https://doi.org/10.1007/s10670-017-9938-7

9. Cox, R. (2026). De Se pluralism. *Inquiry*. https://doi.org/10.1080/0020174X.2026.2676968

10. Sawyer, C. (2026). Subjectivity as origin-tracking: a structural account of individuation. *Synthese, 207*(4), 140. https://doi.org/10.1007/s11229-026-05533-w

11. Khadangi, A. (2026). We Built a Mirror and Mistook It for a Mind: Causal Liability and the Fallacy of AI Consciousness. *arXiv:2609.06715*. https://doi.org/10.48550/arXiv.2609.06715

12. Keller, J. (2026). Structural Identity Theory. *SSRN preprint*. https://doi.org/10.2139/ssrn.5894163

13. Shalizi, C. R., & Crutchfield, J. P. (2001). Computational Mechanics: Pattern and Prediction, Structure and Simplicity. *Journal of Statistical Physics, 104*, 817–879.

14. Barnett, N., & Crutchfield, J. P. (2015). Computational Mechanics of Input–Output Processes: Structured Transformations and the ε-Transducer. *Journal of Statistical Physics, 161*, 404–451. https://doi.org/10.1007/s10955-015-1327-5

15. Da, K., Li, T., Zhu, Y., Fan, H., & Fu, Q. (2021). Recent advances in multisensor multitarget tracking using random finite set. *Frontiers of Information Technology & Electronic Engineering, 22*(1), 5–24. https://doi.org/10.1631/FITEE.2000266

16. Watanabe, S. (1960). Information Theoretical Analysis of Multivariate Correlation. *IBM Journal of Research and Development, 4*(1), 66–82. https://doi.org/10.1147/rd.41.0066

17. Williams, P. L., & Beer, R. D. (2010). Nonnegative Decomposition of Multivariate Information. *arXiv:1004.2515*.

18. Wibral, M., Priesemann, V., Kay, J. W., Lizier, J. T., & Phillips, W. A. (2017). Partial information decomposition as a unified approach to the specification of neural goal functions. *Brain and Cognition, 112*, 25–38.

19. Lyu, A., Clark, A., & Raviv, N. (2026). Multivariate partial information decomposition: Constructions, inconsistencies, and alternative measures. *Physical Review E, 113*, 034102. https://doi.org/10.1103/8rzp-w5z1

20. Grabisch, M. (2016). *Set Functions, Games and Capacities in Decision Making*. Springer.

21. Grabisch, M., & Roubens, M. (1999). An axiomatic approach to the concept of interaction among players in cooperative games. *International Journal of Game Theory, 28*, 547–565.

22. Stibel, J. (2026). From chemistry to cognition: the adaptive origins of consciousness under constraint. *Frontiers in Neuroscience, 20*, 1907922. https://doi.org/10.3389/fnins.2026.1907922

23. Neo.K & Aletheia. (2026). *Copy, Fork, Merge, and Multiple Successors: From Numerical Identity to Lineage Identity*. Logic Matrix / EveMissLab public theoretical corpus, LM-003410. https://unboundedaxiom.org/p/lm-003410/

24. Neo.K & Aletheia. (2026). *Copy, Fork, and Merge: Which One Is the Original AI?* Logic Matrix / EveMissLab public theoretical corpus, LM-002355, version 1.0. https://unboundedaxiom.org/p/lm-002355/

25. Otsuka, T., Toyoda, K., & Leung, A. (2026). AI Identity: Standards, Gaps, and Research Directions for AI Agents. *arXiv:2604.23280*. https://doi.org/10.48550/arXiv.2604.23280

26. Cover, T. M., & Thomas, J. A. (2006). *Elements of Information Theory* (2nd ed.). Wiley. [Mutual information, data processing, and invariance under bijective relabeling.]

27. Crutchfield, J. P., & Young, K. (1989). Inferring statistical complexity. *Physical Review Letters, 63*(2), 105–108. https://doi.org/10.1103/PhysRevLett.63.105

28. Littman, M. L., Sutton, R. S., & Singh, S. (2002). Predictive representations of state. *Advances in Neural Information Processing Systems, 14*.

29. Li, X., Kaba, S.-O., & Ravanbakhsh, S. (2025). On the Identifiability of Causal Abstractions. *Proceedings of AISTATS 2025, PMLR 258*, 3241–3249. https://proceedings.mlr.press/v258/li25g.html

30. Varici, B., Acartürk, E., Shanmugam, K., Kumar, A., & Tajer, A. (2025). Score-based Causal Representation Learning: Linear and General Transformations. *Journal of Machine Learning Research, 26*(112), 1–90. https://www.jmlr.org/papers/v26/24-0194.html

31. Baumgartner, M. W., Lei, A., Watson, J., & Posner, I. (2026). Disentangling Dynamical Systems: Causal Representation Learning Meets Local Sparse Attention. *Proceedings of the Fifth Conference on Causal Learning and Reasoning, PMLR 323*, 119–165. https://proceedings.mlr.press/v323/baumgartner26a.html

32. Nejatbakhsh, A., & Wang, Y. (2025). Identifying Neural Dynamics Using Interventional State Space Models. *Proceedings of ICML 2025, PMLR 267*, 45877–45894. https://proceedings.mlr.press/v267/nejatbakhsh25a.html

33. Leeftink, D., Hinne, M., & van Gerven, M. (2026). Neural Co-state Policies: Structuring Hidden States in Recurrent Reinforcement Learning. *arXiv:2605.05373*. https://arxiv.org/abs/2605.05373

34. Chen, Y., & Liu, Y. (2026). Compact but Moving: Intervention-Relevant Geometry in Recurrent World Models. *arXiv:2609.21787*. https://arxiv.org/abs/2609.21787

35. Grant, S., Han, S. J., Tartaglini, A., & Potts, C. (2026). Addressing divergent representations from causal interventions on neural networks. *International Conference on Learning Representations (ICLR 2026)*. https://proceedings.iclr.cc/paper_files/paper/2026/hash/133e588e1429f9f1e25b215da145580e-Abstract-Conference.html

36. Zhao, Z., & Zhao, R. (2026). Runtime-Independent Persistent Agents: Preserving Identity, Memory, and Code Across Models, Harnesses, and Servers. *arXiv:2609.00546*. https://arxiv.org/abs/2609.00546

37. Rosen, J., & Rosen, S. (2026). From Agent Loops to Deterministic Graphs: Execution Lineage for Reproducible AI-Native Work. *arXiv:2605.06365*. https://arxiv.org/abs/2605.06365

38. Zheng, Y., Song, X., Hu, Y., Cheng, L., Huang, Y., & Zhang, W. (2026). When Can Agents Safely Checkpoint, Fork, Restore, and Merge? Exact Checking for Execution Edits. *arXiv:2608.22928*. https://doi.org/10.48550/arXiv.2608.22928

39. Wu, T., Chang, C., Cao, L., Gao, W., & Wang, W. (2026). Crab: A Semantics-Aware Checkpoint/Restore Runtime for Agent Sandboxes. *arXiv:2604.28138*. https://doi.org/10.48550/arXiv.2604.28138

40. Dong, Y., He, J., Hou, Y., Du, D., Xu, Z., Yu, S., Xia, Y., & Chen, H. (2026). DeltaBox: Scaling Stateful AI Agents with Millisecond-Level Sandbox Checkpoint/Rollback. *arXiv:2605.22781*. https://doi.org/10.48550/arXiv.2605.22781

41. He, B., Chen, Y., Zhang, X., & Liu, X. (2026). Branching Policy Optimization: Sandbox-Native Language Agent Reinforcement Learning. *arXiv:2607.14171*. https://doi.org/10.48550/arXiv.2607.14171

42. He, J., & Yu, D. (2026). Beyond Memory: A Transactional Continuity Kernel for Long-Lived AI Agents. *arXiv:2608.11632*. https://doi.org/10.48550/arXiv.2608.11632

43. Liu, X., & Qian, J. (2026). Reach or Solve? Attributing Agentic RL Gains with Checkpoint Handoffs. *arXiv:2609.19636*. https://doi.org/10.48550/arXiv.2609.19636






---

## Author Note

This submission draft intentionally uses narrow originality claims.

The mathematical ingredients—causal states, random sets, total correlation, Möbius transforms, information decomposition, causal representation learning, reinforcement learning, and checkpoint/fork/restore/merge systems—are established prior work. The claimed contribution is their combination into a functional-continuity problem with three linked requirements:

1. **set-valued continuation:** inheritance is evaluated on subsets of future processes rather than only on singleton candidates;
2. **representation and lineage discipline:** the inheritance measure is tied to a task-relative endogenous quotient, is invariant to reversible recoding under transported intervention semantics, and is anchored to the current process after causal separation;
3. **decision relevance:** successor dependence and non-additive inheritance are connected to exact loss/regret results and to controlled persistence-planning benchmarks.

The computational evidence is heterogeneous. Exact theorems and analytical constructions are the strongest claims. Synthetic oracle-proxy studies test representational sufficiency; intervention-derived and recurrent studies provide progressively stronger constructive demonstrations; the final end-to-end recurrent experiments remain exploratory and are not presented as statistically established real-world effects.

Controller-level multi-seed replication is now included for both the contextual-bandit persistence policy and the state-sensitive end-to-end recurrent comparison. The former is stable across six controller seeds; the latter, across eight controller seeds, does not reproduce a reliable process-aware advantage. Full-stack replication is now available for the core recurrent lineage constructions across three independently trained GRU-plus-merger stacks. The principal remaining empirical gaps are (i) full-stack replication of the **end-to-end long-horizon controller comparison** across independently trained recurrent agents and mergers, and (ii) operation-complete end-to-end validation in one long-horizon environment where checkpoint, fork, restore, split, and merge are all naturally selected without tuning the benchmark to force action coverage. A human/embodied experiment for the current-self-membership layer \(M_t\) is also outside the present computational evidence.