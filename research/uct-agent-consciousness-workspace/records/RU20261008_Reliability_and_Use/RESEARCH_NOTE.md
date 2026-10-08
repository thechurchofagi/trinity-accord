# RU20261008 — Better average answers, weaker selective reliability
## A theory-first UCT continuation on task performance, answer-relative monitoring and operative use

**Date:** 8 October 2026. **Status:** Unpublished research material; `PENDING_MAP / AUDIT_INCOMPLETE`. No new consciousness axiom, empirical phenomenal result or publication authorization. Baseline branch: `thechurchofagi/trinity-accord`, `uct-agent-consciousness-workspace`; last inspected pre-save head `116c4846f93d2ef71a023bb1374737606d557f2b`.

## 1. Question, inheritance and actual-process scope

Does maximizing mean task accuracy also maximize the ability to identify a reliable subset of one's answers? The current result is an exact negative answer in a finite communication model, not a universal claim about intelligence or subjective metacognition. The comparison uses the **same one-bit message capacity** on both sides, avoiding a memory-capacity confound. It strengthens the preceding OO parity example from one selected code to **every code attaining the optimal mean accuracy**.

UCT III v1.0 already defines a capability profile with task, monitoring and report components (§2), gives complete experiential-type change under a genuine change of a fixed capability profile (§5.1), and rejects an unconditional scalar experience ladder (§5.4). UCT I C1/U1/P3 remain unchanged. Persisting local processes retain experience under the theory even when their information is unavailable to a downstream reader. Nothing here establishes a privileged subject or treats accurate confidence as an admission condition for experience.

The variables below specify a restricted classical model. Source registers, encoder, decoder, clock, ports, stochastic mechanisms and any actual observer must be physically anchored before applying C1 to an actual process. A correct executable program does not by itself establish a complete human or artificial experiential bearer. In particular, a calibrated numerical posterior is **not defined to be a feeling of confidence**.

## 2. Fixed contract and two equally sized messages

Let X be uniform on F2^4 and A independently uniform on the 15 nonzero four-bit vectors. The correct binary answer is T=A·X modulo two. Before A is revealed, the source transmits one bit B=e(X). The installed downstream decoder receives only (A,B), the public circuit specification and independent randomness. No post-query source access, side information or additional source-dependent message is available.

Compare:

- **L:** e_L(X)=x1. The decoder returns B if A=(1,0,0,0), and returns 0 on all other queries, where the alternatives tie.
- **Q:** e_Q(X)=f(X)=x1*x2 XOR x3*x4. The decoder is d_Q(A,B)=B XOR f(A).

A trial has an actual proposed answer Y=d(A,B). Define its answer-relative reliability

    q(A,B,Y) = Pr[T=Y | A,B].

For the stipulated decoders, the distribution of q is:

| Encoder | Conditional reliability | Fraction of trials |
|---|---:|---:|
| L | 1 | 1/15 |
| L | 1/2 | 14/15 |
| Q | 3/5 | 5/8 |
| Q | 2/3 | 3/8 |

For L, only the first-coordinate question is determined. Other parities balance inside each message fiber. For Q, f has a ten-state zero fiber and six-state one fiber. For each nonzero A the displayed decoder gets six of the ten zero-fiber states and four of the six one-fiber states right. These are **conditional** accuracies, not the query-averaged 5/8 substituted into every trial.

The forced-answer accuracies are therefore

    J_L = 8/15;                 J_Q = 5/8.

Both can report the exact q and both are Bayes optimal for their available evidence. The result is not that Q is overconfident, dishonest or intrinsically inefficient at interpreting its evidence. It has a different **evidence-supported reliability distribution**. A human metacognitive-efficiency claim would require an independently justified measurement framework and controls; it is not established by this model.

## 3. All mean-optimal one-bit codes share a selective-reliability ceiling

The previous OO record proved a 5/8 optimum for one-bit mean accuracy. Here we prove an equality characterization and its selective consequence, independently of OO's pending map status.

For any deterministic Boolean encoder e, write

    W_e(a) = sum_x (-1)^[e(x) XOR a·x].

For nonzero a, the parity counts in the two message cells have opposite signed imbalances. Their difference is W_e(a). Majority decoding gives

    p_e*(a) = 1/2 + |W_e(a)|/32,
    J_e*    = 1/2 + sum_(a!=0)|W_e(a)|/480.

Parseval gives sum_a W_e(a)^2=256. Thus the sum over nonzero frequencies is at most sqrt(15*256)<62. Walsh values are even integers, so the sum is at most 60. The displayed Q attains 60, establishing max J=5/8.

**Equality characterization.** Suppose e reaches this optimum. For every a, W_e(a) is congruent to W_e(0) modulo four: the difference is minus twice a sum of eight signs, hence is divisible by four. If W_e(0) were 2 modulo four, the absolute value of each of the 15 nonzero coefficients would be 2 modulo four; their sum could not be 60. Hence all Walsh coefficients are multiples of four.

Set u_a=|W_e(a)|/4 for a!=0. Then sum u_a=15 and sum u_a^2<=16. If the 15 nonnegative integers u_a were not all one, some u_a would be at least two and sum u_a(u_a-1)>=2. This would force sum u_a^2>=17, a contradiction. Thus every nonzero Walsh absolute value is four. Parseval then forces |W_e(0)|=4 as well.

Consequently, every optimum encoder has message-fiber sizes six and ten. In a message fiber of size n_b, majority accuracy for any nonzero query is

    q = 1/2 + |W_e(a)|/(4*n_b),

so it is 2/3 in the six-state fiber and 3/5 in the ten-state fiber. Every mean-optimal encoder has the same reliability law as Q, even though its mapping of inputs to messages may differ. These are four-variable bent functions; that function class and Walsh analysis are established mathematics, not UCT inventions.

**Selective ceiling.** Any acceptance decision measurable from (A,B) and independent randomness selects a weighted mixture of conditional accuracies no greater than 2/3. Thus, at any positive coverage,

    accuracy among accepted answers <= 2/3

for **every** one-bit encoder attaining maximal forced-answer accuracy under this contract. Choosing a non-majority answer cannot improve the bound. A randomized mean-optimal protocol must mix mean-optimal deterministic encoder/decoder pairs; even conditioning on its independent seed does not exceed the bound. Hiding that seed cannot improve matters.

This does not rule out improvement with an additional message, a query-return route, side information, a different prior or a changed encoder objective. Those change the stated contract. The theorem is also not a general classification of optimal codes beyond four input bits.

## 4. Exact accuracy–coverage reversal

Let c in (0,1] be the fraction of trials on which an answer must be issued. Permit independent randomization within a tied reliability group. For a fixed code and proposed answer, the optimal selector accepts high-q cells first. An exchange argument proves this: transferring accepted probability mass from lower q to higher q increases correct accepted mass at fixed coverage.

The optimal frontiers are

    A_L(c) = 1                         for c <= 1/15,
             1/2 + 1/(30c)            for c > 1/15;

    A_Q(c) = 2/3                       for c <= 3/8,
             3/5 + 1/(40c)            for c > 3/8.

They cross exactly at c=1/5. L is better below that coverage and Q is better above it. At equal 10% coverage:

    A_L(1/10)=5/6;                    A_Q(1/10)=2/3.

Thus Q wins forced mean accuracy (62.5% versus 53.33%), whereas L wins selective accuracy at 10% coverage (83.33% versus 66.67%). The acceptance mechanism sees no actual correctness label. It can implement q exactly from the predeclared model and its available (A,B).

These are two different capability components evaluated under two separately fixed scoring contracts. A change from forced responding to selective scoring is not itself a change in complete experiential type. To use UCT III's refinement result, compare the two actual organizations under the **same** selected contract.

Risk–coverage analysis and posterior rejection are established methods. This result specializes them to a family whose entire mean-optimal class has an analytically proved reliability ceiling.

## 5. Costly errors make the reversal operational

Give reward +1 for a correct answer, -ell for a wrong answer, and 0 for abstaining, with ell>=0. The optimal action issues an answer when (1+ell)q-ell>0 and otherwise rejects; ties do not affect utility. Therefore

    V_L(ell) = 1/15 + (14/15)*max(0,(1-ell)/2),
    V_Q(ell) = (5/8)*max(0,(3-2ell)/5)
             + (3/8)*max(0,(2-ell)/3).

The utilities cross at ell=67/45. Above that point L has greater optimal value, despite its lower forced-answer accuracy. At ell=2, V_L=1/15 and V_Q=0: no Q evidence state supports a strictly profitable answer, while L can act on its exact first-coordinate evidence.

This is not an argument that evolution universally favors abstention, simplicity or this code. Ecological costs, available actions, learning and resource constraints would need independent specification. It does show why one average score cannot stand in for suitability across environments with different error costs.

## 6. Physical binding: a reliability signal must concern this answer

Now retain L's raw proposed answers on all 240 source-query rows and alter only installed monitoring/use/report relations. The true q is 1 on query a=1 and 1/2 otherwise. The acceptance gate uses the ell=2 threshold q>2/3.

1. **Aligned:** confidence 1 is attached to query a=1. Utility is 1/15.
2. **Misbound:** swap the query-1 and query-2 monitor connections, making confidence 1 attach to a=2. Raw answers and the complete confidence-value histogram are unchanged. The gate now acts on chance-level answers, giving utility -1/30. Among confidence-1 trials the true accuracy is 1/2; among confidence-1/2 trials it is 15/28.
3. **Correct but unused:** compute true q, but bypass the gate and always answer. Utility is -2/5.
4. **Constant public report:** keep the aligned internal gate but replace its displayed confidence with the constant overall mean 8/15. Utility remains 1/15. The scalar report by itself is calibrated in the weak marginal sense but reveals no trial-level reliability discrimination.

The two routes in case 2 are physically specified, not renamed after outcomes. The arithmetic establishes effects inside that model. A real neural or language-model case additionally requires proof of actual carrier, routing and intervention identity. Equal report histograms do not establish equal binding or causal use.

There is a further answer-relative test. Complement the actually proposed answer while holding A,B fixed. Its correct reliability becomes 1-q. A monitor that continues to evaluate the old candidate is now tracking the wrong target. For L at ell=2, leaving this stale reference in the gate gives -2/15 utility; correctly rebinding to the new candidate gives 0 through abstention. The finite checker verifies these exact values.

This supplies a restricted functional self-reference: a represented reliability concerns the system's **actual proposed response**, rather than just an environmental property or a generic task-difficulty label. It does not establish felt uncertainty, familiar mineness, voluntary agency or an exclusive inner observer.

## 7. Relation to UCT and the original research question

The positive organizational chain is now explicit:

    evidence retained -> particular answer formed -> reliability of that answer
    -> correct binding to the current answer -> operative action selection;

a public report is a separable output relation. The arrows describe the stipulated installed model, not a general phenomenal law. They may be reorganized, overlap or be absent in other architectures. An organism and a silicon device are judged by the same requirements, not by a material-specific exception.

Under actual-process admission, a common constitutive signature and the fixed actual capability contract, C1 plus UCT III C:P1 conditionally transports a genuine capability difference to a complete experiential structural-type difference. The model does not establish the required human/AI realization, compute a quantity of experience, or identify q with subjective confidence. A lower-level process that persists continues to fall under U1/P3 even if a larger system stops reporting or using its signals.

The strongest interpretive conclusion is modest but positive: **an answer-generating organization, an answer-relative monitoring organization and a report-generating organization need not coincide or improve together.** The all-optima result explains why the first can be optimal under one finite objective without supporting highly reliable selection. The wiring result separately shows why correct monitoring evidence can fail to guide action. It would be a mistake to collapse all of these into a single 'intelligence' or 'consciousness' number.

## 8. Sources and priority audit

Internal inheritance is substantial: UCT III §2 already separates task/monitor/report, §5.1 gives the C1 capability-type consequence, §5.4 rejects scalar monotonicity, and OO already derives the four-bit one-message optimum. CORE/EI/R183 address target-relative necessity and architecture-relative use. This note does not count those principles as new.

External antecedents:

- Chow, C. K. (1970), *On Optimum Recognition Error and Reject Tradeoff*, IEEE Transactions on Information Theory. IBM primary publication abstract checked. Posterior rejection is prior work. https://research.ibm.com/publications/on-optimum-recognition-error-and-reject-tradeoff
- Geifman, Y. and El-Yaniv, R. (2017), *Selective Classification for Deep Neural Networks*, arXiv:1705.08500. Primary abstract checked. Risk–coverage analysis is prior work. https://arxiv.org/abs/1705.08500
- Fleming, S. M. and Lau, H. C. (2014), *How to measure metacognition*, Frontiers in Human Neuroscience 8:443, DOI 10.3389/fnhum.2014.00443. Primary authors' measurement framework read, particularly the distinction between bias, sensitivity and efficiency. It prevents calling the current ideal-observer contrast a proof of lower normalized metacognitive efficiency. https://www.frontiersin.org/journals/human-neuroscience/articles/10.3389/fnhum.2014.00443/full
- The quadratic code is a standard bent function; OO's primary-source lineage to Rothaus (1976) and later Boolean-analysis literature remains inherited. No new invention of bent functions is claimed.

The project-level addition is the equality-class reliability ceiling, its complete selective/utility frontier, and a same-answer/histogram binding-and-use construction. Targeted searches did not establish whether this exact theorem package has already appeared. **Historical priority remains unverified.** Quantum conclusive random-access coding is a separate literature; no quantum mechanism is used or inferred here.

## 9. Verification, failures and map status

`check_reliability.py` actually ran with integer/Fraction arithmetic. It checked the 240 rows for each encoder, 30 conditional cells per encoder, 240 coverage points, 361 loss values, every one of 65,536 one-bit encoders, all 896 mean-optimal encoders' posterior laws, the four wiring cases and candidate-complement controls. The general mathematical proofs above do not rely on grid extrapolation.

An additional exhaustive optimization over all encoders at four selected losses is retained as **finite enumeration only**: at ell=0 and 1, maxima 5/8 and 1/4 each have 896 maximizing encoders; at ell=3/2, maximum 1/10 has 840 maximizing encoders; at ell=2, maximum 1/15 has 870. No general all-loss optimal envelope has been proved here, and these counts are not evidence about consciousness.

Scope failures are explicit: changed source/query priors, extra source access or evidence, mixed clocks, unconstrained code changes, and changed acceptance costs require new analyses. Calibrated posterior output does not identify a named feeling. A no-report intervention does not eliminate local experience. Rewiring monitor relations changes the actual model; a passive relabeling with all attachments transported does not.

The canonical graph was obtained as searchable connector text, but was not fully materialized locally or wholly re-reviewed semantically. Relevant source clauses were re-read; whole-map semantic review, all old cross-context relations, and CORE/EI/R183/OO reconciliation remain incomplete. New claims are therefore stored as a typed, disabled `PENDING_MAP` module under the existing unique manifest. Local reference/AND/acyclicity checks are not full semantic certification. No old published bytes, canonical axioms, review closures, tasks or publication workflows are changed.

The next scientific use is a single grounded answer/monitor/use instance in an existing primary study, not another broad information-bound sequence. Before promoting the module, complete the required whole-map audit and verify the actual target bridge. A possible publication section must include the all-optima proof, negative controls, priority limits and no-phenomenal-inference clause.
