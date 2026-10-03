# Internal cycles are essential: an all-dimensional cut-budget failure

Status: analytic all-dimensional exclusion of a sufficient-proof route,
and a protected block-scan lower bound. Neither the main M_n target nor
the universal paired-sibling quarter conjecture is disproved.

## 1. A five-dimensional seed with independent integer certificates

Take w=(1,14,4,8,16). All 32 subset scores are distinct. Its paired linear
graph has D=0,K=6,W=18. The root-to-top cut lambda in its complementary
half graph is 1: the top has just the edge (0,15) of capacity 1, and
root-to-top path (14,0,15) carries one unit. Thus

    D+K+lambda=7<8=N/4.

The three cycles

    (14,1,12,2), (14,6,13,5), (14,0,15,7)

are negative, have unit multiplicities, and use disjoint coupling edges.
Their successive signed weights are respectively
(1,1,-1,1), (1,1,-1,1), (1,-1,1,1).
They certify phi>=3. Mask 3128 has energy 12=W-2*3 and has R=10, so
phi=3 and the family minimum is exactly 10, independently of a solver.
The scan is a counterexample to the proposed cut-only quarter budget,
not a counterexample to a quarter lower bound for paired ranks.
The already audited complete signed Q4 chambers satisfy the cut-only
quarter budget; n=5 is the least dimension at which this route fails.

## 2. A genuine scan family in every dimension

Start with this seed and append each new highest input coordinate with
coefficient 1+sum(previous coefficients). Thus coordinates h>=5 have
weights 44*2^(h-5). For n>=5 put L=2^(n-5). The scan is precisely L
contiguous core blocks, ordered by the numerical tail value. Every block
uses the same five-coordinate seed order. Genericity follows from the
separated 44-wide tail values and core scores in [0,43].

Within a block the paired variables of core coordinates h<=3 carry the
fixed tail prefix, so their internal couplings are distinct from those
in other blocks. The core top variable at h=4 is shared only between
tail rows differing in coordinate 5; its Gray signs in the second row
are reversed. This is a sign switch at that variable and preserves all
cycle signs and magnitudes. Shared vertices do not create shared cycle
edges, because the other endpoints of all core edges are row-specific.

Every inter-block comparison changes a coordinate at least 5, while the
adjacent last/first core comparisons change coordinate 0. Thus it supplies
two distinct mixed raw products at different low-coordinate variables.
Each such low variable is used at only that one boundary: the last core
prefix has bits 2,3,4 all one, and the first has them all zero. None of
these boundary pairs coincides with a core pair or another boundary pair.
There are no additional forced turns and no boundary cancellations.
Consequently the exact quantities in every dimension are

    D_n=0,  K_n=6L,  W_n=18L+2(L-1)=20L-2.

## 3. The half cut stays equal to one

After appending a new dominant highest coordinate, its top variable has
only one incident coupling in the left half, of unit capacity. Hence
lambda_n<=1. The old full graph embeds into that half, with old top now
the new root. In the seed the old top is connected to both the first
and last comparison variables, via unit-capacity edges (15,0) and (15,7).
This connectivity property persists under a dominant-coordinate lift:
the new top connects to the last variable of the left block and the
first variable of the right block, and within each block the old top
connects to both of its endpoint variables. Thus it connects to both
endpoint variables of the new full scan. The old top-to-last path in
the left half, followed by the new top edge, carries an integer unit flow.
Therefore lambda_n=1 for every n>=5.

It follows that the cut-only budget is

    D_n+K_n+lambda_n=6L+1=(3/16)*2^n+1 < 2^(n-2).

The valid general cut bound supplies only R>=6L+2. This is a strict
all-dimensional failure of that particular proposed proof route using
actual generic additive scans, with no fake-order or sampling premise.

A concurrent canonical checkpoint 7e46d325493863bb175cbe2dce6db79e1f74ea17,
PAIRED_COMPLEMENT_HALF_GRAPH.md, gives an exact cut-plus-residual formula
and a different lift of this seed: it appends dominant coordinates BELOW
the five rank coordinates, translates the seed variables, and obtains
lambda=2L-1, phi=4L-1, R_min=10L. This note instead retains the seed in
coordinates 0,...,4 and appends dominant coordinates ABOVE it. The paired
controller/prefix structure distinguishes these lifts; their different
cuts and minima are consistent and must not be interchanged.

## 4. Internal cycles survive and give a stronger block theorem

The three seed cycles embed separately into every core block, keep their
negative sign products under its possible core-top switch, and have
disjoint edge loads across all L blocks. Boundary edges do not affect
their couplings. Therefore phi_n>=3L and every paired rank satisfies

    R >= 1+K_n+phi_n >= 9L+1 = (9/32)*2^n+1.

The same protected bound holds if all slow rows are traversed in any
order while preserving each complete seed core block: each block's
restricted paired rank has at least ten runs, hence at least nine
internal run boundaries. Those raw positions are disjoint across blocks,
and extra inter-block boundaries cannot reduce their number. This uses
ordinary block lifting, not a claim to invent that method.

For genuine additive scans it is sufficient that the five core weights
induce the seed core order and the slow-coordinate subset scores have
adjacent gaps larger than the core score range. Slow coordinate signs
and row priorities need not be lexicographic. This is a restricted
scan theorem, not a bound uniform over every generic weight vector.

## 5. Reproducible audit and precise next gap

verify_paired_cut_budget_failure.py checks actual integer score orders,
D,K,W, integer flow and cut, all mapped cycle signs and capacity loads,
for n=5,...,18. It checks exact ancestor optima and directly counted
attaining ranks through n=12. For higher dimensions the formulas and
complete generated packings contribute exact digests. This computation
audits the formulas; the proofs above establish all-dimensional scope.

Finite exact minima in n=5,...,12 happen to be
(10,19,38,75,150,299,598,1195), equal to ceil(7*2^n/24).
The local packing proof supplies 9L+1. The concurrent canonical checkpoint
8e0a9c9558f0dc1794d0d3ce06435a3054c9bc3d,
PAIRED_DOMINANT_HIGH_TAIL.md, has now proved the stronger exact closed
formula by a four-state endpoint transfer. Its result agrees with every
local exact optimum; this independent formula/packing audit is not a
claim to replace that analytic transfer proof. The present n<=18 audit
additionally verifies every inherited cycle and cut formula through n=18.

The new gap is a load-respecting internal-cycle certificate for arbitrary
interleavings of these or other small cores. The universally valid cut
packing cannot absorb all missing budget. A proposed replacement that
adds maximal internal half-cycle packings must respect shared capacities
with cut paths; summing independently optimized packings is invalid in
general. Seek a single compatible packing, or a dual certificate that
uses internal frustration without double-counting edge loads. Published
v1.0 is unchanged, and the denominator n^2 in the M_n lower bound remains.

The concurrent checkpoint already proves the capacity-compatible joint
path/cycle lower bound and exact residual formula; do not repackage that
as an unproved or new next-step invention. Moreover failure at the quarter
constant does not exclude a smaller positive constant, which suffices for
the primary problem. A valuable next gap is to test and then prove or
refute a weaker uniform positive-density inequality for D+K alone or
for its sum with a compatible residual certificate. Any claimed constant
must remain independent of n and hold over all genuine generic scans.
