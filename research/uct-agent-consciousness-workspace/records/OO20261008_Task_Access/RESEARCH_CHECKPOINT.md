# OO20261008 — Task-access structure, exact distinctions and predictive usefulness

8 October 2026. Unpublished UCT theory-first research supplement. Read baseline: d8fe35b450fef523c9d48ded5639ef49bb10a999. Preserve the highest guide, canonical graph, CORE and EI. **PENDING_MAP / AUDIT_INCOMPLETE**; no automatic theorem promotion, publication, subjective-experience measurement or historical-priority claim. This remote checkpoint preserves the substantive proofs and a reproducible core program. The downloadable expanded package has longer discussions, additional verifiers and logs; it is not claimed to be a byte-identical remote copy.

## 1. Actuality, inheritance and fixed question

The author asks why experience and intelligence appear coupled in biological systems while a calculator computes accurately and a language model can describe human experience. C1/U1/P3 are unchanged: every admitted actual process has nonempty experience; a persisting local process does not lose experience merely because a larger process exists or a downstream reader cannot access it. An abstract register, decoder or fitted model is not automatically a complete actual human/AI process.

UCT III §5 already gives complete experiential-type change under genuine fixed-contract capability change, without a scalar richness ladder. IE20261008 already supplies exact calculation versus context choice/report and the late-query example. EI20261008 already supplies architecture-relative task dependence; CORE supplies target-relative minimal supports. The present increment is a constructive separation between exact recoverable distinctions and graded predictive usefulness, together with noise and query-direction controls. The mathematics is established linear algebra, Boolean analysis and communication theory.

Fix X uniform in F2^n and a nonzero query a independent of X. The requested answer is a dot X modulo two. A pre-query circuit sends Y=e(X); a later installed decoder d(a,Y) answers, without other source access. The task weights, deadline, memory/communication accounting and evaluated process are declared. All parity questions have equal weight only in the explicitly uniform battery. Scores below are optimal/attained accuracies for these tasks, not IQ, consciousness amount or named qualia.

The original n registers may either be outside an isolated-synopsis scope or remain within a persistent-source assembly. Distinguish those scopes. Loss of downstream recoverability is not global physical erasure.

## 2. Linear access theorem and exact task-direction comparison

Let e(X)=HX over F2, U=row(H), r=rank(H). For any decoder, including nonlinear/randomized ones,

    p_H*(a)=1 if a in U, and 1/2 otherwise.
    J_w(H)=1/2 + weight_w(U minus {0})/2.
    J_uniform(H)=1/2+(2^r-1)/(2(2^n-1)).

Proof: if a=lambda^T H, the installed decoder returns lambda^T Y. Otherwise there is v in ker(H) with a dot v=1. Pair x with x+v in each message fiber: the message agrees and the answer flips. Uniformity makes both answers equally likely. No postprocessing can improve on a guess. Averaging proves the score formulas. A decoder can predeclare the first solution lambda for each public a, and output zero when none exists; no external oracle is required.

For n=4 compare Y_item=(x1,x2) and Y_relation=(x1 XOR x3,x2 XOR x4). Both are two uniform bits, rank two, with mean 3/5 over all fifteen nonzero parity queries. On the four coordinate questions the scores are 3/4 versus 1/2. On the two cross-pair questions (x1 XOR x3,x2 XOR x4), they are 1/2 versus 1. Same information amount and same overall score conceal different task directions.

Within this linear/source/task class, U dominates V for every task weighting iff V is a subset of U. Inclusion gives pointwise dominance; a in V minus U supplies a single-query counterexample. Incomparable rowspaces therefore have opposite rankings under suitable tasks. This is not a universal partial order on actual conscious systems.

## 3. Nonlinear counterexample: better score without more exact answers

For n=4 use the one-bit encoder

    f(X)=x1*x2 XOR x3*x4

and the fixed decoder d(a,b)=b XOR f(a). It scores 5/8 on EACH nonzero parity, with no parity answered perfectly. Any rank-two linear encoder scores 3/5 on the uniform battery; a rank-one linear encoder scores 8/15 and answers exactly one parity perfectly. Thus the one-bit nonlinear code scores better than every rank-two linear code on this battery, despite retaining no perfectly answerable parity query.

This is a restricted-class comparison, not a claim that the unrestricted two-bit optimum is below the one-bit optimum. A two-bit system can emulate this one-bit encoder. No contradiction of UCT III C:P7 (value of added information) arises.

### General proof and four-variable optimality

For any Boolean encoder f define W_f(a)=sum_x (-1)^(f(x) XOR a dot x). For nonzero a and uniform X, majority decoding in the two message cells gives

    p_f*(a)=1/2+|W_f(a)|/(2*2^n).

The two cells' signed parity counts sum to zero and differ by W_f(a), proving the formula. The two-variable identity sum_(u,v)(-1)^(uv XOR au XOR bv)=2*(-1)^(ab) factors over pairs. For the displayed four-variable f, W_f(a)=4*(-1)^f(a), hence d(a,b)=b XOR f(a) attains 5/8.

For ANY four-variable one-bit encoder, Parseval gives sum_a W_f(a)^2=256. Cauchy–Schwarz yields sum_(a!=0)|W_f(a)| <= sqrt(15*256)<62. Walsh coefficients are even integers, so this sum is at most 60. Uniform mean accuracy is at most 1/2+60/(2*16*15)=5/8, attained above. Randomized strategies are mixtures of deterministic encoder/decoder pairs and cannot improve the average optimum. Exhaustive code finds 896 maximizing encoders among 65,536 functions; the proof is independent of that enumeration.

For every n=2m, set f_m(X)=XOR_j x_(2j-1)*x_(2j). Tensor factorization gives W_(f_m)(a)=2^m*(-1)^f_m(a). One nonlinear bit achieves

    1/2+1/(2*2^m),

whereas any rank-m linear message achieves

    1/2+1/[2*(2^m+1)].

The positive gap is 1/[2*2^m*(2^m+1)]. Global optimality over all nonlinear codes is claimed here only at n=4. The gap shrinks rapidly with n. These are classical quadratic bent functions; their mathematics is not invented by UCT. Historical priority for this exact explanatory/numerical package is unverified.

## 4. Noise changes the effective comparison

For full-row-rank H, let Y=HX XOR E with independent Bernoulli(epsilon) errors, 0<=epsilon<=1/2. If a=H^T lambda,

    p*(a)=[1+(1-2epsilon)^weight(lambda)]/2;

otherwise p*=1/2. Proof: HX is uniform, so posterior error bits remain independent with the declared probabilities. The target error is lambda dot E; its signed expectation is the product (1-2epsilon)^weight(lambda). The parity decoder is Bayes optimal. Outside row(H), the earlier fiber pairing still prevents recovery.

Compare encoding (x1,x2) with encoding (x1 XOR x2,x2), followed in each physical device by fresh independent 10% errors. Noiseless access and total mutual information agree, but optimal x1 accuracy is 9/10 versus 41/50. The second answer combines two noisy channels. The common mutual information is 2[1-h2(epsilon)].

This is not a failure of representation invariance. A PURE coordinate change also transports the noise and intervention law. Re-applying independent noise after each distinct physical encoder changes the actual device. Properly transported correlated noise restores equivalence. Biological/silicon substitution cannot be treated as a mere relabeling without checking these implementation conditions.

## 5. A late query may recruit retained local information

In the persistent-source version, all n source bits remain stored. A real reverse route carries the late query a to the source-side parity circuit, which returns a dot X in ONE forward bit. Every query is answered correctly. Count n backward query bits for arbitrary parities (ceil(log2 n) for an individual-coordinate index), n source-memory bits, source-side gates and round-trip time.

In contrast, a fixed one-bit synopsis sent before the task cannot answer every query perfectly. The coordinate queries alone distinguish all 2^n source states, requiring at least 2^n distinct fixed messages for zero error. At n=4 the best one-bit synopsis averages only 5/8, as proved above.

No lower bound is violated: the retained source and newly admitted query-return route change the communication architecture. Thus flexible task use need not place all relevant information simultaneously in a small central register. It can be distributed and recruited over time. This is a communication/organization result, not a proof that human attention or subjective unity equals reverse routing. Cutting the reader route does not annul experience in physically persisting local processes under U1/P3.

## 6. Connection to UCT and failure conditions

For a real application, independently establish actual P/Q, common constitutive signature K, time, boundaries, installed encoders/consumers, noise/ports and agreement between the model score and true fixed J. Only then apply inherited C:P1: a genuine capability-profile difference implies different complete experiential structural types under C1. A mathematical curve does not identify redness, pain, effort, mineness, subject count, or the current assistant's consciousness.

Reject the following shortcuts: more task accuracy means more exactly retained distinctions; fewer bits are generally better; rank counts experience; noiseless equality establishes full noisy equivalence; a one-bit answer means one-bit total organization; externally decodable information is automatically used by the system; inaccessible local information means absent local experience; query feedback is a basal-experience gate.

Failure controls: a nonuniform source can make out-of-rowspace guesses exceed 1/2; nonlinear encoders invalidate the exact linear-access dichotomy; dependent H rows invalidate the unique-lambda noise formula; side information or return queries invalidate the isolated-synopsis scope; changing the task weights can reverse the encoder ordering. No selected-feeling bridge is closed by any of these constructions.

## 7. Map status and actual verification

Canonical blob 172c254c5f09ce83a5daf67244f36fbc5a3b9254 was obtained as searchable decoded Git-data text after contents returned empty. Direct compute download failed DNS. The whole large graph was NOT materialized locally, all old nodes/rules were NOT individually re-reviewed, and CORE/EI full semantic reconciliation remains incomplete. Preserve the unique UCT_FORMAL_GRAPH_MODULES.json entry and append OO only as disabled/pending. Do not treat files in records as automatic established premises.

Direct inherited anchors: A:C1, A:C1_OI, A:U1, A:ACTUAL_TOKEN, C:FIXED_J, C:P1, C:P2_COORD, C:P3, C:P7. Rule c01 has A:C1_OI AND C:FIXED_J; c12 uses C:DECISION. Persistence cites original UCT I P3 rather than guessing a new canonical node ID.

Expanded local module: 24 typed nodes, 12 conditional rules, explicit guards for instantiated examples and actual-realization claims. Local references/AND dependencies and acyclicity checked; all local proofs and limits reviewed. Full semantic audit remains AUDIT_INCOMPLETE after every substantive block. Newly derived mathematics remains candidate material, not an automatically promoted UCT result.

Actually executed: 5,054 small binary matrices with exact task-profile checks; all 65,536 four-input one-bit encoders; 300 rational noise cases; six even-variable families through n=12; all 67 binary four-dimensional subspaces and 4,489 dominance comparisons; 4,284 query-return cases in a separate verifier. A copied IE verifier was rerun successfully as inherited regression, not a new experiment. Integer/Fraction arithmetic is used for claims. No human, animal or actual language-model intervention was run.

## 8. Primary source lineage and read scope

- UCT III v1.0, DOI 10.5281/zenodo.23137088, §5 directly reread; graph c01/c12 inspected. UCT I C1/U1/P3 and TA25 remain inherited foundations. IE, EI and CORE overlaps are explicitly credited.
- Baker et al. (2026), Use and usability: concepts of representation in philosophy, neuroscience, cognitive science, and computer science. DOI 10.51628/001c.160037; arXiv:2604.13829v1. Publisher abstract and §§3.2–3.3 read. Direct prior account of information, useful/usable format, availability and actual downstream use; not UCT inventions.
- Gur-Arieh, Geva and Geiger, Mixing Mechanisms: How Language Models Retrieve Bound Entities In-Context, arXiv:2510.06182v2 (28 May 2026 revision). Abstract and causal-model/ablation discussion read; no raw-data reanalysis. Multiple retrieval mechanisms provide functional evidence. Their roughly .95 Jensen–Shannon similarity is not consciousness accuracy or a general 95% task score.
- Feng and Steinhardt, How do Language Models Bind Entities in Context?, arXiv:2310.17191. Abstract read; binding-ID findings are functional, not phenomenal, evidence.
- Potapov, Taranenko and Tarannikov (2021), An asymptotic lower bound on the number of bent functions, arXiv:2108.00232. Abstract read for the established flat-Walsh definition. Rothaus (1976), On bent functions, DOI 10.1016/0097-3165(76)90024-8, bibliographic identity verified through primary later references; direct original retrieval failed.
- Roughgarden, Communication Complexity (for Algorithm Designers), arXiv:1509.06257 (2015). Primary source text for INDEX one-way versus interaction located; full collection not audited. The elementary bounds above are independently proved.
- Ritchie et al., Decoding the Brain: Neural Representation and the Limits of Multivariate Pattern Analysis in Cognitive Neuroscience, PMC6505581. Decoding/use discussion inspected.

The record is a substantive theoretical application and counterexample package, not an independently established new consciousness law. Novelty of the exact specializations remains PRIORITY_UNVERIFIED. Next: return to one grounded actual encoder/consumer/feedback episode and an independently specified experiential relation rather than expanding generic information bounds. First complete the pending whole-map audit before any promotion or publication.
