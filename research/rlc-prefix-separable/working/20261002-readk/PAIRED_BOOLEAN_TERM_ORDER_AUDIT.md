# Translation cancellation is stronger than coordinate directions

Status: a new exact finite relaxation audit, not an all-dimensional run
theorem. Main M_n constant-density target remains OPEN. Published v1.0 is
preserved. No universal flip-connectivity or completeness assertion is made.

## 1. The known domain and the current proof question

Primary source: Diane Maclagan, *Boolean Term Orders and the Root System B_n*,
arXiv:math/9809134v2, 10 March1999, https://arxiv.org/pdf/math/9809134.
Definitions1.1,2.4 and3.4, Proposition3.7 and Section6 were read directly.
Boolean term orders, their flips, coherent realizations, antipodal complement
symmetry and the noncoherent examples below are PRIOR WORK, not discoveries
of the current RLC project. The new audit applies the existing paired rank
optimization to a specifically stronger comparison-consistency domain.

A positive Boolean term order is a total order with empty set first, whose
comparisons are preserved on adding any common disjoint coordinate subset.
Every positive additive scan is such an order. The converse is false; an
order is coherent when one additive weight vector represents it. Thus a
proof using translation invariance alone would have to survive NONCOHERENT
term orders too. Coordinate-direction consistency is much weaker, as the
new all-dimensional O(n)-run poset obstruction already proves.

Source Section6 lists546 sorted Q5 term orders versus516 coherent ones;
its two counts are not new. Its six-variable examples and noncoherence
certificates are likewise known. The claim here concerns the independently
calculated paired run minima on the30 additional orders.

## 2. Enumeration, exact certificates and limited coverage

probe_paired_boolean_term_orders.py starts at numeric Q5 order, and performs
every primitive flip preserving singleton coordinate order. It produces a
connected546-order component with2914 directed flips. EVERY order is checked
for common-intersection cancellation, positivity and complement reversal.
The count agrees with the primary paper's total. Component closure alone is
NOT treated as a proof of global flip connectivity in arbitrary dimension.

All516 coherent members have explicit INTEGER weight witnesses: every
consecutive score difference is strictly positive. For each of30 noncoherent
members, a nonzero nonnegative INTEGER vector y on consecutive comparison
inequalities satisfies y^T A=0. Strict additive feasibility would allow
Aw>=1 after scaling, giving0=y^T Aw>=sum y>0. Thus all noncoherence claims
are exact. SciPy only finds candidate witnesses; integer checking certifies
them. Full orders, witnesses and sparse Farkas vectors are retained.

The independently saved complete COHERENT Q5 paired bound9 is not recomputed
or reclaimed as progress. Instead optimize ONLY the30 noncoherent orders,
with every120 coordinate permutation and every32768 paired rank orientation
via exact ancestor-conditioned optimization. The attaining ranks are
evaluated directly on each word. New cases:3600. The joint minimum over
this additional domain is EXACTLY12, exceeding the coherent minimum9.
No consequence in all dimensions is inferred from that observation.

## 3. Two specified noncoherent Q6 examples

The complete words are reconstructed from the first32 entries given in
Maclagan Remark3.10 and Proposition6.2, using complement-reversal. Each is
directly checked as a full term order, and has an INTEGER noncoherence
certificate. All720 coordinate priorities and all2^31 paired masks are
optimized by the certified ancestor method. Their exact minima are33 and26.
These are TWO specified cases, not all169444 sorted Q6 term orders and
not coherent scans. The current audit provides no fullQ6 classification.

The complete candidate audit finishes in2.434493704000488seconds, with
digestfa323abbe6c6522623cab1af09b08bfd31fdf4b35034dd93c3ec997ae349fb49.
Its lossless certificate is paired_boolean_term_orders_certificate.json.gz.
Decompressed raw bytes SHA256
e15823266371b9792d2ef45a2cae6627066b7468fc53e9d94d35e9668d4b449f.

## 4. Independent no-LP, no-ancestor verification

verify_paired_boolean_term_orders.py independently checks EVERY permitted
common disjoint addition (rather than the generator's cancel-intersection
test), every component neighbor, every integer weight and Farkas vector.
It recomputes all3600 Q5 and1440 Q6 paired minima by a DIFFERENT elimination:
fix the upper paired mask, build each four-face's explicit four-state turn
costs, minimize its low bit, then enforce opposite second phases on each
sibling pair. This uses the already proved controller identity, not the
ancestor optimizer or an LP solver. The reconstructed attaining full rank
is evaluated directly for every priority. All complete run histograms agree.

The final verifier uses no SciPy import or solver; it retains a separate
run receipt and result with exact coverage and digest. Its first audit
shared the generator's cancellation checker; that was replaced by direct
common-addition enumeration for stronger independence. No minima changed.

## 5. Exact restart target

The previous direction-only relaxation has an O(n) paired witness. This
stronger translation-consistent relaxation has NO obstruction among the
newly tested noncoherent examples. This leaves a precise live route:

    Do all Boolean term orders force D+K+phi >= c*2^n
    for the paired rank family, for some fixed positive c?

This is an UNPROVED stronger-domain question, not a result of these finite
checks. A successful proof would cover actual positive additive scans;
input reflection closes signed scans for the paired family. Conversely,
a noncoherent counterexample would reject this stronger-domain shortcut
without rejecting the actual M_n target.

The next substantive step should derive a capacity-compatible crossing
inequality from common-addition consistency, or find a sharply specified
counterexample with exact term-order verification. Do not enumerate the
known coherent Q5 base again; do not label Boolean term orders a new concept;
do not substitute finite no-failure lists for an all-dimensional argument.
