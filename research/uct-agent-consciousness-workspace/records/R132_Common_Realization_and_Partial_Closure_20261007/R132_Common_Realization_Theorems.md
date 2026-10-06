# Common realization, resource obstructions, and partial controlled closure

R132 research checkpoint, 7 October 2026 (Asia/Shanghai). Fixed basis: A/I 1.2, B/II 1.1, C/III 1.0, D/TA-TR-2026-24 1.0, and the R131 map. No empirical run or publication release.

## 1. The specific gap

R131 certifies transition-law closure for a declared family of **total** operations. R126 already warns that partial operations also require preserved availability. The recovered X01 case demands a common operating witness instead of combining achievements from incompatible modes. This note completes a scoped constructive connection: a resource model determines feasible joint operation menus, and a finite partial stochastic interface must preserve both those menus and the joint next-state/output law.

This is a project-level extension, not the invention of Hall's theorem, probabilistic bisimulation, partition refinement, or the distinction between current prediction and reusable state. It adds no experience-existence gate to A:U1.

## 2. Resource model and adequacy premise — R132:SLOT_MODEL

Fix one horizon, physical boundary and port interpretation. There are n requested unit tasks I and a finite set R of distinguishable resource-time slots. Task i may occupy a slot in N(i) subset R. A legal simultaneous schedule is an injective assignment w with w(i) in N(i); each task occupies exactly one whole slot and each slot serves at most one task. Time windows and allowed ports may restrict these neighbor sets.

For the **combinatorial model**, these are all constraints. Applying the result to an actual system additionally requires an implementation-adequacy premise: assignments faithfully represent feasible executions within the specified horizon, with no omitted coupled costs, precedence, interference, multi-slot duration, shared consumables or unrepresented control restriction. If that premise fails, the graph can overstate actual feasibility. A task needing a bundle of slots is not covered merely by giving it several alternative neighbors.

An admissible partial schedule serves a subset of I under the same rules. Completion below means performance of the specified scheduled unit task, not an ungrounded guess of its output. Extending the deadline or allowing an external device changes the model.

## 3. Theorem 1: common-witness and exact deficit — R132:HALL and R132:DEFICIT

Write N(J)=union_{i in J} N(i). There is a schedule serving every requested task iff

\[
|N(J)|\ge |J|\quad\text{for every }J\subseteq I.
\]

**Proof (Hall's classical argument, restated).** Necessity follows because distinct assigned slots for J belong to N(J). For sufficiency induct on n. If some nonempty proper J satisfies equality, match J to N(J) inductively. The remaining graph satisfies Hall: for T outside J, applying the original inequality to T union J gives |N(T) minus N(J)|>=|T|. Match the remainder inductively. Otherwise every nonempty proper subset has at least one surplus neighbor. Assign any task one neighbor and remove both; every remaining subset loses at most one neighbor and still satisfies Hall. Induction finishes; n=0 and n=1 are immediate. QED.

Define

\[
\delta=\max_{J\subseteq I}(|J|-|N(J)|)\ge0.
\]

The maximum number of tasks any partial schedule can complete is **n-delta**.

**Proof.** A maximizing J forces at least delta tasks to be unmatched, hence at most n-delta completions. Add delta new slots adjacent to every task. The augmented graph satisfies Hall, because |N(J)|+delta>=|J| for every nonempty J. A complete augmented matching exists. Remove the matches using new slots: at least n-delta original matches remain. The upper bound gives equality. QED.

Thus failure can be explained by a concrete overloaded coalition J, not merely by an unsuccessful search for one schedule. These are standard matching consequences used here as finite common-realization certificates.

## 4. Theorem 2: proper-subset success does not certify the whole — R132:HIGH_ORDER

For every n>=3, take n tasks with every N(i) equal to the same n-1 slots. Every proper subset of tasks has a complete schedule; the full set does not. Its deficit is exactly one. Therefore even testing **every proper coalition**, including all pairs, does not universally establish joint realization in this model class.

**Proof.** Any subset of size at most n-1 can be assigned distinct slots. The entire set violates Hall by one. QED.

If each trial randomizes uniformly over which task to omit and completes the others, then

\[
P(X_i=1)=1-\frac1n\quad\text{for each }i,
\qquad P(X_1=\cdots=X_n=1)=0.
\]

More generally, for any randomized admissible partial schedule,

\[
\sum_{i\in I}P(X_i=1)\le n-\delta,
\qquad
\min_{i\in J}P(X_i=1)\le \frac{|N(J)|}{|J|}
\quad(J\ne\varnothing).
\]

The first inequality follows by taking expectations of the per-trial completion bound. The second follows from sum_{i in J} X_i<=|N(J)| and the fact that a minimum is at most an average. If all per-task completion probabilities are at least 1-epsilon, epsilon>=delta/n. The complete n-to-(n-1) graph attains epsilon=1/n. For n=100, every marginal completion rate is 99% while all-at-once completion is impossible.

This does not say 99% accurate AI components must fail together. It is a specified counterexample to that inference without a joint resource model. Marginals cannot determine a joint event in general; D and the historical PLT ledger already establish related dependence limitations. Here a named resource obstruction supplies the common-witness failure. More trials estimate this same obstruction; a longer horizon or different resources can remove it.

## 5. Partial stochastic interface — R132:PARTIAL_MODEL

Let S, U, O be finite sets of sufficient model states, fixed operation labels, and output symbols, with S and O nonempty. Each state has an enabled menu E(s) subset U. For each a in E(s), specify a probability kernel

\[
L_a(s;s',o),\qquad \sum_{s',o}L_a(s;s',o)=1.
\]

An output symbol can be an entire within-horizon output vector, including timing if timing is relevant. S includes required resource state, memory and phase. Operations, deadline and scheduler meanings are fixed across comparisons. If several schedules realize one request, its label must include a fixed scheduler policy, or the unresolved scheduler choice must remain an explicit action/nondeterministic variable. Existence of a matching does not select a probability law.

For a declared unit-slot implementation, E(s) can be computed by the Hall conditions for each requested task profile, **provided** the slot adequacy and scheduler premises hold. The closure theorem itself accepts any explicitly specified E and L and does not require a matching model.

Fix p:S -> Z onto its image. By an exact interface quotient we mean a menu Ebar(z) and kernels Lbar_a(z;z',o) preserving **both** enabledness and the joint next-summary/output law, for every represented state and operation. This target is stronger than current-score preservation and deliberately stronger than mere observation-trace equivalence.

## 6. Theorem 3: exact common-operation closure — R132:PARTIAL_CLOSURE

Such a quotient exists iff for every p(s)=p(t):

\[
\tag{E}E(s)=E(t),
\]

and, for each a in this common menu and all z',o,

\[
\tag{J}
\sum_{s':p(s')=z'}L_a(s;s',o)
=\sum_{s':p(s')=z'}L_a(t;s',o).
\]

**Proof.** A quotient assigns one menu and one law to a common z, so both conditions are necessary. Conversely define Ebar(z)=E(s) and Lbar by the displayed row sums using any representative s of z. (E) makes the domain independent of the representative, and (J) makes the kernel independent of it. Nonnegativity and normalization are inherited. QED.

For each finite horizon this preserves joint summary/output histories under any **shared policy depending only on summary/output history**, including randomized policies, selecting enabled operations and halting when the menu is empty. Proof is by induction: matched histories give the same policy distribution over the same enabled actions; (J) gives the same distribution of the next summary and output. Arbitrary hidden-state-dependent policies are not covered. Disabled operations must not be silently treated as enabled self-loops. A declared, observable rejection action with its own semantics is a different totalized interface.

**Relation to R131 — R132:PROBE_CERTIFICATE.** On the finite alphabet Z x O, choose fixed exact expectation probes whose matrix together with normalization has full column rank. Conditional on (E), equality of those next-summary/output probe expectations within fibers is equivalent to (J), by R131:COMPLETE_LAW. Probes of next summary and output separately need not span the joint law. If the alphabet has one element the law condition is automatic, but (E) is still required.

## 7. Neither condition replaces the other

**Availability counterexample.** Two hidden states s_0,s_1 have the same p. Each accepts any subset of three named unit tasks. At s_0 only two slots are available; at s_1 three are. All tasks can use any available slot. Any proper task subset is enabled at both states and produces the same constant output; the state is unchanged. The three-task request is enabled only at s_1. Every common enabled operation satisfies (J), but (E) fails and no exact quotient exists.

**Joint-law counterexample.** Take S={0,1}^2 with p(x,b)=x, the same singleton menu at every state and a fresh fair U. Put x'=U, b'=b and output o=U XOR b. For states sharing x, the next-summary marginal is fair and the output marginal is fair; both match. But the next-summary/output pair has even parity when b=0 and odd parity when b=1, with TV=1. Thus (E) and both marginal-law conditions hold while (J) fails. The existing R128/PLT parity idea is reused here, not claimed as newly discovered.

These counterexamples show why collecting correct separate response tables can still miss either resource compatibility or dependence between observation and future state.

## 8. Theorem 4: minimal finite repair — R132:REFINEMENT

Start with a partition P_0 specified by the distinctions one wishes to retain. Given P_k, split each block using the signature

\[
\left(E(s),\left(\sum_{s'\in B}L_a(s;s',o)\right)_{a\in E(s), B\in P_k,o\in O}\right).
\]

The resulting sequence stabilizes after at most |S|-|P_0| strict refinements. Its terminal partition P_* is the unique coarsest refinement of P_0 satisfying (E) and (J).

**Proof.** Each nontrivial refinement increases the number of nonempty blocks, bounded by |S|. At a fixed point, signatures agree within blocks, exactly giving (E) and (J). For coarseness, let Q be any stable partition refining P_0. Inductively suppose Q refines P_k. Any P_k block is a union of Q blocks, so equality of all Q-block/output transition probabilities implies equality of all P_k-block/output sums; stable Q also preserves menus. Hence no pair in one Q block is split at stage k+1. Q refines every P_k, including P_*. This proves coarseness and uniqueness. QED.

This is finite probabilistic partition refinement with preserved menus and joint outputs. The coarsest claim is about this fixed supplied model, all states and this exact quotient criterion. It does not assert a unique best sensory representation, minimal neural circuit, model-independent state under uncertainty, or coarsest quotient under representative-dependent support-only updating. The process can refine to singletons; useful compression is not guaranteed.

## 9. Cross-paper interpretation and remaining work

- **A:** U1 is unchanged. Passing a joint realization test is not required for experience existence; failing it does not establish experiential absence.
- **B:** time, boundary, ports and intervention interpretation remain explicit. An externally assembled matching graph is not itself an actual process realization.
- **C:** capability remains task/resource relative. Two actual systems with different well-defined joint capability profiles satisfy C:P1's type-distinction implication under its complete-type premises. No scalar experiential ranking follows.
- **D:** consequences and installed use must be assessed under the same action/scheduler interface. Matching separate outcomes cannot replace the joint next-state/output law, nor does continuation control establish valence.

R132 makes the common-witness requirement operational in a limited resource class and completes the earlier partial-operation caveat. It does not solve arbitrary multi-resource scheduling or general biological integration. The next theory question is **implementation uncertainty**: when each candidate mechanism admits a schedule, does one policy using only available observations work across all candidates? The quantifiers forall model exists policy and exists policy forall model differ. A proof must specify observation access, adaptation and persistence of the actual model rather than pasting incompatible model-specific witnesses. No new experiments are needed to state this next target.

## 10. Source and originality audit

Project reading: R131 proof and map; R126 §§2–4; C §5.2 and transmission closure; B §2.1's pointed/port-aware view; D/R96D's payoff-relative interface; recovered X01; prior marginal/joint counterexamples. Four pinned paper bytes are retained.

Hall (1935), *On Representatives of Subsets*, DOI 10.1112/jlms/s1-10.37.26: primary publisher metadata verified. The matching theorem is explicitly classical; a self-contained proof is supplied above.

Givan, Dean and Greig (2003), *Equivalence notions and model minimization in Markov decision processes*, DOI 10.1016/S0004-3702(02)00376-4: original article PDF inspected in §§3–4 and related proof locations. Stochastic state equivalence and finite refinement are established prior art, not new UCT mathematics. https://ics.uci.edu/~dechter/courses/ics-295/winter-2018/papers/givan-dean-greig.pdf

Takahashi (2026), *Reusable Consequence States Under Partial Support and Model Uncertainty*, DOI 10.5281/zenodo.22170023: author-hosted abstract and SSRN abstract inspected; full proofs not reviewed. It addresses nearby questions about reusable states and model uncertainty, so broad novelty claims for that research direction are unwarranted. Our fixed-model, preserved-enabledness theorem must not be confused with its stated support/uncertainty setting. https://kadubon.github.io/github.io/papers/2026-08-30-reusable-consequence-states-under-partial-support-and-model-uncertainty-22170023/

Current status: complete manual conditional proofs and targeted exact finite checks; not historical-priority certification, independent peer review, proof-assistant certification or empirical validation of C1.
