# Exponential coupling in a coherent cardinality refinement

Date: 2026-10-03. Research lemma and counterexample to an intermediate
proof route. The constant-density lower bound for M_n remains OPEN.
No historical-priority claim is made. The Gray reflection graph and
numeric-prefix cancellation used below are inherited audited tools.

## 1. Exact all-dimensional statement

For n>=4 put

    b=(2,4,8,1,16,32,...,2^(n-1)),   B=2^n,
    w_j=B+b_j.

These are positive generic additive weights: their order is exactly
(Hamming cardinality, b dot x). Indeed the entire secondary range is
2^n-1<B, and b is a permutation of the binary place values.
There are only q=n+1 primary cardinality buckets.

Let D be the equal-label triple count and J the inherited off-diagonal
Gray reflection coupling. Then

    D=2^(n-3)+4,
    J_(1,2)=2^(n-3),   all other J_(h,k)=0,
    W=E_*=2^(n-3),     min over reflections C=2^(n-1)+2.

The graph convention uses zero-based input coordinates and forward
Gray rank gamma(x)=x XOR (x>>1). The cyclic count C is the number of
changes in the cyclic comparison-sign word.

For n>=5 the smallest weight belongs to coordinate 3, which is not
the highest coordinate, so every reflected scan has R=C. For n=4,
R=C-1. All reflections are themselves genuine signed additive scans.

Consequently E_* is exponential even though q is linear. In particular
E_*<=2q fails for every n>=8, and no dimension-uniform bound E_*=O(q^d)
for a fixed d can follow from the bucket count and coherent secondary
additivity alone. This does NOT falsify a half-density bound: here
E_*-D=-4, so the exact minimum is slightly above one half.

## 2. Proof

### 2.1 Core and ordered tail blocks

Separate the four low coordinates from the tail coordinates 4,...,n-1.
Write a tail assignment as t. Inside each cardinality bucket k, tail
assignments occur in increasing numerical order. For a fixed t the
core vertices form one complete block, ordered by the secondary weights
(2,4,8,1), with core cardinality k-|t|. Empty blocks are omitted.
This follows because the core secondary span is 15, below the least
tail secondary place value 16. Every core cardinality block is
replicated once for every one of the 2^(n-4) tail assignments when all
primary cardinalities are taken together.

The five core blocks, listed as input integers, are exactly

    [0],
    [8,1,2,4],
    [9,10,3,12,5,6],
    [11,13,14,7],
    [15].

Direct integer comparisons of their forward Gray ranks give interior
diagonal count 2 and the only nonzero interior off-diagonal sum
J_(1,2)=2. This is a 16-vertex certificate, not a sampled parameter
claim; the verifier recomputes every contributing triple.
Adding a fixed tail changes none of the comparison labels below 4,
and none of their comparison-sign products. Thus the core contributions
replicate to D_interior=2*2^(n-4) and J_(1,2)=2*2^(n-4).

### 2.2 No extra interior diagonal count

An edge between two tail blocks has label at least 4. A core edge has
label below 4, so a mixed triple is not diagonal. If both edges of an
interior triple cross tail blocks, the middle block must be a singleton.
The three tails increase strictly numerically. Two successive highest
differing-bit labels in a strictly numerically increasing triple cannot
be equal: equality at h would require the middle h-bit to be both 1
(relative to the first tail) and 0 (relative to the last tail).
Therefore every interior diagonal contribution is in a core block.

### 2.3 Cancellation of every other interior coupling

Consider an interior mixed-label triple with max label m>=3.
If m<n-1, toggle the common input bit m+1 of all three vertices.
The higher-priority tail coordinates from 4 upward have ordinary
numerical order. In a cardinality bucket, vertices having a fixed
common prefix at these coordinates form a consecutive interval.
Toggling that prefix bit maps the whole interval to a consecutive
interval in the adjacent cardinality bucket and preserves its
secondary ordering. This proves, including translated buckets,
that a consecutive triple stays consecutive. Its labels are preserved.
Precisely the comparison with label m reverses under the toggle,
so its mixed-label product changes sign. This is a fixed-point-free
involution and cancels that coupling.

If m=n-1, complement every input coordinate and reverse the triple.
Positive additive scans are centrally complemented in reverse order.
The complement flips the highest Gray output bit and no other output
bit, so the mixed-label product changes sign. A triple cannot be
fixed because its middle Boolean vertex is not its own complement.

All remaining mixed labels are below 3, hence below the tail
coordinates, and are already exhausted by the core-block calculation.
Indeed any edge crossing tail blocks has label at least 4.
This proves the stated complete interior coupling.

### 2.4 Boundary triples

For n>=5 the increasing secondary priority list is

    pi=(3,0,1,2,4,5,...,n-1).

The first vertex of cardinality k uses the k least priority coordinates;
the last uses the k greatest. The n+1 cyclic edges crossing cardinality
boundaries have highest differing-bit label n-1, except the first
edge 0 -> 2^3 and the final edge (all-ones XOR 2^3) -> all-ones,
which have label 3.

The two exceptional edges each meet a same-label core edge on their
interior side, giving two diagonal triples. The boundary from
cardinality 1 to 2 meets the final singleton-layer edge of label n-1,
and the boundary from n-2 to n-1 meets the first edge of that
next-to-full layer, also of label n-1. These give the other two.
No further adjacent boundary pair has equal labels. This can also be
seen from the extremal-neighbor formulas: the predecessor of the last
k-subset replaces pi_(n-k) by pi_(n-k-1); the successor of the first
k-subset replaces pi_(k-1) by pi_k.

Every mixed-label boundary triple involves label n-1; any triple
incident to either exceptional label-3 boundary is diagonal on its
interior side and has label n-1 on its other side. Complement-reversal
preserves the boundary class and negates all its mixed products.
Therefore boundary off-diagonal sums are zero, and boundary D=4.
The n=4 case is checked directly by the displayed 16-vertex certificate.

Finally the graph has one positive edge, so E_*=W=2^(n-3), attained
with equal spins at coordinates 1 and 2. The audited identity
C_min=(2^n+D-E_*)/2 gives 2^(n-1)+2. The positive scan itself attains
this value. The endpoint identity for the unique least magnitude
gives the stated linear counts.

## 3. Executable checks and pressure context

verify_arbitrary_secondary_energy.py independently sorts actual integer
scores, checks every graph contribution and its interior/boundary
classification, verifies the exact predicted graph for n=4,...,18,
and independently sorts all reflections through n=9. In larger
dimensions it checks an attaining reflection and graph prediction.
These finite checks stress the proof; the general proof is Section 2.

probe_cardinality_interior_lift.py retains the discovery route.
Its first core arose at n=4 after all 6 binary-priority permutations
at n=3 and the first 10 at n=4. This is not a minimality claim over
arbitrary real secondary weights.

probe_arbitrary_coherent_secondary.py retains the preceding pressure
with seed 202610030812, dimensions 6,8,...,18, primary ones and k3,
four draws of each of three modes. It tested 168 genuine generic
integer magnitudes and optimized every sign orbit exactly by a
Gray-code spin traversal, cross-checked with the inherited optimizer
through n=12. All optimizers were realized by independently sorted
signed integer scans. There were 75 cases E_*>2q, but none below
half density. Those sampled magnitudes give no chamber completeness
or all-dimensional half-density theorem.

The valuable remaining gap is E_*-D, not E_* alone. One promising
restricted conjecture is that every cardinality-first coherent
secondary scan has E_*<=D+O(n); neither this proof nor the pressure
proves it. For general magnitudes the main target still requires
E_*-D <= (1-epsilon)*2^n for some uniform epsilon>0, or a different
prefix-separable family avoiding this Gray-specific route.
