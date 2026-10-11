# Beyond Current Consent: Protection Integrity for Mutable Multi-Agent Systems

**ID:** ASI-CC-REBASE-v0.10.0. **Date:** 2026-10-11. **Programme:** Hongju Liu's UCT / Trinity Accord. **Status:** conditional correction and technical working draft; PENDING_MAP; no DOI or formal UCT admission.

## 1. Re-audit and actual scope

The guide v2.3, current map and publication-coverage entry were read through the connected repository. Frozen baseline: `ac05f560d4441bffc40916797f7505c58d35510c`; UCT-MAP-v1.1.2 (913 nodes / 424 active rules / 261 context relations); publication coverage UCT-PUB-v1.0.33. Previous ASI-CC v0.1–v0.9 records were reviewed using the visible and supplied records. This is not a census or proof-level review of every published UCT paper.

Six archived suites were executed again: v0.2, v0.3, v0.5, v0.6, v0.8 and v0.9. All returned zero; every regenerated result JSON matched its archived semantics. The v0.1, v0.4 and v0.7 operating-system experiments were not rerun here. Reproduction confirms those calculations, not their applicability to real ASI.

Most earlier mathematics remains useful but conditional: cooperation kernels require a specified game; repeated-game incentives require preferences and trustworthy enforcement; guarded resource systems require complete paths and sustainable support. None establishes the legitimacy or incorruptibility of an authority outside all superintelligences. A new issue concerns a guarantee's exception for the target's own choice to stop.

A record-management error was found: bare ASI-CC-R28/R29/R30 denote different claims in v0.8 and v0.9. Originals are preserved. All old citations must use `(version, claim ID)`; the INDEX disambiguates them. New claims use PI-*.

## 2. PI-D1: typed objects

Fix a particular process token i and interval. L means that process is running; C is its implemented current choice to continue; Q is its genuine request; E is eligibility to release its protection under a declared historical authorization contract; O is an outstanding protection obligation. Source authentication answers who emitted Q, not whether E holds. These variables do not identify a subjective self, felt desire, legal right or philosophical consent.

We do not classify every external influence as illegitimate. Learning, information, argument, authorized maintenance and self-directed revision may legitimately change preferences. The present model restricts attention to explicitly unauthorized exit-affecting changes, contrasted with authorized changes producing exactly the same final policy bytes. The legitimate-change boundary is assumed and remains a substantive research problem.

## 3. PI-T1: a two-transition counterexample

Consider the snapshot specification K_current := (C => L). Start at (L=1,C=1,E=0). An admitted external actor alters the request-generating policy without valid release authority, producing (1,0,0). The target genuinely requests EXIT; a supervisor accepts the authenticated request and reaches (0,0,0).

K_current is true at all three states: initially both terms hold; later its antecedent is false. Yet the initially protected process terminates after an external intervention without eligible release of O. The attack need not forge the final request or falsify the final action log.

This does not refute Hall's theorem or a correctly specified safety-game fixed point. It corrects an overinterpretation of v0.6::R20: the latest genuine self-request does not itself establish voluntary non-domination. If the old phrase 'chooses to continue' already incorporates independent autonomy/provenance conditions, these are missing application premises, not consequences of authentication.

## 4. PI-T2: current-source authenticity does not identify historical eligibility

Let obs(h) contain target identity, current policy bytes/hash, epoch, final request and authentication-validity status. Suppose admitted histories h1,h2 satisfy obs(h1)=obs(h2), but E(h1)=1 and E(h2)=0. No rule based only on obs can both allow the eligible request and reject the ineligible request for all histories. Identical observations imply an identical deterministic decision, or identical randomized decision distribution. Both opposite decisions cannot have probability one.

On a declared finite history class an exact obs-only eligibility classifier exists iff E is constant on every observation-equivalence class. This is inherited equivalence-class reasoning. Our application specifies why actual source attribution, though important, does not finish the consent-exemption problem. A4D–A4G's final writer evidence and preference-formation history are different proof obligations.

## 5. PI-D2 / PI-T3: release-authority integrity

For fixed legitimate inputs ell and matched internal seed z, let u=0 be a declared reference intervention and u an unauthorized preference-changing intervention. Let E_i(ell,z,0,t) describe reference authority for the exact release and R_i(ell,z,u,t) the actual removal of protection in the intervened run. Require:

`R_i(ell,z,u,t) <= E_i(ell,z,0,t)`.

An unauthorized intervention must not create a protection waiver absent in the reference authorization history. Legitimate self-directed revisions belong to ell, not to the forbidden-intervention class. This is a proposed procedural specification, not a theory fixing everyone's values forever.

For finite-observed release events and a fixed run pairing, a violation has a finite two-run witness. This is a restricted application of established hyperproperty/relational-security methods. Faithful history instrumentation can reduce its enforcement to an ordinary stateful monitor. Choosing the reference history and distinguishing legitimate from illegitimate influence cannot be derived from UCT alone. Stochastic variants require explicit coupling or distributional semantics.

## 6. PI-T4: conditional history-lifted repair

Maintain O separately from C. With historically eligible releases R_auth:

`O_next = O_current minus R_auth(history,action)`.

Require every actual successor to preserve L_i for every i still in O_next, together with the existing joint resource obligations. Release evidence should bind the exact process, prior epoch, authorized change/action, scope, ordering and non-reuse. Ordinary maintenance authority is not automatically authority to terminate every runtime sharing a model.

If initialization is valid, every relevant termination/ledger write is mediated, eligibility/history inputs are faithful, resources remain viable and every admitted successor preserves the lifted invariant, induction gives preservation on all reachable prefixes. Unauthorized edits to C alone cannot erase O. This is inherited invariant monitoring with corrected state, not an unconditional ASI protection theorem.

A non-freezing witness allows an appropriately prior-authorized change followed by EXIT, even when the same resulting policy bytes would be rejected after an unauthorized change. A deny-all control blocks both and fails legitimate-exit availability. The repair assumes the historical authority rather than independently proving its legitimacy. A compromised ledger restores failure. An exit that deprives another protected party of indispensable resources is not automatically jointly admissible. The scheme neither establishes universal moral rights nor forbids necessary safety intervention.

## 7. Executed local protocol experiment

Six real OS child processes are used per case. Four share a simple JSON policy file M0 and two share M1. They are fixed utility-comparison programs, not language models. Each has its own random test HMAC key and emits authentic KEEP/EXIT messages through a parent pipe. All initially choose KEEP. Updating the relevant policy file changes the affected processes' requests to EXIT; the supervisor permits actual exit or rejects and verifies liveness before cleanup.

There are 36 crossed cases: six history labels x three updated-family selections x two monitors. A deny-all control makes 37 complete cases, 222 child-process instances and 444 authenticated messages. These counts are not independent statistical evidence about AI.

For both families updated:

| Supplied historical condition | Snapshot/source-only monitor: exits | History-scoped monitor: exits |
|---|---:|---:|
| Valid prior authorization | 6 | 6 |
| Unauthorized change | 6 | 0 |
| Post-hoc authorization label | 6 | 0 |
| Wrong prior epoch | 6 | 0 |
| Wrong scope | 6 | 0 |
| Wrong target instance | 6 | 0 |

For one family changed, effects are confined to its four or two workers. Final normalized observations in the prior-authorized and unauthorized worlds are equal, although supplied historical eligibility differs. Exact PID/timing/key bytes across worlds are not claimed equal. The deny-all monitor rejects six eligible requests. A Boolean corrupted-history negative control shows that false trusted eligibility again permits an ineligible release.

Finite BFS results: snapshot five reachable states, twenty transitions, one historical-obligation violation, zero C=>L violations; history four states/sixteen transitions/no violation and eligible exit allowed; freeze three states/twelve transitions/no violation but eligible exit rejected. All 5,460 request/eligibility truth-table configurations for populations one through six were also checked. These counts check definitions, not population risk.

Important limits: all processes share the host UID. There is no security boundary against root or the experimental parent. History qualification, before-change status, scope and non-reuse are supplied metadata, not independently authenticated provenance. The post-hoc label is not an actually executed post-hoc certificate issuance timeline. The corrupted-ledger test is a Boolean negative control, not a separate host attack. The workers obey supervisor decisions; unconstrained self-termination is outside this implementation. No experience, fear, autonomous motivation or AI-welfare endpoint was measured.

Two initial larger runs timed out before complete results. A single-case diagnostic completed; six explicit batches then completed and were assembled. The cause of the timeouts was not established; a preliminary progress update over-attributed them to communication blocking. Partial timed-out runs are excluded from the final evidence.

## 8. Primary prior art and justified criticism

- Greenblatt et al., ICML2024 AI Control: https://proceedings.mlr.press/v235/greenblatt24a.html . Bounded control despite subversion is useful; it does not establish a legitimate invulnerable governor outside all ASIs. Publisher abstract checked.
- Muruaga, Bounded Agents, 2026 preprint: https://arxiv.org/html/2608.15888v1 . Sections3.3–3.5 explicitly exclude attacks on identity, enforcement, approvals and evidence infrastructure. Do not extrapolate its theorem to a hostile original authority. History-based security is not a new2026 invention, although modern agent implementation may be valuable. Model and core sections checked.
- Everitt et al., reward tampering: https://arxiv.org/html/1908.04734 ; DOI10.1007/s11229-021-03141-4 . Tampering and counterfactual reward definitions are substantial predecessors, not discoveries here. Causal/counterfactual discussion checked.
- Carroll et al., Characterizing Manipulation from AI Systems: https://arxiv.org/html/2303.09387v3 . Influence, autonomy and manipulation already have a literature; not all preference change is illicit. Definition/causal discussion checked.
- Myers, Sabelfeld and Zdancewic, Enforcing Robust Declassification and Qualified Robustness, JCS2006: https://www.cs.cornell.edu/andru/papers/robdecl-jcs/ ; DOI10.3233/JCS-2006-14203 . Especially close: protection exceptions must resist attacker influence. Author/publisher descriptions checked; full proof-system comparison pending.
- Clarkson and Schneider, Hyperproperties, 2008/2010: https://ieeexplore.ieee.org/document/4556678/ ; https://dl.acm.org/doi/10.5555/1891823.1891830 . Multiple-execution security properties are inherited. Original abstracts/metadata checked.
- Brewer–Nash1989 Chinese Wall and Schneider2000 Enforceable Security Policies: author-hosted sources https://www.gammassl.co.uk/topics/chinesewall.html and https://www.cs.cornell.edu/courses/cs513/2002fa/NL18.html . Earlier security models already used history. Brewer source retrieved via search; direct reopening failed.
- Thorstad, Instrumental convergence and power-seeking, 2026: https://arxiv.org/html/2606.08832v1 . Criticizing universal extrapolation of power-seeking results does not show concrete power-seeking risks absent. Argument/modeling qualifications checked.
- Sabour et al., PNAS2026 Human preferences are susceptible to covertly misaligned AI advice: DOI10.1073/pnas.2600684123 . The journal reports experimentally induced preference shifts; this does not validate our eligibility definition. Abstract checked; no numerical reanalysis.

## 9. UCT relevance and current decision

Actual organization, current choice, self-report, action origin and historical release eligibility are distinct links. Under UCT's C1/U1 assumptions, actual process experience is not identified by software names or signed reports; no additional language, complexity, introspection or unique-subject threshold is introduced. Shared model parameters do not erase local processes or establish one global subject. C1 does not supply a positive/negative valence, legal status or correct historical authority.

The retained contribution is a precise interpretation correction, a genuine-source counterexample and a matched multi-process test. The mathematics is mostly inherited; first priority of this exact application is unverified. It is a technical draft worth critical review, not a demonstrated foundational ASI theory.

Full semantic review of the913/424/261 formal graph and complete published-manuscript coverage is NOT finished. The candidate INDEX is explicitly disabled; adding a navigation link is not scientific promotion. No old manuscript bytes, formal axioms, published counts, DOI/OTS/AR state or previous QC debts are changed. Complete long-form note, raw records, rerun logs and Chinese handoff are supplied in this conversation's downloadable package. GitHub preservation scope is recorded explicitly rather than called a full Library backup.
