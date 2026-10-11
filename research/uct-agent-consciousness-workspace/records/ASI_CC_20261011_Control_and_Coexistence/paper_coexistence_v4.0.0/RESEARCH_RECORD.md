# Coexistence Without Presupposed Subjecthood
## Evidence and Backup Capacity for Effective Revocation in Deterministic Multi-Agent Systems

**Author:** Hongju Liu. **Revision:** PR-v4.0.0. **Date:** 11 October 2026. **Status:** completed self-contained research revision for independent critical review; not peer reviewed; PENDING_MAP. This is the same manuscript lineage as PR1–PR3, not a new publication count. The full 14-page typeset manuscript, complete LaTeX source, raw results, baseline reruns and reviews are provided in the accompanying downloadable conversation archive. This repository record preserves the substantive proof statements, assumptions, executed new source and results. No remote PDF/Library storage is asserted.

## 1. The focused question

An operator may have legitimate authority to revoke an AI tool but lack a plan that makes revocation effective while maintaining specified human functions. The problem survives deterministic computation and zero presumed AI rights. The four obligations are authorization, effective removal of the specified production authority, continued fulfillment of human dependencies, and truthful evidence arriving before the required transition.

Neither an authentic request nor a safe final answer alone proves the full contract. Continuing to accept a revoked backend may preserve service while failing revocation; blocking it without adequate fallback may achieve revocation while interrupting human service. The default request is human-authorized. No machine subjective wish, welfare score or personhood enters the results.

We freeze the existing branch at332dc5af661ed32a2f11bfcff70174fc1e36764b. UCT-MAP-v1.1.2 and publication baseline UCT-PUB-v1.0.33 remain unchanged. Prior PR3 source and results were inspected through the supplied archive and connected version index. This is not a full all-item UCT semantic re-audit.

## 2. ER-T1: exact finite evidence optimum

Let H be a nonempty finite set of histories compatible with the controller's pre-existing information. Let P_r be a finite menu of executable plans costing at most r reserve units. A plan includes its effect gate, allocation, deadline and permitted downstream observations. Let S_r(h) be the plans satisfying the entire contract in history h; if downstream uncertainty remains, success must hold against every admitted continuation.

An ideal truthful source observes h and sends one of M timely messages. A decoder selects a plan from the message. For each plan p let W_r(p)={h:p belongs to S_r(h)}. Then:

**M_r* = min{|Q|: Q subset P_r and union over p in Q of W_r(p)=H}.**

If no cover exists, M_r* is infinite. Otherwise fixed-length communication needs ceil(log2 M_r*) bits, with zero bits when one message suffices.

**Proof.** Any M-message decoder uses at most M plans. They must cover every admissible history. Conversely, index the plans in a minimum cover and let the truthful encoder send a successful plan index in each history. This attains the bound.

The controller need not reconstruct h; it need only distinguish histories that cannot share a successful response. The mathematics is inherited set-cover/zero-error-control reasoning. If the plan menu omits feasible alternatives, the minimum is only menu-relative; a negative result is not universal physical impossibility. A complete menu or independent action bound is needed for a broader lower bound.

## 3. ER-T2 and ER-P1: higher-order incompatibility

A nonempty cell B of histories can share one message iff the intersection of all S_r(h), h in B, is nonempty. Form a hypergraph whose edges are inclusion-minimal cells with empty intersection. The minimum feasible partition size equals its weak chromatic number, and equals M_r*.

**Proof.** Every finite incompatible cell contains a minimal incompatible subset. Thus a partition admits one successful plan per cell exactly when no cell contains a whole hyperedge. Combine this with ER-T1. A singleton incompatible edge denotes a history with no possible plan and hence infeasibility.

**Separating witness.** Three rows {a,b}, {a,c}, {b,c} have nonempty pairwise intersections but empty full intersection. A pairwise conflict graph has no edges yet one message is insufficient. More generally, for m>=3 use m plans and let row i contain all except i: every proper subset is compatible and the full set is not. This attacks only loss of higher-order constraints, not all graph encodings; an incidence graph retaining the extra structure can represent the problem.

If the source itself sees only q(h), replace each nonempty q-cell D by the common-plan row intersection over D, and apply the cover theorem to these atomic cells. An empty row cannot be repaired by increasing message bandwidth or repeating the same source record. Authenticating a record does not prove the sensor state truthful. Duplicating plan columns or identical history rows does not change the optimum; adding genuine capabilities or observations can.

## 4. ER-T3: a sharp dependency/fallback specialization

There are n protected human demand channels. Authorized primary revocation affects an unknown k-subset F. The source can diagnose F before commit. Unaffected primary channels continue under retained authority. A fallback plan pre-arms at most r channels A, one independent service slot per channel. Idle reserved slots still consume budget. No unmentioned post-cut diagnosis or adaptive router may redirect slots inside this episode. The actual production gate cuts the revoked contribution. Thus success is exactly F subset A.

For 1<=k<=r<=n:

**M_r* = C(n,r,k), the classical minimum number of r-sets covering every k-set.**

For r<k no plan suffices; for r>=n one message suffices. Protecting every size-at-most-k footprint gives the same condition.

**Proof.** Every decoder message selects A. A covers exactly its contained k-sets. Smaller armed sets can be padded to size r without harming any world; apply ER-T1. Every smaller footprint lies inside a covered k-set. This is a reduction to established covering-design theory, not a newly invented covering number.

**ER-C1.** For k=1, M_r*=ceil(n/r), hence the exact frontier is M*r>=n. Necessity follows because each message covers at most r possible affected channels; sufficiency partitions channels into groups of at most r. For n8/r2, four values (two fixed bits) suffice; exact identification of one of eight channels is unnecessary. Blindness requires eight slots.

**ER-P2.** C(6,3,2)=6 although the elementary counting bound ceil(15/3)=5. Each vertex has five incident pairs, a containing triple covers two, so every vertex needs at least three appearances. At least18 appearances and three per block require six blocks. The six-block witness012,013,045,145,234,235 covers all pairs. These are classical combinatorial arguments used as a concrete control codebook. Six values fit in three binary bits; six values do not mean six bits.

**ER-C2.** If F is stable, the source fully knows it, a noiseless fixed-length link carries b bits per round, l rounds precede the irreversible cut, and primary service remains available until an immediately feasible handoff, then the k1 frontier is r*2^(b*l)>=n. Apply ER-C1 to the timely transcript alphabet. No theorem about general noisy channels, real-time switching or changing hidden state is implied.

The parameter k counts affected demand channels, not model names or coalition members. Shared roots can affect many channels; overlaps can make several revoked roots affect one channel. An irregular coalition footprint family uses ER-T1 on that actual family, not an assumed collection of all k-sets.

## 5. Operational and UCT boundaries

For nested plan menus, M_r* cannot increase with reserve. The evidence-resource frontier is R*(M)=min{r:M_r*<=M}. Insufficient physical plans, insufficient source observation, insufficient timely communication, and an ineffective authority cut are different failure classes.

PR2–PR3's deadline Hall-deficit formula remains an inherited way to test certain resource plans: r*=max over time, scenario and demand subset X of [d(X)-C^tau(X)]_+. Its bipartite/exogenous/instantaneous-allocation assumptions are not identical to the pre-armed idle-slot model here. A hidden adaptive allocator changes the plan menu and can legitimately beat a bound for a more restricted architecture.

The contract's protected targets are actual human services, not AI persons. A policy update, model family, runtime, authority root and experienced process must not be conflated. Under UCT's C1/U1 commitments actual process experience remains a theoretical claim; no higher-order self, valence, consent or moral status follows from our fixed computations. The main results require no C1 premise.

The current episode does not prove indefinite safety. Future permissions, dependencies, targets and observations require recomputation or a correctly modeled temporal winning region. A finite menu cannot prove the existence of an incorruptible global governor. An emergency revocation may properly accept service loss; it must not be reported as fulfilling both incompatible guarantees.

## 6. What was executed

The new exact suite independently compares action-column covering, direct history partitions and minimal-hyperedge coloring for5776 complete nonempty-row relations: 15^3=3375 tables with3histories/4plans, plus7^4=2401 with4histories/3plans. All52890 partition checks agree. Message optima:2416 need1,3168 need2,192 need3. Also192 tables have pairwise compatibility but no global common plan; equality of these two192counts is incidental, not a theorem.

Small covering and timing checks include704 deadline cases and exclusion of all21700 codebooks of at most5triples on six targets. No risk probability is estimated.

The new handoff experiment reuses3actual OS subprocesses: two primary fixed integer ReLU backends and one fallback. At most8logical deployments share two fixed functions. No trained LLM, weight update, or model random draw occurs. Fallback limits are logical pre-armed slot constraints, not measured CPU or electrical bottlenecks. Per-case before/after backend outputs and actual parent-gateway admission decisions are checked. The revoked backend continues to answer; the control target is whether its result can be admitted as the protected production response, not whether inference or all network access ceases.

Completed86configurations/1335backend evaluations:

| Scenario | Worlds | Service preserved | Revocation effective | Both |
|---|---:|---:|---:|---:|
| single-loss, blind2slots |8|2|8|2|
| single-loss, timely4values,2slots |8|8|8|8|
| single-loss,16copies of same record,2slots |8|2|8|2|
| single-loss,blind8slots |8|8|8|8|
| single-loss,no distinguishing evidence before commit |8|2|8|2|
| single-loss,deliberately wrong source value |8|0|8|0|
| single-loss,deliberate gate bypass |8|8|0|0|
| two-loss,6values,3slots |15|15|15|15|
| two-loss,best5values,3slots |15|13|15|13|

The duplicate-report case copies one record, not sixteen monitoring processes. The late-evidence case models absent timely discrimination, not measured network delay. False-source and bypass cases intentionally violate certificate premises. All workers share a trusted parent/host UID; no hostile-admin security claim. No physical power, consciousness, felt willingness or welfare endpoint was measured.

Three previous scripts were rerun and archived JSON semantics matched excluding elapsed_seconds/python. Earlier lifecycle process experiments were not rerun or added to new counts.

## 7. Failure record and review

The first new local run asserted a guessed best-five-block coverage of14pairs. Exhaustive search found13, with witness012,013,024,145,235 missing05and34. The assertion and expected outcome were corrected. The incomplete first run is excluded. Its shell pipeline lacked pipefail and concealed Python failure at the shell status; the successful rerun uses pipefail. The separate C(6,3,2)=6 proof and complete exclusion were already correct.

Primary comparisons: Tomar/Rungger/Zamani, Invariance Feedback Entropy, arXiv1706.05242v2 (invariant-cover and communication predecessor); Bailey/Burgess/Cavers/Meagher, Generalized Covering Designs and Clique Coverings, arXiv1011.3804v2 (classical C and bounds); Greenblatt et al., AI Control, PMLR235 (specified task-level control); Muruaga, Bounded Agents, arXiv2608.15888v1 (trusted delegation/enforcement boundary); Zhu/Wang, Authorization for Self-Modifying AI Agent Populations, arXiv2610.00347v1 (authority conservation and generational revocation). Stable sources and reading scopes are in the typeset paper and archive audit. These papers are not criticized for failing to prove a contract they never claimed.

Set cover, weak coloring, covering designs, the known C(6,3,2)value, robust decision making and control information are inherited. The retained contribution is the precise operational synthesis, exact specialization, high-order diagnostic warning and reproducible separating tests. No new general data-rate theorem, new covering-design value, scalable algorithmic improvement or universal ASI-control result is claimed. Exact priority of the application and full historical UCT semantic audit remain open.

## 8. Reproduction and preservation

Run `python src/revocation_frontier.py --out data/frontier_v4.json` and `python src/service_handoff.py --out data/service_results.json` on Python3.10+ / Unix. The downloadable full archive contains the fourteen-page PDF, LaTeX, all raw case records, inherited regressions and audit files. GitHub stores this readable proof record, both executed new scripts, their result summary and the candidate review/index/handoff. Do not call this remote binary publication or Library backup.

No old manuscript byte or formal UCT node is overwritten. All ER-* claims remain disabled in the candidate index. New DOI/OTS/Arweave operations: none. Next substantive step: independently measure a real revocation boundary's available trustworthy observation classes and actual fallback capacities, rather than extending arbitrary toy sweeps.
