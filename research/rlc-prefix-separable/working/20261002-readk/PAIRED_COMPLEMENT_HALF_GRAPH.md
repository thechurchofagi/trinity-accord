# Complement half graphs: exact frustration formula and an exponential cut gap

Date: 2026-10-03. Unpublished structural research note.
The main all-dimensional constant-density M_n problem remains OPEN.
The published TA-TR-2026-22 v1.0 is unchanged.

This extends PAIRED_ANTIPODAL_HALF_GRAPH.md, saved at commit
4755740efbe9518bd7a1bb958ca7074756e281b1. That concurrent checkpoint
already proves complement decomposition, the two-boundary energy sum and
the cut lower bound, and rejects the universal cut-only quarter budget.
Sections 1-2 and the cut inequality below restate those prerequisites.
The increments here are the exact cut-plus-residual-frustration formula,
a joint path/cycle certificate, and two quantified all-dimensional lifts.

The signed-graph, frustration, flow and switching tools used below are
standard. The claim here is their exact application to the paired-sibling
comparison graph, with a genuine all-dimensional obstruction to replacing
its frustration by an ordinary terminal cut.

## 1. Definitions and scope

Let n>=2, N=2^n, q=N/2. For a generic signed additive scan p, the
paired-sibling family has the previously established exact identity

    min_theta R(rho_theta composed with p) = 1+D+K+phi(G).

Here D counts consecutive identical comparison variables, K counts
opposite raw products canceled at identical unordered variable pairs,
G has the remaining integer couplings J_uv, W=sum |J_uv|, and phi(G)
is the minimum weighted number of unsatisfied signed edges. Every member
of this family is a bijective prefix-separable rank. This note optimizes
family members at ONE scan; it does not take the RLC minimum over scans.

Use the existing ancestor layout. The virtual root is r=q-1. A nonroot
node with depth d and binary prefix P has index

    u(d,P)=q-2^(d+1)+P,  0<=d<=n-2, 0<=P<2^d.

Its comparison coordinate is h=n-2-d. Put a=u(0,0)=q-2. Let H contain
r, a and every node with d>=1 whose first prefix bit is zero, together
with all induced nonzero couplings. Both terminals are retained even
when isolated. Write W_H=sum_(e in H) |J_e|.

## 2. Exact complement decomposition, for every generic additive scan

Let c(x)=x XOR(N-1). Additivity and genericity imply

    p[N-1-i]=c(p[i]).

No positivity or cardinality assumption is used. Forward Gray satisfies

    gamma(c(x))=gamma(x) XOR 2^(n-1).

Consequently, after reversing the reflected comparison, its Gray sign
is unchanged when its highest differing coordinate is n-1, and negated
otherwise. Complement acts on variable labels by

    tau(r)=r,
    tau(u(d,P))=u(d,2^d-1-P).

Set epsilon_r=+1 and epsilon_u=-1 for every nonroot node. Every raw
mixed turn at pair {u,v} is mirrored at {tau(u),tau(v)} with product
multiplier epsilon_u epsilon_v. The linear turn positions i and N-3-i
are paired without fixed points. Therefore

    J_tau(u),tau(v) = epsilon_u epsilon_v J_uv,
    J_ra=0.

The previously certified ancestor embedding ensures that a nonterminal
edge cannot join opposite first-prefix subtrees. Indeed, both labels
then condition on the top input bit, which is common to the triple.
Thus G consists of H and its mirrored copy sharing only r,a; there is
no terminal-to-terminal edge, and W=2W_H.

For spins on H, fix sigma_r=+1. Let E_+ and E_- be the maximum energies
with sigma_a=+1 and -1 respectively, and put

    f_+=(W_H-E_+)/2,  f_-=(W_H-E_-)/2.

In a full spin assignment with sigma_a=s, switch the reflected copy by
its epsilon factors. The switched reflected root remains +1, whereas
its a spin becomes -s. The two interiors are independent. Hence, exactly,

    E_max(G)=E_+ + E_-,
    phi(G)=f_+ + f_-.

In particular, the optimum full energy does not depend on the chosen
spin of a. This is a structural all-dimensional identity, not an
inference from numerical sampling. It also holds for any complementary
vertex order satisfying the same symmetry; additivity is sufficient.

## 3. Cut plus residual frustration: an exact formula

For S contained in V(H), with a in S and r outside S, let delta(S) be
its cut, cap(S)=sum_(e in delta(S)) |J_e|, and H-delta(S) retain all
noncut edges. Denote by phi_free the ordinary minimum weighted signed
frustration without terminal constraints. Then

    phi(G) = min_(a in S, r not in S)
                 [cap(S)+2 phi_free(H-delta(S))].                 (1)

Proof: take an equal-terminal assignment x and an opposite-terminal
assignment y. Their disagreement set S separates a,r. On a cut edge
exactly one assignment is unsatisfied, costing |J_e| in their sum.
On a noncut edge their satisfaction agrees, costing either zero or
2|J_e|. For fixed S, deleting its cut separates the two terminals into
different components, so a freely optimal residual assignment can be
switched on these components to make x_r=x_a=+1. Put y=x with spins
reversed on S. This attains cap(S)+2 phi_free(H-delta(S)), proving both
inequalities in (1).

Let lambda(H;r,a) be the unsigned weighted terminal minimum cut. Then

    phi(G)>=lambda(H;r,a),
    R_min_family>=1+D+K+lambda(H;r,a).                            (2)

If H is balanced, every subgraph is balanced and its free frustration
is zero, so equality phi(G)=lambda holds. Balance is sufficient, not
assumed. Even a disconnected terminal pair need not give phi(G)=0.

A useful certificate works without balance. Pack unsigned r-a paths
and negative signed cycles in H, with nonnegative amounts and TOTAL
edge loads at most |J_e|. If the packed path mass is P and cycle mass
is C, then

    phi(G)>=P+2C,
    R_min_family>=1+D+K+P+2C.                                  (3)

Each terminal path has incompatible endpoint parity in one of x,y,
so requires at least one unsatisfied edge across their two assignments.
Every negative cycle requires an unsatisfied edge in each assignment.
Summing and using the shared capacity bound proves (3). Ordinary
integer max flow is the paths-only specialization. A prospective
universal quarter proof can seek D+K+P+2C>=N/4; this remains OPEN.

## 4. Genuine cardinality seed: zero cut, positive frustration

Take n=5 and weights

    w=(34,36,40,33,48)=32+(2,4,8,1,16).

The common coefficient 32 dominates the total secondary span 31, so
this is a cardinality-first scan with a permuted superincreasing
secondary order. It is generic. Its complete integer subset-sum order is

    (0,8,1,2,4,16,9,10,3,12,5,6,24,17,18,20,
     11,13,14,7,25,26,19,28,21,22,15,27,29,30,23,31).

The raw forced turn positions, starting from zero, are
(0,4,7,8,21,22,25,29), giving D=8. The complete half graph, terminals
r=15,a=14, has these five nonzero edges:

| u | v | J_uv |
|---:|---:|---:|
| 8 | 12 | 1 |
| 8 | 15 | -1 |
| 9 | 12 | 1 |
| 9 | 15 | -1 |
| 12 | 15 | 2 |

Vertex a is isolated, so lambda=0. The negative triangles
(8,12,15) and (9,12,15) each have capacity one; their shared edge
(12,15) has capacity two. Their loads are admissible. Thus each
conditional half has frustration at least two. Assigning all spins
+1, with either isolated-terminal spin, attains two. Consequently

    f_+=f_-=2, phi(G)=4, W=12,
    K=(32-2-8-12)/2=5,
    R_min_family=1+8+5+4=18.

Mask zero (the forward-Gray rank) attains R=C=18. This counterexample
already lies within the cardinality-first class. It refutes both
universal half-graph balance and exact replacement of phi by lambda;
it does NOT refute any quarter lower bound.

## 5. All-dimensional lift: the omitted cycle term is N/8

For every n>=5, put ell=n-5 and T=2^ell. Use positive integer weights

    w_j=192*2^j for 0<=j<ell,
    (w_ell,...,w_(n-1))=(34,36,40,33,48).

The core subset scores lie in [0,191] and are distinct. The full scan
therefore consists of T consecutive rows in numerical low-bit order,
each reading exactly the five-bit core order above. This is a genuine
generic additive scan in every dimension; larger lifts are row scans,
not claimed to remain cardinality-first.

Every comparison variable lies in the top five-coordinate core. Its
index is the seed index plus q-16. Each internal raw turn is repeated
T times. At a row boundary the last core comparison and the first core
comparison use the same node a; the closing comparison uses r. The
two added raw products at {a,r} are +1 and -1. Thus each of the T-1
boundaries contributes one cancellation, no nonzero coupling and no
forced turn. Exactly,

    D=8T, K=5T+(T-1)=6T-1, W=12T.

The half graph is precisely the displayed five-edge graph translated
by q-16 and with every coupling multiplied by T. Its a remains
isolated, giving lambda=0. The two negative triangles have packed mass
2T, so (3) gives phi(G)>=4T. Mask zero attains this, hence

    phi(G)=4T=N/8,
    phi(G)-lambda=N/8,
    R_min_family=18T=(9/16)N, attained with R=C by mask zero.

This is an exact all-dimensional obstruction to a claim
phi(G)=lambda+O(n), even for positive genuine weights and admissible
ranks. It shows why the residual signed-frustration term in (1) cannot
be dropped. Since D+K is already larger than N/4 in this family, it
neither falsifies the stronger possible certificate D+K+lambda>=N/4
nor supplies a counterexample to the main M_n target. The cut-only
quarter budget is already false for a different genuine scan, as proved
at the preceding checkpoint; the following lift makes that failure
all-dimensional.

## 5b. All-dimensional cut-budget failure, repaired sharply by joint packing

The preceding checkpoint's genuine seed w=(1,14,4,8,16) has
D=0,K=6,lambda=1,phi=3. For every n>=5 retain ell=n-5, T=2^ell
and use low coefficients 44*2^j followed by this seed. Its score span
is 43, so exactly the same disjoint-row argument applies. Translate
all seed labels by q-16. The entire half graph is:

| seed u | seed v | lifted J_uv |
|---:|---:|---:|
| 0 | 12 | T |
| 0 | 14 | T |
| 0 | 15 | -(2T-1) |
| 1 | 12 | T |
| 1 | 14 | T |
| 2 | 12 | -T |
| 2 | 14 | T |
| 3 | 12 | -T |
| 3 | 14 | -T |

Here a=14,r=15 before translation. The closing comparison creates
one new negative product at {0,r} in each half per row boundary;
its sign agrees with the old product. Thus D=0, K=6T, W=20T-2.
The only r incident edge has capacity 2T-1. Pack these terminal paths:

    (r,0,a)          with amount T,
    (r,0,12,3,a)     with amount T-1.

Their total flow is 2T-1; the singleton cut {r} has that capacity.
Hence lambda=2T-1 exactly. Consequently, for EVERY n>=5,

    D+K+lambda=8T-1=N/4-1 < N/4.

This disproves the exact cut-only quarter budget in all dimensions.
It does not rule out a weaker positive-density cut-only inequality.

Now also pack the negative cycle (1,12,2,a) with amount T. Its four
edges are disjoint from both terminal paths. All shared path loads
are within the displayed capacities. The joint certificate (3) is

    P+2C=(2T-1)+2T=4T-1.

For completeness, the conditional half optima are

    E_+=4T+1, E_-=8T-1.

To verify analytically, write b for the spin of node 12, s for that
of a, and keep r=+1. Optimizing the four leaf spins gives energy

    |T(b+s)-(2T-1)|+2T|b+s|+T|s-b|.

For s=+1 its maximum over b is 4T+1; for s=-1 it is 8T-1.
Thus E_max=12T, phi=4T-1, and the joint certificate is exact. The
corresponding cut-plus-residual identity (1) is also exact at the
singleton root cut: deleting it leaves free frustration T.

The admissible rank mask 56 shifted left by q-16 attains

    R_min_family=1+0+6T+(4T-1)=10T=(5/16)N,
    C_at_witness=10T.

This optimizes the rank family at the displayed scan; it is not an
RLC lower bound or an upper bound on M_n. It supplies a concrete,
all-dimensional mechanism by which internally packed negative cycles
repair the cut's missing budget. The gap phi-lambda=2T=N/16 is itself
exponential, even though the cut-only quarter shortfall here is one.

## 6. Reproducible audit and next problem

paired_complement_half_graph.py supplies integer conditional recursion,
complement decomposition, balance/negative-cycle inspection and exact
integer max flow with a residual cut certificate. The recursion uses
the existing ancestor layout; it is an independent implementation, not
a new general graph optimizer.

verify_paired_complement_half.py checked 360 fresh generic scans in
n=2,...,10, seed 202610031153, including signed scans and cardinality
perturbations. No ties were rejected. Every conditional-energy sum was
compared with the exact full ancestor DP, with independent full
recursion through n=7. Small instances also exhaustively checked all
terminal cuts and spin assignments in (1). Among the finite samples,
113 had phi>lambda; none violated D+K+lambda>=N/4. Neither observation
is a chamber classification or an all-dimensional theorem.

Both explicit all-dimensional lifts were audited in all n=5,...,12, checking
actual integer score order, complete half couplings, shared path/cycle
capacities, exact family optima and both explicit attaining rank masks.
All checks passed in 2.7763767930009635 seconds. The complete certificate digest
is 707557f827bb51525f0191229e29a878568dd5328aedb1529f030cd6e242b743.

The next analytic task is to obtain path/cycle capacity from translation
consistency of genuine scans, with a positive fraction of N uniformly
in the weight vector. A failure of a cut-only certificate is distinct
from failure of the true D+K+phi budget. The existing nonadditive
hierarchy witness remains excluded by this genuine-coherence requirement.
