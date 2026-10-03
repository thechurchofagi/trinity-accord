# Random coordinate choices do not remove the coherent-prefix tail

Date: 2026-10-03. Research draft and excluded proof route.
The main M_n >= c 2^n target is OPEN. This note extends the recorded
fixed-hierarchy tail obstruction to a precisely specified larger tree
distribution. It does not exclude existence of exceptional good trees.

## 1. Coordinate-adaptive prefix-separable trees

At a node corresponding to a face with m free coordinates, choose a free
coordinate uniformly, independently of other nodes conditional on their
faces. Independently choose a fair sign that determines which child is
traversed first. Repeat to single vertices. Different branches may choose
different coordinate hierarchies. Each path still splits every coordinate
once, and every node has two children of equal size.

Every resulting traversal rank is prefix-separable. If z is the first
excluded vertex of a prefix, let j_l and xi_l be the coordinate and sign
on its path at depth l, for l=0,...,n-1. Set

\[
 L_z(x)=\sum_{\ell=0}^{n-1}
       3^{n-1-\ell}\xi_\ell(x_{j_\ell}-z_{j_\ell}).
\]

The first path coordinate at which x differs from z is their common
splitting node. Its term dominates the sum of all later terms, irrespective
of which coordinates the other branch subsequently selects. Consequently
L_z(x)<0 exactly for vertices earlier than z, and L_z(z)=0; the integer
threshold -1/2 separates the prefix strictly. This is the existing tree
separator argument extended to path-dependent coordinate choices.
Neither decision trees nor that dominance method are claimed as new.

## 2. Exact obstruction for the unconditioned distribution

**Theorem.** Fix 1<=d<=n. Put k=2^d, N=2^n, and split vertices as (z,y),
with z the top d coordinates and y the remaining n-d. The fixed positive
integer weight vector

    w_j=k*2^j       for 0<=j<n-d,
    w_(n-d+h)=2^h  for 0<=h<d

has score ky+z and is generic. For the distribution above,

\[
 \Pr\{R(\rho\circ\pi_w)=2^{n-d+1}-1\}
 \ \ge\
 P_{n,d}:=\prod_{\ell=0}^{d-1}
          [2(n-\ell)]^{-2^\ell}
 \ \ge\ (2n)^{-(2^d-1)}.
\]

**Proof.** Impose the following event on the first d tree levels:
at every depth l node choose coordinate n-1-l and orientation +.
There are 2^l such nodes and n-l eligible coordinates at each one.
Conditioning on previous prescribed levels leaves independent uniform
choices and fair signs, so the event has exactly probability P_(n,d).
All descendants below these levels are unrestricted, including their
coordinate choices, signs, and ranks.

On this event each z-face occupies the rank interval
[z*2^(n-d),(z+1)*2^(n-d)-1]. The genuine sweep visits z=0,...,k-1 for
each y=0,...,2^(n-d)-1. Every within-row comparison is positive and every
inter-row comparison negative, independently of the unrestricted ranks
inside each face. The sign word has exactly 2*2^(n-d)-1 runs (including
the n=d case of one row). This proves the event inclusion. The final
bound uses 2(n-l)<=2n and sum_l 2^l=2^d-1. End of proof.

Fix any c>0 and choose d with 2^(1-d)<c. For all n>=d the exhibited run
count is below cN. Yet P_(n,d) has negative logarithm at most
(2^d-1) log(2n). Thus this UNCONDITIONED adaptive-tree model cannot have
any uniform fixed-sweep bound of the form exp(-a n^alpha), a,alpha>0,
at threshold cN, let alone exp(-aN). A direct union bound requiring an
exp(-Theta(n^2)) tail cannot be justified by merely randomizing the
coordinate choice in the old construction.

Unlike the fixed-hierarchy example, this lower probability tends to zero
for fixed d. It does NOT prove that this adaptive model cannot succeed
with high probability. It also does not prove that all methods based on
this model lose n^2: structural sweep classes, conditioning, and a
different nonuniform union argument remain possible.

## 3. Exact verifier and next route

verify_adaptive_tree_tail.py enumerates every coordinate/sign configuration
in dimensions two and three, distinguishing configurations from distinct
rank permutations. The distribution gives each configuration equal
probability at a fixed dimension. The event probabilities are checked
as rational numbers, not estimated.

At n=4,...,12 it samples unrestricted completions conditional on the
specified event with seed 202610030740, realizes the row scan by distinct
integer scores, checks the exact run count, and audits separators.
Every prefix and vertex is audited through n=8; only the recorded selected
prefixes are audited above n=8. This finite coverage pressure-tests the
analytic all-dimensional separator and event proof.

The new increment relative to NOTE.md is the explicit polynomial-probability
tail obstruction under path-dependent random coordinates. The old row
identity, known probabilistic tools, and tree representation are reused.
Targeted primary-source searches did not establish historical priority;
no novelty priority claim is made. The published paper and its source
references remain the baseline.

The precise next step is to forbid or quantitatively control shared small
coordinate sets at coarse tree levels, while preserving prefix separation
and auditing the changed distribution's independence. For actual Gray
scans, the alternative remains full translated-difference consistency,
not bounded-dimensional face agreement. The primary asymptotic theorem
has not improved in this note.
