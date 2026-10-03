# Exact larger cores and their all-dimensional extensions

Date: 2026-10-03. Research counterexamples in a specified scan family.
Main M_n constant density remains OPEN. No historical-priority claim.

## 1. New explicit family

Take the nine-coordinate secondary core

    b=(108,106,105,102,110,126,32,170,0).

It is generic within each cardinality layer, certified by 502 positive
integer adjacent comparison margins, whose minimum is 1. The exact
interior graph is

    D_int=40, E_int=W_int=116,
    edges ((1,2,32),(1,3,32),(1,5,-4),(2,3,32),
           (3,5,-4),(3,6,4),(4,5,4),(5,7,4)).

The spin mask 78 satisfies every edge. Its input reflection is z=116.
This is an independently checkable integer certificate, not a claim of
optimality over every nine-dimensional secondary vector.

For any n>=9 put m=n-9, L=2^m, append secondary tail coefficients
860*2^j, j=0,...,m-1, and set the common primary coefficient
B=1+sum(all secondary coefficients)=860L. The resulting genuine
positive integer weights w=B+b order vertices by cardinality first
and additive secondary score second.

The exact all-dimensional graph has interior contributions L times
the displayed graph, boundary D=4 and zero boundary off-diagonal
coupling. Hence

    D_n=40L+4,   E_n=W_n=116L,
    min signs C_n=218L+2=(109/256)*2^n+2.

For n>=10 the least coefficient is coordinate 8, below the highest
coordinate, so min signs R_n=C_n. For n=9 that coordinate is highest,
so min signs R_9=C_9-1=219. Reflection 116 attains these exact minima.

The limit 109/256 is strictly below the five-core optimum 7/16,
because 109<112. It remains ABOVE the known unrestricted Gray ceiling
5/16, so it gives no improved unrestricted upper bound and no lower
bound for M_n.

## 2. All-dimensional proof

The core sum is 859, so the tail base 860 exceeds its complete span.
The general cardinality-core extension theorem in
CARDINALITY_HALF_DENSITY_COUNTEREXAMPLE.md applies: all core interior
graphs replicate L times, additional interior diagonal count is zero,
and all mixed-label tail crossings cancel by numerical-prefix
translation or central complement-reversal. Core highest couplings
vanish, so a fixed-tail flip of that Gray output bit causes no error.

To sharpen its O(n) error to an exact formula, use that the least core
secondary coefficient is coordinate 8 and the next least is coordinate
6. For n>=10 the top secondary coefficient is a numerical tail bit
at the global highest coordinate. Every cyclic cardinality boundary
edge has label n-1 except the first and final edges, each of label 8.
Each exceptional edge meets an interior label-8 edge. The boundary
between layers 1 and 2 meets the final singleton-layer label-(n-1)
edge, and the boundary between n-2 and n-1 meets the first
next-to-full layer label-(n-1) edge. These are exactly four diagonals.

As in the earlier exact family, the extremal predecessor/successor
of a k-subset exchanges its nearest secondary-priority neighbor.
No other boundary triple is diagonal. Every remaining mixed-label
boundary triple involves the global highest coordinate, and central
complement-reversal cancels it. Thus boundary D=4 and J=0 for every
n>=10. The n=9 base is a direct 512-vertex integer certificate.

The core graph's edge signs are all simultaneously satisfied at mask
78. It follows that the full energy maximum is 116L, independently
of additional tail spins. The exact Gray reflection identity proves
the minimum over all signs, and reflection 116 gives a genuine signed
integer weight witness. The least-magnitude endpoint identity supplies
the linear correction.

## 3. Discovery and independent audit

probe_larger_cardinality_cores.py performed 19,000 deterministic
candidate evaluations in dimensions 6,...,10 with seed 202610030845.
It normalizes secondary coefficients, resolves any fixed-cardinality
ties by a coherent integer perturbation N*b_j+2^j, then optimizes all
signs exactly. Dimensions 6,7,8,9,10 had 1,771, 2,241, 1,988, 1,165,
and 656 distinct sampled orders respectively. Candidate repeats and
tie refinements are recorded. This is not chamber completeness.

Best interior net energies were 8,16,36,76,152. The eight-core example
has limiting density 55/128; the nine- and ten-core examples have
109/256. The ten-core best extends the nine-core value and does not
improve its constant. No failed search is interpreted as optimality.

compress_cardinality_core_certificate.py uses a floating LP ONLY to
propose smaller coefficients. Rational reconstruction yields integer
weights, and every adjacent comparison row is checked with exact
integer arithmetic. Every compressed order hash and graph is compared
with its original. No numerical LP optimum is claimed as a theorem.
The nine-core coefficients shrink from values up to 330,347 to at
most 170 with no order change.

verify_larger_cardinality_core_extension.py does not depend on SciPy.
It independently regenerates all exact comparisons and every graph
coefficient, exhausts signed scans of the nine-bit base and specified
extensions, and verifies the symbolic graph through n=18.

The current useful gap is a dimension-uniform bound on coherent
core interior net energy, or a rigorous family driving its normalized
value toward one. Improving a restricted upper example alone cannot
prove the main lower bound. Next test whether repeated insertion of
a small highest secondary coefficient increases the normalized
interior net energy, while preserving a certificate for every
candidate. The common-offset step cannot be assumed to double net
energy under arbitrary interleavings; only the numeric-tail extension
already proved has that guarantee.
