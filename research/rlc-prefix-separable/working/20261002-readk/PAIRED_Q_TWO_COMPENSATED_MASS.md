# Sharp q=2 mass compensation despite unbounded couplings

Status: ALL-dimensional analytic theorem for the ORIGINAL small-support
branch, with exact independent certificates and a rejected intermediate
conjecture. Main M_n>=c*2^n is OPEN. Published v1.0 unchanged. This does
not extend a finite-dimensional optimum by assertion: the proof works
for every n and every paired orientation.

## 1. Exact objects and the false shortcut

Use the existing paired rank, RAW NON-TOP comparison support q, forced
same-label turns D, signed off-diagonal baseline Gray couplings J and
W=sum|J|. The exact inherited run identity is R=(N+D-E)/2. Baseline Gray
means FORWARD g(x)=x XOR(x>>1), never its inverse.

For a centrally symmetric vertex permutation p, raw support is invariant
under the complementary-prefix involution C. At q=2 it consists of ONE
pair A=(h,z), B=C(A), h<=n-3. The only possible nonzero couplings are
J_root,A=c and J_root,B=-c. The A-B coupling is zero because adjacent
comparisons at the same h cannot have different fixed prefixes.
Therefore W=2|c|, and minimizing over ALL paired masks gives E_max=W:
these two edges form a star and the two active spins can be selected
independently. Every inactive paired label is arbitrary.

The proposed |c|<=1, suggested by the earlier Q2..Q4 actual receipts, is
FALSE for genuine scans. A smallest-dimension genuine obstruction is
the positive generic five-dimensional integer vector

    v=(3,22,2,12,6).

Its exact graph has q=2, D=16, c=3, W=6, K=4; its paired minimum is21.
Direct sorting of its 32 distinct integer scores is independently
checked. The earlier complete signed Q2..Q4 enumerator found no |c|>1,
so the obstruction dimension is minimal relative to that audited
coverage. Coordinate sign reflections preserve coupling magnitudes
through the inherited paired input-reflection relabeling/gauge identity.
The present Q5 pressure run checks positive coordinate orders only.

The obstruction is NOT just finite. Introduce d LOW input/HIGH score
coordinates with weights46,92,...,46*2^(d-1), retaining v at the HIGH
input coordinates. For n=5+d,T=2^d its genuine generic scan has

    q=2, D=16T, c=2T+1, W=4T+2, K=6T-2,
    min_(every paired mask and root) R=22T-1.

Internal rows replicate c=3; each join subtracts1 from J_root,A and
adds1 to J_root,B, so c_new=3T-(T-1)=2T+1. Joins are different-label
triples, hence D_new=16T. Exact spin minimization yields the stated
minimum. Thus individual couplings are unbounded at FIXED raw q=2.
Its run density tends11/16, so it does NOT refute positive-density M_n.
It excludes bounding coupling magnitude from raw support alone.

## 2. The repaired ALL-dimensional theorem

**Theorem.** Every centrally symmetric complete vertex permutation on
Q_n with q=2 satisfies W<=D+2. Consequently EVERY paired rank has

    R>=(N/2)-1.

In particular this holds for every actual generic signed additive scan.
The theorem in fact needs central symmetry rather than full additive
coherence. The failed individual-coupling bound is repaired by counting
the forced diagonal turns that compensate large coupling mass.

## 3. Proof by two distinct budgets

Choose A with its prefix top bit0, so B has top bit1. Split the VERTEX
word into maximal blocks separated by TOP-leading comparisons. A block
of size l>=2 has only non-top comparisons. Its label must be entirely
A or entirely B; leading bit h fixes every input bit ABOVE h, including
the controller bit h+1. Input bit h alternates at every internal step.
A singleton block has two TOP comparisons next to it unless it is a
whole-word endpoint. Such an internal singleton contributes one forced
root-root turn to D.

Write d_non for the sum max(l-2,0) over A-blocks: these are their forced
non-top same-label turns. Write d_single for the number of INTERNAL
singleton vertex blocks lying in A's prefix cylinder. Singleton blocks
elsewhere may give extra D and can be ignored. Mirror symmetry pairs
all A and B blocks and their interior singleton counts. Thus

    D>=2*(d_non+d_single).

At most one whole-word endpoint block lies in A's cylinder: the first
and last vertices are complementary and lie in opposite top faces.
Let eN indicate that this endpoint block exists and has size>=2; let eS
indicate that it is a singleton. Then eN+eS<=1. An endpoint outside the
cylinder makes both indicators zero.

Let tau be the fixed sign of a TOP comparison entering A's top face;
its exiting TOP sign is -tau. In an A-block let eta be its first natural
Gray comparison sign. The signs alternate along the block. For an
INTERIOR block its contribution to c is zero if l is even, and 2*tau*eta
if l is odd and l>=3. An endpoint non-singleton block contributes only
one product of magnitude1. Each interior odd block consumes at least
one d_non turn, so

    |c|<=2*d_non+eN.                         (1)

Now use vertex balance, not the same budget a second time. Define the
controller-weighted signed h-bit mass of a block by

    f(block)=sum_(x in block) (-1)^(x_(h+1))*(1-2*x_h).

For even l it is zero. For odd l it is +1 or-1, and in a non-singleton
block equals eta. It is also defined for singleton blocks. Every vertex
of A's prefix cylinder appears exactly once. For either controller
value, the numbers with x_h=0 and x_h=1 are equal. Hence the sum of
f over ALL these blocks is EXACTLY zero, without any score assumption.

Replace the interior odd non-singleton sum contributing to c by the
negative of the internal singleton sum and the endpoint imbalance.
The endpoint correction has magnitude1 if it is non-singleton: for
odd l the usual 2*tau*f term becomes tau*f, and for even l the mass is0
but the single boundary product is +/-1. If the endpoint is singleton,
there is no non-top boundary product but its mass correction has
magnitude2. If it is outside the cylinder, no correction occurs. Thus

    |c|<=2*d_single+eN+2*eS.                (2)

Add (1) and (2), rather than replacing either by an unsupported bound
on its own. Because eN+eS<=1,

    W=2|c|<=2*(d_non+d_single)+2*(eN+eS)
           <=D+2.

The inherited rank identity and E<=W now give R>=(N-2)/2=N/2-1.
This proof covers all lower coordinates, all raw prefix choices and
all paired labels, including arbitrarily large c. It does not assume
that row boundaries are disjoint faces or that generic scalar doubling
holds. The two separately charged turn budgets are essential.

## 4. Sharp genuine weights in EVERY dimension

For n>=3 put d=n-3 and use the actual generic weights

    w=(8,16,...,8*2^(d-1),1,4,2),

with no initial weights when d=0. The three-dimensional core has q=2,
D=0 and c=1. Its low-input/high-score rows retain q=2; joins subtract1
from c, so the full c=T*1-(T-1)=1 and D=0. Thus W=2 and the exact paired
minimum is N/2-1. With root0, a mask having only the B label set attains
it: in repository indexing this is 1<<(2^(n-1)-3). All inactive labels
may be chosen arbitrarily. These are permuted binary-power scores and
their complete genericity is explicit. Thus the q=2 lower constant and
its finite -1 are sharp for every n>=3.

## 5. Audit files, failed routes, and limits

probe_q_two_root_coupling.py retains the rejected |c|<=1 hypothesis,
seed202610031930, all parameters, relaxed nonadditive counterexamples
and96 genuine positive Q5 counterexamples. Its inherited516 coherent
sorted orders yield61920 coordinate orders,1348 q=2 cases, maximum|c|=3;
the positive-only coverage is explicit. Runtime1.9325449160096468 seconds,
audit507a90f3f8d94f159a33273146a55b15919a77bf38b8cd30295f08c6c4c04930.
This finite result is NOT the general compensated-mass proof.

verify_q_two_unbounded_coupling.py independently computes integer scores,
raw labels, D,J,W,K and direct rank words; no graph optimizer is used.
It audits Q5..Q13,216 direct mask/root/lower-pattern words, the complete
two-active-spin optimization and exact arbitrary-lower-label argument.
Zero violations,1.1179496170079801 seconds; audit
536b1ec79d69fe242c15dfa7b2b4073c028bed6026420f01999b683984b9e6cf.

verify_q_two_compensated_mass.py explicitly reconstructs the block
budgets, vertex-balance sums, endpoint indicators and BOTH inequalities
(1),(2). It checks ALL384 centrally symmetric Q3 permutations (64 have
q=2),790 constructed centrally symmetric q=2 permutations Q4..Q13,
and the sharp genuine family in all11 dimensions Q3..Q13. The random
central permutations are NOT asserted additive, and are valid stress
tests because the theorem genuinely covers the larger class. Zero
violations,2.6369136150024133 seconds; audit
a2c6ce1f1d54a2d910d2bbb0ebc1f75b58be842561eb0e832065f1aa46c0d584.
Its gzip receipt expands415694 bytes, SHA256
d779f66d56f50aef043fce1bd3f57484ba59b62534a2329b50100c4503af3e72.

The analytic all-n proof is primary; finite computations pressure every
step and preserve exact failures. Block/Ising accounting is not a new
general method by name. Narrow literature searches on Gray monotone
runs and Boolean term orders on2026-10-03 did not retrieve this exact
raw-support theorem; this is not a comprehensive priority determination.
The main theoretical effect is closing the exact q=2 base case while
identifying compensation, rather than small coupling, as the useful
quantity. General support growing with n remains unproved.

## 6. Immediate continuation gap: third raw label

At q=3 the support consists of the C-fixed label S=(n-2,0) and one
complementary pair A,B at some h<=n-3. The graph is a four-cycle: root-A
and root-B have opposite couplings c,-c; S-A and S-B have equal couplings
e,e; root-S and A-B are structural zeros. Exact spin optimization gives

    E_max=|c+e|+|c-e|=2*max(|c|,|e|).

The q=2 block proof no longer directly applies: S comparisons can split
its blocks and consume the vertex balance. The precise next sufficient
claim is 2*max(|c|,|e|)<=D+2, or a weaker dimension-independent deficit
bound. First seek genuine counterexamples, retain them if present, and
then charge the extra S transitions without double-counting. Do not
replace this missing theorem by more q=2 verification.
