# Paired sibling orientations: a protected rank family and a sharp row theorem

Date: 2026-10-03. Unpublished continuation. The main constant-density
M_n problem is OPEN. This note constructs admissible ranks in every
dimension and proves sharp bounds for specified genuine scan families.
The bounds do not yet cover every generic additive scan.

## 1. Why change the rank family

Previous independent fair coordinate trees admit a constant-probability
event making every node in a fixed top tree point the same way. A scan
that repeatedly traverses that top face then has arbitrarily small
normalized run count as the top face grows. The saved all-dimensional
certificate rules out the old uniform fixed-sweep concentration route.

We impose a concrete constraint at every level: the two orientations
with the same higher prefix and opposite controller bit are opposite.
The top event just described is then impossible already on a two-bit
top face. The theorem below proves that this removes that particular
bad-sweep mechanism; it does not establish concentration for arbitrary
weights. Tree ranks, Gray ranks, sign graphs and negative-cycle packing
are inherited mathematical tools. Historical priority for this precise
family and its scan formulas has not been audited or claimed.

## 2. Definition, admissibility and reflection closure

Use coordinate 0 least significant and let N=2^n. For h<n-1 choose an
arbitrary Boolean function theta_h of the bits strictly above h+1.
Choose also a constant theta_(n-1). Define rank bits by

    rho_theta(x)_h = x_h XOR x_(h+1) XOR theta_h(x_(h+2),...,x_(n-1)),
    rho_theta(x)_(n-1) = x_(n-1) XOR theta_(n-1).                    (1)

Interpret the output bits as a binary integer. The mapping is bijective:
recover the input bits successively from highest to lowest. The number
of independent orientation bits is

    1+sum_(h=0)^(n-2) 2^(n-h-2) = 2^(n-1).

At the coordinate-h tree node the orientation sign is

    xi_h(prefix) = (-1)^[x_(h+1) XOR theta_h(higher prefix)].

Changing only the common controller x_(h+1) reverses this orientation.
Every realization remains a fixed-coordinate binary-tree rank and is
prefix-separable. To verify the strict separators directly, take the
first excluded vertex z of any rank prefix, and put

    L_z(x)=sum_(h=0)^(n-1) 3^h xi_h(prefix of z) (x_h-z_h).

At the highest input difference h, the term of magnitude 3^h dominates
all smaller terms, whose total magnitude is at most (3^h-1)/2. Its sign
is the sign of rho_theta(x)-rho_theta(z). Hence every vertex earlier
than z has L_z(x)<=-1, and z and every later vertex have L_z(x)>=0.
Threshold -1/2 strictly separates every nonempty proper rank prefix.

For an input reflection z, rho_theta(x XOR z) belongs to the same family:

    theta'_h(p)=theta_h(p XOR (z>>(h+2))) XOR z_h XOR z_(h+1),
    theta'_(n-1)=theta_(n-1) XOR z_(n-1).                           (2)

Complementing every OUTPUT bit also preserves the family and reverses
all comparisons. R and C are unchanged, so theta_(n-1)=0 can be fixed
when enumerating ranks. This normalization leaves 2^(N/2-1) members.
It does not amount to fixing arbitrary other orientation variables.

## 3. Exact natural-lexicographic linear range

Let r_n(theta) be R for input order 0,1,...,N-1. This is the genuine
additive scan of any positive magnitudes satisfying

    a_h > sum_(j<h) a_j.

The coordinate order is fixed; arbitrary permutations of coordinate
priorities are not included. By (2) the same bounds hold for every
independent coordinate-sign choice.

**Theorem 1.** Over the complete rank family, the exact range is

    ceil(2^n/3) <= r_n(theta) <= floor(2^(n+1)/3).                  (3)

Every integer in this interval occurs, and both endpoints are attained
in every dimension. This is an analytic family theorem, not an
extrapolation from the finite audit.

**Proof.** For n>=3 put T=2^(n-2) and partition the numerical scan into
quartets (4t,4t+1,4t+2,4t+3). The first and last comparison signs in a
quartet are a_t and -a_t, where a_t=(-1)^theta_0(t). The middle sign is
irrelevant to the total: the two internal turn indicators sum to one.
The signs a_t are mutually independent choices. The upper bits form
an arbitrary member of the same family in dimension n-2. Write s_t
for its comparisons between t and t+1 and R_U for its linear count.

At the join from quartet t to quartet t+1, the two turn indicators are

    1{-a_t != s_t} + 1{s_t != a_(t+1)}.

At an interior quartet t, its two join costs minimize to zero when
s_(t-1)=-s_t and to one otherwise. They maximize to two in the former
case and to one in the latter. Each endpoint contributes minimum zero
or maximum one. The exact attainable extrema for fixed upper rank are

    min_(a_t) r_n = 2T-R_U,
    max_(a_t) r_n = 2T+R_U.                                      (4)

Each intervening integer is possible: interior turning positions add
increments of two, and the two endpoint choices supply increments of
zero, one, or two. The functions theta_1 have no effect on this total.

For n=1 and n=2 the count is respectively 1 and 2. If U_n and L_n are
the upper and lower endpoints, (4) gives

    U_n=2^(n-1)+U_(n-2),  L_n=2^(n-1)-U_(n-2).

Solving these recurrences yields U_n=floor(2^(n+1)/3) and
L_n=ceil(2^n/3). The intervals for different upper ranks are nested
around 2T, and the maximal upper rank supplies the full asserted range.
This proves the theorem and the attaining constructions.

## 4. Cyclic extrema and a sharp all-dimensional row bound

Let c_n(theta) be the cyclic turn count in the same numerical scan.
For n>=2 its exact extrema are

    c_min(n) = (2^n+2(-1)^n)/3,
    c_max(n) = (2^(n+1)-2(-1)^n)/3.                              (5)

For n=1 the cyclic count is 2. To prove (5), use the same quartets,
now with cyclic joins. For an arbitrary upper cyclic sign word with
count C_U, each quartet's join costs have minimum zero or one, and
maximum two or one, according as the two adjacent upper signs are
different or equal. Consequently

    min_(a_t) c_n = 2T-C_U,
    max_(a_t) c_n = 2T+C_U.

The bases c_1=2,c_2=2 give (5). Endpoints are attained recursively.

Now fix a dimension d, 2<=d<=n, and ell=n-d. In each row fix the lower
ell input bits and scan the top d bits in their natural numerical order.
Rows may be listed in any order. The genuine positive integer example is

    w_h=2^d*2^h       for h<ell,
    w_(ell+j)=2^j    for j=0,...,d-1.                            (6)

Then the scan is p_(r*2^d+i)=(i<<ell)|r. These weights are distinct
binary place values in a permuted coordinate order, so no ties occur.
All signed versions are included using (2). More general separated
lower-row additive scores are allowed; their particular row order has
no effect on the argument.

Write H=2^d, T=2^(n-d), and let R_U,C_U be the counts of the induced
top-d rank in the reflected numerical top scan. Comparisons WITHIN a
row depend only on that top rank. At every row join, the last top vertex
resets to the first, and their topmost input bit differs. The lower bits
and all lower orientation choices therefore cannot affect the join sign.
The cyclic comparison word is exactly T copies of the upper cyclic word,
and the two comparison signs bordering the removed closing edge are
also those of the upper word. Thus

    C_full=T C_U,
    R_full=T C_U+(R_U-C_U)=(T-1)C_U+R_U.                        (7)

**Theorem 2.** The exact minimum over EVERY rank in (1) for the fixed
d-dimensional row scan, including all its sign reflections, is

    min R_full =
      T*(H+2)/3,          if d is even,
      T*(H-2)/3+1,        if d is odd and d>=3.                   (8)

The independent minima of C_U and R_U in (3),(5) give the lower bound
in (8). They can be attained simultaneously. For odd d, every cyclic
minimizer has R_U=C_U+1 because R_U>=c_min(d)+1 and |R_U-C_U|<=1.
For even d, a linear minimizer necessarily has C_U=R_U=c_min(d): C_U
is even, and any larger possible value is at least c_min(d)+2. This
proves simultaneous attainment and hence equality in (8).

For n>=3, minimize also over d. The odd case d=3 gives the exact
universal row-family minimum

    R_full >= 2^(n-2)+1,     with equality possible.              (9)

All larger odd dimensions have larger density, and every even case
is at least N/3, exceeding N/4+1 whenever required; the few small bases
are explicit. A one-bit fast top face, omitted from (8), has R=N-1
and does not lower (9). This proves an N/4+1 bound for every completion
of every paired-sibling rank against this precisely defined row family.
It is not a bound against arbitrary additive weights.

For the three-bit fast face, with top orientation normalized positive,
the event a_0=-1,a_1=+1 forces C_U=2 and R_U=3. In the distribution
choosing the free theta bits independently fairly, this event has
probability exactly 1/4, independent of n and every remaining choice.
Thus that fixed row sweep has R=N/4+1 with probability 1/4. The old
arbitrarily-small-density row event has disappeared, but a uniform
strong lower tail at thresholds cN with c>1/4 is still impossible.
This argument leaves smaller positive thresholds open.

## 5. A concrete all-sweep obligation involving cancellation and cycles

For an arbitrary genuine additive scan p, let h_i be the highest input
coordinate changing on edge i. Let e_i be the comparison sign of forward
Gray rank. Let v_i identify the free theta bit controlling that edge:
it is (h_i, common prefix strictly above h_i+1), with a single top variable.
Equation (1) gives the exact comparison

    s_i = e_i sigma_(v_i),     sigma_v=(-1)^theta_v.

Two consecutive equal v_i come from the same h and common controller,
and force a turn. Let D count these equal-variable pairs among the N-2
linear triples, and set

    J_uv=sum e_i e_(i+1) for unordered distinct variables u,v,
    W=sum |J_uv|,
    E_*=max_sigma sum J_uv sigma_u sigma_v,
    K=(N-2-D-W)/2,   phi=(W-E_*)/2.

Here K counts opposite-sign raw mixed contributions canceled BEFORE
optimization; it must not be omitted. Both K and phi are nonnegative
integers. Maximizing energy chooses a rank in the family, and the exact
minimum over that family at this fixed scan is

    min_theta R = 1+(N-2+D-E_*)/2 = 1+D+K+phi.                  (10)

Global inversion of all spins is output-rank reversal, so fixing the top
spin does not change this minimum. This E_* is an optimization over
different ranks, unlike the earlier Gray graph's optimization over
coordinate reflections of one rank.

Every fractional packing of negative cycles with edge loads at most
|J_uv| gives a rigorous lower certificate P<=phi. A sufficient new
all-dimensional proof obligation is therefore

    D+K+P >= N/4  for EVERY generic additive scan.                (11)

Proving (11), or directly D+K+phi>=N/4, would give RLC(rho)>=N/4+1
for every rank in this family and would settle the main constant-density
target. Neither inequality is proved here. There is no such assertion
for arbitrary vertex permutations: a permutation equal to a rank's own
traversal has R=1. Genuine additive coherence must enter the argument.

For a small exact illustration, take positive weights (1,6,8,4). The
linear graph, with free variables numbered by level and then high prefix,
has D=0,K=2,W=10 and edges

    (0,6,-1),(0,7,2),(1,6,1),(1,7,1),
    (2,6,1),(2,7,-1),(3,6,-1),(3,7,-2).

The cycles (0,7,1,6,0) and (2,7,3,6,2) are negative, edge-disjoint,
and each supports amount one. Thus phi>=2. Mask 8 (only variable 3
negative) has unsatisfied weight exactly two, so E_*=6 and the exact
family minimum is R=1+0+2+2=5. Dropping the negative-cycle term would
miss this sharp quarter-bound instance: W-D=10 exceeds N/2-2=6.

This example also shows why Theorem 1's ceil(N/3) lower bound cannot be
extended directly to arbitrary weights: this actual scan has R=5<6.
The weaker quarter obligation (11) survives this particular test.

## 6. Exact audit, pressure and what remains open

The standard-library verifier checks the strict separator at all rank
prefixes through n=4, every reflection of every normalized rank through
n=4, the attained linear and cyclic extrema through n=16, and exact
row-copy identities in actual signed integer scans through n=12. It
also checks the negative-cycle certificate without an LP solver.

Using the inherited certified 5376 signed Q4 chambers, it exhausts all
128 normalized paired-sibling ranks: 688128 rank/sweep pairs. The RLC
histogram is {5:88,6:32,7:8}. Thus some members outperform ordinary
forward Gray rank's Q4 RLC=6. This finite observation is candidate
selection evidence, not an all-dimensional lower bound or a historical
priority claim for a seven-run four-bit rank.

An independent Q5 pressure run exhausts all 32768 normalized ranks at
each of 57 sampled generic positive weight vectors (seed 202610030929).
It found minimum 10, and omits most weight chambers. A separate integer-
witness pressure uses a floating MILP only to propose orientations at
40 generic scans through n=10. Further local mutations at n=6,7,8 make
3500 proposals starting at the exact row boundary. No smaller witness
was retained. These sampling results prove neither (11) nor optimizer
coverage. Returned witnesses are independently checked with exact
integer ranks, exact additive scores and actual turn counts; solver
status alone is never used as a mathematical certificate.

The next step is a structural negative-cycle or translation argument for
(11), or an exact genuine counterexample to it. Repeating finite rank
enumeration or inferring positivity from the absence of sampled
counterexamples would not advance that proof obligation.

All published versions, DOI and archive bytes remain unchanged.
