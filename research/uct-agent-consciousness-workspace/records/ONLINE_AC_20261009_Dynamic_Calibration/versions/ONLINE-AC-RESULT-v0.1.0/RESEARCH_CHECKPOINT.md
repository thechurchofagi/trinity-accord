# Successful calibration need not preserve the information required for the next calibration

**Result ID:** `ONLINE-AC-PROBE-20261009`  
**Date:** 2026-10-09  
**Status:** `PENDING_MAP` research checkpoint; independent review pending.  
**Authoring/review role:** `/root/theory`, with root's independent proof and code review.  
**Scope:** an exact finite action-calibration problem motivated by the UCT memory/use line. No frozen R188 result or UCT-MAP-v1.1.2 item is changed. The mathematics does not depend on UCT's truth.

## 1. Outcome and current paper judgment

The initial proposal to add history-dependent readers to static memory transport did not itself yield a new result. A fixed target already decoded by a persistent reader can simply be cached. General invariant transport and inductive interface composition are already in the project, and adaptive readout of drifting neural representations has substantial external predecessors. Those routes are recorded below as rejected novelty candidates.

A more concrete problem does produce a useful finite result. A controller can successfully act on the same fixed goal after one unknown rewiring while failing to learn what it will need for the next rewiring. With at least three ports, one binary-vector probe after an arbitrary possible transposition requires the controller to distinguish every possible old wiring, even when the only goal is one fixed effect port. Static control of that goal requires only its old inverse port. Moreover, from a completely known initial wiring, one probe per round cannot guarantee success for two rounds. This remains true with complete terminal-action feedback and unlimited retention of the observed history. For the three-port uniform drift law, the exact probability that both round deadlines are satisfied is at most **7/8**, and that value is attained. Two probes per round permit an indefinitely repeatable construction in the same three-port model.

This is more specific than appending a time index to RT or restating that endpoint success differs from continuous use. It exposes and quantifies failure to preserve the premise of an otherwise correct one-round repair. It is still a small classical-method application, not a demonstrated foundational breakthrough or an established standalone-paper contribution. The appropriate current disposition is to preserve it for independent review as a potential **dynamic extension of AC**, then judge the net contribution together with the already disclosed corpus. No external historical priority is claimed.

## 2. Prior coverage and actual attempts rejected

| Predecessor inspected | Already available result | What it excludes as a new claim here |
|---|---|---|
| R157 effective `COORDINATE_TRANSPORT` and `SEMANTIC_RESIDUAL` | Isomorphism transports correctly grounded definable relations; a familiar experiential name needs a separate bridge. | Renaming a retained task relation as a new experiential theorem. |
| TE effective `SELECTED_TRANSPORT`, `RELAY_PROVENANCE`, `ACTUAL_TEMPORAL_BRIDGE` | Selected relational transport; finite faithful relay substitutions preserve ancestry/value; actual read/use needs grounding. | A fresh theorem saying a correctly copied target can survive moving supports. |
| TH effective signal/noise, read-port, fresh-chain, and reused-mask nodes | Exact finite-field recovery, stored versus read information, no regeneration across a complete cut, and correlated information returning later. | Another endpoint rank formula or parity-chain recovery formula. |
| IE `QUERY_SUFFICIENCY`, `LATE_QUERY`; R149 and R177 | Fixed target-vector factorization; query timing; inverse-compensated readout. | Claiming that later questions or installed inverse maps are new issues. |
| R167–R170 effective contextual-use and coverage results | Redundant routes, compensation timing, partial views, calibrated bounds, and unresolved remainder. | Another isolated null-test or late-compensation warning. |
| R171 `INDUCTIVE_RANGE_CLOSURE`; R172 `INTERFACE_COMPOSITION_THEOREM` | All-successor inductive coverage and composition only when actual interface and input conditions remain valid. | A general theorem that an invariant persists if every transition preserves it. |
| Published RT/TH v1.0.0, §§3–8, 11 | Static route-blind recovery, target-invariant transport, route metadata, access and endpoint qualifications; history-dependent readers are expressly left open. | Calling the presence of a remembered route or an installed inverse a new solution. |
| AC-RESULT-v1.0.0, §§3–6, 8 | Exact calibration classes, goal-specific control, task-relative retained-state counts, and explicit exclusion of changing connections. | Calling permutation identification, its binary signature bound, or static task factorization new mathematics. |

These effective-node readings are of the frozen graph statements, proofs, limits, and source locators. They are not a claim to have recovered and reread every original source file. The published RT/TH and the saved AC checkpoint were read directly. The main publication assessment is `RESIDUAL_RESEARCH_ASSESSMENT.md`; the full published-map overlay is a separate audit product.

### Rejected attempt A: a fixed remembered target with an unrestricted persistent reader

**`ONLINE_AC:CACHE_CONTROL` — exclusion witness, not a science-map addition.** If a reader has already correctly decoded a fixed target \(T\), may keep a persistent register with enough states for \(T\), and must merely answer that same target later, set the register to \(T\) once and thereafter output it. Later changes to an external representation do not create a calibration requirement for this task.

This directly defeats the unspecialized proposal “derive a cost for maintaining the same memory while its representation changes.” A nontrivial problem must independently justify reader replacement, a memory bound, genuinely fresh target information, or a current action requirement that cached content alone cannot fulfill. Such a condition cannot be added merely to manufacture difficulty.

### Rejected attempt B: general online drift compensation

Rule and O'Leary's 2022 PNAS paper already studies stable readout of changing codes using plasticity, redundancy, and recurrent constraints without an external error signal. Micou and O'Leary's 2026 PLOS paper expressly constructs a reader that uses prior tuning and current activity statistics without fresh stimulus labels, and studies ambiguity, noise, drift statistics, and accumulated error. The former's abstract and accessible primary record and the latter's model and results sections were inspected. A June 2026 preprint by Zaid and Schaffer also proposes a geometry-based adaptive-decoding framework; its primary full-text retrieval returned 403, so only abstract-level overlap is recorded. These are reasons to avoid claiming the general adaptive-reader question as an untouched discovery. See the source interface in section 12.

### Rejected attempt C: one known old wiring and one involution

If the old wiring \(\pi\) is known, the new one is \(\sigma\pi\), and \(\sigma^2=I\), applying the old inverse to an observed image implements the inverse needed for the target. This is elementary composition. Likewise, calibration before an unknown future goal versus calibration after a known goal is already part of AC/IE/RT's task-access framework. That one-round observation is inherited scaffolding here.

The substantive next question is whether successful use preserves the knowledge on which that one-round construction depends. It need not.

## 3. Full finite contract

**`ONLINE_AC:CONTRACT`.** Fix \(n\ge3\) labelled command ports, \(n\) labelled effect ports, and one goal port \(g\). Labels refer to fixed ports in this finite model. Let \(e_g\) be its binary unit vector. A physical binary command vector \(u\in\{0,1\}^n\) acts on the same plant state \(x\in\{0,1\}^n\) by

\[
x\leftarrow x\oplus P_\pi u,
\]

where \(P_\pi\) is the permutation matrix taking command port \(i\) to effect port \(\pi(i)\). Rewiring changes this action map; it does not relabel or permute the existing plant state.

At the beginning of each round,

\[
\pi_t=\sigma_t\circ\pi_{t-1},
\]

where \(\sigma_t\) is either the identity or one transposition of two effect ports. The wiring is then fixed throughout the round. A round consists of:

1. The controller chooses one arbitrary parallel binary probe \(u_t\), using all information it currently has.
2. The probe changes the plant and returns its **entire \(n\)-bit effect vector** \(y_t=P_{\pi_t}u_t\).
3. The controller issues one terminal parallel binary command \(v_t\), which also changes the plant. The main model returns its entire effect vector \(z_t=P_{\pi_t}v_t\).
4. The deadline is scored. Success means that this round's **net effect**, including the probe, is exactly

\[
y_t\oplus z_t=e_g.
\tag{1}
\]

The terminal command may be zero or may activate multiple ports. “One command” means one committed binary vector, not one activated actuator. Calibration is therefore not treated as a free read or a reset. The goal is the same named toggle every round, even if the target port's current value alternates. Requiring a constant final value already attained would allow a trivial do-nothing controller and would be a different problem.

Initial plant state is known. With the complete main-branch effect feedback and issued commands retained, the controller can reconstruct every actual plant state. It may keep its entire observed history and use independent randomness. No hidden current-wiring state, extra action, within-round rewiring, or further correction before the same deadline is supplied. The controller need not know whether the allowed transposition occurred.

For the worst-case results, the quantifier is over every fixed legal drift sequence. An adversary need not adapt to an actual private random tape. For the exact three-port probability, \(\pi_0=I\), \(g=0\), and the two \(\sigma_t\) are independent uniform choices from

\[
\{I,(01),(02),(12)\}.
\tag{2}
\]

This is a uniform law on 16 fixed two-round sequences. It is not a uniform law on all six current permutations at every time.

The scored prefixes are the **round deadlines**. Nothing requires the plant to have its target value immediately after the calibration probe, and this is not a theorem of uninterrupted correct state at every microstep.

## 4. One-round attainment from the complete old wiring

**`ONLINE_AC:ONE_ROUND_REPAIR` — inherited elementary construction.** Suppose the complete old \(\pi\) is known. Set \(a=\pi^{-1}(g)\) and probe \(u=e_a\). The returned unit vector is \(y=e_h\), where \(h=\sigma(g)\). Because the allowed change is an involution, \(\sigma(h)=g\). Therefore

\[
b=\pi^{-1}(h),\qquad v=e_a\oplus e_b
\tag{3}
\]

gives

\[
P_{\sigma\pi}(u\oplus v)=P_{\sigma\pi}e_b=e_g.
\]

If the probe itself already achieved the goal, \(v=0\). Otherwise the terminal vector both cancels the probe's wrong toggle and performs the desired toggle. Thus its actual physical effect is included in the score.

This establishes current success, not full identification of \(\sigma\pi\). If \(\sigma\) only exchanges non-goal ports, the probe returns the same value as no change.

## 5. The old-state information required for one-probe adaptation

**`ONLINE_AC:OLD_WIRING_INJECTIVITY`.** Let \(\mathcal H\subseteq S_n\) be any nonempty admitted family of possible old wirings. Before the fresh change, the controller has a retained state \(m(\pi)\). Count **all old-wiring-correlated information accessible to the controller** in this state, as required by AC's memory contract. If one probe and one terminal command must achieve (1) for every \(\pi\in\mathcal H\) and every allowed fresh \(\sigma\), then \(m\) is injective on \(\mathcal H\). Conversely, an injective retained state permits the one-round construction above.

In particular, for \(\mathcal H=S_n\), the minimum number of distinguishable retained old-wiring states is

\[
M_{\min}^{\text{one-probe adaptation}}=n!,\qquad n\ge3.
\tag{4}
\]

Static exact control of the same singleton goal requires only \(n\) states under AC3. Equation (4) concerns distinctions necessary for this specified adaptive capability; it does not count every physical state of the controller.

If the old wiring is publicly fixed as identity, then \(\mathcal H\) is a singleton and no nontrivial retained wiring state is required. Equation (4) is not a storage requirement imposed on that initial condition. Hardware settings, weights, accessible plant states, and external records correlated with an uncertain old wiring must all be included in \(m\); excluding them would invalidate the lower bound. The zero-error quantifier covers every admitted old wiring and every allowed next transposition. It is not an average-error assertion under an arbitrary prior or a theorem for a smaller permitted drift family.

**Proof.** Fix any retained-state cell and the probe \(u\) chosen in that cell. For each old \(\pi\) in the cell, consider the no-change response \(y=P_\pi u\). Any transposition of two effect ports having equal bits in \(y\) leaves that observation unchanged. If \(g\) shares its bit value with another effect port \(h\), no change and the transposition \((gh)\) give the same probe response but require distinct inverse-goal commands. Indeed, (1) uniquely requires

\[
v=u\oplus P_{\sigma\pi}^{-1}e_g.
\tag{5}
\]

Consequently, \(g\) must be alone in its bit class in \(y\). The probe must be either the singleton old inverse-goal port or its complement. Since \(n\ge3\), these have different cardinalities; one fixed \(u\) therefore selects the same alternative throughout the retained-state cell. All old wirings in that cell have the same \(a=\pi^{-1}(g)\).

Now choose any effect port \(h\), using no change when \(h=g\) and \((gh)\) otherwise. Every old wiring in the cell produces the same probe response: \(e_h\), or its complement. The required net inverse-goal command is \(e_{\pi^{-1}(h)}\). A single terminal rule can satisfy all those worlds only if \(\pi^{-1}(h)\) is equal throughout the cell. This holds for every \(h\), so the entire old wiring is equal throughout the cell. The encoding is injective. The construction in section 4 proves sufficiency. \(\square\)

Independent randomization cannot avoid the zero-error conclusion. On a finite full-support input family, probability-one success on every input yields, after conditioning on independent tapes, deterministic legal strategies with the same requirement. Stochastic retained states shared by two possible old wirings face the same response conflict. An extra correlated seed or uncounted external record would change the information contract.

The restriction \(n\ge3\) is necessary. With two ports, one probe of either fixed command identifies the current two-port permutation directly, irrespective of the old one; no old-wiring memory is needed. This exception was checked explicitly.

## 6. Two rounds cannot be guaranteed with one probe per round

**`ONLINE_AC:TWO_ROUND_OBSTRUCTION`.** Under the contract with \(n\ge3\), a completely known \(\pi_0\), and the same fixed singleton goal, no controller using one probe per round guarantees (1) at both of the first two deadlines. Complete terminal feedback and unlimited memory of the returned history do not remove the obstruction.

**Proof.** A controller that guarantees the first deadline must isolate the old inverse-goal port in its first probe, by the first part of the preceding proof. Choose two distinct non-goal effect ports \(r,s\). The first-round alternatives

\[
\sigma_1=I \quad\text{and}\quad \sigma_1=(rs)
\]

produce the same probe observation and require the same correct terminal command. Moreover, on any successful round,

\[
z_1=y_1\oplus e_g.
\tag{6}
\]

Thus complete terminal feedback is already determined by the observed probe and the fixed goal. Both alternatives give the same physical end state, as well as the same issued commands and returned history. They nevertheless leave two different old wirings for round two. `OLD_WIRING_INJECTIVITY`, applied to that two-element family and the allowed next change, rules out guaranteed second-round success. \(\square\)

For a concrete indistinguishable pair in the three-port example, start at identity and use the first probe \(e_0\). No change and the non-goal swap \((12)\) both return \(e_0\); the successful terminal command is zero and both end states are \(e_0\). If the next change is \((01)\), the two resulting wirings are

\[
(0\mapsto1,1\mapsto0,2\mapsto2),\qquad
(0\mapsto1,1\mapsto2,2\mapsto0).
\]

A second probe of port 0 returns effect port 1 in both, but the required net inverse-goal actions are ports 1 and 2. The general proof covers every possible second probe; this displayed pair illustrates one simple choice and is not substituted for that universal argument.

The failure comes from missing observations of non-goal changes, not from insufficient storage space. Preserving the complete observed history cannot distinguish histories that are identical.

## 7. Exact three-port two-round value: 7/8

**`ONLINE_AC:TWO_ROUND_VALUE`.** Under the independent uniform law (2), the maximum probability that **both** deadlines satisfy (1) is

\[
\max_\text{legal policies}\Pr(E_1\cap E_2)=\frac78.
\tag{7}
\]

The optimum includes full terminal feedback. Independent randomization cannot improve it because average success under a fixed law is affine in the mixture of complete deterministic policies.

**Proof.** Any deterministic policy that fails on one of the four first-round drift choices has first-round success at most \(3/4\), and hence joint success at most \(3/4\). A policy improving on that must succeed on all four first-round choices. Its first probe is therefore \(e_0\) or its complement, and its first terminal rule is forced by (5).

With total probability \(1/2\), the goal port is exchanged with a non-goal port. Its probe response identifies that exchange and therefore the complete first-round wiring; section 4 achieves second-round success one. With probability \(1/2\), the probe response leaves the old wiring equally likely to be \(I\) or \((12)\). Fresh uniform drift produces the following second-round law, written as command-to-effect tuples:

| Current wiring | Conditional mass | Inverse port of goal 0 |
|---|---:|---:|
| `(0,1,2)` | 2/8 | 0 |
| `(0,2,1)` | 2/8 | 0 |
| `(1,0,2)` | 1/8 | 1 |
| `(1,2,0)` | 1/8 | 2 |
| `(2,0,1)` | 1/8 | 1 |
| `(2,1,0)` | 1/8 | 2 |

Every three-bit probe is constant, a singleton, or the complement of a singleton. Constant probes leave best success \(1/2\). A probe of port 0 identifies the inverse-goal port on the mass-\(4/8\) response at effect port 0, while each of the two remaining response cells has two equally weighted conflicting inverse-goal ports. Its optimum is \(6/8\). Probes of ports 1 and 2 each yield three cells with maximum masses \(2/8,2/8,2/8\), also \(6/8\). Complementing a probe complements its observation and leaves exactly the same distinguishability. The exact conditional optimum is therefore \(3/4\). Equation (6) shows that first terminal feedback cannot refine the ambiguous branch.

Combining the two first-round branches gives

\[
\frac12\cdot1+\frac12\cdot\frac34=\frac78.
\]

Each branch has an explicit attaining rule. A complete attaining policy and its 16 traces are saved in the result receipt. \(\square\)

This is a fixed-prior average over complete drift sequences. It does not assert per-sequence success \(7/8\), a per-round error probability of \(1/8\), or a minimax randomized value against every sequence. The existence of a positive average loss also rules out a policy with guaranteed zero error for all 16 sequences.

## 8. Positive construction and the feedback control

**`ONLINE_AC:TWO_PROBE_REPAIR`.** For three ports, two full binary-vector probes per round suffice at every finite horizon, with the same actual plant and deadline rule. Probe command ports 1 and 2 individually. Their two returned unit vectors identify their current effect destinations; bijectivity identifies the remaining destination. Let \(\widehat\pi_t\) denote the resulting complete current wiring. Set

\[
v_t=u_t^{(1)}\oplus u_t^{(2)}\oplus P_{\widehat\pi_t}^{-1}e_g.
\tag{8}
\]

The round's total command is exactly the inverse-goal command, so its actual net effect is \(e_g\). This works independently in every round because the wiring remains fixed during its two probes and terminal action. It is a direct AC calibration construction plus explicit compensation for the probes' effects. The arbitrary-horizon statement follows algebraically per round, not from merely testing a two-round run.

For general \(n\), the inherited distinct-binary-signature schedule with \(\lceil\log_2n\rceil\) probes similarly identifies the entire current wiring and permits net-effect correction. The result here does not establish that this many probes are necessary for indefinitely maintaining one fixed goal when more than one probe is allowed.

**`ONLINE_AC:FEEDBACK_AND_OBJECTIVE_CONTROL`.** Full terminal feedback does not improve (7). If the first deadline is dropped and the objective is only the **second round's net increment**, however, full first terminal feedback can be used for additional calibration and the optimum becomes one. The first probe and first terminal action may then be selected as two identifying probes, without a first-round success constraint. Once \(\pi_1\) is known, section 4 solves the second round.

This alternate objective is named `last_round_increment_only`. It does **not** require the actual final plant state to equal the value it would have under two successful rounds. The first-round error may remain in the plant. The first draft's name `last_prefix_only` was corrected during root review to prevent that confusion. A standalone final-plant-state comparison to the two-success target zero would itself be trivial here: issuing only zero commands would attain it. No such comparison is offered as evidence of memory recovery.

For completeness, a separately labelled variant withholds the terminal effect observation and does not reveal it before the next probe. The probe instrument returns the effect increment only, not an additional absolute-state observation. The verifier finds \(7/8\) for both that variant's all-prefix and last-round-increment objectives. This is a different observation interface; the main result already permits the stronger, complete-feedback interface and does not rely on the withheld-feedback variant.

## 9. Actual finite verification and source fields

The verifier `next_probe/check_online_calibration.py` was executed locally with exact integer counts and rational final values. It enumerates actual binary commands and actual permuted effects, rather than importing the injectivity theorem or its reduction.

- For each of the six known three-port old wirings, it checks all eight probes; exactly two permit guaranteed one-round control.
- For every one of the 15 two-element old-wiring families, it checks every probe and the terminal-action cells; none permits guaranteed control after the fresh change.
- It checks the two-port exception directly.
- In each two-round feedback/objective variant, it enumerates eight first probes and all **3,088 first terminal policies**. For every resulting observable history it optimizes all second probes and all eight terminal vectors in each response cell. Disjoint histories can be optimized independently, so this is exhaustive finite dynamic programming over the legal policy class; it does not materialize the full Cartesian product of every complete policy tree.
- It then executes one attaining complete policy on all 16 fixed sequences and records commands, feedback, wiring, actual plant end states, and both round success flags.
- The two-probe construction is executed on all 16 two-round sequences. Its longer-horizon validity is proved in section 8.

| Returned terminal feedback | Objective | Exact optimum | First terminal policies | Distinct cached second-stage problems |
|---|---|---:|---:|---:|
| Withheld | Both round increments correct | 7/8 | 3,088 | 6 |
| Withheld | Second round increment only | 7/8 | 3,088 | 7 |
| Complete | Both round increments correct | 7/8 | 3,088 | 6 |
| Complete | Second round increment only | 1 | 3,088 | 8 |

In the all-prefix dynamic program, first-failed worlds contribute zero to joint success. Removing their score weight does not grant the reader knowledge of which world occurred: the chosen probe and terminal action remain a single policy for each actually observed history. Such worlds cannot contribute to the joint objective under any continuation. Root independently reviewed this point and the scoring rule.

The receipt's central fields are `contract`, `one_round_known_old_wiring`, `one_round_two_old_wirings`, `n2_exception_perfect_probes_without_old_wiring`, `two_round_policy_search`, and `two_probe_repair`. Each policy-search entry includes exact success, enumeration counts, the attaining policy, and every attainment trace.

Current preserved execution anchors:

| Artifact | SHA-256 |
|---|---|
| `next_probe/check_online_calibration.py` | `bc829ade2c93197c86aed4646ae119628b8b4ebe25181f595dd6b7ee605bd304` |
| `next_probe/EXACT_RESULTS.json` | `7054e1f31175f799c71e3bd6e21430017f90e557bb3659ef731faa4d4b8aa8a7` |
| Captured corrected-run stdout | `8c4e8e033d2f8ec055b847aa894640a2923fe7e093dd7344282d08a8c28e289e` |

`RUN_RECEIPT.json` records the actual command, timestamps, exit status zero, hashes, and empty stderr. `REVIEW_CHANGES.md` records the scoring-name correction and the initial execution hashes. The first draft's original bytes were not separately retained before overwrite and were not reconstructed. The preserved corrected rerun uses the same code and produces the same result hash as the preceding corrected execution. This is one local verifier and a manual proof, not two independently implemented verification systems or an empirical experiment.

## 10. Increment, limits, and what must not be claimed

The useful project-level increment is the **dynamic preservation of a calibration premise**: a correct action does not generally preserve the information needed to correct the same action after another allowed organizational change. It is quantified here by the injectivity requirement, an all-history two-round obstruction, and the exact three-port \(7/8\) law with full feedback. AC's static singleton sufficiency count and its explicit changing-connection exclusion make the distinction precise.

The proof still uses ordinary indistinguishable-world reasoning, finite decision optimization, and task-specific state sufficiency. R171/R172 already explain why local certificates require preserved interface premises; RT already distinguishes a route-aware reader from a blind one. This example is a concrete failure and resource calculation under a newly specified dynamic access contract. It should not be marketed as the invention of dynamic state abstraction, active system identification, memory lower bounds, or feedback control.

The proposed stable claim IDs in this note are identifiers for review, not enabled scientific graph nodes. The classical one-round construction, cache exclusion, and two-probe signature repair should be labelled inherited or control material if later integrated. The precise new finite statements are `OLD_WIRING_INJECTIVITY`, `TWO_ROUND_OBSTRUCTION`, and `TWO_ROUND_VALUE`, with their complete common contract retained.

The model does not establish that a biological or deployed AI controller has these ports, a permutation action law, the stated change family, or the stipulated command deadlines. A command law with continuous feedback and additional intra-action corrections is a different class. So is a drift that alters the plant state, acts during calibration, is known to omit some port pairs, or supplies a logged wiring-change signal. A scalar feedback instrument is weaker than the full-vector instrument proved here and requires separate achievable bounds.

A fixed target memory can remain correctly cached throughout this example; what fails is its conversion into the next correct physical effect. This is a selected functional relation, not a proof of the loss of a remembered experience, personal identity, agency feeling, or any named quale. Under UCT's existing U1/P3 commitments, independently continuing local processes retain their status regardless of this control score. Comparing one-probe and two-probe budgets is not, by itself, an independently grounded fixed-J comparison or a quantity of experience.

## 11. Narrow next step and stopping condition

The present checkpoint should receive independent proof, protocol, and publication-overlap review before any map integration or paper decision. The finite example has a positive repair and a useful obstruction; it should be assessed on that content, not on its node count or how readily a manuscript can be written.

One unresolved mathematical question is whether, for larger \(n\), a bounded multi-probe policy can maintain this one fixed goal indefinitely with fewer probes per round than complete reidentification. The present result gives a lower bound of two and an inherited upper bound \(\lceil\log_2n\rceil\); these coincide for \(n=3,4\), but no equality is established for \(n\ge5\). A meaningful extension would characterize what uncertainty can be allowed to accumulate while remaining correctable under the next permitted change. Repeating general belief-state recursion without solving a specific remaining case would not add the needed knowledge.

No further model expansion is needed merely to rescue standalone-paper status. If the current result is covered by earlier dynamic calibration or task-abstraction literature, record that overlap and retain it as a cited application. Whether it helps a larger AC/IL synthesis become worth an independent paper remains a separate evidence-based decision.

## 12. Sources and reading interface

1. **AC-RESULT-v1.0.0**, *Action-Port Calibration and Task-Relative Self-Model Sufficiency*, §§2–8. Read from `publication_audit_work/sources/workspace/records/AC20261009_Action_Calibration/RESEARCH_CHECKPOINT.md`. It explicitly excludes changing connections from its exact theorems. Publication/disclosure status is tracked separately; it is a project predecessor, not new material in this note.
2. **Task-Relative Continuity Through Changing Representations**, v1.0.0, §§3–8, 11. [DOI 10.5281/zenodo.23251651](https://doi.org/10.5281/zenodo.23251651). Full local published text read; source path is in the residual assessment.
3. **UCT-MAP-v1.1.2 effective graph**, selected predecessors listed in section 2. Local path: `uct/research/uct-agent-consciousness-workspace/versions/UCT-MAP-v1.1.2/UCT_EFFECTIVE_GRAPH.json`. The published MGTD attachment supplies the older disclosed map baseline; no later graph relabelling creates originality.
4. **Rule, M. E., and O'Leary, T. (2022).** *Self-healing codes: How stable neural populations can track continually reconfiguring neural representations*. PNAS 119(7), e2106692119. [DOI 10.1073/pnas.2106692119](https://doi.org/10.1073/pnas.2106692119). Primary abstract and accessible article record inspected for overlap; no claim to a complete theorem-by-theorem rereading in this probe.
5. **Micou, C., and O'Leary, T. (2026).** *Statistics of cortical representational drift can enable robust readout*. PLOS Computational Biology 22(6), e1014297, published 8 June 2026. [Full primary article](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1014297). Introduction and normative adaptive-decoder/drift-comparison result sections read. This source already makes the non-oracular historical-reader problem explicit; it is not represented as solving the present permutation/control contract.
6. **Zaid, H., and Schaffer, E. S. (2026).** *Preserved geometry during representational drift enables stable perception and memory*. [bioRxiv DOI 10.64898/2026.06.25.734656](https://doi.org/10.64898/2026.06.25.734656). Abstract-level scope only; primary full-text retrieval was blocked. No detailed originality comparison or theorem attribution relies on inaccessible content.

External historical priority for the exact dynamic permutation result is **UNVERIFIED**. This source list is a targeted predecessor check, not an exhaustive search of adaptive control, permutation learning, or finite-state identification.
