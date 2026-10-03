# Uniform density for signed and permuted binary secondary priorities

Status: an analytic ALL-dimensions/all-permutations/all-secondary-signs
scan-class theorem. Main all-weight M_n constant density remains OPEN.
Published v1.0 is preserved. Known tree ranks, Gray transforms, signed
input-reflection closure and standard window capacities are inherited.
The claim here is a new audited sufficient-class bound in this research
continuation, not a literature-priority claim for a new order concept.

## 1. Statement and quantifiers

Let n>=5, lambda>0, pi ANY permutation of{0,...,n-1}, and epsilon_j ANY
signs. Set

    b_j=lambda*epsilon_j*2^(pi(j)), B>2*sum_j abs(b_j),
    w_j=B+b_j.

Then the genuine generic additive scan with actual positive weights w
has, for EVERY paired rank rho_theta and either root phase,

    R(rho_theta along this scan) >= 1+ceil(2^n/128).

The bound holds simultaneously for EVERY pi, EVERY secondary sign vector,
EVERY admissible B and lambda, and EVERY dimension n>=5. This is not a
finite permutation audit extrapolated to n. It is still a RESTRICTED
scan class: binary secondary magnitudes with a dominant cardinality
primary. Thus it is NOT a lower bound for RLC over ALL generic additive
scans and does NOT remove the published general n-squared denominator.

The inherited signed-input-reflection closure also extends the same
statement to arbitrary signs of the ACTUAL weights, sigma_j*w_j.
Actual signs and secondary signs are different quantifiers.

## 2. A controller may lie outside the low-priority coordinates

Select the FIVE input coordinates with smallest secondary magnitudes,
namely lambda*(1,2,4,8,16). Sort their INPUT positions as

    t0<t1<t2<t3<t4.

Use k=t4 as the high INPUT atom. Among b_(t0),b_(t1),b_(t2), at least
two lie on the same side of b_k. Choose such a pair with INPUT positions
i<j. This elementary pigeonhole statement uses the actual values, not
the secondary-priority order. Thus b_k, and equivalently w_k, is extreme
among the three chosen atoms.

Since j<=t2 and there are still t3,t4 above it,

    k>=j+2.

The required adjacent controller is c=j+1. It is none of the three atoms.
It need NOT be one of the five smallest-magnitude coordinates. Include
it in the free set

    C={t0,t1,t2,t3,t4} union{c}, |C|<=6.

This is why the proof works for arbitrary coordinate permutations;
assuming a convenient lowest contiguous input block would be incorrect.
Unused free coordinates are fixed0 in each witness, not varied as if
they were additional independent obligations.

The score diameter D of the three atomic weights equals their secondary
diameter, since the primary B cancels. Among signed magnitudes1,2,4,8,16,
the largest possible range is24lambda: at most one magnitude16 occurs,
so the opposite-sign endpoint has magnitude at most8. Therefore

    D<=24lambda.

## 3. Outside score gaps are uniformly larger than D

Every coordinate outside C has secondary magnitude at least32lambda.
For two outside subsets with EQUAL cardinality, their actual score
difference is a nonzero multiple of32lambda. It is nonzero because
signed binary subset scores are unique: the highest differing power
strictly exceeds the sum of all smaller powers. Therefore the absolute
difference is at least32lambda.

For two outside subsets with DIFFERENT cardinalities, the primary
difference has magnitude at least B. Their secondary difference has
magnitude at most sum_outside abs(b_j), because every coefficient in
the difference is0 or+/-1. Thus their actual score difference is at least

    B-sum_outside abs(b_j) > sum_all abs(b_j).

If outside coordinates exist then n>=6, and sum_all abs(b_j)>=63lambda,
so this is strictly greater than32lambda. For n=5 there are no outside
coordinates and the gap condition is vacuous. The argument also covers
an empty outside set in higher dimensions.

Consequently the outside subset-score gap is at least32lambda>D for
EVERY permitted sign vector and secondary priority permutation.

## 4. Exact half-weight certificate and density

For every outside assignment f with score s_f, order its single-atom
triple(e_i,e_j,e_k) by actual score, and toggle the common controller c.
The two highest changed input bits are j,k. The paired comparison with
leading bit j reverses; the one with leading bit k stays unchanged.
Hence one of the two triples forces a full-scan turn for EVERY paired
orientation. This is the previously proved noncontiguous translation
identity; neither BRGC inverse ranking nor an incorrect face-complement
recursion is substituted.

The two score windows of each witness have width D. Original windows
for different f are disjoint by the outside gap, and translated windows
are separately disjoint. A turn position therefore belongs to at most
TWO witness unions. Exact mass1/2 per witness is a feasible fractional
turn-position packing. There are

    F=2^(n-|C|) >= 2^(n-6)

witnesses. Summing the pointwise turn obligations gives

    R >= 1+ceil(F/2) >= 1+ceil(2^(n-7)).

This is the stated1/128 density. If the controller is already among the
five low-priority coordinates, |C|=5 and the certificate itself yields
the stronger1+ceil(2^(n-6)); no uniform1/64 bound is asserted without
that additional condition. Cross-phase score-window disjointness is
not assumed and can fail; the two-load certificate handles that conflict.

Full genericity follows separately: equal-cardinality scores have unique
signed binary secondary scores, while different cardinalities are
strictly separated by B>2sum|b|. Prefix separability of EVERY paired rank
uses the existing all-dimensional paired-rank separator lemma, not a
new separability claim derived from the scan weights.

## 5. Actual signed weights and robustness

For actual signs sigma define d_j=1 exactly when sigma_j=-1 and reflect
input y=x XORd. The signed scan is the positive w scan in y, up to an
irrelevant constant. For paired rank bits

    rho_j(x)=x_j XOR x_(j+1) XOR theta_j(x>>(j+2)),

input reflection gives another paired rank with

    theta'_j(z)=theta_j(z XOR(d>>(j+2))) XOR d_j XOR d_(j+1),

and root phase toggled by d_(n-1). Thus the same bound applies to every
paired rank on the actual signed scan. This existing closure property
is written out to distinguish actual signed weights from signed secondary
coefficients. It does not add a new reflection technique.

Baseline positive scan gaps are at least lambda: within cardinalities
they are nonzero integer multiples of lambda, and between cardinalities
the primary margin is much larger. Hence any perturbation of the entire
actual weight vector with l1 norm<lambda preserves the complete order
and the same bound. The theorem also covers these open neighborhoods;
it does not cover all real secondary metrics by continuity.

## 6. Executable audit and limits

verify_permuted_signed_binary_cardinality_windows.py checks88 positive
generic actual scans Q5..Q15,88 independently sorted reflected actual
signed scans, and704 directly read paired rank words. Every certificate
checks the selected INPUT atoms/controller, the five low-magnitude
coordinates, actual outside gap>=32, atomic diameter<=24, complete order,
all interval-support loads<=2 and exact half-weight objective. There are
39 cases needing SIX free coordinates. A specified negative control
spreads the low-priority coordinates across positions0,2,4,6,8, forcing
controllers outside the five; these healthy cases must not be rejected
for lack of a contiguous low-input block.

All parameters, actual positive and signed weights, reflection masks,
free sets, gaps, capacities and support digests are retained in the
certificate and run log. The analytic proof above justifies ALL pi,
epsilon and n; the finite audit only pressure-tests its critical steps.
No ancestor optimization or random success is treated as a general proof.

The next precise gap is general secondary geometry: remove the power-of-two
outside gap while retaining a constant-size sparse cylinder or a global
capacity-compatible packing. Generic real secondary coefficients can
have very small outside subset-score gaps, so the binary-grid argument
cannot be reused without a replacement. Seek a strict obstruction to
constant-size same-phase separation before proposing it as universal.
The main M_n existence target and the stronger all-paired/all-scans
quarter-density conjecture remain separate OPEN questions.
