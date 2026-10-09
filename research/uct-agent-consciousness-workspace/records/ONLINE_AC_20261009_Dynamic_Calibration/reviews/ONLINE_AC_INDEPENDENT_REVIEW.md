# Independent review of the online action-calibration checkpoint

**Review ID:** `ONLINE-AC-INDEPENDENT-REVIEW-20261009`  
**Reviewed result:** `ONLINE-AC-PROBE-20261009`, the one-probe obstruction and three-port two-round benchmark.  
**Reviewer:** `/root/map_audit`; scoped independent receipt replay by `/root/map_audit/online_trace_check`.  
**Disposition:** **PASS for the explicitly conditional mathematics, observation protocol, and reviewed finite calculation. PENDING_MAP remains in force.**  
**Scientific promotion:** none. This review does not change the effective graph, any previous review status, the pending AC/IL modules, or publication counts.

## 1. What passed, and what this review covers

The three central statements are valid under the checkpoint's full finite contract:

1. For \(n\ge3\), a one-probe controller that must adapt to identity or any single fresh effect-port transposition must distinguish every admitted old wiring. The minimum is \(|\mathcal H|\) retained information states for an admitted old-wiring family \(\mathcal H\), and \(n!\) only when \(\mathcal H=S_n\).
2. Even from known initial wiring and with complete terminal feedback and unlimited retention of all observations, one probe per round cannot guarantee the fixed net goal at both of the first two round deadlines.
3. For three ports, initial identity, and the specified independent uniform law on four changes per round, the optimal probability of satisfying both deadlines is exactly \(7/8\).

I independently derived the indistinguishability arguments and the \(7/8\) decomposition, then checked the author's final statement and entire original verifier. I read the complete AC checkpoint and its 26-node, 11-rule, 8-context pending overlay, and reread the specific effective-map contracts listed in section 8. I also directly read UCT III v1.0 §§6.4–7.2 for the published dynamic-closure predecessor. This is a scoped follow-up review; it is **not another 1,608-item whole-map audit** and does not reread every original source behind those old map items.

The extra executed check addressed a concrete remaining risk: whether the serialized attaining policies really follow their permitted observations and whether their saved scores include both probes' and terminal actions' effects on the persistent plant. A separately written simulator replayed all **64** saved traces, matched **1,088** trace fields, and independently optimized the eight-world ambiguous one-round subproblem. It did not import or execute the original optimizer and did not independently enumerate all 3,088 first-round terminal policies. The general proofs and original code review supply the parts that a witness replay alone cannot establish.

The mathematical claims do not require UCT to be true. No biological, deployed-AI, phenomenal, subject-count, or complete-organization premise was discharged. A later proposed five-port closed controller is a separate follow-up and is outside this reviewed checkpoint; this report makes no claim about that certificate.

## 2. Exact evidence anchors

Paths below are relative to `/workspace/scratch/328b6dbb55c2`. SHA-256 identifies the bytes actually reviewed; later revisions require a new version or an explicit review amendment.

| Evidence | Path | SHA-256 |
|---|---|---|
| S1: reviewed note | `publication_audit_work/NEXT_RESEARCH_PROBE.md` | `e4cc302bae8b722eb109605dfdebafd2f9d13902e42bb5841ccab04880c16b5c` |
| S2: complete original verifier | `publication_audit_work/next_probe/check_online_calibration.py` | `bc829ade2c93197c86aed4646ae119628b8b4ebe25181f595dd6b7ee605bd304` |
| S3: original exact results | `publication_audit_work/next_probe/EXACT_RESULTS.json` | `7054e1f31175f799c71e3bd6e21430017f90e557bb3659ef731faa4d4b8aa8a7` |
| S4: preserved corrected run receipt | `publication_audit_work/next_probe/RUN_RECEIPT.json` | `5b84310de0228ed0e3f0b454805780ebd6b17e0e405731aa90d8cb05b9cf4fab` |
| S5: correction history | `publication_audit_work/next_probe/REVIEW_CHANGES.md` | `7656815978eefd166d9c22ae74a5fba243e227e80d225467e20ae5a8e249955b` |
| S6: independent replay program | `publication_audit_work/next_probe/independent_trace_replay.py` | `f5a522fc26797e3dfecc62cdcc19c94d07e11ccdd4b0985ad181ec7a58b3214b` |
| S7: independent replay result | `publication_audit_work/next_probe/INDEPENDENT_TRACE_REPLAY.json` | `5bc03613d2e99f71ddd6bc78962a11e3411f1d197c6dd5449f159c21cb48986c` |
| S8: static AC checkpoint | `publication_audit_work/sources/workspace/records/AC20261009_Action_Calibration/RESEARCH_CHECKPOINT.md` | `4277fd417003554ee10d7e1a22e594b7e4094f6335c349d5a047474a9ff8f058` |
| S9: pending AC overlay | `publication_audit_work/sources/workspace/records/AC20261009_Action_Calibration/MAP_EXTENSION.json` | `c2544dce8abc0e3867a4eb603528a880e17017d72bc34551fe0b8eaefb1b817a` |
| S10: effective graph used for compatibility | `uct/research/uct-agent-consciousness-workspace/versions/UCT-MAP-v1.1.2/UCT_EFFECTIVE_GRAPH.json` | `0973600f1be5cf21614592ca901112b26f9f0c9f6df36294a5dbb049efcf7612` |
| S11: UCT III v1.0 | `publication_audit_work/sources/fulltext/uct_iii/C_UCT_III_v1_0.md` | `2721672485b055c26ec83a64d36fd5713e349cabe0494edd52b626aa7b9903e2` |

S4 records the actual corrected execution, exit status zero, and the S2/S3 hashes. Its stdout hash is `8c4e8e033d2f8ec055b847aa894640a2923fe7e093dd7344282d08a8c28e289e`; preserved stderr is empty. S5 explicitly records that the first draft's original bytes were overwritten before a separate archive was made. This review does not reconstruct those bytes or treat their reported old hashes as equivalent to a preserved artifact. The new independent replay supplements the corrected evidence; it does not retroactively change the history recorded by S4/S5.

## 3. The contract necessary for the conclusions

The plant is \(x\in\mathbb F_2^n\). A labelled command vector \(u\) acts by

\[
x\leftarrow x\oplus P_\pi u.
\]

Before each round, \(\pi\) changes to \(\sigma\pi\), where \(\sigma\) is identity or one arbitrary effect-port transposition. The wiring is fixed throughout the round. Rewiring changes the action law and **does not permute the stored plant state**. Each probe or terminal command may be any entire binary vector, including zero. Counting one probe therefore counts one vector command and its full vector observation, not one activated actuator or one observed bit. These are model premises, not experimentally established properties of a nervous system. [S1 §3; S2; S8 §2]

The main interface returns the complete probe effect \(y=P_{\sigma\pi}u\), then the complete terminal effect \(z=P_{\sigma\pi}v\). The terminal observation arrives after the command has been chosen. No further correction is available before that round's deadline. Success is

\[
E:\quad y\oplus z=e_g.
\]

Both actions physically affect the same plant. With arbitrary starting state \(x_0\), the successful round ends at \(x_0\oplus e_g\). It need not have its target value immediately after the probe. Thus “all prefixes” in the checker means **all scored round deadlines**, not every physical microstep. No continuously correct trajectory theorem follows.

All accessible old-wiring-correlated information must be included in the retained state: hardware settings, weights, accessible plant state, external records, and retained observations. Independent private randomness is allowed; an uncounted wire-correlated seed is a changed problem. The controller may retain all its actual observations. It receives no direct wiring label, drift log, or additional absolute-state measurement beyond the specified interface. [S1 §§3,5; S8 §§2,6]

For the worst-case statements, the requirement is success on every fixed legal change sequence. The adversary need not see a private random tape. The numerical benchmark instead fixes a probability law: \(n=3\), \(\pi_0=I\), \(g=0\), and two independent uniform choices from \(\{I,(01),(02),(12)\}\). This is a distribution on 16 fixed sequences. It is not a uniform distribution on the six current permutations at every round and is not a minimax evaluation.

## 4. Independent proof of the old-wiring information requirement

Fix a retained-state cell containing old wirings \(\mathcal C\), and fix the independent policy tape. The controller issues the same first probe \(u\) on every old wiring in that cell. Write \(S\) for the support of the no-change observation \(P_\pi u\).

**Isolation lemma.** For any fixed old \(\pi\), the goal port \(g\) must be alone in its probe-bit class. Otherwise choose \(h\ne g\) with the same bit as \(g\). Identity and the transposition \((gh)\) return the same probe vector, since swapping equal bits changes nothing. Their unique successful terminal commands differ, because for any current wiring \(\rho\),

\[
P_\rho(u\oplus v)=e_g
\quad\Longleftrightarrow\quad
v=u\oplus P_\rho^{-1}e_g.
\tag{R1}
\]

Consequently the controller cannot correct both worlds from that shared observation. The only safe probe supports are the old inverse-goal singleton or its complement.

For \(n\ge3\), those supports have different cardinalities. One common \(u\) fixes which alternative is used throughout \(\mathcal C\), and all old wirings in the cell must share \(a=\pi^{-1}(g)\).

Now let \(h\) be any effect port. Use drift \((gh)\), with identity when \(h=g\). Every \(\pi\in\mathcal C\) gives the same response \(e_h\), or its complement. The correct net command is

\[
P_{(gh)\pi}^{-1}e_g=e_{\pi^{-1}(h)}.
\tag{R2}
\]

A common response-dependent terminal action can work only if \(\pi^{-1}(h)\) is constant on the retained-state cell. This must hold for every \(h\), so the entire inverse permutation is constant. The cell has at most one old wiring. Thus \(m\) must be injective on the admitted family \(\mathcal H\).

Conversely, an injective code with its admitted decoder can recover the complete old \(\pi\). Probe \(e_a\) for \(a=\pi^{-1}(g)\); if the response is \(e_h\), issue

\[
v=e_a\oplus e_{\pi^{-1}(h)}.
\]

Because the fresh change is an involution, the total physical effect is \(e_g\). Necessity and sufficiency therefore give

\[
M_{\min}=|\mathcal H|,
\qquad M_{\min}=n!\text{ when }\mathcal H=S_n.
\]

A fixed-length binary storage bound is \(\lceil\log_2(n!)\rceil\), under that full-family contract. This is an information-state requirement, not a count of all physical controller states, total entropy under an arbitrary prior, or subjects. It does not impose \(n!\) storage on a publicly known initial identity: that initial family has size one.

For finite zero-error input families, independent randomized policies can be conditioned on complete private tapes. A finite intersection of probability-one success events still has probability one, so randomization cannot evade the deterministic impossibility. With stochastic finite-alphabet retained encodings, a retained outcome having positive probability for two old wirings faces the same conflict. An actual implementation still requires access to and use of its codebook; mathematical sufficiency does not prove installation.

The \(n=2\) exception is real: a single fixed singleton probe identifies the current two-port wiring, regardless of the old one. The distinction between singleton and complement cardinalities used above fails. S3 checks this exception and all six singleton/all 15 distinct-pair old families for \(n=3\); those finite checks corroborate, but do not prove, the general-\(n\) argument.

The reduction explains the inheritance precisely. Although the external goal stays fixed, the fresh transposition makes the observed \(h\) a delayed query for an arbitrary entry of the **old inverse map**. Once the isolation lemma establishes that reduction, the requirement to support all inverse-port queries is the static AC3 full-singleton factorization requirement. The new application is the reduction under this dynamic command contract; the \(n!\) counting principle itself is inherited. [S1 §§4–5; S8 §6; S10 `R127:P1`]

## 5. Independent two-round obstruction, including full terminal feedback

Assume a controller guarantees the first deadline. The isolation lemma forces its first probe to isolate the known old inverse-goal port, or its complement. Because \(n\ge3\), choose two distinct non-goal effect ports \(r,s\).

First-round identity and first-round \((rs)\) give the same probe response. The successful terminal command is the same in both worlds. Moreover, whenever the round succeeds,

\[
z=y\oplus e_g.
\tag{R3}
\]

Complete terminal feedback is therefore already determined by the probe response and the fixed net goal. It carries no additional distinction along this successful shared history. The issued commands, all permitted feedback, and actual plant end state are identical, but the wirings that become the two possible old wirings for round two differ.

The old-wiring injectivity result applies to this two-element family. A second round with one probe cannot guarantee correction for both old wirings and every fresh allowed change. This contradicts the proposed two-deadline guarantee.

The proof does not assume the controller forgot anything. It can store the whole history, but the two histories are identical. The distinction is between **having enough capacity to represent the required old information** and **obtaining enough observations to refresh it**. Complete initial knowledge suffices for round one and can cease to be available after a successful round. The finite set of fixed legal change sequences also permits the same independent-tape argument for randomized zero-error policies. [S1 §6]

## 6. Independent proof and check of the sharp three-port value

For a deterministic policy, any first-round failure occurs on at least one of the four equally likely first changes. Such a policy has joint two-round success at most \(3/4\). Therefore a policy attaining more than \(3/4\) must satisfy the first deadline for all four changes. Its first probe is \(e_0\) or its complement, and equation (R1) fixes its successful terminal rule.

The first response identifies a goal-involving swap on total mass \(1/2\). The controller then knows the entire new wiring, so the known-old repair gives second-round success one. On the other mass \(1/2\), the old wiring is equally likely to be \(I\) or \((12)\). After the next independent uniform change, the conditional current-wiring weights are:

| Wiring as command-to-effect tuple | Weight among 8 worlds | Inverse goal port |
|---|---:|---:|
| `(0,1,2)` | 2 | 0 |
| `(0,2,1)` | 2 | 0 |
| `(1,0,2)` | 1 | 1 |
| `(1,2,0)` | 1 | 2 |
| `(2,0,1)` | 1 | 1 |
| `(2,1,0)` | 1 | 2 |

Every three-bit probe is constant, a singleton, or a singleton's complement. A constant leaves best success \(4/8\). For probe port 0, the response at effect 0 has mass \(4/8\) and one correct inverse action. Each other response has two equally weighted conflicting inverse actions, contributing only \(1/8\). The total is \(6/8\). Probes of ports 1 and 2 each have best response-cell weights \(2/8,2/8,2/8\), also \(6/8\). Complementation changes observation labels and terminal compensation but preserves the partition and optimum.

Thus the exact ambiguous-branch optimum is \(3/4\), giving

\[
\frac12(1)+\frac12\left(\frac34\right)=\frac78.
\]

This is attainable: use the known-old repair on the identified branches; on the ambiguous branch, probe port 0 and choose a best common terminal action in each response cell. Independent randomization is a mixture of complete deterministic policies and cannot increase average success under this fixed prior. Equation (R3) shows why full first terminal feedback does not improve the bound. [S1 §7; S3]

The independent response-cell implementation in S6/S7 used a coordinate-wise persistent plant, including a nonzero starting state, and checked all eight terminal commands for every probe and all eight labelled worlds. Its **512 terminal/world evaluations** gave:

| Probe integer | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Maximum successful worlds out of 8 | 4 | 6 | 6 | 6 | 6 | 6 | 6 | 4 |

This independently verifies the numerical subproblem used in the analytic proof. It does not prove that every arbitrary two-element old family has value \(3/4\); the displayed weights and family are part of the claim.

The number \(7/8\) is not a per-sequence guarantee, a per-round error rate of \(1/8\), or a computed randomized minimax value. It is the optimal fixed-prior probability of the joint event \(E_1\cap E_2\). In particular, positive average error establishes the absence of a policy that succeeds on every supported sequence, but does not identify the minimax value.

## 7. Code quantifiers, information flow, and physical scoring

### 7.1 Exhaustive policy scope of the original verifier

S2 represents permutations in the declared command-to-effect direction. `compose(drift, old)` is effect-port left composition. `apply_wiring` combines destination bits with OR; since the wiring is a bijection, no command bits collide, so this agrees with XOR in this model.

The original two-round search enumerates all eight first probes. Constant probes have one possible first response and hence eight terminal rules each; the six nonconstant probes have three possible first responses and \(8^3\) terminal rules each. The total is

\[
2\cdot8+6\cdot8^3=3,088.
\]

For each first observable history it then optimizes every second probe and all eight terminal actions in each second response cell. Histories and response cells are disjoint decision points, so this decomposition explores the complete deterministic policy class without materializing the Cartesian product of every complete policy tree. The original search counts and saved attaining rules are consistent with that enumeration. No hypothesis about an optimal singleton probe is imported into the search.

### 7.2 The history keys do not grant hidden information

With full terminal feedback the key is \((y_1,z_1)\); with withheld feedback it is \((y_1)\). The first probe is fixed within the first policy being evaluated, and its terminal command is already a fixed function of \(y_1\), so omitting those known actions from the stored key does not discard relevant permitted information. The controller selects one common second probe for each such history and one common terminal command for each resulting response. It does not choose separately by actual wiring.

For all-prefix scoring, the dynamic program removes the score weight of worlds whose first deadline already failed. This is legitimate optimization, not a hidden success oracle. A failed world has zero joint payoff for every continuation. The chosen continuation remains one fixed action rule on each actually observable history, including histories shared by failed and successful worlds. A response cell reached only by failed worlds may be completed by any legal action; the code uses zero. This argument relies on the present model's common unconstrained action menu. It would need reconsideration if ignored worlds imposed different legality or safety constraints.

Caching second-stage problems by the weighted distribution of current wiring is sufficient here because the remaining effect law and net-increment score do not depend on the old plant value, unrecorded resources, or additional history. The plant really does change; its absolute value simply cancels from the declared next-increment objective. This cache key is not a certificate for an absolute-state target, state-dependent actions, nonlinear plant, changing deadline, or history-dependent drift outside the stated law. The four variants' optima are:

| Terminal feedback | Objective | Original exact optimum | First terminal rules enumerated |
|---|---|---:|---:|
| Withheld | Both round increments correct | 7/8 | 3,088 |
| Withheld | Second increment only | 7/8 | 3,088 |
| Full | Both round increments correct | 7/8 | 3,088 |
| Full | Second increment only | 1 | 3,088 |

The finite known-old singleton checks do not establish the general old-family theorem; section 4 supplies that proof. The code's two-probe positive run covers 16 two-round paths; arbitrary-horizon validity comes from the per-round algebra below, not from extrapolating those tests.

### 7.3 Independent replay and the objective correction

S6 uses an independent coordinate-wise environment and a separate observable controller. The environment owns the true wiring and a persistent mutable plant. The controller receives the serialized policy and only the permitted effects. True wiring, drift, plant state, and success flags are not controller inputs. All 64 paths and 1,088 saved fields matched, and every variant covered the 16 legal sequences exactly once. [S7]

| Terminal feedback | Objective | Scored successes | First-round successes | Both-round successes | Final plant equals initial |
|---|---|---:|---:|---:|---:|
| Withheld | Both increments | 14/16 | 16/16 | 14/16 | 14/16 |
| Withheld | Second increment only | 14/16 | 8/16 | 6/16 | 6/16 |
| Full | Both increments | 14/16 | 16/16 | 14/16 | 14/16 |
| Full | Second increment only | 16/16 | 0/16 | 0/16 | 0/16 |

These extra columns describe the **saved attaining policies**, not every optimal policy. In particular, the last saved policy uses its first terminal feedback to finish calibration and preserves a first-round error on every path. This demonstrates why its value one is not final-plant recovery. It does not show that every policy attaining second-increment value one must fail all first deadlines.

The earlier name `last_prefix_only` was misleading for the implemented second-increment score. The corrected `last_round_increment_only` accurately denotes

\[
x_{\mathrm{end},2}\oplus x_{\mathrm{start},2}=e_0.
\]

Dropping the first deadline permits the two first-round actions to function as identifying probes when both effects are returned. Once the first-round wiring is known, the next one-probe repair succeeds. Withheld terminal feedback changes that interface; its probe instrument supplies only an effect increment, not an absolute-state observation that would indirectly reveal the missing terminal effect. S1 and S5 now make this distinction explicit.

### 7.4 Positive repair and its exact scope

For three ports, probe two distinct command ports and read their full effect vectors. Bijectivity identifies the remaining destination, giving the entire current \(\pi\). With probes \(u_1,u_2\), choose

\[
v=u_1\oplus u_2\oplus P_\pi^{-1}e_g.
\]

The total physical effect is exactly \(e_g\), regardless of the plant's starting value. This is a per-round identity while the wiring stays fixed, so it proves a repeatable construction at every finite horizon. Full signature calibration gives the inherited \(\lceil\log_2 n\rceil\)-probe upper bound for general \(n\). The reviewed checkpoint does not prove its minimality for a sustained fixed goal at larger \(n\). [S1 §8; S8 §5]

## 8. Compatibility and inheritance against existing contracts

The following are the specific predecessor records reread for this review. They are dependencies or compatibility anchors, not additional new results.

| Existing source or stable ID | Existing scope and relation to this checkpoint | Required treatment |
|---|---|---|
| UCT III v1.0 §6.4, Proposition 6; §7.2 | Published capability closure requires equality of destination-class row sums for all states in a capability class. The matched circuits already show equal current capability with unequal possible future gains. | Credit the general dynamic-closure distinction as published inheritance. Noninjectivity alone does not prove future relevance. The present controlled information requirement is a specific application, not the discovery of that general distinction. |
| `R127:P1`, `R127:FUTURE_EQ` | Task encoding separates unequal response profiles; future-operation equivalence requires all words over the same admitted operation alphabet. | The inverse-map query reduction and indistinguishability proof use inherited methods. Do not identify present singleton sufficiency with sufficiency for a larger future operation family. |
| `R132:PARTIAL_CLOSURE` | Equal summaries must preserve common enabled menus and joint next-summary/output laws. | A present-action summary can fail closure after new drift. The dynamic failure is compatible with the old closure criterion; the old criterion did not assert all coarse summaries close. |
| `R133:PERSISTENT_MODEL`, `R133:COMMON_POLICY` | One common observable-history policy, no model/menu oracle, fixed finite horizon, persistent hidden model and sufficient state. | Encode an entire fixed drift sequence as the immutable hidden model plus phase/current wiring, or use an explicit fixed drift kernel in the sufficient state. Do not import an assumption that the changing current permutation itself is immutable. |
| `R134:VECTOR_RECURSION`, `R134:ROBUST_LP` | Pure-policy success profiles and mixtures, common histories, independent private seeds; minimax is distinct from a supplied prior. | The finite decision optimization is inherited. The new calculation fixes a prior and does not solve the robust LP or claim a minimax value. |
| `R136:CAUSAL_LP` | Passive exogenous streams without action feedback into future observations. | It is not a direct theorem for the present controlled observation process. Do not use a passive full-path translator as the complete feedback proof. |
| `R137:CLOSED_LOOP` | A fixed observable action decoder preserves joint controlled rows under an exact interface; finite sufficient state and explicit menus are required. | Feedback must be represented by controlled rows. A history-dependent calibration policy requires explicit state augmentation; it is not automatically the original memoryless decoder class. |
| `R171:INDUCTIVE_RANGE_CLOSURE`, `R172:INTERFACE_COMPOSITION_THEOREM` | Closure and composition require all-successor preservation of the same admitted interface and input conditions. | The new two-round example witnesses failure to preserve a premise. It does not replace these conditions or invent the general principle of inductive premise preservation. |
| `AC20261009:CONTRACT`, `AC20261009:PRIOR`, `AC20261009:POSTERIOR` | Fixed wiring across calibration; the posterior formula uses uniform initial wiring under a fixed policy. | Do not AND a globally fixed wiring premise with across-round rewiring. Each within-round signature use requires a binding to that same round. The dynamic posterior is not generally uniform on all permutations. |
| `AC20261009:MEMORY_CONTRACT`, `AC20261009:STATE_BOUND`, `AC20261009:STATE_EXAMPLES` | Static task-relative state count; every accessible wiring-correlated resource is included. A single fixed singleton needs \(n\) states, all singleton queries need \(n!\). | The new \(n!\) result changes the required adaptive capability, not the old theorem. Preserve both results with their separate contracts. |
| `AC20261009:PARALLEL_BOUNDS`, `AC20261009:FAILURE_CONTROLS` | Binary signatures identify a fixed permutation; changing wiring and extra feedback are already explicit failure controls. | Credit the positive full-reidentification schedule and domain warnings as inherited. The exact dynamic obstruction and value are the candidate additional applications. |
| `AC20261009:REALIZATION`, `AC20261009:FIXED_J_DIFFERENCE`, `AC20261009:INTERPRETIVE_LIMIT` | Actual model agreement, same capability evaluation, and any named experiential relation require independent grounding. | Comparing one-probe and two-probe budgets changes the resource contract. It does not by itself establish a fixed-J inequality between two actual admitted systems or a named feeling. |
| `R188:INFERENCE_CONTRACT` | A violated score bound rejects a combined law/access/timing/protocol contract; it does not uniquely locate a hidden wire or establish experience. | This general inference discipline remains applicable. R188's specific reader/source/alphabet model is not silently reused as the dynamic calibration model. |

The dynamic checkpoint remains compatible with independently admitted local-process persistence and the existing U1/P3 reading. Failure of downstream action calibration does not erase a local process, make experience conditional on control, count owners, or imply a change in a named quality. A cached target may remain perfectly retained while its next correct physical use fails. That is a selected functional statement with an explicit interface, not an experiential identity theorem. [S1 §10; S8 §7; S9]

## 9. Claim-by-claim disposition and remaining obligations

| Candidate ID | Mathematical review | Contribution treatment |
|---|---|---|
| `ONLINE_AC:CONTRACT` | Explicit finite premise package; coherent | Definition and assumptions, not a discovery or established actual premise |
| `ONLINE_AC:CACHE_CONTROL` | Valid under unrestricted persistent target storage | Exclusion/control; fixed-target caching is inherited |
| `ONLINE_AC:ONE_ROUND_REPAIR` | Valid for known old wiring and allowed involution | Elementary inherited construction |
| `ONLINE_AC:OLD_WIRING_INJECTIVITY` | PASS for \(n\ge3\), all admitted old wirings and all permitted fresh changes | Candidate specific dynamic reduction and exact resource statement; factorization/counting inherited |
| `ONLINE_AC:TWO_ROUND_OBSTRUCTION` | PASS including full terminal feedback and all retained histories | Candidate finite failure of preserving calibration information |
| `ONLINE_AC:TWO_ROUND_VALUE` | PASS, exact fixed-prior \(7/8\) with an attaining policy | Candidate explicit finite value; no minimax or global-priority claim |
| `ONLINE_AC:TWO_PROBE_REPAIR` | PASS for the three-port per-round construction and the stated general identification upper bound | Inherited signature calibration plus explicit physical compensation |
| `ONLINE_AC:FEEDBACK_AND_OBJECTIVE_CONTROL` | PASS with the distinct named feedback/score contracts | Interpretation and scoring control; not final-state or continuous-state recovery |

The candidate increment is a reusable finite theorem package: a constant external goal can induce a need for the entire old inverse map; a successful correction may fail to refresh that map; and this failure has a sharp two-round value under a specified law. The new application may be worth preserving and citing. The review does **not** establish a standalone-paper-sized advance, external priority, or an untouched general research topic.

S1's targeted external predecessor search is recorded by its author. This independent review did not conduct a new exhaustive literature search or independently reread those external papers. Historical priority for the exact dynamic permutation package remains **UNVERIFIED**. The separate publication/reuse review and the single project coverage overlay govern disclosure classifications; a new local note is not a new published work.

Before any future scientific-map integration, the proposed claims need an explicit typed module with separate bindings for the general zero-error old-family theorem, the two-round known-initial theorem, and the three-port uniform-prior value. Any use of static AC formulas must be scoped to fixed wiring within the relevant calibration interval. Integration must preserve the existing actual/experiential obligations, the pending AC/IL status, and all suspended rules. This local PASS cannot substitute for that integration review.

The review found **no remaining correctness blocker in the exact S1/S2/S3 checkpoint**. Remaining limitations concern external priority, actual realization, fixed-J use, named experiential interpretation, and follow-up mathematical questions beyond its scope. No old source, frozen map, ledger, guideline, or publication artifact was modified by this review.
