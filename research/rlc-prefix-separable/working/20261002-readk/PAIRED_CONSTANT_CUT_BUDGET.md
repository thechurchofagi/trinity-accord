# Every positive-density cut-only route fails on genuine additive scans

Status: analytic all-dimensional theorem with integer certificates and
independent attaining ranks. This is a rigorous exclusion of a proof
route, not a counterexample to the primary M_n target. It also gives an
exact minimum over the entire paired-sibling rank family at two explicit
scan families. These are fixed-scan minima, not their ranks' RLC values.
Published v1.0 remains unchanged.

We use the existing paired-sibling family, raw-turn quantities D,K,W,
signed frustration phi, complementary half graph H and root-to-top cut
lambda. For every rank in the family, its scan run count is at least
1+D+K+phi, with equality at a maximizing spin assignment. The existing
complementary half reduction gives E_max=F_++F_-. Its capacity-compatible
certificate is phi>=P+2C for half terminal paths of total mass P and
negative half cycles of total mass C, using their COMBINED edge loads.
These are already established tools, not methods newly invented here.

## 1. A periodic overlapping-row family with D+K=2 in every dimension

For k>=4 set T=2^(k-4), N=16T, q=N/2, and take weights, in numerical
input-coordinate order from least to most significant,

    v_k=(16*2^(k-5),...,16,1,6,8,4).

The low-coordinate tail is empty at k=4. Its subset scores are precisely
16t, 0<=t<T. The four-coordinate core scores, with their vertices, are

    vertices: 0,1,8,9,2,3,4,5,10,11,12,13,6,7,14,15
    scores:   0,1,4,5,6,7,8,9,10,11,12,13,14,15,18,19.

Their residues modulo 16 exhaust all residues, so all full scores are
distinct. Reading the core part of each scan vertex gives the exact word

    I V^(T-1) F,
    I=(0,1,8,9,2,3,4,5,10,11,12,13,6,7),
    V=(0,1,14,15,8,9,2,3,4,5,10,11,12,13,6,7),
    F=(14,15).

Unlike disjoint block lifting, adjacent score rows overlap. Consecutive
core vertices are always different, so the highest differing coordinate
is always in the core. The paired comparison label and forward Gray
comparison sign therefore ignore the tail. This is about forward rank
x XOR(x>>1), not inverse BRGC ordering. There are only six active graph
variables: u_i=q-8+i, i=0,...,3, a=q-2 and b=q-1.

Put A=2T-1, B=2T=A+1. The exact graph is

| Edge | Coupling | One extra V increment |
|---|---:|---:|
| u0,a | -A | -2 |
| u0,b | B | 2 |
| u1,a | A | 2 |
| u1,b | A | 2 |
| u2,a | A | 2 |
| u2,b | -A | -2 |
| u3,a | -A | -2 |
| u3,b | -B | -2 |

Here is a finite local proof of the formula for every T. At T=1 the
word I F has D=0,K=2 and the displayed graph with A=1,B=2. Inserting an
additional V before F leaves the final turns (6,7,14),(7,14,15) unchanged.
The new turns are exactly the 16 cyclic turns of V. Their label products,
using core labels 0,1,2,3,6,7, are

| Core triple | Labels | Product |
|---|---|---:|
| 0,1,14 | 0,7 | 1 |
| 1,14,15 | 7,3 | -1 |
| 14,15,8 | 3,6 | -1 |
| 15,8,9 | 6,2 | 1 |
| 8,9,2 | 2,7 | -1 |
| 9,2,3 | 7,0 | 1 |
| 2,3,4 | 0,6 | -1 |
| 3,4,5 | 6,1 | 1 |
| 4,5,10 | 1,7 | 1 |
| 5,10,11 | 7,2 | -1 |
| 10,11,12 | 2,6 | 1 |
| 11,12,13 | 6,3 | -1 |
| 12,13,6 | 3,7 | -1 |
| 13,6,7 | 7,1 | 1 |
| 6,7,0 | 1,6 | 1 |
| 7,0,1 | 6,0 | -1 |

Each edge receives two contributions, all with its existing net sign;
no forced turns or additional cancellations occur. Induction gives

    D=0, K=2, W=6A+2B=16T-6.

This proves that no c>0 can satisfy D+K>=c*2^k uniformly over all generic
additive scans in all sufficiently large dimensions.

For completeness, the exact family minimum follows without a solver.
Normalize spin b=+. Optimizing the four u spins with a fixed gives

    E=|B-Aa|+A|a+1|+A|a-1|+|Aa+B|=2(A+B)=8T-2.

In particular, u0=+,u3=- at either choice of a. The two negative cycles
(a,u0,b,u1) and (a,u3,b,u2), each of multiplicity A, are edge-disjoint
and certify phi>=2A. Mask 1<<u3 attains that frustration. Thus

    phi=2A=4T-2,  R_min=4T+1=N/4+1.

The half graph consists of u0,u1,a,b. Its two internally disjoint terminal
paths have capacities A and A, while cutting the two a edges costs 2A;
hence lambda=2A=phi. This half is unbalanced, showing again that balance
is sufficient but not necessary for exactness of the terminal-cut bound.

## 2. One highest dominant coordinate makes D+K+lambda=5 constant

Now let n=k+1>=5, T=2^(n-5), N=32T, and append H=1+sum(v_k)=16T+4 as
the new highest numerical coordinate. The scan consists of two complete
copies of the previous scan. It is generic because their score ranges
are disjoint. The old top b becomes the new root; every other old active
variable has a left and a right copy. Internal right-copy couplings at
the old top switch sign, exactly as in the established half reduction.

The first and last old comparisons change the first core coordinate
(weight 1), with forward Gray signs + and -. The boundary between the
two scan copies supplies only the new couplings

    (left u3,new top)=-1, (right u0,new top)=+1.

They are distinct from every internal pair and from each other. Therefore

    D_new=0, K_new=4, W_new=2(16T-6)+2=N-10.

The new half graph is exactly one full old graph plus the unit edge from
old u3 to the new top. Cutting that leaf costs 1, and the old top-to-u3
edge has capacity B>=1. Thus lambda_new=1 and

    D_new+K_new+lambda_new=5   for EVERY n>=5.

For every fixed c>0 this eventually lies below c*2^n. Consequently there
is no positive-density uniform D+K+lambda-only certificate at ANY normal
constant, not just at the previously rejected quarter constant. This
uses real generic additive scans, not arbitrary permutations or sampled
chambers. The correct full frustration remains extensive.

## 3. Exact internal-cycle repair with shared capacities

Let the new top spin be +. With old top +, the old optimum has u3=-,
so the new half optimum is F_+=E_old+1. With old top -, u3 has positive
field B-Aa>=1. For each old middle-root choice, forcing u3=- costs at
least 2 in old energy; it gains at most 2 at the new unit leaf. Hence
F_-<=E_old-1, and an old optimum with u3=+ attains equality. Therefore

    E_new=F_++F_-=2E_old=16T-4,
    phi_new=(W_new-E_new)/2=8T-3=N/4-3,
    R_min=1+4+phi_new=8T+2=N/4+2.

An independent integer packing proves the same value. In the new half,
pack the two old negative cycles, each with mass A. Their combined cycle
mass is C=2A. The edge old top-to-u3 has capacity B=A+1; after its cycle
load A, it has exactly one remaining unit. The terminal path
(old top,u3,new top) uses this unit and the new unit leaf, so P=1. Its
combined loads with the two cycles respect every edge capacity. The
existing joint bound gives

    phi_new>=P+2C=1+4A=8T-3,

matching the energy upper certificate. Independently maximizing paths
and cycles without combining their loads would not justify this claim.

Writing q=N/2, an explicit attaining rank has negative-spin indices

    {q-13,q-12,q-11,q-10,q-3},

and all other normalized spins positive. The first index is left u3;
the next three are right u0,u1,u2; the last is the right old middle root.
At n=5 this is mask 8312. This also independently confirms the exact
fixed-scan optimum; no floating-point certificate is involved.

## 4. Verification, novelty scope and next gap

verify_paired_constant_cut_budget.py independently enumerates the base
and one-period raw-turn counts, builds actual integer score scans for
both families through dimension 18, checks their complete signed graphs,
integer cuts, all negative-cycle signs and COMBINED half capacities,
and checks constant-size exhaustive active-spin optima. Through dimension
12 it also compares with the separately implemented ancestor optimizer
and directly counts the explicit rank's runs. Its complete certificate
and run log are paired_constant_cut_budget_certificate.json and
paired_constant_cut_budget_run.log. Audit: 29 dimension-family cases,
zero violations, 1.6772213429940166 seconds, SHA256
801de14ec9409a97751d2534ff5341cbe92d295b143b697c94b86934b7177729.
The finite audit checks the analytic local-induction proof, rather than
substituting for all-dimensional justification.

The original increment here is the realizable overlapping-row family
with constant cancellation budget and its dominant-top lift with constant
terminal-cut budget, together with exact energy and packing certificates.
The four-coordinate seed, paired family, signed frustration, cut theory,
block lifting and joint P+2C theorem are previously recorded results.
In particular, the seed was already documented in
verify_paired_sibling_ranks.py; its rediscovery is not claimed as novelty.

The primary M_n theorem, explicit construction uniformly hard over ALL
scans and the universal paired-sibling quarter conjecture remain OPEN.
The periodic core and its high lift have extensive frustration, so they
refute only a sufficient-proof shortcut. The precise next target is a
single compatible path/cycle certificate with D+K+P+2C>=c*N, c>0 uniform
over every genuine generic additive scan. Internal weighted cycles cannot
be omitted or bounded by O(n): on this family almost the entire linear
budget is carried by just two cycles with exponentially large capacities.
Counting distinct active variables or unweighted cycles is also inadequate.
