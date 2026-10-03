# Coherent coordinate faces and exponential single segments for forward Gray

Date: 2026-10-03. Research lemma and excluded proof route.
The main M_n constant lower bound remains OPEN. The forward Gray rank
is gamma(x)=x XOR (x>>1); the inverse BRGC rank is not used here.
No new Gray-code definition or historical-priority claim is made.

## 1. Exact characterization of coherent faces

For x_n=0, the integer rank has the multilinear expansion

    gamma(x)=sum_{j=0}^{n-1} 2^j*(x_j+x_(j+1)-2*x_j*x_(j+1)).

Let F be a coordinate face with free coordinate set I, and all other
coordinates fixed. The following conditions are equivalent:

1. The restriction of gamma to F is an affine rank function.
2. The gamma order on F is induced by a generic additive linear score.
3. No two consecutive numerical coordinates belong to I.

Proof: if I has no adjacent positions, each quadratic product has at
least one fixed argument. Thus the displayed expression restricts to an
affine function. The coefficient of any free j is nonzero, and all ranks
remain distinct, so this affine function gives a generic additive score.

Conversely suppose j,j+1 are both free. Fix every other free coordinate
arbitrarily, and compare the two edges that increase coordinate j from
0 to 1, first with x_(j+1)=0 and then with x_(j+1)=1. The highest Gray
output bit that changes is j; its crossing direction is determined by
x_(j+1). Therefore the two rank differences have opposite signs. A
linear score would assign the same difference w_j to both translated
edges, which is impossible. The quadratic coefficient -2^(j+1) also
shows that the rank restriction is not affine. This proves equivalence.

Hence the maximum dimension of a coherent coordinate face is ceil(n/2),
the independence number of a path on n positions. This says nothing
about more general coherent vertex sets or score slabs.

## 2. General coherent-face block realization

If ANY rank has a coordinate face whose restricted order is additive,
let a_i be generic inducing coefficients on the free positions. Choose
A>sum_i |a_i|. Give each fixed coordinate j a coefficient
(1-2*y_j)*A*2^r, where y_j is its specified value and r indexes the fixed
coordinates. Keep the free coefficients a_i. Up to an additive constant,
the full score is

    A*sum_r 2^r*(x_j XOR y_j) + sum_i a_i*x_i.

Every fixed-coordinate pattern has a disjoint score interval, and the
prescribed face is the first block. Within it the ranks increase. The
full scan is generic, because every free face has the same distinct
score differences and the block intervals are disjoint. Therefore a
coherent face of size L yields a contiguous monotone segment of at least
L vertices in a genuine full-cube linear scan.

## 3. Explicit all-dimensional forward-Gray witness

Take I to be the even numerical positions and fix every odd position to
zero. Put

    a_0=1, a_j=3*2^(j-1) for even j>=2,
    S=sum_{j even} a_j, A=S+1,
    w_j=a_j for even j,
    w_(2r+1)=A*2^r for odd j=2r+1.

The free coefficients are strictly superincreasing, so their subset
scores are distinct and agree with numerical order. On the zero-odd
face they are exactly gamma(x). The full score is A*y+gamma(x_even),
where y is the odd-bit binary integer, and 0<=gamma(x_even)<=S<A.
Consequently the first L=2^ceil(n/2) vertices form one strictly increasing
Gray segment. Thus no polynomial-in-n upper bound on the maximum
monotone segment length can hold uniformly over all Gray linear scans.

This does NOT imply a subconstant total run density. In fact, this
particular displayed scan has exactly R=2^(n-1) runs for every n>=1.
Here is a direct all-dimensional verification of that claim.

Let m=floor(n/2), L=2^ceil(n/2). The scan consists of 2^m even-bit blocks,
one for each odd-bit integer y. Inside each block, binary increments
change free coordinates in numerical order. Their highest changed
coordinate h is even, and the comparison sign of gamma is
(-1)^(x_(h+1)), with x_n=0. Every pair of adjacent internal comparison
signs has exactly one edge with h=0 and one with h>=2. Averaging over all
odd-bit patterns makes those signs disagree exactly half the time,
because x_1 and x_(h+1) are different fixed odd coordinates, or the
latter is the constant x_n=0. For n>=3, the total internal-block turns
are (L-2)*2^(m-1). For n=2 there are no internal-block turns.

At each boundary between consecutive blocks, the last internal edge of
the old block and the first internal edge of the new block both have
h=0. Their signs are opposite, since the least odd bit toggles at every
odd-bit increment. Whatever the intervening boundary comparison sign,
exactly one of its two neighbouring positions is a turn. Hence the
2^m-1 boundaries contribute exactly 2^m-1 turns. Adding the initial
run yields R=1+(L-2)*2^(m-1)+(2^m-1)=L*2^(m-1)=2^(n-1).
The cases n=1,2 are checked directly and satisfy the same formula.

## 4. Evidence and consequence

Run verify_gray_coherent_faces_long_segments.py. The verifier audits all
coordinate faces through n=9, checking affine reconstruction at every
face vertex and exhibiting opposite translated-edge demands for every
noncoherent face. It then independently sorts all full integer scans
through n=18, verifies the whole first face, directly counts total runs
and the longest run, and checks the half-density formula.

The reusable obstruction is an all-dimensional statement. Its role is
to reject a tempting maximum-segment argument before using it in a
general lower-bound proof. A positive lower bound must control the total
or average turn budget, rather than requiring every individual segment
to be short. Existing published n^2 denominator and the stronger draft
coefficient remain unchanged by this lemma.

Next: retain exact opposite translated comparisons as a linear
coherence obstruction, but ask for many disjoint obligations that cannot
all be absorbed into a small number of turns. A single long coherent
face or a single incompatible square is insufficient for that task.
