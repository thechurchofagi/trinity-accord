# A coherent cardinality refinement below one-half density

Date: 2026-10-03. Unpublished all-dimensional counterexample to a
restricted conjecture. The positive constant-density M_n problem remains
OPEN. The Gray graph, reflection identity and common-prefix cancellation
are inherited methods, not newly named inventions. Historical priority
for this precise refinement family has not been established.

## 1. Exact theorem

For any n>=5 set L=2^(n-5) and secondary weights

    b=(4,6,3,0,8,32,64,...,32*2^(n-6)),
    B=1+sum b=32L-10,   w_j=B+b_j.

For n=5 the tail is empty and B=22. Every weight is strictly positive.
The actual score order is (input cardinality, b dot x): a cardinality
difference dominates the total secondary span. Within a cardinality
layer the scores are distinct, since the first five coefficients have
distinct subset sums of each fixed cardinality, and the tail binary
place values are multiples of 32, above the core span 21.
There are just q=n+1 distinct primary cardinalities.

For forward Gray rank the exact reflection graph is

    D=2L+4,
    J_(1,2)=-2L,  J_(1,3)=-2L,  J_(2,3)=2L,
    all other off-diagonal J=0,
    W=E_*=6L,    E_*-D=4L-4.

The triangle is unfrustrated: take spin 1 negative and spins 2,3
positive. The input reflection z=3 realizes these spins. Therefore

    min over all sign reflections C = 14L+2 = (7/16)*2^n+2,
    min over all sign reflections R = C.

The unique least weight is coordinate 3, which is not the highest
coordinate for n>=5, so the linear endpoint correction vanishes.
The signed integer weights (-w_0,-w_1,w_2,...,w_(n-1)) attain this
minimum; they are genuine generic additive weights.

This refutes E_*<=D already for n=6, and E_*<=D+O(n) asymptotically.
It also refutes the proposed general extension of the numerical
secondary theorem to every coherent secondary order, even with a
linear number of buckets and an asymptotic half-density allowance.
It does NOT refute any positive constant-density theorem. The known
unrestricted Gray ceiling 5/16 is smaller than 7/16, so this is no
improvement to the unrestricted upper bound.

## 2. Proof of the complete graph

Use five core coordinates and the tail above them. Within cardinality
k, tail assignments occur in increasing numerical order; each tail t
has a complete core block of cardinality k-|t|. The tail span separates
these blocks because its least place value 32 exceeds the entire core
span 21. Summed over all cardinalities, each core layer is copied
exactly L times.

The five-bit interior graph, restricted to triples wholly in one core
cardinality layer, has D_int=2 and off-diagonal edges
((1,2,-2),(1,3,-2),(2,3,2)). Its complete finite certificate consists
of all 32 input vertices sorted by (cardinality,(4,6,3,0,8) dot x).
The verifier writes every layer and recomputes every contributing
triple with integer comparisons.

Adding a fixed tail can flip the core highest Gray bit 4, but all
mixed couplings involving that bit sum to zero by core complement
and reversal across paired layers. All three nonzero core edges use
labels below 4 and remain unchanged. Diagonal products are unchanged.
Thus core contributions multiply by L.

A crossing between tail blocks has label at least 5, while a core
edge has label below 5. A mixed triple cannot be diagonal. If two
tail crossings meet at a singleton core block, their three tails are
strictly increasing numerically, and their highest differing-bit
labels cannot coincide. Hence there are no other interior diagonals.

For mixed-label interior triples with maximum label m>=5, toggle
the common bit m+1 when m<n-1. All tail priority above the core is
ordinary numerical priority. A fixed high tail prefix is a consecutive
interval in a layer, so this translation maps a consecutive triple
to a consecutive triple in the adjacent cardinality layer.
It preserves labels and negates exactly the label-m comparison,
cancelling its product. For m=n-1, complement and reverse the triple;
this also preserves the interior class and negates the mixed product.
Thus no additional interior off-diagonal term survives.

For n>=6 the increasing secondary coefficient priority is

    pi=(3,2,0,1,4,5,...,n-1).

Every cyclic boundary edge between cardinality layers has label n-1,
except 0 -> 2^3 and (all-ones XOR 2^3) -> all-ones, which have label 3.
Each exceptional edge meets one interior edge of label 3, since the
next least coefficient has coordinate 2. The boundary from layer 1
to 2 meets the final singleton-layer edge of label n-1. The boundary
from n-2 to n-1 meets the first next-to-full layer edge of label n-1.
These four and only these four boundary triples are diagonal.

To verify the last assertion symbolically, the predecessor of the
largest k-subset replaces pi_(n-k) by pi_(n-k-1), and the successor
of the smallest k-subset replaces pi_(k-1) by pi_k. These substitutions
are the unique nearest extremal subset sums for distinct coefficients.
Their differing input coordinates give exactly the four equalities
above; all other boundary neighbor pairs have distinct labels.
Every mixed-label boundary triple involves the global highest label.
Complement-reversal pairs these products with their negatives, with
no fixed middle vertex. Consequently boundary couplings vanish and
boundary D=4. The n=5 case is the direct base certificate.

This proves the stated full graph. Its three edge signs have positive
product, so all edges can be satisfied together and E_*=W=6L. The
audited identity C_min=(2^n+D-E_*)/2 proves the exact count for all
sign reflections, not only the displayed optimizing weight vector.

## 3. General core reduction, with an explicit boundary error

The same argument works for ANY fixed k-coordinate coherent secondary
vector b whose subset sums are distinct within each cardinality layer.
Normalize b to be nonnegative by subtracting its smallest coefficient,
which preserves ordering within each layer. Choose a tail base A larger
than sum b. Append m numerical binary tail coefficients A*2^j, and
choose common primary coefficient B larger than the total secondary
span. All resulting weights are positive and generic.

Let D_int and J_int be the core contributions from triples inside a
single cardinality layer, and let E_int be the maximum spin energy
of J_int. Complement-reversal makes the core highest off-diagonal
couplings zero. Core triple products below that coordinate replicate
2^m times; the possible fixed-tail flip of the core highest bit has
no effect on the resulting summed core graph.
Numeric-prefix cancellation eliminates every mixed-label contribution
crossing tail blocks. Tail numerical monotonicity excludes extra
interior diagonals. At most 2(n+1) triples contain a cardinality boundary,
so their residual graph energy and diagonal count each have absolute
error at most 2(n+1). Thus, for n=k+m,

    D_n = 2^m D_int + d_boundary,   0<=d_boundary<=2(n+1),
    |E_n - 2^m E_int| <= 2(n+1).

The second inequality follows because the energy perturbation is
uniformly bounded at EVERY spin choice, then taking maxima preserves
the bound. Every core spin choice extends to the full coordinate set.
In particular,

    |C_min,n - 2^(m-1)(2^k+D_int-E_int)| <= 2(n+1),
    lim C_min,n/2^n = (2^k+D_int-E_int)/2^(k+1).

The linear count differs by at most one and has the same limit.
This is a genuine all-dimensional extension of the core's interior
net energy. For the displayed core, D_int=2 and E_int=6, so the limit
is 14/32=7/16; Section 2 gives its stronger exact finite formula.
This general reduction does not establish how small that limit can
be as the core dimension k itself grows.

## 4. Finite evidence and exact remaining gap

verify_cardinality_half_density.py checks the displayed exact family
through n=18, directly sorts every reflection through n=10, and checks
larger selected minimizing integer scans. It also checks the general
core reduction on independently specified core vectors, including
ones whose numerical coordinate order and secondary priority differ.

The preceding complete binary-priority audit covers all n! positive
secondary priority permutations for n=2,...,8, hence 46,232 positive
orders and 2,754,350 optimized spin vectors after symmetries.
Its maximum net energy is zero in every dimension and W<=D throughout.
This finite statement DOES NOT extend to arbitrary secondary vectors:
the displayed (4,6,3,0,8) core is not a binary-priority order on its
fixed-cardinality layers, and its extension has positive net energy.
The exact optimizer's symmetry-reduced spin count must be read from
the receipt rather than inferred as a full direct sorting of all signs.

The reused strict pair-sum chamber certificate also classifies EVERY
five-dimensional cardinality-first coherent secondary order: 1,440
positive orders and 46,080 independently sorted signed scans. Its
minima R=15, C=16 and histograms are recorded in the separate receipt. Although
the full five-dimensional net energy is at most zero, the interior
core net energy can be positive; boundary terms disguise this at
the base dimension and do not survive at comparable density after
extension. This is why direct finite minima did not settle the
all-dimensional half-density conjecture. A separate exact audit of all
1,440 interior graphs gives maximum E_int-D_int=4, attained by exactly
eight orders. Thus the general core reduction proves that 7/16 is the
optimal limiting density among ALL five-dimensional coherent cores
under this specified numerical-tail extension. This is a statement
about a rigorously defined family over all tail dimensions, not a
claim that unrestricted Gray RLC has that value.

The next useful problem is whether arbitrary coherent core interiors
admit a positive dimension-uniform lower density, or can have
(E_int-D_int)/2^k approach 1. Finite priority scans and finite
cardinality subclass results cannot decide that problem. It remains
a restricted route to the main goal, which quantifies over ALL
generic additive scans of an admissible order.
