# Exact Gray face-merge costs, the Q5 optimum, and a hierarchy obstruction

Date: 2026-10-03. Research draft; published TA-TR-2026-22 v1.0 is preserved.
The primary target M_n >= c 2^n remains OPEN. No asymptotic improvement
is claimed in this note. This round develops an all-dimensional merge
identity and uses a certified finite computation to settle the forward-Gray
candidate in dimension five. It also excludes one proposed simplification
of the all-dimensional proof.

## 1. Definitions and the admissible relaxation

Write gamma_d(x)=x XOR (x >> 1), using coordinate 0 least significant.
R is one plus the number of sign changes in the nonclosing comparison
word; C is the number of sign changes when the comparison word is closed
cyclically. Put G_d=min_w R(gamma_d o pi_w) and
F_d=min_w C(gamma_d o pi_w), over all generic signed additive weights.
These are candidate-specific minima, not the maximum M_d over all
prefix-separable ranks.

Let d>=1, L=2^d, and p=(p_0,...,p_(L-1)) be a parent additive order.
Its complement identity is p_(L-1-i)=p_i XOR (L-1), also with signed weights.
Set A_i=gamma_d(p_i). When adding a new highest coordinate with weight t>0,
the two faces have common vertex order p and rank lists

    A,       B = L + reverse(A).

Indeed gamma_(d+1)(x+L)=L+(gamma_d(x) XOR (L/2)), and
gamma_d(p_(L-1-i))=gamma_d(p_i) XOR (L/2).

The actual scan is a shuffle of the two identical parent score lists,
the second shifted by t. Its layer word b has these necessary properties:

1. It has L zeros and L ones and preserves the order inside each face.
2. Every prefix has at least as many zeros as ones, because the i-th
   lower-face score precedes the i-th upper-face score.
3. b_(2L-1-i)=1-b_i, by additive complement symmetry.

Call a word satisfying these properties a reflected Dyck merge. Its first
half is any length-L nonnegative ballot prefix, and its second half is
the bitwise complement of the reversed first half. This is a relaxation:
some such words are not realizable with a given additive parent, and
some hierarchically repeated words violate translation consistency on
other faces. We never replace the actual chamber set by this relaxation
with an equality assertion.

If the new highest weight is negative, negate the entire weight vector.
This reverses the full scan and preserves both R and C, leaving a positive
highest weight and another signed additive parent. Thus the relaxation
is sufficient for lower bounds against every signed actual scan.

## 2. Exact all-dimensional paired cost

For a reflected Dyck merge, consider only the first L vertices. Let
b_0,...,b_(L-1) be its layer word. For each internal triple, define delta:

| Triple layers | Paired cyclic contribution delta |
| --- | --- |
| 000 or 111 | Twice the turn indicator of those three consecutive entries in A or B |
| 010 or 101 | 2 |
| 001, 011, 100 or 110 | 1 |

**Theorem 1.** In every dimension and for every such parent and word,

    C = 2 + [b_0 != b_1] + [b_(L-2) != b_(L-1)]
          + sum_(k=0)^(L-3) delta_k,

    R = 2 + [b_(L-2) != b_(L-1)]
          + sum_(k=0)^(L-3) delta_k.

The empty sum is zero at L=2. No realizability assumption on the merge
word is needed for the formula. Parent complement symmetry is required.

**Proof.** The mirrored full vertex order is obtained by reversing and
complementing the first half. Complementing the input toggles only the
highest bit of its forward-Gray rank. A within-face edge has its comparison
sign negated under this mirror; a cross-face edge has its sign unchanged.
For a triple whose two edges are within a face, its turn is therefore
repeated in the mirrored triple. For two cross-face edges, both triples
are forced turns. For one edge of each type, exactly one of the two
mirrored triples is a turn. This proves the delta table.

At each symmetry axis (the center and the cyclic closing boundary), the
axis edge crosses the highest coordinate. The pair of adjoining turns
has total 1 if the adjoining first-half edge stays in a face, and total
2 if it crosses faces. Adding the two axes gives the C formula.
Deleting the cyclic closing edge removes 1+[b_0 != b_1] turns and
introduces the initial 1 in R, giving the second formula. End of proof.

This explicitly tracks the turns hidden by merging and their replacement
costs. It is more informative than a scalar parent run count, but it is
not yet an all-dimensional density inequality.

## 3. Exact shortest-path lower relaxation

A state (i,j,u,v) records how many entries of A and B have been used and
the last two layer bits. Require i>=j and i+j<=L. Initialization at length 2:

    (2,0,0,0): cost 0;
    (1,1,0,1): cost 1 for C, or 0 for R.

Append b in {0,1}, update i or j, and add the table entry delta.
For a homogeneous triple the exact three parent indices are determined
by i or j. At length L add 2+[u != v] and minimize.

The recurrence enumerates every admissible half word through its path,
and every state transition appends one admissible letter. Future costs
depend only on the displayed state and the fixed parent arrays. Induction
over path length therefore proves the Bellman recurrence exactly.
It has O(L^2) scalar states and transitions, rather than enumerating all
binomial(L,L/2) half words. Dynamic programming, ballot paths, and the
underlying symmetry are established tools; the table and endpoint costs
are their Gray-specific application here. Historical priority is unconfirmed.

For an actual additive child, its R and C are bounded below by the
corresponding relaxed shortest-path minima of its actual parent.
There is no assumption that all score orders are signed lexicographic.

## 4. Certified finite conclusion: G5=F5=10

The standard Q4 generator provides 5,376 distinct signed additive orders.
They are realized by exact integer weights generated from 14 positive
sorted chamber representatives, all coordinate assignments, and reflections.
Coverage uses the characteristic polynomial in Maclagan's Section 4:

    chi_H4(x)=(x-1)(x-11)(x-13)(x-15).

The region formula stated there gives |chi_H4(-1)|=5,376. Since every
generated order is generic and distinct, the count certifies exhaustion.
This literature count is prior work, not a contribution of this round.

For EVERY one of these parents, the exact DP yields both relaxed minima
at least 10. The linear minimum histogram is

    {10:64, 12:506, 13:124, 14:1554, 15:504, 16:2624},

and the cyclic histogram is

    {10:64, 12:506, 14:1678, 16:3128}.

Every generic Q5 scan has one of these Q4 parents after, if necessary,
negating all weights. Theorem 1 and the recurrence imply R>=10 and C>=10.
The exact generic integer vector (1,14,4,12,20) attains R=C=10.
Consequently G5=F5=10.

This settles all magnitude chambers and weight signs in dimension five
for the FORWARD Gray rank. It is not an exact value for M5, not an inverse
BRGC statement, and not a proof that G_n=(5/16)2^n in larger dimensions.
The existing all-dimensional row lift supplies only the upper ceiling
G_n<= (5/16)2^n for n>=5.

The machine-assisted part of the lower proof is fully reproducible from
the 5,376 parent costs in gray_q5_parent_dp_certificate.json and the
independent standard-library verifier. The certificate packs the costs
into two character strings, in lexicographic parent order, with the full
parent-order SHA-256 and the exact generator seeds. Its encoding is stated
in the file. No floating-point solver is used.

## 5. Same-order hierarchy and uniform edge signs remain insufficient

Consider this centrally symmetric Q6 permutation q:

    (7,6,5,15,14,23,22,21,39,38,37,47,46,3,4,13,
     31,30,19,20,55,54,53,35,36,45,29,2,63,62,51,52,
     11,12,1,0,61,34,18,27,28,10,9,8,43,44,33,32,
     50,59,60,17,16,26,25,24,42,41,40,49,48,58,57,56).

Its two highest-coordinate face restrictions have identical lower-vertex
orders. This repeats recursively at every level of the fixed coordinate
hierarchy, and at every node, with central symmetry at each level.
Moreover each coordinate has a uniform edge comparison direction across
the whole cube: (-,-,-,+,+,+). Hence it also satisfies coordinatewise
monotonicity after one input reflection.

Nevertheless R(gamma_6 o q)=C(gamma_6 o q)=12 < 64/4.
Its successive hierarchy projections have (R,C)
(10,10),(8,8),(4,4),(2,2),(1,2).

**Exact nonadditivity certificate.** In q, vertex 0 precedes 10, but
62 precedes 52, at positions 35<41 and 29<31 respectively. Both comparisons
have identical difference vector, because 62=52 OR 10 and 52 AND 10=0.
An additive weight would have to satisfy both w_1+w_3>0 and
w_1+w_3<0. This is impossible.

Thus the same-order condition for just the fixed hierarchy, even with
central symmetry and uniform coordinate edge signs, cannot prove a 1/4
Gray density bound. Consistency across ALL translated faces is essential.

**All-dimensional lift of this route exclusion.** For n>=6 and m=n-6,
enumerate vertices (q_i << m) OR y, with y=0,...,2^m-1 as the outer
binary counter and q as the inner row. Every comparison changes a high
coordinate and has the same Gray sign as the corresponding cyclic q
comparison. Therefore R=C=12*2^m=(3/16)2^n. The fixed-hierarchy consistency,
central symmetry and uniform coordinate edge signs persist. The exact
translation contradiction persists in any fixed lower-coordinate slice.
This lift is a vertex permutation, NOT an additive scan or a counterexample
to the primary target. It excludes the proposed hierarchy-only proof
of the stronger 1/4 bound in every dimension n>=6. It does not exclude
every possible positive constant under that relaxation.

## 6. Verification, provenance, and next obligation

Run python3 verify_gray_face_merge_dp.py. The receipt records:

- Exhaustive full-word verification of the paired identity and DP against
  brute force on all signed Q1--Q3 parents (6,772 relaxed merge words).
- Every signed Q4 parent, with separate linear and cyclic DP minima.
- Genuine positive translation intervals at the specified integer
  representative of each Q4 parent (105,984 intervals); this validates the word constraints
  and endpoint accounting, not entire Q4 cones or all Q5 chambers by sampling.
- The exact Q5 additive witness, Q6 hierarchy/nonadditivity certificate,
  and hierarchy lifts through n=14.

The analytic merge formula holds in all dimensions. The exact G5 lower
bound uses certified finite coverage; finite calculations are not an
asymptotic proof. Exploratory searches before the final verifier also found
hierarchy permutations with C=18 on Q7 and C=22 on Q8; these are not needed
for any theorem here and no zero-density conclusion is drawn from them.

After that checkpoint, a separate pressure step checked the fully
translation-consistent, noncoherent five-dimensional term order in
Maclagan Example 2.5. All 945 nonempty common translations pass, and all
3,840 coordinate assignments/reflections have minimum R=C=18. This single
prior-work order does not refute the 1/4 or 5/16 candidates. Its replay is
verify_term_order_pressure.py and its receipt is
noncoherent_term_order_pressure.json. This is a finite negative pressure
result; it does not prove that translation consistency alone is sufficient.

Primary source rechecked: Diane Maclagan, *Boolean Term Orders and the Root
System B_n*, Sections 2 and 4, https://arxiv.org/pdf/math/9809134,
DOI 10.1023/A:1006207716298. Complement symmetry, translation invariance,
chamber counts, and dynamic programming are existing methods. Targeted
searches did not establish historical priority of the exact Gray application.

The precise remaining obligation is to constrain the merge paths jointly
with restrictions on non-hierarchical faces, or otherwise prove a uniform
deficit E_*(a)-D(a)<=(1-epsilon)2^n for actual additive magnitude chambers.
The new DP is a reusable lower certificate for a specified parent family.
Its hierarchy-only extension is invalid as a proof of 1/4 density.
The primary constant-density target and the n^-2 denominator are unchanged.
