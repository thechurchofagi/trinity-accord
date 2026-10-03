# Complement symmetry, a half-graph identity, and a general cut certificate

Status: all-dimensional identities and certificates proved. The general
constant-density lower bound is OPEN. This note applies standard signed
graph switching, integer dynamic programming and max-flow/min-cut to the
paired-sibling scan graph; none of those general methods is claimed new.
The precise specialization and its limitations are the research increment.

## 1. Complement symmetry of every genuine scan

Let n>=2, N=2^n, and let p be the tie-free order induced by arbitrary real
additive coefficients, with any signs. With Cx=x XOR (N-1),

    p_(N-1-i)=C p_i,

because score(Cx)=sum_j w_j-score(x). A paired comparison variable at
coordinate h<n-1, higher prefix P, is mapped under C to the same coordinate
with complemented higher prefix. Denote this involution on variables by T.
The top variable b and the root variable a (coordinate n-2) are fixed by T;
all other variables form pairs. The forward Gray map satisfies
gamma(Cx)=gamma(x) XOR 2^(n-1). Reversing the comparison endpoints therefore
negates its Gray sign for h<n-1 and preserves it for h=n-1.

For raw mixed-turn couplings this proves

    J_(Ta,Tb)=J_(a,b)                  if neither endpoint is top,
    J_(Ta,top)=-J_(a,top).

Here a in the second display denotes an arbitrary non-top variable, not
necessarily the root. In particular J_(root,top)=0. Forced raw turns occur
in complement pairs, so D is even.

Every nonzero edge has ancestor-comparable endpoints in the binary prefix
tree (PAIRED_ANCESTOR_OPTIMIZATION.md). Apart from the fixed root and top,
split its vertices by the leading bit of their nonempty higher prefix.
There is no edge between the two branches. They are copies under T, with
all internal and root incident couplings identical and top incident
couplings negated. Let H be the half graph on leading-prefix-bit-zero
vertices together with root and top, and let A=sum_(e in H)|J_e|. Then
W=2A. These facts hold for every generic additive scan, without any
cardinality or block-contiguity assumption.

## 2. Exact two-boundary energy reduction

Normalize the top spin to +1. Write F_+ and F_- for the maximum half-graph
energies with the root fixed respectively to +1 and -1. On the opposite
half, negating its top incident couplings is equivalent to reversing
all of its non-top spins, including the prescribed root. Thus for either
fixed root sign the full maximum is

    E_max = F_+ + F_-.

The full minimum does not favor a root sign: both signs have attaining
ranks. Define the integer half frustration costs

    f_+=(A-F_+)/2,  f_-=(A-F_-)/2.

They are nonnegative, and the full frustration is exactly f_++f_-. Hence

    min_theta R = 1+D+K+f_++f_-.

An independent ancestor recursion computes both F values using integers
and reconstructs two full attaining masks. The exact identity is proved
by branch independence, rather than inferred from that computation.

## 3. A cut lower bound even when the half is unbalanced

Let lambda be the root-to-top minimum cut in H with unsigned capacities
|J_e|. It is an integer for the integral scan couplings. Take optimal
half spin assignments for the two root boundary conditions. The vertices
where these assignments differ form a cut shore containing the root and
excluding the top. Every edge crossing that shore is unsatisfied under
exactly one assignment; other edges contribute either zero or twice their
capacity to the sum of the costs. Consequently

    f_++f_- >= lambda,
    R(rho_theta along p) >= 1+D+K+lambda        for every theta.

There is also a constructive negative-cycle packing proof. Decompose an
integer maximum flow in H into root-to-top simple paths with positive
integer multiplicities. For each path, follow it to the top and return
along its mirrored path in the other half. The two halves have disjoint
interiors. The resulting simple cycle is negative: its mirrored path has
the opposite sign product because it contains precisely one top incident
edge. Path loads are bounded by |J_e|, so the mirrored cycles form an
integer capacity-respecting packing of value lambda. Thus this route
supplies reusable explicit cycles for all dimensions and all genuine scans.

If H is balanced, switch its signs to make every edge positive. One root
boundary condition satisfies all edges; the other costs exactly the
unsigned root-to-top minimum cut. If root and top are disconnected both
conditions cost zero and lambda=0. Therefore, in the balanced case only,

    f_++f_-=lambda.

This is a standard switching/min-cut fact. General unbalanced halves may
have further internal frustration, which the root-to-top flow omits.

## 4. An already known obstruction has a dimension-minimal half

The previously saved genuine scan w=(1,6,8,4) already supplied two negative
cycles in the full paired graph. One of them lies in H: (7,0,6,1), with
successive signed couplings (2,-1,1,1). It is a negative four-cycle.
Thus the proposed simplifying assumption that all half graphs are balanced
fails already at n=4. This is a new diagnostic use of an existing cycle,
not a claim to have discovered that cycle anew. At n<=3 a half graph has at
most one interior vertex and no root-top edge, hence has no cycle; n=4 is
the least possible dimension. Initial verification incorrectly conjectured
balance through n=4; the first exhaustive audit rejected it at this known
integer witness. The final verifier retains the correct balanced and
unbalanced histograms.

Appending a new highest coordinate with coefficient 1+sum(w) puts two
copies of the old scan in separate blocks. The old full graph embeds in
the new left half (old top becomes the new root), with its signed internal
couplings unchanged. New inter-block raw turns couple only to the new top.
The displayed negative cycle therefore persists in every dimension n>=4.
The exact verifier audits these lifts through n=12; the embedding argument
proves the all-dimensional claim.

## 5. Verification and the remaining quantitative gap

paired_antipodal_half_graph.py returns the two conditional energies, exact
attaining masks, signed-graph balance witness or negative cycle, integer
max flow and cut, and load-checked mirrored cycle packing. The verifier
checks all 5480 signed scan chambers in n=2,3,4, using the already audited
positive-chamber representatives, and fresh signed integer scans in
n=5,...,10. Full ancestor DP and direct rank runs independently agree;
small conditional optima also agree with exhaustive masks. This audit
does not claim chamber completeness in n>=5.

The candidate D+K+lambda>=N/4 would suffice to prove a universal quarter
bound for the whole family, but is already rejected by the genuine n=5
integer scan w=(1,14,4,8,16): D=0,K=6,lambda=1, so its budget is 7<8.
The full frustration is 3, and the true family minimum is 10; this is
not a quarter-bound counterexample. Internal negative cycles are essential
even when the cut packing is small. The next precise task is to extend
this cut-only failure to all dimensions, preserve the independent internal
cycle packing, and isolate how its additional load can replace the
missing quantitative cut budget.
