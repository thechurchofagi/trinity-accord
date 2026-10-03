# Genuine row lifts preserve raw comparison support

Status: analytic all-dimensional quantifier reduction for the ORIGINAL
small-support proof obligation. The constant-density M_n target is OPEN.
This does not refute any genuine-additive lower bound. Published v1.0
is unchanged. Row sign-word identities and the low-input/high-score
construction were already used in earlier handoffs; their raw-support
invariance and the resulting quantifier reduction are the point audited
here, not a renamed claim of a new general permutation statistic.

## 1. Definitions and the genuine lift

Let m>=2, let v be ANY signed generic additive weight vector on Q_m,
and let p=(p_0,...,p_(M-1)), M=2^m, be its increasing score order.
Let rho be ANY paired-sibling rank, with either fixed root phase.
Non-top rank bit h is

    x_h XOR x_(h+1) XOR theta_h(x>>(h+2)).

Write q(p) for the number of DISTINCT NON-TOP labels

    (h,p_i>>(h+2)), h=highestbit(p_i XOR p_(i+1))<m-1,

in the RAW comparison word, before any graph cancellation.

For arbitrary d>=1, put n=m+d, T=2^d and choose L>sum_j |v_j|.
Place the OLD core in the HIGH input coordinates d,...,n-1. Give the NEW
LOW input coordinates weights L,2L,...,2^(d-1)L. Thus the new weight vector
is W=(L,2L,...,2^(d-1)L,v_0,...,v_(m-1)). These are genuine additive
weights; core signs need not be positive. Their order is EXACTLY

    P=((u<<d)|t : t=0,...,T-1, u in p).

Indeed a core row has score span sum|v|<L, so successive low assignments
have disjoint score intervals, and within each row the generic core order
is preserved. Thus the entire new order is generic in every dimension.

Extend the old high-input paired labels unchanged and choose ALL new
lower paired labels arbitrarily. Then

    floor(rho_new((u<<d)|t)/2^d)=rho(u)

for every u,t. In the repository's mask indexing, Q_m=2^(m-1),
Q_n=2^(n-1) and Delta=Q_n-Q_m; the full non-top mask is

    (core_mask<<Delta) OR arbitrary_mask_below_Delta.

This follows because the old level-h offset Q_m-2^(m-h-1) becomes
Q_n-2^(m-h-1) at new level d+h. Both root phases are inherited. Prefix
separability of every such extended paired rank is the existing audited
family theorem, not a condition inferred from the scan.

## 2. Exact raw-support invariance

Within each core row, an old leading bit h becomes d+h. The label prefix
is unchanged:

    ((u<<d)|t)>>(d+h+2)=u>>(h+2).

Every old comparison is replicated in every row, hence its DISTINCT
non-top support becomes precisely {(d+h,z):(h,z) in support(p)}.

There is no additional non-top support at row joins. The score-minimizing
core vertex has input bits 1 exactly at negative coordinates; the
score-maximizing vertex is its bitwise complement. They differ at the
core's top input bit, so EVERY join from old last to next old first has
leading bit n-1, whose root label is fixed and excluded from q. Therefore

    q(P)=q(p) EXACTLY.

This is raw support, not surviving Ising-graph edge support. In particular
q(P)/2^n tends to zero for EVERY fixed original core scan as d tends to
infinity. Small relative raw support contains lifts of all original core
scans, including whatever genuine hard scans might eventually be found.

## 3. Exact rank runs, independent of ALL new lower labels

Let a_i=sign(rho(p_(i+1))-rho(p_i)), let R be its run count, and set
j=sign(rho(p_0)-rho(p_(M-1))). Highest differing rank bits are in the
core, so the full comparison word is exactly

    a,j,a,j,...,j,a,

regardless of every new lower label. With

    beta=1[a_(M-2)!=j]+1[j!=a_0] in {0,1,2},

directly counting changes gives

    R_new=1+T*(R-1)+(T-1)*beta
         =T*(R-1+beta)+1-beta
         <=T*(R+1)-1.

The exact formula is an inherited elementary sign-word identity; the
new support result above tells us what it means for this proof route.

## 4. Quantifier reduction for the original-target small-support route

Suppose a>0, b>=0 are absolute and, for all sufficiently large n, EVERY
paired rank and EVERY actual generic additive scan satisfy

    R_new>=a*2^n-b*q(P).

Fix ANY m, ANY actual core scan p and ANY paired core rank rho, and apply
this assertion to the preceding lifts. Divide by T and let d tend to
infinity. Because q(P)=q(p) is fixed, this forces

    R-1+beta>=a*2^m, hence R>=a*2^m-1.

The conclusion holds for EVERY paired rank and EVERY actual core scan,
not merely for the existence of one good prefix-separable rank per m.
It is a substantially stronger quantifier than the primary M_n target.

Even the weaker-looking universal small-support assertion

    q(P)<delta*2^n ==> R_new>=a*2^n

for any fixed delta>0 and every paired rank implies the same conclusion:
every fixed core lift eventually falls below this support threshold.
Conversely a universal paired positive-density theorem trivially handles
small support. The possible additive -1 above is harmless asymptotically:
it implies density a/2 for all m with 2^m>=2/a. We do not claim exact
finite-dimensional equivalence of constants without this adjustment.

Thus the large-support entropy/small-support UNIVERSAL deterministic
split is a valid sufficient strategy, but its small-support branch does
not avoid proving a universal paired density theorem. This neither
invalidates the split nor refutes its remaining inequality, and it is
not an upper bound against M_n. No low-density genuine paired core is
exhibited here.

## 5. Exact executable stress test

Run python verify_raw_support_row_lift.py. It independently sorts all
integer scores, verifies full raw-label sets and leading-bit relabeling,
compares imported rank values against an independent MSB-first closed
formula, and checks the ENTIRE sign word and exact run identity.

Coverage: core dimensions 2..7; four generic mixed-sign core vectors per
dimension; all core masks through m=3 and four specified masks thereafter;
both root phases; d=1..5; three new lower-mask patterns (zero, all ones,
alternating). There are 208 core-rank-root contexts, 120 distinct lifted
actual weight orders and 3120 direct lifted rank audits. All beta values
0,1,2 occur. Finite pattern tests do NOT replace the analytic arbitrary-
lower-label proof. Zero violations, 8.419329936004942 seconds; audit digest
0cca1a0a373dd510ee576ac9d233ef49c4ce21c75982bbdbec79887f84a76371.
The gzip certificate expands to 1148170 bytes with SHA256
bb07c792829d39e49f558841ae8e5b75ea429c265e8f20b25d5efc2a404a3956.
Weights, core masks, roots, raw support sets, signs, beta, L, d, low-mask
patterns and whole order/rank-word digests are reproducible in the receipt.

## 6. Exact restart

Retain the universal small-support inequality as an unproved strong
sufficient obligation, not an easier established subcase. Next classify
the smallest raw-support scans using genuine common-addition constraints;
seek a mass bound from their comparison-word structure that is valid
without an unjustified scalar doubling induction. In parallel with this
conceptual choice (not additional agents), consider existential selection
that handles a hierarchically compressed family of small-support scans
without demanding success for EVERY paired orientation. Published v1.0
and all archived DOI bytes remain untouched.
