# Dominant higher coordinates: exact four-state recurrence and a linear cut deficit

Date: 2026-10-03. Unpublished all-dimensional diagnostic theorem.
The main constant-density M_n theorem is OPEN; published v1.0 is unchanged.

This continues PAIRED_ANTIPODAL_HALF_GRAPH.md and
PAIRED_COMPLEMENT_HALF_GRAPH.md. It uses standard conditional signed-graph
optimization, specialized here to an exactly realizable additive scan.
The distinction between higher and lower new coordinate positions matters:
the lower-coordinate lift of this seed has lambda=2T-1, whereas the
higher-coordinate lift proved below has lambda=1.

## 1. Exact statement for every dimension

For n>=5 let T=2^(n-5) and choose positive integer weights

    w=(1,14,4,8,16,44,88,...,44*2^(n-6)).

For n=5 the tail is empty. These weights are generic; the five-coordinate
core has distinct scores in [0,43], and higher-coordinate subset scores
are distinct multiples of 44. The scan reads T core copies in numerical
higher-coordinate order. Let G_n be its paired-sibling comparison graph,
and let lambda_n be the unsigned terminal cut in its antipodal half.
Exactly,

    D_n=0, K_n=6T, W_n=20T-2, lambda_n=1,
    phi_n=(10T-c_n)/3,
    min_theta R_n=(28T+3-c_n)/3,

where c_n=1 for odd n and 2 for even n. Thus

    D_n+K_n+lambda_n=6T+1=(3/16)2^n+1,
    2^n/4-(D_n+K_n+lambda_n)=2T-1=2^n/16-1,
    lim_n (min_theta R_n)/2^n=7/24.

The cut-only quarter budget therefore fails with a linear, rather than
merely additive, deficit in every n>=5. This does not refute a smaller
positive cut-only coefficient, the true quarter budget D+K+phi, or the
main M_n problem. These are exact minima over ranks at the specified
scan, not minima over all scans for an individually fixed rank. The
7/24 limit is not claimed as an improved extremal upper bound: the
previous fast-top-three family already attains asymptotic density 1/4.

## 2. The genuine graph doubling and its two boundary fields

Append the next highest coordinate of weight 44T. Its two blocks are
copies of the n-coordinate order, since 44T exceeds its total old score
span 44T-1. The old top comparison variable becomes the shared depth-zero
node a of G_(n+1). Every other old variable has two distinct copies.
When the new input bit is one, the Gray sign of an old top comparison
changes, while every other old comparison sign is unchanged. Therefore
all old top incident couplings negate in that copy; other couplings agree.

The minimum coefficient is always w_0=1. The first comparison uses
coordinate zero with higher prefix all zeros; call its variable L_n.
The last uses coordinate zero with higher prefix all ones; call it U_n.
Explicitly L_n=0 and U_n=2^(n-2)-1 in the ascending-coordinate layout.
Their Gray signs are +1 and -1. The inter-block comparison is the new top
variable r, with Gray sign +1. The ONLY additional graph edges are

    J_(U_n in left copy,r)=-1,
    J_(r,L_n in right copy)=+1.

They do not overlap old internal edges. Neither boundary turn is forced.
Consequently D_(n+1)=2D_n, K_(n+1)=2K_n, and W_(n+1)=2W_n+2.
The seed has D_5=0,K_5=6,W_5=18, proving the displayed all-dimensional
D,K,W formulas.

The half H_(n+1) is one complete old graph G_n plus the new top vertex
attached to U_n by one unit edge. The seed active graph is connected;
doubling and the displayed new edges preserve connectivity of all active
vertices. In particular U_n is connected to the old top, now terminal a.
Thus a unit terminal path exists, and the singleton new-top cut has
capacity one. This proves lambda_(n+1)=1. The seed lambda_5=1 is the
known exact half-cut certificate.

## 3. Four endpoint states, with an analytic seed certificate

Fix the top spin of G_n to +1. For endpoint spins s,t in {+1,-1}, define

    F_n(s,t)=max energy with sigma_L=s, sigma_U=t.

For the seed, its left half has terminals a=14,r=15 and edges
(0,12,+1),(0,14,+1),(0,15,-1),(1,12,+1),(1,14,+1),
(2,12,-1),(2,14,+1),(3,12,-1),(3,14,-1).
Its opposite half is determined by complement switching. Write b,c for
the spins of the two intermediate nodes 12,13. Optimizing the six
nonterminal leaf spins independently gives

    F_5(s,t)=max_(a,b,c in {+1,-1})
      [s(b+a-1)+2|b+a|+|a-b|
       +t(c+a+1)+2|c+a|+|a-c|].

Only eight explicit terms remain; no full rank or chamber enumeration
is required for this certificate. In the state order (++,+-,-+,--),

    F_5=(12,6,10,12).

Let u be the last endpoint spin in the left copy and v the first endpoint
spin in the right copy. Optimizing the shared old top sign gives exactly

    F_(n+1)(s,t) = max over u,v of
      max{ F_n(s,u)+F_n(-v,-t)-u+v,
           F_n(-s,-u)+F_n(v,t)-u+v }.                         (1)

The first alternative has shared old top +1; normalizing the negated-top
right copy reverses all its spins. The second alternative has shared top
-1 and reverses all left-copy spins instead. The -u+v terms are the two
new unit edges. Conversely any maximizing choices and old conditional
assignments reconstruct an attaining full rank, so (1) is an equality.
This is a constant-size max-plus transfer, despite exponentially many
free rank orientations.

## 4. Algebraic profile induction and the closed forms

Applying (1) to the seed gives

    F_6=(24,22,26,24), F_7=(52,50,50,52).

For any scalar A, direct substitution of the four spin choices shows

    (A,A-2,A-2,A)   maps to (2A,2A-2,2A+2,2A),
    (B,B-2,B+2,B)   maps to (2B+4,2B+2,2B+2,2B+4).

These symbolic formulas hold for every integer energy scale, including
arbitrarily large dimensions. They alternate from n=6 onward. If
E_n=max F_n, it follows, including the checked n=5 first step, that

    E_(n+1)=2E_n+2  when n is odd,
    E_(n+1)=2E_n    when n is even.

Since W_(n+1)=2W_n+2, the frustration obeys

    phi_(n+1)=2phi_n      when n is odd,
    phi_(n+1)=2phi_n+1    when n is even,
    phi_5=3.

Solving this elementary recurrence gives phi_n=(10T-c_n)/3. Substituting
in the exact linear identity R_min=1+D+K+phi gives
R_min=(28T+3-c_n)/3 and the limit 7/24. All fractions are integers:
T=2^(n-5) has the required residue modulo three.

The endpoint recurrence provides a constructive optimal orientation
assignment recursively in every dimension. The verifier additionally
reconstructs ranks with the independent full ancestor optimizer and
checks their actual integer runs. No inference of all-dimensional
validity is made solely from those finite checks.

## 5. Independent cycles supply the missing positive density

The seed full graph has three capacity-one edge-disjoint negative cycles

    (14,1,12,2), (14,6,13,5), (14,0,15,7).

Each row retains its complete internal signed graph, up to switching its
old top according to the next input bit. All these cycles remain negative.
Two rows may share an old top variable, but every other internal variable
and every cycle edge has its own higher-prefix label. Inter-row edges
have a comparison coordinate >=5 and cannot cancel any core internal
edge. Thus their T translated copies form a capacity-respecting packing
of value 3T in the FULL graph. This gives phi_n>=3T and hence

    R_min>=1+9T > 1+8T=1+2^n/4.

The inherited cycles already repair the linear quarter deficit that the
single terminal-flow path misses. The exact transfer determines the
remaining frustration beyond 3T; it is not needed for this repair.
This illustrates the required distinction between a failing certificate
and a failing lower bound. A universal construction of analogous
capacity across arbitrary genuine weights is still missing.

## 6. Reproducible scope

verify_paired_dominant_high_tail.py checks n=5,...,12 against genuine
integer subset-sum orders, the complete two-copy edge embedding, exact
integer ancestor optima, direct attaining-rank run counts, unsigned
terminal cuts and all 3T inherited cycle loads. It also checks the
symbolic two-profile maps at representative arbitrary integer scales;
the all-dimensional claim follows from the displayed substitution proof.

All checks passed in 0.18527246599842329 seconds. Certificate digest
68b52f66cca76cff80176f4c86c7b043d8db35deb1b26cc5960d66c04fe49b0c.
The accompanying JSON preserves every listed weight vector, attaining
mask, four-state profile, score-order digest, and exact objective.

Next analytic task: extend a joint flow/internal-cycle construction to
arbitrary non-block additive scans. The general exact residual-frustration
formula from the companion note remains available; general constant
M_n density and all-scan paired quarter density both remain OPEN.
