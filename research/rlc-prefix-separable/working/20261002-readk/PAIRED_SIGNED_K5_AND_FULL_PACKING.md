# A nine-coordinate signed obstruction, an exact lift, and a full packing reduction

Status: an exact certificate and two all-dimensional statements. The primary
constant-density M_n problem remains OPEN. The original seed in this note has exact actual-capacity packing. A different
real scan and its all-dimensional gap are proved in PAIRED_ACTUAL_JOINT_GAP.md. Published TA-TR-2026-22 v1.0 is unchanged.

## 1. Reconciliation and the precise increment

Concurrent canonical commit 50072f8d3591a0885cf359cfd2efbadbe5bd7111,
PAIRED_SIGNED_ODD_K5_OBSTRUCTION.md, already proves the failure of universal
weak bipartiteness on REAL scan supports using a ten-coordinate seed, lifts
it to every n>=10, and supplies diagnostic capacity gaps. That route exclusion
is credited there, not reclaimed here. Its actual-capacity joint packing
still equals its frustration.

The present independent increment is a smaller nine-coordinate seed with
six branch-tree edges, a single explicit integral packing that remains
optimal in every higher dimension, and an unconditional reduction of the
half joint fractional packing to ordinary full-graph negative-cycle packing.
Dimension nine is an exhibited seed; no minimality claim is made.

We retain the established paired-sibling rank family, the exact identity
R_min=1+D+K+phi, and the antipodal half decomposition from
PAIRED_COMPLEMENT_HALF_GRAPH.md. These optimize the rank separately for
each fixed score scan; they do not compute M_n or a fixed rank's RLC.

## 2. A compact genuine score scan and a signed minor certificate

In numerical coordinate order use the positive integer weights

    w=(216,246,244,442,248,642,6,601,128).

All 512 subset scores are distinct; their minimum consecutive gap is one.
These weights were obtained by solving a chamber feasibility problem only
as a candidate generator. The exact integer score order was independently
checked to coincide with the initially found weights

    (32839405,37622620,37555007,67589735,37835205,
     98178771,902781,92167916,19595755).

The full comparison graph has D=64,K=178,W=90. Its complementary half has
17 active vertices, 33 edges, terminals a=254,r=255 and norm 45. Its exact
frustration is 22, hence the fixed-scan rank-family minimum is 265.
Section 4 supplies a solver-free packing/witness proof of these optima.

Take five pairwise disjoint branch sets with the following simultaneous
switching gauges. A plus/minus after a vertex is its gauge, not its original
coupling sign.

| Branch | Vertices with gauges | Positive spanning-tree edges after switching |
|---|---|---|
| A | 194+,254- | 194-254 |
| B | 199-,202+,255- | 199-255,202-255 |
| C | 205+ | none |
| D | 207+,243- | 207-243 |
| E | 200-,240+,252- | 200-252,240-252 |

For every pair use the bridge below. The SAME gauges make every bridge
negative, while making every listed branch-tree edge positive.

| Branch pair | Bridge | Original coupling |
|---|---|---:|
| A,B | 194-255 | 1 |
| A,C | 254-205 | 1 |
| A,D | 254-243 | -2 |
| A,E | 254-240 | 3 |
| B,C | 255-205 | 1 |
| B,D | 255-207 | 1 |
| B,E | 255-252 | -3 |
| C,D | 205-243 | 1 |
| C,E | 205-252 | 1 |
| D,E | 243-252 | -2 |

Delete unwanted edges, then contract the six positive tree edges. The ten
remaining edges form all-negative K5: an exact signed odd-K5 minor of a
REAL additive scan half support. The full support contains that half and
therefore the same minor. This strengthens the exhibited dimension range
of the concurrent obstruction, without establishing least dimension.

For the definition of signed contractions and the weak-bipartite
characterization, a primary source checked on 2026-10-03 is A. Schrijver,
A short proof of Guenin's characterization of weakly bipartite graphs,
JCT B 85 (2002), 255-260, https://doi.org/10.1006/jctb.2001.2101,
author text https://homepages.cwi.nl/~lex/files/guenin2.pdf. A negative edge
is switched positive before contraction; the result is unique up to switching.
The diagnostic below also witnesses nonidealness directly.

## 3. A positive-capacity diagnostic gap, distinguished from scan couplings

Keep all 33 original half edges and signs. Replace their capacities by
208 on the six selected tree edges, 52 on the ten bridges and 1 on each
of the remaining 17 edges. These are alternative graph capacities, NOT
asserted to be couplings of any score scan.

Every spin assignment has cost at least 208. A violated selected tree
already costs 208. If all selected trees are satisfied, switch using the
displayed gauge and contract them. Their ten bridges are the all-negative
K5 with uniform capacity 52. At most six of its ten edges can be satisfied,
so at least four bridges cost 4*52=208. Extra edges have nonnegative cost.

The saved rational primal and dual certify the fractional negative-cycle
packing optimum EXACTLY 535/3. The verifier checks all capacities and
all 437 simple negative-cycle dual constraints with Fraction arithmetic.
Thus 535/3<208 proves a genuine integrality gap on the entire signed support,
using strictly positive integral capacities, even without trusting the
integer optimizer. Independently enumerating all 65536 active spin
assignments with one global gauge fixed, and checking the ancestor recursion,
gives the exact integer frustration 211 and exact gap 98/3.

This is a support-wide capacity obstruction. The ACTUAL score scan has
packing value phi=22; it does not exhibit an actual-capacity packing gap.

## 4. Every-dimensional genuine lift with an optimal integral packing

Let n=9+m, T=2^m, L=1+sum(w)=2774. Put the m new LOW coefficients below
the old core:

    w_n=(L,2L,...,2^(m-1)*L,216,246,244,442,248,642,6,601,128).

The initial list is empty when m=0. Tail rows are spaced by L, exceeding
the whole old score range 2773. The actual order is exactly

    ((x<<m)|t : t=0,...,T-1, x in the original core score order).

There are no ties, and every comparison has its highest differing coordinate
in the old core. Old variables shift by delta=2^(n-1)-256. The inherited
low-tail boundary proof from PAIRED_JOINT_PACKING_AND_MINOR_AUDIT.md yields
the following complete graph formula on shifted old labels:

    J_n=T*J_9+(T-1)*B,
    B_(252,255)=-1, B_(253,255)=+1, all other B=0.

The core's least coefficient is coordinate 6. Its first and last comparison
labels are 252 and 253, so these are precisely the two row-boundary
increments. Both reinforce their old coupling signs. All other nonzero
edges simply scale by T. No new lower variable is active. In particular
the same signed minor, with labels shifted by delta, survives for EVERY
n>=9. The full norm and raw terms are exactly

    D_n=64T, K_n=178T, W_n=92T-2.

Here is the entire half packing. Shift every vertex by delta. Every cycle
is negative. Give each cycle mass T, except the marked cycle, whose mass
is T-1; it is absent at T=1.

| Cycle | Mass |
|---|---:|
| (194,254,243,207,255) | T |
| (199,252,255) | T-1 |
| (200,242,202,255,252) | T |
| (201,242,252,255) | T |
| (203,242,255) | T |
| (204,243,205,255) | T |
| (205,252,240,254) | T |
| (206,243,252) | T |
| (240,252,241,254) | T |
| (240,252,243,254) | T |
| (241,254,242,255) | T |
| (242,252,255) | T |

A direct finite edge check proves the twelve unit cycles fit capacities
|J_9|+1_(252,255). Their load on (252,255) is four. Scaling the list by T
and subtracting one copy of the marked triangle therefore fits every
capacity of H_n: the exceptional edge has load 4T-1 and capacity 4T-1;
every other load is at most T times its base capacity. This proves
capacity compatibility for all real T>=1, hence for every dimension.

Their half mass is 12T-1. Mirror every cycle into the complementary half.
Switching preserves the cycle sign, the half interiors are disjoint and
there is no a-r edge, so the combined FULL packing has mass 24T-2. It
lower-bounds full frustration without any graph-idealness hypothesis.

For an attaining rank put negative spins precisely on the shifted vertices

    {202,204,208,214,215,216,221,241,243,245,246,253},

and positive spins everywhere else. The core energy is exactly 46. Its
spins at 252,253,255 are (+,-,+), so the two boundary increments contribute
-2(T-1). Thus its full energy is 46T-2(T-1)=44T+2, and its frustration

    (92T-2-(44T+2))/2=24T-2

matches the packed lower bound. Exactly, for EVERY n>=9,

    phi_n=24T-2;
    min_theta R(rho_theta along this score scan)=266T-1;
    max compatible half (P+2C)=24T-2, attained with P=0.

The packing is integral with capacity-respecting multiplicities. The
support is nonideal, yet these ACTUAL scan capacities admit exact packing
in every dimension. Nonideal support alone therefore neither forces nor
excludes an actual-capacity packing gap. This family is not a counterexample
to a positive-density run bound, and its rank varies with the fixed scan.

## 5. General reduction: the joint half LP is exactly a full cycle LP

This statement applies to ANY signed two-copy graph with the existing
antipodal structure, not only the displayed family. The halves share only
a,r, have no edge a-r, and have identical mirrored capacities. The mirror
changes the sign of an a-r path and preserves the sign of a cycle, since
epsilon_a=-1 and epsilon_r=+1.

Let nu^*(G) be the fractional packing optimum of all negative simple
cycles in the full graph, with its actual edge capacities. Let Q^*(H)
be the compatible half LP over all simple a-r paths and negative simple
cycles, maximizing P+2C under COMBINED loads. Then unconditionally

    Q^*(H)=nu^*(G).

First lift any feasible half packing. A path p of mass t and its mirror
have opposite sign products. Joining p with the reversed mirror of p
makes a negative simple full cycle of mass t. The two half interiors are
disjoint. A negative half cycle of mass c gives that cycle and its mirror,
each of mass c. All full edge loads remain within their mirrored capacities.
The resulting full objective is exactly P+2C. Hence nu^*(G)>=Q^*(H).

Conversely, take any feasible full packing, without assuming symmetry.
A simple full cycle lies wholly in one half, or crosses both halves.
In the latter case it must visit a and r exactly once each and is the
union of two simple a-r paths, one in each half. There is no other way to
change halves without repeating a terminal. A full negative cycle wholly
in one half projects, after mirroring if necessary, to a negative H cycle
with HALF its mass. A crossing negative full cycle projects its two paths
to H, each with HALF its mass. Their path parities coincide after mirroring,
although the half LP does not need this additional restriction.

For each half edge e, the projected combined load is exactly

    (full_load(e)+full_load(tau(e)))/2 <= cap(e).

Each internal full cycle contributes twice its half cycle mass; each
crossing full cycle contributes the sum of its two half path masses.
Therefore the projected half objective equals the ORIGINAL full cycle
mass. This gives Q^*(H)>=nu^*(G) and proves the identity.

Equivalently, a half joint dual length y lifts to symmetric full cycle
dual length y/2 on both copies: internal negative cycles have length at
least one, and crossing cycles have two half paths of length at least one
before halving. This also explains the factor two in the joint objective.

This closes the purely fractional reduction between the terminal and
cycle formulations. It DOES NOT prove nu^*(G)=phi(G), an integral optimum,
or any quantitative D+K+Q^*(H)>=c*2^n inequality. The full supports can
contain the signed obstruction just proved, so universal idealness cannot
be invoked to fill the remaining gap.

## 6. Reproduction and continuation

probe_paired_signed_k5.py is a bounded candidate search. It retains BOTH
parallel signs after contractions; they are never numerically canceled.
Every hit is validated using connected disjoint branch trees, a single
gauge and all ten bridges. Its fresh search seed was 202610031330; the
first hit was the third Q9 candidate, after 243 preceding scans, on the
first contraction trial. No-hit rows prove no exclusion. Runtime
2.0902236070105573 seconds; raw search report SHA256
7dcf0c272a937d94ff38d79b3f3996dbe6d7b4197b7f0a1631891fdc59c16417.

paired_signed_k5_seed_certificate.json contains the exact branch gauges,
trees, bridges, twelve cycles, attaining spins and diagnostic rational
primal/dual. verify_paired_signed_k5_obstruction.py uses integer/Fraction
arithmetic throughout. It independently checks all diagnostic cycle
inequalities, exhaustive spins, the complete genuine graph/score lift
through Q18, the shifted signed minor, both half/full cycle loads, energy,
and actual rank runs. Its separate mixed path/cycle audit projects an
UNSYMMETRIC full packing and lifts it back, checking both directions of
the general reduction. The analytic boundary/capacity argument proves
all dimensions; Q9..Q18 checks audit its implementation, not an extrapolation.

Results and execution log are paired_signed_k5_obstruction_verification.json
and paired_signed_k5_obstruction_run.log. The run completed with zero
violations; the exact timing and audit digest are in those files.

The unresolved step is ACTUAL additive coupling geometry or a weaker
positive-density certificate. The concurrent plan to cross exact score
order walls near a signed-obstruction seed remains useful. This compact
Q9 seed is an additional tractable starting point, with its exact integral
packing cone explicit. Do not repeat completed support searches as a
substitute for a uniform argument over all generic weights.

## 7. Subsequent actual-capacity wall crossing

The completed coordinate-six wall audit has now found a REAL packing gap.
PAIRED_ACTUAL_JOINT_GAP.md proves phi=24T-1 and joint optimum=23T-1/2
for every n>=9, T=2^(n-9). Thus universal actual-capacity exactness is false
as well. This supersedes the exactness-search target above; the remaining
main target is quantitative positive density over every genuine scan.

## 8. Ancestor incident budgets alone do not encode additive coherence

The latest concurrent quantitative plan suggests the local bound
sum_(v ancestor of u) |J_uv| <= 2^(h+2), for the variable at coordinate h.
This bound is correct, but it holds for EVERY vertex permutation, including
nonadditive ones. A raw mixed turn incident to u is indexed by its UNIQUE
middle vertex. That vertex belongs to the prefix subcube of u, fixing all
bits above h+1, of size 2^(h+2). Distinct raw turns have distinct middle
vertices. Aggregation can only reduce the incident absolute sum, proving
the inequality without using a score vector or translation consistency.

Here is an all-dimensional limitation of the budget by itself, even with
ancestor support and antipodal order. List the leading-top-bit-zero
vertices in increasing forward-Gray rank; then append their complements
in reverse order. The actual Gray values of this proposed permutation are

    0,1,...,N/2-1,N-1,N-2,...,N/2.

It is antipodal and has exactly TWO runs in every n>=2. Every ancestor
incident budget holds by the preceding injection. For n>=3 its first
four vertices are (0,1,3,2): additive ordering would require both w_0>0
from 0<1 and w_0<0 from 3<2. Thus it is explicitly NONADDITIVE, including
for signed score vectors. Its comparison graph has D=K=0 and frustration
one when n>=3; a single negative cycle and the all-positive Gray spin
witness certify this. At n=2 it instead has K=1 and no graph edges.

Consequently local incident budgets, ancestor support and antipodal
symmetry alone cannot prove ANY uniform positive-density lower bound.
This example does not have additive coordinate-direction consistency and
does not refute combining the budgets with actual additive restrictions.
The point is to retain that extra hypothesis explicitly, rather than
treating the local budget as new evidence of score realizability.

The exact verifier audits this construction and the incident bound through
Q14, including the one-cycle certificate and the prefix contradiction.
The rank formula and charging argument prove the arbitrary-dimensional
statement. This is a distinct clarification of the concurrent next-step
proposal, not a claim to exclude its budget-PLUS-coherence route.
