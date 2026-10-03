# Genuine translations, local controller fields, and two excluded recursions

Status: three analytic results with independent executable audits. The general
constant-density problem for M_n remains OPEN. These results do not replace the
published TA-TR-2026-22 v1.0 and establish no new bound for M_n. No least
counterexample dimension or global literature priority is claimed. Standard
Gray ranks, Boolean-poset extensions, run counting and finite-state elimination
are inherited tools; the contribution here is the precise quantified
construction and the proof-route exclusions.

## 1. Definitions and the retained controller identity

Use the forward Gray RANK g(x)=x XOR (x>>1), not the inverse rank of a BRGC
vertex listing. A paired-sibling rank has bits

    r_h(x)=x_h XOR x_(h+1) XOR theta_h(x>>(h+2)), h<n-1;
    r_(n-1)(x)=x_(n-1).

The previously verified paired-prefix separator lemma makes every such rank
strictly affine prefix-separable. We use that lemma, not a claim that arbitrary
permutations satisfy it. Input coordinates and bit numbers start at zero.

Write x=(x0,x1,y), F=2^(n-2). Fix a paired upper rank B(y). A face has scores
s_y+(0,a,b,a+b) and ranks 4B(y)+(g_2(u) XOR (b0+2b1)). Here b0 is free on
each face, while b1(y)=y0 XOR theta1(y>>1). The two faces 2z,2z+1 therefore
have OPPOSITE phases. A cross-face comparison depends only on B. A turn is
constant, or belongs to the two lower bits of one face. With the notation of
PAIRED_QUARTET_CONTROLLER_POTENTIAL.md, let

    A_y(t)=min_b c_y(b,t), Delta_y=A_y(1)-A_y(0).

Then the exact fixed-upper paired minimum is

    C + sum_y min_t A_y(t)
      + sum_z 1[Delta_(2z)*Delta_(2z+1)>0]
                * min(abs(Delta_(2z)),abs(Delta_(2z+1))).

This identity is valid for any event interleaving. The open problem is a
uniform positive-density bound when s is genuinely additive and B genuinely
paired, not the elimination identity itself.

## 2. Exact geometric formulas for the controller bias

Assume a,b>0 and all complete scores distinct. An internal comparison can
only join consecutive vertices in the restricted four-vertex score word;
otherwise the intermediate face vertex would intervene in the complete
word. Maximal consecutive internal comparisons form components. Signs of
comparisons entering or leaving a component are the fixed cross-face signs.
A missing global endpoint has exterior sign zero.

### 2.1 The cone a<b

The face input word is (0,1,2,3), with comparison signs

    ((-1)^b0, (-1)^b1, -(-1)^b0).

Only the middle comparison can involve b1. If it is absent from the complete
scan, Delta=0. If all three comparisons are consecutive, the two internal
turns sum to one, independently of both bits, so again Delta=0.

In every remaining case where the middle comparison is present, its maximal
internal component has one or two comparisons. Write s_L,s_R for the fixed
exterior signs of this component. Then EXACTLY

    Delta = s_L+s_R.

For a one-comparison component the two boundary turn costs are
1[s_L != t]+1[t != s_R], where t=(-1)^b1. Their difference between t=-1 and
t=+1 is s_L+s_R. For a two-comparison component, the b0 comparison sign is
free. Minimizing its two adjacent turn costs makes that half cost
1[s_L != t], or 1[t != s_R], respectively; the other exterior term is
unchanged. The same difference follows, including a missing exterior term.
Other components depend only on b0 and contribute no bias after elimination.

Thus ordinary-face nonzero bias is +/-2 and occurs exactly when the component
passes through its face rank interval in the same direction on both sides.
A rank peak or valley has opposite exterior signs and zero bias. Endpoint
exceptions can have bias +/-1.

### 2.2 The cone a>b

The input word is (0,2,1,3). All three internal comparisons have highest
changed input bit 1; their signs are t*(+,-,+), t=(-1)^b1. The bit b0 has NO
effect on any comparison, including cross-face comparisons. For each maximal
internal component consisting of restricted edges i through j, i,j in{0,1,2},
put q_i=(-1)^i and q_j=(-1)^j. Internal turns do not depend on t. Its boundary
bias is q_i*s_L+q_j*s_R. Consequently

    Delta = sum_components (q_i*s_L+q_j*s_R).

In fact no two consecutive complete scan vertices can differ ONLY in bit0:
for x0=0, if x1=0 the vertex x+e1 is between x and x+e0; if x1=1 the
vertex x+e0-e1 is between them. Both statements use 0<b<a. Thus deleting bit0 yields two shifted
copies of the upper additive scan, and the full comparison word is determined
by the upper paired rank and the merged projected word. This fact does not
imply that run counts double; Section 3 gives a real counterexample.

Audit: verify_quartet_middle_bridge_bias.py checks BOTH formulas for all
39648 wall/upper-rank cases of the earlier fixed-upper two-weight arrangement,
317184 face checks, zero violations. It reuses those cells to independently
test the NEW formulas, not as new chamber coverage. Upper metrics are fixed:
this is not all Q5 weight chambers. Runtime7.7929913840052905 seconds; audit
SHA256 4e21ad0915071fea9fa6cf2a5ba33d245eeee0fc2bb238f12497b704bb3f8315.
Full parameters/examples and bias histogram are in
quartet_middle_bridge_bias_certificate.json; run receipt in the matching log.
The local derivation above, rather than the finite check, establishes all n.

## 3. A genuine all-dimensional failure of scalar doubling

Proposed recursion: for every genuine scan in the a>b cone and every paired
rank, R_merge >= 2R_upper-1. It is FALSE, even with actual additive upper
scores and an actual paired upper rank.

The Q4 seed has positive weights(4,3,2,8). Its forward Gray rank word has
R=10, while deleting bit0 gives weights(3,2,8), upper Gray word with U=6.
The complete seed order and rank values are

    p=(0,4,2,1,6,5,3,8,7,12,10,9,14,13,11,15),
    g(p)=(0,6,3,1,5,7,2,12,4,10,15,13,9,11,14,8).

For n=4+m, T=2^m, use positive generic weights

    (4,3,2,8,18,36,...,18*2^(m-1)).

The seed span is17, so the scan consists of T complete seed rows in numeric
outer order z. Put u=x&15, z=x>>4, epsilon_z=g(z)&1, and define

    rho_n(x)=16g(z)+(g_4(u) XOR (15epsilon_z)).

Its upper projection is

    sigma_(n-1)(x>>1)=8g(z)+(g_3(u>>1) XOR (7epsilon_z)).

These are actual paired ranks: below the core root each theta_h is epsilon_z
(a function only of the allowed higher prefix); at the core root theta is
the next outer input bit; above that root theta=0. This proves admissibility
in every dimension through the inherited strict prefix separator lemma.
In particular floor(rho_n(x)/2)=sigma_(n-1)(x>>1).

The full seed row has9 turns, the upper seed row5 turns; both first signs
are positive and last signs negative. Complementing all core rank bits
negates endpoint signs and preserves internal turns. Both words have the
SAME extra cost at every outer-row boundary. Numeric outer increments that
flip their lowest bit without carry flip epsilon and have boundary cost2;
there are T/2 such increments. The other T/2-1 increments preserve epsilon
and have cost1. Hence for T>=2 the boundary cost B=3T/2-1 and

    R=9T+1+B=21T/2, U=5T+1+B=13T/2,
    (2U-1)-R=5T/2-1=(5/32)2^n-1.

For T=1, B=0, R10,U6, deficit1. Every score is a distinct integer: seed
scores are distinct in[0,17] and outer rows have spacing18. This is a REAL
all-dimensional scalar-recursion obstruction, not a nonadditive toy model.
Nevertheless R is a positive fraction of 2^n; the result refutes neither
the paired quarter conjecture nor the main constant-density M_n target.

verify_paired_two_copy_scalar_obstruction.py independently checks actual
scores, orders, projection, rank masks and exact formulas for n4..18;
prefix separators checked directly through n6. Paired-mask equality is
checked at every vertex through n12 and1024 sampled vertices above n12;
the displayed bit identities supply the general proof. Zero violations,
runtime1.3972133049974218 seconds, audit SHA256
a526b2c93c7393fd6b523a19928a70dd93dea2e8cd1d21f12da11e7faf85f57f.
Certificate and run log retain every parameter and checked scope.

## 4. Even coherent coordinate DIRECTIONS do not give density

A Boolean-poset extension lists x before x+e_j whenever x_j=0. Such an
extension respects every positive coordinate direction. It need not come
from one additive score vector. The distinction is necessary, not cosmetic.

### 4.1 Every paired rank admits an O(n)-run poset extension

For every paired rank on Q_n, n>=2, there exists a Boolean-poset extension
whose rank word has at most6n-7 runs.

Proof. Partition into four-vertex faces with fixed y=x>>2. On each face the
natural input order(0,1,2,3) is a poset extension and its paired rank word is
unimodal: first/last signs are opposite, with one turn. Group faces by the
Hamming weight of y and by their common peak/valley type theta0(y). Different
faces in one weight layer are incomparable in their upper coordinates.

For a peak group, split every local face word at its peak, keeping the peak
in the first part. Merge all first parts by increasing rank; then merge all
remaining parts by decreasing rank. Every local face order is preserved and
the combined word has exactly two runs. Its global maximum lies in the
first part, so the joining comparison is negative. The valley group uses
the reverse directions and also has exactly two runs. Concatenate groups
in increasing upper weight, either type order within one weight.

Within a face all poset relations hold. Between different comparable upper
faces, upper weight strictly increases, so all such relations also hold.
There are G<=2(n-1) nonempty groups. Each contributes one internal turn;
each group join contributes at most two further turns. Thus

    R<=1+G+2(G-1)=3G-1<=6n-7.

### 4.2 An antipodal forward Gray witness with exactly4n-8 runs

For every n>=3, forward Gray admits an ANTIPODAL Boolean-poset extension
with exactly4n-8 runs. First work on the top-input-bit-zero half. Its faces
are y=0,...,2^(n-3)-1. All face types are peaks since theta0=0. Use one
peak merge per upper-weight layer. There are L=n-2 layers. Every layer
starts with sign+ and ends with sign-. A join between successive layers
contributes exactly one turn, regardless of its own sign. The half has

    R_half=1+L+(L-1)=2L.

Let p0 be this half order; complete it by

    p = p0 concatenated with complement(reverse(p0)).

Complement-reversal preserves the poset extension, and all top-coordinate
edges lead from the first to the second half. The order is antipodal.
For forward Gray, g(complement(x))=g(x) XOR2^(n-1). Therefore the second
rank word is the first reversed and shifted by2^(n-1). Its first sign is+
and the joining comparison is+. The preceding sign is-, giving exactly
one extra turn at the join. Thus R_full=2R_half=4n-8.

For n>=5 this construction is explicitly NONADDITIVE. Its order satisfies

    4 before8, and11 before7.

The first comparison requires w2<w3; the second compares scores
w0+w1+w3 and w0+w1+w2, requiring w3<w2. No real additive vector, of ANY
signs, can satisfy both. These comparisons are incomparable face corners;
their nested ordering violates the common translation of identical faces.

Thus coordinate directions, ancestor support, local permutation budgets
and antipodal symmetry STILL do not suffice for a positive-density paired
certificate. This strengthens the earlier R=2 nonadditive obstruction,
which violated coordinate directions. It is NOT an upper bound for M_n:
the constructed order is not a permitted generic additive scan.

Audit: verify_paired_poset_scan_obstruction.py checks every cube edge,
antipodal pairing, exact Gray runs and the signed-graph identity through
n18, plus88 fresh arbitrary paired masks on n2..12. It verifies the two
contradictory translated-face comparisons, and direct prefix separators
through n6. At n18 all2359296 cube edges are checked, R64. Seed202610031348,
zero violations, runtime4.158917008986464 seconds, audit SHA256
c6be4bde84d89d5b3f52771d22c09ef62fed4b137a76c1b3b613fc652d5ca1e3.
The source regenerates complete orders; certificates retain their SHA256,
counts and explicit inequality positions instead of redundant huge lists.

## 5. Restart point and relation to the concurrent Q5 theorem

The latest master version43 adds an independent complete paired Q5 base
(minimum9 over all actual scans and masks) and a quarter-density theorem
for separated or endpoint-only-overlapping five-faces. Those results are
credited to that separate checkpoint; they were not produced or independently
fully audited by these three verifiers. Their limited overlap hypothesis
is retained, and their count must not be substituted for all dimensions.

The next useful target is an interior-overlap charging lemma using BOTH
the actual translate geometry and all upper paired controller constraints.
The exact exterior-field formulas in Section2 identify the phase penalties
that must compensate erased local turns. The O(n) poset construction warns
that preserving directions is insufficient, while Section3 rules out a
scalar two-copy doubling recurrence even with genuine additive structure.
Keep a multistate deficit or explicit capacity-disjoint crossing certificate;
do not reopen either excluded scalar route as an untested conjecture.

No jobs from these three audits remain running.
