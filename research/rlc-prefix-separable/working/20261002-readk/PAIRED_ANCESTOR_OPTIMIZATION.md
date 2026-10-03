# Exact ancestor structure of paired-sibling scan graphs

Date: 2026-10-03. Unpublished structural lemma and exact audit tool.
Main M_n constant density remains OPEN. The paired rank family is from
PAIRED_SIBLING_RANKS.md; tree-depth and ancestor-conditioned dynamic
programming are known methods, not claimed as new general algorithms.

## 1. Couplings always join comparable prefix nodes

For any leaf permutation p, let h be the highest input coordinate that
changes along a consecutive comparison. Its sign under a paired rank is
the forward-Gray comparison sign times the spin

    theta_(h, x>>(h+2)), if h<n-1,
    theta_top, if h=n-1.

The higher prefix is shared by the two endpoints. For a turn triple
(x,y,z), suppose its two highest changed coordinates satisfy h<k<n-1.
Both comparison labels may be computed from the common middle vertex y:

    prefix_h=y>>(h+2), prefix_k=y>>(k+2),
    prefix_k=prefix_h>>(k-h).

Thus the k-variable is an ancestor of the h-variable in the binary
prefix tree. Its depth is d=n-h-2; nodes at depth d have prefixes
0,...,2^d-1. The theta_top variable is an extra ancestor of the root.
Every nonzero coupling joins comparable nodes, for EVERY permutation.
The graph therefore has a known elimination forest of depth at most n.

If h=k, the variables coincide and the two comparison signs are
opposite: the middle vertex's bit h differs from both outer vertices.
These are forced turns counted in D. The usual graph bookkeeping gives

    R_min=1+(N-2+D-E_max)/2=1+D+K+phi,
    K=(N-2-D-W)/2, phi=(W-E_max)/2.

Fix theta_top=+1 without loss: negating every spin reverses all rank
comparisons but leaves each product and the run count unchanged.

## 2. Exact dynamic program

For node u at depth d, condition on the spins s_0,...,s_(d-1) on its
ancestor path. Let F_u(s) be the maximum energy contributed by all edges
whose deeper endpoint lies in the subtree of u. For t in {-1,+1},

    F_u(s)=max_t [
        t*(J_(u,top)+sum_(ancestor a) J_(u,a)*s_a)
        + F_child0(s,t) + F_child1(s,t)].

At a leaf omit the child terms. No edge joins incomparable subtrees, so
conditioning on the ancestors makes the children independent. Each edge
is counted once, at its deeper endpoint. Bottom-up induction proves the
recurrence and gives the exact maximum energy at the root. Retain the
maximizing t in every table cell to reconstruct an attaining rank mask.

There are 2^d nodes and 2^d ancestor assignments at depth d. The exact
number of table states, excluding the fixed top, is

    sum_(d=0)^(n-2) 4^d = (4^(n-1)-1)/3 = (N^2/4-1)/3.

Computing the ancestor field uses at most n arithmetic operations per
state. Thus optimization takes O(n*N^2) integer operations and O(N^2)
table storage, rather than enumerating 2^(N/2-1) masks. This is an
application of established tree-depth DP to the proved cube-prefix
embedding. It is not a general new Max-Cut algorithm.

The executable optimizer uses only exact int64 array arithmetic, checks
sum|J|<2^62 to prevent overflow, verifies every ancestral edge, and
independently recomputes the energy of the recovered mask. It includes a
separate standard-library recursive implementation using explicit spin
tuples; the finite verifier also independently enumerates every small
mask and computes actual integer rank comparisons.

## 3. Audit and exact pressure

The verifier checks 54 arbitrary permutations through n=5 against both
the independent recursion and exhaustive spin energies. Exact negative
controls use the order sorted by forward Gray rank through n=8: their
minimum is one run, despite their perfectly ancestral graphs. Thus this
structural lemma alone cannot prove a quarter lower bound; genuine
additive translation consistency remains necessary.

It also checks 322 genuine additive scans exactly: the saved larger
cardinality cores with numerical tails, every three-coordinate fast
face through n=9, and fresh seeded weight proposals through n=12. These
are new optimizer/structured-scope audits, not reruns of completed Q4
chamber classification. The source seed is 202610030951. No quarter
counterexample appeared, but the scanned weight chambers are not
classified and absence of a counterexample is not a lower-bound proof.

For every listed scan the certificate stores the graph, D,K, exact E,
exact frustration, a recovered rank mask, independently counted actual
runs and a digest of all conditional tables. Zero optimizer violations;
elapsed 4.247 seconds; digest
99ba8cf16c731dbc9f6c0ed704ae2e3939cc801cc797b06a6c941000424430e7.

## 4. Immediate next analytic gap

The pressure suggests a larger restricted theorem, not yet the arbitrary
weight theorem: every signed lexicographic scan in ANY coordinate
significance order may have D+K>=N/4. Prove it using its consecutive
four-vertex blocks and the two fastest coordinates j,k. If j>k, their
highest changed label repeats and forces turns. If k=j+1, the sibling
constraint pairs opposite products within each block. If k>j+1, pair
blocks by reflecting the slower controller j+1. Their mixed products
negate while their variable labels are unchanged. Verify all cases and
retain exact cancellation pairs. This would extend the saved natural
top-face row result, while still leaving interleaved subset-sum scans
outside the proof.

Literature context: the ancestor-forest definition and standard
tree-depth algorithmic framework are described, for example, in
Fomin, Fraigniaud, Montealegre, Rapaport and Todinca,
Distributed Model Checking on Graphs of Bounded Treedepth,
Algorithmica 88:10 (2026; online 24 November 2025),
https://doi.org/10.1007/s00453-025-01349-1,
and in the primary paper Width, Depth, and Space: Tradeoffs between
Branching and Dynamic Programming, Algorithms 11(7):98 (2018),
https://doi.org/10.3390/a11070098. The exact prefix embedding and
displayed recurrence are proved here directly; no priority claim about
the underlying algorithmic methods is made.
