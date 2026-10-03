# Score-window certificates without a cardinality primary

Status: analytic all-dimensional CONDITIONAL packing theorem and genuine
signed non-cardinality scan classes. The main all-weight M_n problem is
OPEN. Standard interval capacities and the existing paired rank definition
are inherited. Published v1.0 is preserved.

## 1. A general sparse-cylinder certificate

Take ANY actual generic signed additive scan with weights w. Choose input
coordinates i<j<k, k>=j+2, with controller c=j+1. Assume w_k is strictly
largest or smallest among w_i,w_j,w_k. Let

    l=min(w_i,w_j,w_k), u=max(w_i,w_j,w_k), D=u-l.

Let C be ANY free-coordinate set containing i,j,k,c, with any number of
additional unused coordinates. For every assignment f to the OUTSIDE
coordinates, set all unused coordinates in C to0, order its three single
atoms e_i,e_j,e_k by score, and translate by toggling the common bit c.

Because w_k is extreme, one adjacent comparison exchanges atoms i,j
and has highest changed bit j; the other has highest changed bit k.
Toggling j+1 reverses exactly the first paired comparison and leaves the
second unchanged. Common score translation preserves both triple orders
even when w_c is negative. The existing noncontiguous lemma gives one
full-scan turn in the union S_f of their two open position intervals,
for EVERY paired orientation, including either root phase.

Write s_f for the outside subset score. The two intervals are contained
in the real score windows

    (s_f+l,s_f+u), (s_f+w_c+l,s_f+w_c+u).

These windows may contain vertices from OTHER outside assignments or
from unused free coordinates. Face ownership is NOT required here.

**Theorem.** If all consecutive outside subset-score gaps exceed D, then

    R >= 1+ceil(2^(n-|C|)/2)

for every paired rank. There is no cardinality-primary, whole-core range,
positive-weight, or controller-range hypothesis beyond full genericity.

Proof. The original window family is pairwise disjoint because its starts
are more than D apart. The translated window family is likewise disjoint
by common translation. At ANY full-scan turn position at most one window
from each family occurs. Thus the UNION-support load is at most2. Put
primal witness mass1/2 on every S_f. Summing valid turn obligations gives
turn count at least ceil(F/2), F=2^(n-|C|). Taking unions rather than
counting an overlap twice also handles the two windows of the SAME witness.
No finite optimized rank, independence assumption or LP is used.

More generally maximum union-window depth lambda gives R>=1+ceil(F/lambda).
If the cross-phase windows also never intersect, lambda=1 and R>=1+F.
That strengthening requires a separate cross-phase condition.

For a contiguous four-block, choose atoms0,1,3 and controller2. This gives
R>=1+ceil(2^(n-4)/2), hence density1/32 for n>=5. For an arbitrary generic
contiguous five-block, at least two of weights0,1,2 lie on the same side
of weight4. Choose their indices i<j<=2, atom4 and controller j+1; the
input gap is automatically at least2. Under outside gap exceeding the
chosen atomic diameter, R>=1+ceil(2^(n-5)/2), hence density1/64 for n>=6.
The unused core/controller weights may be arbitrarily large, unlike a
whole-face protected-center hypothesis. Minimizing D over the three
eligible pairs improves the sufficient gap condition without changing
the argument.

## 2. Cross-phase disjointness is genuinely stronger

Take the generic actual core weights(34,36,33,48) on input coordinates0..3
and outside weights32,64,128,... . All16 core subset residues modulo32
are distinct: the three atomic weights have distinct even subset residues
and the controller adds odd residue1. Outside offsets are distinct grid
points. Original atomic diameter D=14 is smaller than outside gap32, so
the theorem applies in every dimension.

For n>=5, at score68 (vertex outside-bit4 plus core atom1), the original
window for outside prefix1 is(66,80), while the translated window for
outside prefix0 is(67,81). The position is strictly inside BOTH, so union
support depth is exactly2. The general depth<=2 is therefore attained
in a genuine scan in ALL dimensions n>=5. Disjoint-union depth1 cannot
be inferred just from the same-phase gap hypothesis. This is not an
actual RLC upper bound or a claimed optimum fractional packing formula.

## 3. A signed arithmetic class with cross-phase separation

For ANY contiguous four INPUT coordinates a,...,a+3 choose actual weights

    w_a=A+2, w_(a+1)=A+4, w_(a+3)=A+16,
    A in32Z, w_(a+2) in(32Z+15) union(32Z+17).

Choose ANY signed outside weights in32Z with distinct outside subset
scores. There is no cardinality primary or secondary decomposition.
Core weights and outside weights may have either sign. The original
atomic triple has scores s_f+A+(2,4,16) and leading comparison bits
a+1,a+3; the controller translation preserves order.

Original window starts are in32Z+(A+2); translated starts in
32Z+(A+w_(a+2)+2). All windows have width14. Distinct same-phase starts
differ by at least32. Cross-phase starts differ by at least15, because
the controller residue is15 or17. Hence all2F score windows are pairwise
disjoint. The theorem strengthens to

    R >= 1+2^(n-4), ALL n>=4, EVERY paired rank.

Full genericity is automatic. The eight subset residues of the three
atomic weights are(0,2,4,6,16,18,20,22), all distinct and even. Adding
the odd controller residue produces eight distinct odd residues. Thus
all16 core subset residues are distinct modulo32. Different outside
assignments are distinct grid points. Equality of two complete scores
would force identical core residues, hence identical core vertices, and
then identical outside offsets/assignments.

This theorem covers actual signed scans, arbitrary outside priority and
outside metric, and large interleaving of faces. A concrete positive
instance is core(34,36,17,48), outside32,64,... . For n>=5 the interval
of outside prefix1 between its original scores66 and80 contains the
score70 of the TWO-ATOM core vertex3 with outside prefix0. Therefore the
old support-ownership claim is false, while the new score-window proof
works in every dimension. Whole four-faces have span135 and outside
gap32; they are not separated whole faces.

The class has open neighborhoods. Baseline complete scores are distinct
integers, so their differences have magnitude at least1. A perturbation
delta with sum_j abs(delta_j)<1 changes any pairwise score difference by
less than1. The ENTIRE order is unchanged, not merely the chosen triples.
The same lower bound therefore holds in this neighborhood. Rescaling
weights by t>0 gives the corresponding radius t in l1 norm. This does
not enlarge the claim to all additive scans.

## 4. Executable pressure and exact continuation

verify_paired_score_window_grid.py checks60 arithmetic-class scans on
Q4..Q13, including negative weights, both controller residues, arbitrary
active block positions and signed outside metrics. It reads1092 paired
rank words directly, including every128 paired masks on each Q4 example.
There are60 exact rational perturbation/order-preservation checks. Among
the cases58 are non-cardinality scans and9 have support vertices from
different outside faces. The latter are expected and must not be rejected.

The same verifier additionally checks40 generic four-block same-phase
cases Q4..Q13 and36 adaptive five-block cases Q5..Q13, with456 direct rank
audits and exact integer depth<=2. Positive controls attain depth2 for
all n5..13. Five-core examples permit a huge unused/controller coefficient
and choose atoms adaptively. Exact weights, choices, gaps, loads, rational
perturbations and support digests are retained with source and run log.

An implementation refactor initially reused the atom-index variable as
a scan-position loop variable, causing IndexError before the extra audit
completed. The index variables were renamed and the entire final audit
rerun. This was an implementation failure, not a mathematical counterexample;
the final certificate/log records only the successful complete run.

The general all-weight missing theorem is STILL uniform coverage: can
appropriate sparse cylinders, possibly noncontiguous, always be packed
with positive total density? The outside minimum-score gap may be tiny,
so this sufficient gap condition cannot be silently assumed universal.
Immediate next action: apply the general C-set lemma to the five smallest
secondary-magnitude coordinates in cardinality-primary scans with arbitrary
SIGNED/PERMUTED binary secondary priorities. A suitable controller may
lie outside those five; include it as a sixth free coordinate and audit
the resulting all-n depth2 bound before addressing arbitrary secondary
metrics. Do not repeat the finished grid or block calculations.
