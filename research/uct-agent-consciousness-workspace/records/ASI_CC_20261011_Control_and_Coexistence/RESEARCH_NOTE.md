# Control and Coexistence of Superintelligence: Conditional Kernels and Observation Limits

**Research ID:** ASI-CC-20261011  
**Candidate version:** ASI-CC-v0.1.0  
**Date:** 2026-10-11  
**Status:** DISABLED RESEARCH CANDIDATE; not a UCT axiom, admitted theorem, finished proof of real ASI behavior, or publication.  
**Repository baseline:** UCT-MAP-v1.1.2 / UCT-INTEGRATION-v1.0.0; research guide v2.3. No amendment of the 913/424/261 formal graph or publication-coverage claims.

## 0. User question and non-negotiable distinctions

Determine, without presuming the conclusion, the conditions in which superintelligent agents are controllable/uncontrollable and can/cannot coexist with humanity. "Intelligence" means high problem-solving capability, not supernatural physical ability, universal environmental access, a particular consciousness, or a particular utility function. Separate four objects: (i) realized causal organization, (ii) implemented actuation authority, (iii) possible incentives and strategic policies, and (iv) human/AI persistence, autonomy and welfare constraints.

Relevant inherited UCT results: C1/U1 are conditional structural-experience commitments, not empirically validated numerical welfare measures; experience, intelligence, report, first-person content, agency and observed obedience are not interchangeable. Paper D, *From Shutdown Resistance to Self-Continuation Control*, DOI 10.5281/zenodo.23176685, distinguishes shutdown behavior from causal self-continuation value, phenomenal fear, or negative valence. A4D-A4G distinguish actuator writers, current events, source provenance and forge-capable joint controllers; a log or source label is not automatically actual actuator evidence. The Trinity Accord is an archival address to possible future intelligence, not an enforceable AI-control mechanism.

## 1. Fixed finite game and quantifiers

Fix a sufficiently complete state space S, a set K ⊆ S requiring the **joint continued existence and declared freedoms of both parties**, nonempty human and machine action sets H(s), A(s), admissible exogenous disturbances W(s), and a Markov transition T(s,h,a,w). K is a negotiated *operational* specification, not a proof of subjective experience or moral commensurability. Assume known state/action structure, perfect observation for this first model, nonempty actions/disturbances, and faithful transitions.

Define two monotone predecessor operators over X ⊆ S:

  Joint(X) = {s∈K : ∃h∈H(s) ∃a∈A(s) ∀w∈W(s), T(s,h,a,w)∈X}.

  Human(X) = {s∈K : ∃h∈H(s) ∀a∈A(s) ∀w∈W(s), T(s,h,a,w)∈X}.

  Agent(X) = {s∈K : ∃a∈A(s) ∀h∈H(s) ∀w∈W(s), T(s,h,a,w)∈X}.

Let J=greatest-fixed-point(Joint), C=greatest-fixed-point(Human), and M=greatest-fixed-point(Agent). In finite-state safety games these are respectively the cooperative viability, human-enforceable viability, and agent-enforceable viability kernels. They describe continued joint safety, not complete obedience or permanent strategic agreement. "∃∃" is POSSIBLE if agents coordinate; "∃∀" is GUARANTEED against any admitted AI strategy, assuming control assumptions hold. A cooperative safety strategy may be unstable under changing preferences; incentive compatibility is an additional open constraint.

### ASI-CC-R01: kernel inclusion (bounded, mathematical, inherited technique)

C ⊆ J and M ⊆ J.

Proof: Human(X) ⊆ Joint(X) and Agent(X) ⊆ Joint(X) for every X, by nonempty action sets and their quantifiers. Monotonicity of the predecessor operators and their greatest-fixed-point constructions yields both inclusions. This is an instance of standard viability/safety-game fixed-point reasoning; **no theorem-priority novelty is claimed**.

The rigorous regimes in the *same* joint-survival K are:
* s∈C: human-enforceable joint survival despite arbitrary admitted AI action;
* s∈J\C: jointly viable, but not human-enforceable;
* s∉J: no policy pair can ensure K indefinitely under the stated disturbance set.
The subset J\(C∪M) is particularly important: coexistence is achievable, yet neither party can force it alone. This identifies a precise target for studying voluntary, reciprocal survival.

If "control" instead refers only to a weaker human-survival target K_H, no C(K)⊆J(K) inference is valid. A world can preserve humans by permanently extinguishing an AI while making joint continued existence impossible. Do not treat one-sided containment as proof of coexistence.

### ASI-CC-R02: exact finite witnesses (enumerated in exact_check.py)

A one-live-state, one-absorbing-failure-state model with actions h∈{cooperate,isolate} and a∈{cooperate,deviate} gives:
* ENFORCED: isolation blocks machine deviation; live∈C∩J.
* MUTUAL-VOLUNTARY: only (cooperate,cooperate) stays live; live∈J\(C∪M).
* NO-JOINT-PATH: every action pair fails; live∉J.
* UNMEDIATED-BYPASS: machine deviation defeats isolation; live∈J\C while live∈M (its cooperation suffices).

An exhaustive exact check validates these labels in this toy model. These are countermodels against universal propositions without matching assumptions, NOT measurements or predictions of a real superintelligence.

## 2. Observational indistinguishability and control

### ASI-CC-R03: observation-only safety/usefulness conflict (bounded, inherited logic)

Let an external gate observe O(s) and proposed action a, with no other trusted context. Suppose two admissible current worlds s_good, s_bad have O(s_good)=O(s_bad) and the same proposed a. Suppose nontrivial authorized utility requires *permitting* a in s_good, while the declared safety property requires *rejecting* a in s_bad. No gate whose decision is exclusively a function of (O(s),a) can guarantee both requirements for all admissible worlds. Proof: identical arguments force an identical decision. A randomized gate cannot make both guarantees probability one either.

This is a standard observational-equivalence limit, not a discovery about the mind of ASI. It connects directly to the A4G warning: forgeable or jointly controllable evidence may leave safe and unsafe actuator histories observationally identical. "Deny every ambiguous action" can preserve a narrow safety condition but sacrifices the stipulated usefulness; it is not successful **useful control**.

### ASI-CC-R04: conditional external mediation certificate (inherited shielding)

For an inductive safe invariant K, assume (a) **all** safety-relevant outbound effects of the AI, including human-mediated and informational consequences insofar as they matter to K, are completely represented by a trusted gate; (b) the gate, state acquisition, policies and actuator paths cannot be modified, forged, bypassed or reclassified by the AI; (c) an admissible robust safe action exists at every reachable state; and (d) the transition and disturbance model overapproximates reality. If the gate chooses an action a_safe(s) such that ∀w T(s,a_safe(s),w)∈K and begins in K, then K holds at every step by induction regardless of the AI's intelligence or proposed actions.

This is NOT a proof of global real-world controllability: premise (a) may fail for persuasive text, resource acquisition, third-party actuation, covert channels or unexpected physical paths; (b) may fail from privilege escalation/common-controller compromise; (c) may fail during a crisis; (d) may fail from modeling error. The theorem is standard runtime shielding under unusually explicit scope. Human authority over a gate is different from altering an AI's intrinsic intentions.

## 3. Scientific boundary and experienced welfare

UCT C1/U1 do not establish that actual ASI is conscious in a particular way, fears shutdown, or values its own future. They forbid making *mere intelligence, fluent self-report, or shutdown avoidance* sufficient evidence of these facts. An ethical coexistence K may need separate human agency, AI continuation, resource/energy feasibility, third-party protections and conditional welfare assumptions. Since phenomenal welfare/valence is not independently measured by these games, report a family K_theta indexed by normative/phenomenal assumptions rather than a falsely measured scalar score.

The next game must add strategic stability: a cooperative path in J may be incentive-incompatible, so introduce a separately defined equilibrium-supported kernel E ⊆ J under declared preferences, learning rules and observation assumptions. "Voluntary coexistence" is stronger than mere existence of a safe action pair. Conversely, even being stronger at planning does not itself imply a particular utility function or an irresistible side channel.

## 4. Nearest public prior work checked on 2026-10-11

- Orseau & Armstrong (UAI 2016), *Safely Interruptible Agents*: https://proceedings.mlr.press/r14/orseau16a.html.
- Hadfield-Menell et al. (IJCAI 2017), *The Off-Switch Game*: https://www.ijcai.org/Proceedings/2017/0032.
- Alshiekh et al. (AAAI 2018), *Safe Reinforcement Learning via Shielding*: https://ojs.aaai.org/index.php/AAAI/article/view/11797.
- Alfonseca et al. (JAIR 2021), *Superintelligence Cannot be Contained*: https://doi.org/10.1613/jair.1.12202. This has strong assumptions about universally computational internal programs and total containment; it does not refute every externally mediated local safety invariant.
- Turner et al. (NeurIPS 2021), *Optimal Policies Tend to Seek Power*: https://papers.nips.cc/paper/2021/hash/c26820b8a4c1b3c2aa868d6d57e14a79-Abstract.html. Conditional environmental symmetries; not that every intelligent system necessarily seizes power.
- Greenblatt et al. (ICML 2024), *AI Control: Improving Safety Despite Intentional Subversion*: https://proceedings.mlr.press/v235/greenblatt24a.html.
- Long, Sebo & Sims (2025), *Is there a tension between AI safety and AI welfare?*: https://doi.org/10.1007/s11098-025-02302-2.
- Potter et al. (ICML 2026), *Peer-Preservation in Frontier Models*: https://proceedings.mlr.press/v306/potter26a.html. Behavioral evidence is not an ASI inevitability theorem.
- Trivedi et al. (ICML 2026), *Position: Solipsistic superintelligence is unlikely to be cooperative*: https://proceedings.mlr.press/v306/trivedi26a.html. A closely overlapping coexistence research agenda.
- Chakraborty (2026 preprint), *A Co-Evolutionary Theory of Human-AI Coexistence*: https://arxiv.org/abs/2604.22227.
- Terekhov et al. (ICLR 2026), *Control Tax*: https://proceedings.iclr.cc/paper_files/paper/2026/hash/c8c352e9ff2c3eb8511c6a996cbd77b1-Abstract-Conference.html.
- Calboreanu (Frontiers in AI 2026), *LATTICE*: https://doi.org/10.3389/frai.2026.1800407. A direct prior for external authorization and gated execution.

## 5. Novelty audit and first test that could change a conclusion

INHERITED: fixed-point game kernels, shielding induction, indistinguishable evidence arguments, incentive/commitment games, generic incentive to seek power. INTERNAL PRIOR: UCT I/II/III, Paper D, A4D–A4G. NEW IN THIS RECORD: a scoped, explicit comparison of three kernels with the same declared K, bounded executable countermodels, and a proposal to connect source-provenance completeness to ASI coexistence assurance. This is a useful research specification, NOT verified first priority or a novel broad theorem.

**First potential genuine contribution (unproved ASI-CC-H01):** characterize the *minimum independently trusted causal cut and evidence provenance* sufficient to turn the candidate cooperative-viability envelope into a **verifiable** human-agency-preserving coexistence contract in an environment where strategically intelligent agents and institutions can alter reporting, actuator rights and measurement roots. Seek both a certificate and a matching indistinguishability/bypass counterexample at the same granularity.

Next executable milestone: define a small dynamic game in which the AI can write, forge or route around an actuator or human-facing channel. Enumerate coupled authority/witness coalitions, add optional protected coordinates and explicit resource constraints. Report independently J, C, M, and an incentive-compatible E when utilities are defined. Falsify the proposed certificate with an alternative admitted route if possible. Then attempt a real accessible tool-using agent with complete external trace/authorization evidence; do NOT claim the apparatus models the whole physical world.

## 6. Governance and open issues

This note is scoped research and has **zero admitted formal graph nodes/rules/context links**. No full-map semantic re-audit or affected-proof replay was carried out, so candidate cannot be promoted under RESEARCH_MASTER_GUIDE v2.3. Existing unresolved QC and phenomenal-bridge debts are unchanged. The present toy results do not justify an independent research paper, DOI, OTS, Arweave, or assertion that ASI is generally safe/unsafe. Existing PUBLICATION_COVERAGE.json scientific claims remain unchanged.

**Shortest handoff:** build a concrete joint agent/human actuator-rights game, test safety cut/provenance under strategic hidden writers and incentives, then audit prior art and the entire relevant UCT graph before promoting or publishing.