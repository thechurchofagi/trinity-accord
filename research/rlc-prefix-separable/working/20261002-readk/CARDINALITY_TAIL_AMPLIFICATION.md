# A cardinality-class limit and better coherent core densities

Date: 2026-10-03. Unpublished research continuation. The general
constant-density M_n target remains OPEN. This note concerns forward
Gray rank and genuine additive scans ordered first by cardinality.
It does not minimize over every generic additive weight vector.

## 1. Reconciliation and the new claims

The concurrent checkpoint at commit
3cada19bc49430f36ce47a21b4176278d13e1682 already proved that coherent
cardinality refinements can have E_*-D=Omega(2^n), gave a 7/16 limiting
family, and proved a general finite-core extension theorem. Those
results are retained as prior work. Our independently found five-bit
core (10,11,22,4,25) gives the same asymptotic density and is not claimed
as a new improvement.

The additional results here are:

* The optimal normalized interior densities eta_n are nonincreasing.
  The optimal full cyclic and linear densities in the entire coherent
  cardinality subclass converge to their infimum.
* An eight-bit core improves the certified family density to 55/128.
  An eleven-bit core further improves it to 879/2048, about 0.4291992.
* The eleven-bit energy maximum has a short exact certificate: four
  weighted negative cycles force frustration at least 18, and a spin
  assignment attains exactly 18. This certifies E0=554 without relying
  on a heuristic energy optimizer.

Before this note was committed, concurrent checkpoint version 17 at
f363d72f488daff1109dee845ce3031343e6d67b advanced the cardinality family
ceiling further to 109/256 using an unfrustrated nine-bit core. This
stronger result is preserved. The cores below are additional exact
examples; 879/2048 is not the latest best cardinality-family ceiling.
The new limit argument incorporates the stronger prior nine-bit value.

These subclass upper bounds do not improve the already known unrestricted
Gray ceiling 5/16, and do not give a bound for the max-over-ranks M_n.
Positivity of the new cardinality-class limit is still OPEN.

## 2. The general extension, with exact interior identities

Let d>=2, let b in R^d be generic within every fixed-cardinality layer,
and order Q_d by (|x|,b dot x). The latter condition, not genericity of
b dot x alone, is what is required. In each cardinality bucket retain
only consecutive linear triples entirely inside that bucket. Let D0
count equal highest-difference labels, and let J0 be their mixed-label
coupling graph. Define

    E0 = max over spins sigma of sum J0_hk sigma_h sigma_k,
    alpha(b) = 1/2 + (D0-E0)/(2*2^d).

No closing edge is retained as interior. Complement followed by reversal
pairs the interior triples in layer k with those in layer d-k. Products
for mixed pairs involving label d-1 change sign, so the top core label
is isolated in J0.

Extend b by any positive coefficients satisfying

    b_j > sum_{i<j}|b_i|,  for j=d,...,n-1.

Choose L>sum_{j<n}|b_j| and actual positive weights w_j=L+b_j.
They produce exactly the coherent order (|x|,b dot x), since a change
of one in cardinality dominates the whole secondary score span. The
tail also guarantees joint genericity. Put t=2^(n-d), N=2^n, q=n+1.
For the extended order we have the EXACT identities

    D_int(n) = t D0,
    J_int(n) = t J0, with all higher labels isolated.                 (1)

Here is a proof that also addresses triples at transitions between tail
blocks. Within any cardinality bucket, the tail assignments are ordered
by their numerical binary value and are contiguous blocks. This follows
from dominance at the highest differing tail coordinate, regardless of
the core scores. Inside a fixed tail block, the core order is exactly a
fixed-cardinality seed bucket. As all global cardinalities vary, every
tail assignment supplies every one of the d+1 seed buckets once. Thus
all seed triples with both labels below d are replicated t times.

For label d-1, a Gray comparison acquires a common sign factor determined
by tail bit d. Its coupling with lower labels is zero after summing the
seed buckets, by the top-label complement cancellation just stated.
Products with maximum label below d-1 are unchanged by the tail.

A triple with the same label below d must lie wholly within one tail
block. A triple with two equal labels h>=d would require two successive
increases of the highest changing tail bit h. In numerical tail order,
both changes would be 0 to 1, impossible at their common middle vertex.
This proves the diagonal assertion of (1), including block transitions.

For a mixed triple with maximum label h>=d, all three vertices have the
same bits above h. Toggle their common bit h+1. Tail dominance makes
each such high-prefix class contiguous within a bucket; translation
preserves its restricted additive order and hence its consecutive
triples. The image triple is interior in its new bucket. The involution
reverses the Gray sign on the h edge and preserves the lower-label sign,
so its product changes sign. If h=n-1 use complement and reversal instead.
Thus all such mixed couplings cancel. This proves the graph assertion.

There are q designated cyclic joins between cardinality buckets,
including the closing join. Every excluded triple uses a join; there
are at most 2q such triples. Accordingly

    D = t D0 + D_bd,       0 <= D_bd <= 2q,
    J = t J0 + J_bd,       sum |J_bd_hk| <= 2q.                      (2)

Each spin energy changes by at most the last norm, so maximizing gives
|E_*-t E0|<=2q. The reflection identity C_min=(N+D-E_*)/2 yields

    alpha(b)N-q <= C_min(n) <= alpha(b)N+2q.                         (3)
    alpha(b)N-q-1 <= R_min(n) <= alpha(b)N+2q.                       (4)

The linear endpoint correction is between zero and one. If n>d, the
least actual weight belongs to the core and is not the top coordinate;
then R=C for every reflection. In all cases the minimum over every
coordinate-sign choice has normalized limit alpha(b). These statements
apply to a fixed core, and make no assertion that it is globally optimal.

For integer cores an explicit convenient tail is

    M=1+sum_{j<d}|b_j|,
    b_j=M*2^(j-d) for j>=d,
    L=M*2^(n-d).

The total absolute secondary weight is L-1, so all genericity and
positivity assertions are exact integer assertions.

## 3. A limit for the whole coherent cardinality subclass

Let B_n contain all secondary vectors generic within cardinality layers.
There are only finitely many induced strict vertex orders. Each feasible
order occurs in an open set of secondary vectors, so all minima below
are attained, and rational vectors suffice. Define

    eta_n = min_{b in B_n} alpha(b),
    beta_n = min_{b in B_n, reflections} C(b)/2^n,
    lambda_n = min_{b in B_n, reflections} R(b)/2^n.

In beta_n and lambda_n the actual weights are L+b, with L greater than
the absolute secondary sum. Different sufficiently large L give the
same scan. No arbitrary additive order outside this class is included.

The exact replication (1), with just one new dominant tail coordinate,
shows alpha(extended b)=alpha(b). Therefore

    eta_(n+1) <= eta_n.                                             (5)

If T_int is the number of interior triples, then E_int<=T_int-D_int,
because each mixed triple contributes at most one to each spin energy.
Thus alpha(b)>=(N-T_int+2D_int)/(2N)>=0. Consequently the nonincreasing
eta_n converges, with

    eta_infinity = inf_{d>=2} eta_d = inf_{d>=2,b in B_d} alpha(b).   (6)

Apply (2) directly to an arbitrary n-dimensional seed, without any tail.
Equivalently take n=d in (3). Minimizing the resulting uniform inequalities
over every feasible coherent order gives

    eta_n-(n+1)/2^n <= beta_n <= eta_n+2(n+1)/2^n,
    |lambda_n-beta_n| <= 1/2^n.                                    (7)

It follows that BOTH beta_n and lambda_n converge to eta_infinity.
In particular a uniform positive eventual density within this subclass
is equivalent to eta_infinity>0, or to a uniform positive margin in

    E_int-D_int <= (1-2 epsilon)2^d.

The equivalence has not proved such a margin. Also, positive density for
this subclass would be necessary, but not sufficient, for a Gray proof
covering all generic additive sweeps. The principal M_n target allows
other prefix-separable ranks, so even failure for Gray would not settle it.

## 4. Two exact cores below the five-bit density

The eight-bit secondary vector is

    b8=(10,11,22,4,25,73,146,-148).

Its exact interior graph is

    D0=34,
    J12=32, J13=-32, J25=2, J35=-2, J45=2,
    W0=E0=70, phi0=0.

Spin mask 8 (only spin 3 negative) satisfies every edge. Its input
reflection is inverse_gray(8)=15. Therefore

    alpha(b8)=1/2-(70-34)/512=55/128 < 7/16.                       (8)

The eleven-bit vector is

    b11=(10,11,22,4,25,3071,146,-3170,584,1168,2336).

Here D0=264, W0=590, and the nonzero interior coefficients are:

| Labels | J | Labels | J | Labels | J |
| --- | ---: | --- | ---: | --- | ---: |
| 1,2 | 232 | 1,3 | -252 | 1,4 | -4 |
| 2,4 | 12 | 2,6 | 16 | 3,4 | 16 |
| 3,6 | -16 | 3,7 | 2 | 3,8 | -2 |
| 3,9 | -2 | 4,6 | -16 | 4,8 | 6 |
| 4,9 | 6 | 6,8 | -2 | 6,9 | -2 |
| 7,9 | -2 | 8,9 | 2 | | |

A negative signed cycle must contain an unsatisfied edge for every spin
assignment. The following cycle packing respects each edge's absolute
capacity; the amount is charged along every edge in that cycle, including
the last-to-first edge:

| Negative cycle | Amount |
| --- | ---: |
| 1,2,4,6,3,1 | 12 |
| 1,2,6,3,8,9,4,1 | 2 |
| 1,2,6,8,4,9,7,3,1 | 2 |
| 1,3,9,4,1 | 2 |

All four have negative sign product. Sum, over cycles, the packing amount
times the number of unsatisfied edges in that cycle. It is at least
12+2+2+2=18, and at most the total unsatisfied edge weight, since the
loads never exceed capacities. Thus phi0>=18 and E0<=590-36=554.

Spin mask 70 (spins 1,2,6 negative) has exactly the unsatisfied edges
(2,4),(3,8),(3,9),(7,9), of total weight 12+2+2+2=18. Its energy is 554
and its reflection is inverse_gray(70)=123. Hence E0=554 exactly and

    alpha(b11)=1/2-(554-264)/4096=879/2048 < 55/128.               (9)

The integer actual core vector uses M=L=10548, with w=M+b11.
Every one of its 2048 signed scans was independently sorted: its full
minimum is R=C=880. That finite value differs from alpha(b11)2^11=879;
the one-turn difference is a boundary effect. The reported limiting
value is obtained from (1)-(4), not by dropping this difference in a
finite count. In the eight-bit core the least weight is its top coordinate,
so its finite minima are C=112 and R=111; once a positive dominant tail
is appended the endpoint correction vanishes.

The concurrent nine-bit core

    b9=(108,106,105,102,110,126,32,170,0)

has D0=40, E0=W0=116, hence alpha(b9)=109/256. Including that already
saved example, (6) proves the strongest currently recorded bound here:

    0 <= eta_infinity <= 109/256 < 879/2048 < 55/128 < 7/16.

No equality, optimality claim, or positive lower bound is established.
The eleven-bit frustration is essential: substituting W0 for E0 would
give an incorrect certified family density.

## 5. Audit and discovery limits

Run python3 verify_cardinality_tail_amplification.py. It verifies joint
genericity, positive actual-score realization, exact interior replication,
boundary bounds, and the two-sided minimum-density bounds. It includes
the prior seven-bit forced-turn-payment core, both new cores and their
six successive tail extensions, and 42 independent signed-secondary cores
of dimensions 2 through 8 with four tested extension lengths each.
Both improved cores additionally have all 2^d spin energies evaluated;
the cycle-packing certificate uses integer checks and no LP dependency.

The pressure script uses random seed 202610030845, 600 proposals per
dimension 6 through 12. Independent random vectors alternate with one-
and three-coordinate mutations of the retained best. Every retained
vector is generic within layers and its energy is optimized exhaustively.
The eight-bit improvement was exposed inside a nine-bit proposal whose
last coordinate was an already dominant tail. The eleven-bit proposal
was retained on trial 352. Another 8000 one-coordinate mutations of the
eight-bit core found no improvement; this supplies no completeness or
lower-bound evidence.

Next analytic question: can the weighted negative-cycle mechanism or
the translated-prefix structure pay for a fixed fraction of mixed
triples uniformly in growing core dimension? Finite core improvements
alone cannot establish positive eta_infinity. The all-sweep Gray target
still requires a uniform bound on E_*-D beyond the cardinality subclass.

Published editions, archive metadata, DOI and released bytes are unchanged.
