# A genuine periodic overlap family with constant cancellation and cut budgets

Date: 2026-10-03. Unpublished all-dimensional construction and exact certificates.
The primary constant-density M_n problem remains OPEN. Published v1.0 is unchanged.

This extends the paired-sibling comparison-graph framework and the antipodal
half/cut decomposition already recorded. Signed cycle packing and independent
leaf elimination are inherited methods. Concurrent checkpoint
2f9601940107c026a154e11d86b17ab0635c28c7, PAIRED_CONSTANT_CUT_BUDGET.md,
already excludes every positive-density raw/cut-only route using a distinct
constant-active-graph family with D+K+lambda=5. No priority is claimed for
that general exclusion. The increment here is a different realizable
quarter-sharp family with D+K+lambda=4, couplings of magnitude at most two,
an explicit growing cycle packing, and the arbitrary slow-gap extension.
This independently confirms failure of EVERY positive-density bound based
on D+K alone, or D+K plus the ordinary half-graph terminal minimum cut. Its true
frustration remains large and its fixed-scan family minimum is exactly sharp
at the conjectured quarter constant. Thus it excludes an auxiliary proof
route, not the main lower-bound statement.

## 1. Statement and actual generic weights

For every n>=5 put ell=n-5, T=2^ell, N=32T, and choose

    w=(1,10,28,16,56,112,...,56*2^(ell-1),8).

The ell-coordinate tail is placed BETWEEN coordinates 3 and n-1; it is
empty for n=5. The last, highest coordinate always has weight 8. At the
induced generic additive scan, the paired-sibling graph has exactly

    D=0, K=2, W=N-6,
    lambda=6 for n=5, lambda=2 for every n>=6,
    phi=N/4-2,
    min_theta R(rho_theta along this scan)=N/4+1.

Here lambda is the unsigned terminal min cut in the complement half graph.
Therefore for all n>=6,

    D+K=2, D+K+lambda=4.

For any c>0 and any fixed additive allowance A, both proposed universal
inequalities D+K>=cN-A and D+K+lambda>=cN-A fail for arbitrarily large n.
The exponential cycle term is essential even for positive, genuine,
integer additive weights. No fake order or finite sampling premise is used.

The quarter family minimum is for one displayed scan and allows its
attaining rank to depend on n. It is not a statement of the RLC value of
that individual rank, nor an upper or lower determination of M_n.

## 2. Explicit score order from a one-swap overlap

Set a=x_1, c=x_2, b=x_3, z=x_(n-1), and let t be the numerical value
of coordinates 4,...,n-2. Excluding the cheap coordinate x_0, scores are

    56t + 10a + 28c + 16b + 8z.

For one tile t, encode its four bits as q=a+2c+4b+8z. The exact ascending
sixteen-value word is

    Q=(0,8,1,4,9,12,5,2,13,10,3,6,11,14,7,15),
    scores=(0,8,10,16,18,24,26,28,34,36,38,44,46,52,54,62).

Every score is even and distinct. Consecutive tiles differ by 56. The
last score 62 of tile t exceeds the first score 56 of tile t+1, but is
smaller than that next tile's second score 64. The next tile's first
score exceeds the old penultimate score 54. Thus the whole order is
obtained by concatenating T copies of Q and transposing precisely the
adjacent pair (old q=15, next q=0) at EVERY tile boundary. These swaps
are disjoint. No other overlap is possible, including across two tiles.

Equivalently, tile t has unshifted last row S=(a,c,b,z)=(1,1,1,0);
at a boundary the four relevant rows are

    S_t, 0_(t+1), (S with z=1)_t, (0 with z=1)_(t+1).

The cheap coefficient w_0=1 splits each upper row into two consecutive
vertices x_0=0,1. Distinct upper scores differ by at least two, so the
full order is generic and has no interleaving inside these pairs. This
proves the explicit scan word analytically in every dimension.

## 3. Exact signed graph normal form

All consecutive comparisons alternate between a cheap-bit label and a
higher label. Thus consecutive labels are distinct and D=0. The graph
is bipartite: one side consists of the cheap-variable leaves, the other
of higher comparison variables. Its top virtual root is r=16T-1.

A leaf is indexed by its fixed t,b,c,z; its integer variable index is

    u(t,b,c,z)=c+2b+4t+4Tz.

For the higher comparison coordinate 3, put

    B(t,z)=14                            if T=1,
    B(t,z)=14T+floor(t/2)+(T/2)z          if T>=2,
    eta(t,z)=(-1)^z                      if T=1,
    eta(t,z)=(-1)^(t mod 2)              if T>=2,
    s_z=(-1)^z.

Direct inspection of the fixed tile word supplies these couplings:

| (b,c) | J_(u,r), before end corrections | J_(u,B(t,z)) |
|---|---:|---:|
| (0,0) | 2s_z | -eta |
| (1,0) | 2s_z | 2eta |
| (0,1) | 2s_z | -2eta |
| (1,1) | 2s_z | eta |

There are exactly two exterior corrections:

    at u(0,0,0,1), J_(u,r) increases by 1, from -2 to -1;
    at u(T-1,1,1,0), J_(u,r) decreases by 1, from +2 to +1.

These account for the only raw opposite-product cancellations. The
fixed word's non-top comparisons all have highest coordinate 3. At a
tile boundary two additional transitions have the same fixed z, from
S_t to 0_(t+1), for z=0 and z=1. Their highest differing coordinate is

    h=4+v_2(t+1),

where v_2 is the exponent of two dividing t+1. Let V(t,z) be that paired
variable and alpha(t,z) its Gray comparison sign. Each transition adds

    J_(u(t,1,1,z),V(t,z))=-alpha(t,z),
    J_(u(t+1,0,0,z),V(t,z))=+alpha(t,z).

These are unit couplings at different leaves. Their higher coordinate
is >=4, so they coincide with neither the coordinate-3 backbone nor r.
Each such leaf meets at most one tile boundary. Thus all listed edges
are distinct apart from the intended multiplicities, and no hidden
cancellation occurs. Every nonzero coupling has now been listed.

The root norm is 16T-2, the coordinate-3 norm is 12T, and boundary norm
is 4(T-1). Hence W=32T-6=N-6. The raw mixed-turn count is N-2, so

    K=(N-2-W)/2=2.

The table follows, for example, by noting that the six within-tile
non-top transitions go from A to B, AZ to BZ, AB to C, ABZ to CZ,
CA to CB, and CAZ to CBZ. Their coordinate-3 directions are
(+,+,-,-,+,+); each adjacent cheap sign is (-1)^a. All other
within-tile transitions have highest coordinate n-1. The one-swap
boundary modifies only the endpoints just described.

## 4. Full capacity certificate: exactly N/4-2 negative cycles

For EVERY fixed t,z pack these two negative four-cycles:

    (r,u(t,0,0,z),B(t,z),u(t,1,1,z)), amount 1;
    (r,u(t,1,0,z),B(t,z),u(t,0,1,z)), amount 2.

The signed product in both cases is negative, independently of s_z and
eta. The root capacities of the second pair of leaves are two, and
all coordinate-3 edges have exactly the required capacities. The first
pair uses one unit of each root edge. After all these backbone cycles,
its root edges have one unit left, except for the two exterior corrected
edges, which have none. Backbone packed mass is 6T.

For EVERY tile boundary t and z pack the further negative four-cycle

    (r,u(t,1,1,z),V(t,z),u(t+1,0,0,z)), amount 1.

Its product is s_z*(-alpha)*(+alpha)*s_z=-1. Both root edges have the
unused unit, and neither is an exterior exception. The transition
edges also have unit capacity. Different boundaries use distinct
start/end root edges; shared vertices never imply shared capacity.
Thus all backbone and boundary cycles form ONE compatible packing,
not a sum of independently optimized overlapping packings.

Their total mass is

    6T+2(T-1)=8T-2=N/4-2.

The graph has exactly 10T active variables in the original numerical
tail family, and every nonzero coupling has magnitude at most two. The
packing has 6T-2 distinct four-cycles, with multiplicities one or two.
Only two units of graph capacity remain unused. Every negative cycle
requires an unsatisfied edge for any spin assignment, giving
phi>=N/4-2. This is an explicit integer certificate in every dimension.

## 5. Matching upper certificate by telescoping leaf fields

Fix every higher-variable spin to +1. Each leaf independently takes
the sign of its incident field (use +1 at field zero). For type (1,0)
and (0,1), the fields are 2s_z+2eta and 2s_z-2eta. Their absolute-value
sum is four, for every t,z. These two types contribute 8T to the energy.

For type (0,0) the field is

    2s_z-eta + incoming alpha + first exterior correction,

and for type (1,1) it is

    2s_z+eta - outgoing alpha + last exterior correction.

Absent boundary terms are zero. Each field has sign s_z or is zero:
the two signs eta and alpha are individually +/-1, while the only end
correction moves a field toward zero without crossing it. Therefore
its absolute value equals s_z times its field. For each fixed z, the
incoming and outgoing alpha sums telescope across t. The eta terms
cancel between the two leaf types at each t. The two exterior
corrections together reduce the absolute-field sum by two. Thus these
endpoint types contribute 8T-2, and the complete attained energy is

    E=8T+(8T-2)=16T-2=N/2-2.

With W=N-6 this gives phi<=N/4-2, matching the packed-cycle lower
certificate. Hence phi=N/4-2 EXACTLY and

    R_min=1+D+K+phi=N/4+1.

The attaining orientation mask has all higher bits zero and its cheap
leaf bit equal to one precisely when its field is negative. It is a
member of the already certified prefix-separable paired-sibling rank
family, so admissibility holds for every n, without further enumeration.
The explicit rank has cyclic C=R+1=N/4+2: its first and last comparison
signs are both positive and the closing top comparison is negative.
Only the linear minimum is asserted here.

## 6. The ordinary half cut is bounded forever

When T>=2, the depth-zero variable a has coordinate n-2, namely the
highest tail bit. Only the central tile transition t=T/2-1 changes it.
In the half graph z=0 it has exactly two incident unit edges, to
u(t,1,1,0) and u(t+1,0,0,0). Both leaves have root capacity two.
Two edge-disjoint root-leaf-a paths therefore supply flow two; the
singleton cut at a has capacity two. This proves lambda=2. For T=1,
the half is the displayed four-leaf graph between r and B=a. Its four
path capacities are (1,2,2,1), giving lambda=6.

The path capacity in this family is already used in the full cycle
certificate. Counting the terminal flow again would double-count edges.
Retaining only the z=0 cycles gives a compatible negative-cycle packing
INSIDE the half H of mass C_H=3T+(T-1)=4T-1, with path mass P=0.
Thus the half joint certificate P+2C_H=8T-2 equals the proved full
frustration. Since every valid joint certificate is bounded above by
phi, its optimal fractional joint-packing value is EXACTLY phi in this
family. The same equality follows in the conditional slow-order class
below. No general integrality or exactness claim follows from these
specific certificates.

The exact conclusion is that no positive uniform density can be obtained
from the raw D+K budget or that budget plus the ordinary terminal cut.
Internal cycle information is necessary. The combined full frustration
budget still attains the quarter bound sharply in this family.

## 7. A protected overlap theorem for arbitrary slow-coordinate orders

The same exact minimum holds under a broader, conditional genuine scan
class. Keep coefficients (1,10,28,16) on the four low coordinates and
8 on the highest. Allow the ell middle-coordinate coefficients to be
ARBITRARY signed values. Sort their T distinct subset scores, with
vertex rows y_0,...,y_(T-1), and assume EVERY consecutive gap lies
strictly between 55 and 61. Then exactly

    D=0, K=2, W=N-6, phi=N/4-2, R_min_family=N/4+1.

The gap assumption makes each boundary a one-swap overlap: the next
first upper row is strictly between the old penultimate score 54 and
old last score 62, with more than one score unit on either side.
The next tile's second row follows that old last row by more than one
unit. Nonadjacent tiles cannot overlap. Thus the same cheap pairs and
local sixteen-value word are valid in ANY resulting row order.

The cheap-leaf labels retain the ACTUAL tail vertex y_j. Replace each
consecutive numerical pair (t,t+1) in the boundary formulas by
(y_j,y_(j+1)), and place exterior corrections at y_0 and y_(T-1).
The higher-coordinate comparison sign alpha can now be either sign,
and its coordinate/prefix can vary arbitrarily. Its two edge products
are still -alpha,+alpha. Consequently every boundary four-cycle is
negative and its loads remain disjoint. The backbone sign eta is
still determined by the actual coordinate-4 controller bit, not the
row's position in the scan. No numerical row assumption is needed.
The capacity proof and telescoping field proof apply verbatim.

The terminal cut need not stay two in this extension: the highest
slow-coordinate bit can change at several row boundaries. Constant
lambda is proved only for the original numerical power tail. Thus
this is an additional protected scan theorem, not a stronger global
cut counterexample inferred from arbitrary row order.

The class has non-lexicographic full scans and signed, permuted slow
priorities. For example,
assign the middle-coordinate magnitudes near permuted powers
56*2^j, with any signs and total absolute perturbation below 1/4.
All sorted slow gaps lie in (55,61). Rescale all weights together to
obtain integer coefficients. The new audit uses 96 fresh signed,
permuted and perturbed actual sweeps in ell=1,...,8, checks the complete
score order, normal graph, combined cycle loads, and attaining rank;
independent full ancestor DP agrees through n=11. This verifies the
conditional theorem's implementation, not all weight chambers.

## 8. Verification scope and the remaining main problem

paired_periodic_overlap.py generates the genuine weights, explicit scan
word, complete coupling normal form, capacity-respecting cycles and an
attaining rank mask. verify_paired_periodic_overlap.py checks every vertex
and every coupling in n=5,...,18, generic subset scores, direct linear and
cyclic runs, mask bijectivity, all negative signs and all edge loads,
two-unit terminal paths and exact cut equality. Independent full ancestor
DP additionally agrees through n=12, and independent recursion through
n=7. Higher-dimensional exactness comes from the two matching explicit
certificates, not solver optimality.

All original-family checks passed in 8.479891774011776 seconds, digest
d95b242bbae8c06730ee8cbb1d3a6a1db9d7e0457e04989318656e81ee1152d4. The 96 additional conditional overlap scans
passed in 2.293183271001908 seconds, digest
928fcd38a9fa19dc5b8bcaef83a5bf8a712d94e4eb2a21d0f37e1699995812b7.

The formulas and telescoping proof establish arbitrary n. Listed finite
checks audit the implementation; they are not an enumeration of all
weight chambers. Initial verification reached n=16 and stopped only
because a decimal rendering of a huge rank mask exceeded Python's
4300-digit limit. The final verifier hashes its canonical little-endian
binary bytes instead; all requested dimensions then completed. No
mathematical assertion failed in that diagnostic.

Next analytic question: for arbitrary genuine interleavings, force a
positive density of compatible full negative-cycle capacity or equivalent
residual frustration WHEN the raw/cut budgets are small. The special
periodic word provides a complete example of this compensation, but no
uniform argument over all weights is yet proved. In particular the main
M_n target and the universal paired-sibling quarter conjecture remain OPEN.
