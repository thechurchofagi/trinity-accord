# Sharp zero/one raw support and universal segment bounds

Status: all-dimensional analytic partial progress on the ORIGINAL
small-support obligation. General growing q and M_n>=c*2^n remain OPEN.
Published v1.0 is unchanged. Binary-trie monotone accounting, antipodal
score symmetry and Ising run identities are inherited standard tools;
the precise application to raw support and q=0,1 is audited here.

## 1. Every permutation: a monotonic segment uses each label at most twice

Use the existing paired rank and raw labels (h,x>>(h+2)), excluding the
fixed top root. Let p be ANY vertex permutation, q its distinct non-top
raw label count, and N=2^n. No additive assumption is needed in this part.

In a strictly increasing rank segment, a highest differing rank bit h
crosses from 0 to1 within the interval determined by the common rank
prefix ABOVE h. Such a binary-trie node is crossed at most once: after
leaving its interval the increasing sequence cannot return. Decreasing
segments satisfy the same statement with directions reversed.

For the triangular paired rank, input prefix ABOVE h determines rank
prefix ABOVE h bijectively. A raw label (h,z) fixes input bits ABOVE h+1,
and leaves its controller input bit h+1 either0 or1. It therefore
corresponds to exactly TWO binary-trie nodes, one for each controller
value; it can occur as the leading comparison at most twice in one
monotonic segment. The root corresponds to only ONE node and occurs at
most once. Consequently every run has at most 2q+1 comparisons, and

    R(rho composed with p)>=ceil((N-1)/(2q+1)).

This is a quantitative application of elementary trie counting, not a
claim that trie statistics or run terminology are newly invented. It
handles bounded q uniformly, but becomes o(N) when q grows and is NOT
the missing inequality R>=a*N-b*q.

## 2. Actual scans: complementary-prefix support and couplings

Every generic signed additive order is centrally symmetric:

    p_(N-1-i)=p_i XOR (N-1).

Indeed complementary scores sum to the same total weight and all scores
are distinct. This holds with arbitrary coordinate signs. Thus mirror
comparisons map a non-top raw label (h,z) to

    C(h,z)=(h,z XOR (2^(n-h-2)-1)).

The top label is fixed. The ENTIRE raw support is C-invariant. The only
non-top C-fixed label is (n-2,0); all lower labels come in distinct pairs.

For graph coefficients use the natural forward Gray baseline
g(x)=x XOR(x>>1), NOT the BRGC inverse. Complementing x flips only its
top Gray bit. Because mirroring also reverses comparison order, its
baseline sign is preserved at top comparisons and negated at non-top
comparisons. Let kappa_root=+1, kappa_non-top=-1. Mirroring two adjacent
comparisons therefore gives the exact signed-coupling relation

    J_(C(a),C(b))=kappa_a*kappa_b*J_(a,b).

Here J is the sum of baseline adjacent sign products over unordered
DISTINCT raw-label pairs. Same-label neighbors always turn and are
counted in D. A triple mirror has index N-3-i; since N is even, there
is no self-mirrored triple. The relation also follows by summing mirrored
contributions and is valid for any centrally symmetric permutation.

In particular root and the label (n-2,0) are both C-fixed, while their
kappa product is -1. Their coupling is exactly zero in every actual
scan, regardless of n or the other weights. Also labels at the SAME h
but different prefixes cannot be adjacent in the comparison word:
both comparisons share a middle vertex whose prefix would have to be
both different fixed prefixes. This is an exact structural zero.

## 3. Sharp all-dimensional q=0 and q=1 classification

If q=0, every comparison is top. The input top bit flips at every step;
the corresponding rank sign alternates, independently of all paired
labels. Thus R=N-1 EXACTLY.

If q=1, C-invariance forces its unique non-top label to be (n-2,0).
There is only one possible off-diagonal coupling, from it to the root;
the preceding involution cancels that coupling exactly. Thus the run
count is independent of EVERY paired orientation. The inherited exact
sign-graph identity is

    R=(N+D-E)/2,

where E sums J_ab times the chosen label spins. Here E=0, giving

    R=(N+D)/2>=N/2.

D is consequently even. This is an all-dimensional theorem for all
generic signed scans with q=1, not an extrapolation from enumeration.

Both bounds are sharp in EVERY dimension. For q=0, use weights
(2,4,...,2^(n-1),1), where the last input coordinate is fastest. Its
vertices come in top-flipping pairs, with top-flipping pair joins, so
q=0 and R=N-1. For q=1 and n>=2, use weights
(4,8,...,2^(n-1),1,2), with n-2 initial weights, interpreted as (1,2)
when n=2. The low-input/high-score lift of the two-dimensional core
has raw q=1. Its core R=2 and beta=1 for both core labels and both
root phases, hence the exact row identity gives R=N/2 regardless of
ALL new lower labels. The weights are a permutation of binary powers
and are generic integers.

## 4. Exact audit and retained scope

Run python verify_tiny_raw_support_structure.py. It checks all 40344
arbitrary vertex permutations on Q2,Q3 against ALL paired masks and both
roots, 645216 direct rank words. At every monotonic segment it audits
the per-label multiplicity2 and root multiplicity1, not just the final
run inequality. This exhaustiveness is finite pressure evidence; the
all-dimensional result is proved above. Permutation digest:
4f3b2b0029230a87774e5136bb25035a6cf9cdc925ddbb009c74fee0fd47b48e.

It checks 5480 actual signed chamber representatives on Q2..Q4 from the
existing small-chamber enumerator, plus96 generic signed scans Q5..Q12,
and144 sharp mask/root contexts through Q13. All raw support involutions,
coupling relations, forbidden same-level pairs and q=0,1 identities are
audited exactly. The representative coverage is inherited from that
enumerator; no new chamber completeness claim is based on random scans.
The ordinary scan cases use one specified mask each; the ALL-orientation
claim for q=0,1 follows from complete coupling cancellation, not from
pretending every large-dimensional mask was enumerated.

Zero violations, 5.122911365993787 seconds; audit SHA256
811d9d3af25a9f2b5d7f0cc39ca1a1e53d38467cffda23ec1f352d7f30c98b73.
Gzip expands to3113167 bytes, SHA256
e30b9ab1dde51694348bb5665ae4337772cea6bfe22930f86f643393f848abd0.
Weights, masks, roots, supports, D, graph couplings and runs are retained.

## 5. Next precise gap

For q=2 the active labels form ONE complementary-prefix pair at the same
level h<=n-3. Root-to-pair couplings are opposite; pair-to-pair coupling
is structurally zero. Unlike q=1, these two root couplings can be nonzero,
so q=1 cancellation cannot simply be repeated. Determine their exact
genuine-scan mass bound and whether a structural compression yields a
uniform density at q=2 and beyond. Do not promote bounded-q results or
the universal N/(2q+1) estimate to the intermediate-support theorem.
