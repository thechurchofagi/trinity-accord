# Real additive scans have a linear joint path/cycle packing gap

Status: a strict all-dimensional counterexample to actual-scan joint
exactness and every additive O(n) repair of that equality. The main M_n
constant-density lower-bound problem remains OPEN. This example has large
D+K and is not a counterexample to any quarter/density bound. Published
v1.0 is unchanged. The existing paired-rank graph reduction and joint
packing inequality are inherited; the realizable gap family is the new
result. Signed cycle packing itself is established literature, not renamed
as an innovation.

## 1. Exact definitions and result

For a generic additive scan, the already audited paired-sibling rank family
has minimum runs

    1 + D + K + phi(G).

Here D counts forced same-label turns, K counts mixed-sign cancellations,
W is the full signed graph norm and phi(G)=(W-E_max)/2. Its complementary
half H has terminals a,r. A joint fractional packing assigns nonnegative
mass to simple a-r paths and simple negative cycles, with their COMBINED
edge load bounded by |J_e|. Write L(H)=max(P+2C). The inherited inequality
is L(H)<=phi(G); joint exactness asserted equality on every actual scan.

For EVERY n>=10 put m=n-10,T=2^m, and let

    b=(10480038,3358564,4427690,18199924,7393112,
       7711178,15108776,968084,2436896,16335859),
    A=1+sum(b),
    w_n=(A,2A,...,2^(m-1)A,b_0,...,b_9).

The new coordinates are LOW input-coordinate indices; the tail is empty
at n=10. These positive integer scores are generic. Exactly,

    D=338T, K=287T-2, W=112T+2;
    phi(G_n)=29T;
    L(H_n)=28T+1/2;
    phi(G_n)-L(H_n)=T-1/2=2^n/1024-1/2;
    min_theta runs(scan_w_n,rank_theta)=654T-1.

Thus even phi=L+O(n), uniformly over all generic scans, is FALSE. This is
an ACTUAL additive-capacity gap, unlike the modified-capacity diagnostic
in PAIRED_SIGNED_ODD_K5_OBSTRUCTION.md. None of these formulas is an
individual rank's RLC, since only one specified scan is minimized over
the rank family.

## 2. The finite signed core

At n=10, a=510,r=511. The half has these 36 integer signed edges:

    (448,496,1) (448,504,-1) (449,496,1) (449,510,1)
    (454,504,1) (454,511,-1) (460,499,1) (460,505,1)
    (462,499,1) (462,510,-1) (482,508,-1) (482,510,-1)
    (486,508,1) (486,510,1) (496,504,2) (496,508,1)
    (496,510,-2) (496,511,-1) (497,504,-3) (497,508,-2)
    (497,510,-1) (497,511,-4) (498,505,1) (498,508,-2)
    (498,510,1) (498,511,-4) (499,508,2) (499,510,1)
    (499,511,-1) (504,508,-2) (504,510,1) (505,508,-2)
    (505,510,-4) (505,511,-4) (508,510,1) (508,511,1).

The core has exactly 490 simple terminal paths and 2148 simple negative
cycles. They are independently re-enumerated in the verifier. Its joint
packing is 57/2, with retained rational primal and dual certificates.
Every load and every dual inequality is checked exactly; numerical LP
generation is not the proof of feasibility or optimality.

## 3. All-dimensional score and capacity proof

Use the existing support-lift theorem, whose boundary formula is also
audited directly here. Since A exceeds the entire core score span, the
score order is T consecutive complete core copies, indexed by the added
low-coordinate binary value. No scores within or between rows coincide.
Comparison labels shift by delta=2^(n-1)-512.

The cheapest core coordinate is index7. The first comparison label is
508 and the last is509. At every boundary between consecutive complete
copies the two new mixed turns contribute -1 to edge508-511 and +1 to
its complementary edge509-511. Consequently, after undoing label shift,

    H_T = T H_1 - (T-1) e_(508,511).

The boundary half edge stays POSITIVE with coefficient1; every other
coefficient is multiplied by T. Define H_0 to be H_1 with coefficient
508-511 replaced by0 (the zero edge is retained only for certificate
bookkeeping). Thus H_T=T H_0+e_(508,511), with norm56T+1.
All path/cycle signs in H_T are the same as in H_1.

The full signed norm is twice the half norm: W=112T+2. Same-label
forced turns are simply copied, D=338T. The identity

    2^n-2 = D+2K+W

then gives K=287T-2. This proves the raw/cancellation formulas without
extrapolating from finite tests.

## 4. Integer frustration certificate, valid for every T>=1

With r fixed positive, exhaustive INTEGER enumeration of the 16384
active free-spin assignments in H_0 gives these conditional optima:

| a spin | Maximum energy | Minimum frustration | One negative set |
|---|---|---|---|
| +1 | 34 | 11 | {482,497,498,505} |
| -1 | 20 | 18 | {497,498,505,510} |

Every assignment has H_0 frustration at least11 or18 for its root sign.
The displayed optimizers both satisfy the positive boundary edge508-511.
For H_T, the frustration of any assignment is T times its H_0 cost,
plus either0 or1 for that edge. Hence the conditional frustrations are
EXACTLY 11T and18T for every T>=1. The complementary two-copy reduction
therefore gives phi(G_n)=11T+18T=29T.

To construct an attaining full rank, mirror the negative-root half
assignment AND negate all its non-top spins. This restores the shared
root spin and compensates for the reversed top-incident couplings in
the complementary half. Mere mirroring is insufficient. The verifier
checks the explicit full energy54T+2 and directly counts runs through
n=12. Every paired-family rank remains prefix-separable by the existing
3^h separator proof; no new rank admissibility assumption is inserted.

## 5. Fractional joint certificate, valid for every T>=1

The retained H_1 primal packing has value57/2. The retained H_0 primal
packing has value28 and uses ZERO mass on edge508-511. Combining the
first packing with (T-1) times the second gives a valid H_T packing:
each edge load is bounded by |H_1|+(T-1)|H_0|=|H_T|. Its value is

    57/2 + 28(T-1) = 28T+1/2.

The H_1 dual assigns nonnegative edge lengths; EVERY terminal path has
length>=1 and EVERY negative cycle length>=2. Its length on508-511 is
1/2 and its H_0 capacity cost is28. Since H_T has unchanged signed
support, that SAME dual is feasible at every T and costs28T+1/2.
Matching rational primal and dual prove the displayed optimum. The
certificate includes every rational mass, length, combined edge load,
and the affine slope/intercept of each packed path/cycle. No solver
or finite extrapolation is required for the all-dimensional step.

## 6. Search coverage, independent audit and failures

probe_paired_odd_k5_actual_walls.py visits EVERY generic open interval
in each of the ten one-coordinate +/-5% windows around the preceding
Q10 signed-minor seed. It does not cover all ten-dimensional chambers.
It completed2280 intervals,2212 unique signed capacity graphs:1730 exact
rational LP optima,68 cached identical graphs,482 explicit enumeration
limits. Five REAL exactness-gap graphs were found, each with gap1/2.
No enumeration-limited graph is classified as exact or gap-free.
Time368.4331102149881s; digest
5c33cc57f260ce6a4b1adf26114d443e4c2f603b9df53612187b58bc339b4286.
The lossless gzip report is699451 bytes, decompressing to20280587 bytes,
SHA256244a824316815f5794da3cb1a2ed7bf69284a05bcac58d5ff38df5e25198711b.

prepare_paired_actual_joint_gap_certificates.py reselects the specified
second gap and generates exact checked rational candidates for H_0.
verify_paired_actual_joint_gap.py uses an INDEPENDENT iterative path/cycle
enumerator, integer spin exhaustion rather than ancestor DP, independent
raw-turn counts, all rational inequalities, and actual generic scans for
n=10,...,18. Zero final violations;1.064471698991838s; digest
63d8aa8d8e4609963cfb5de860d433ee4cc04e4d1af61869b58663d8120a3403.
This finite audit supports the affine proof above; it is not its scope.

An initial verifier compared a list with a tuple; this reporting assertion
was normalized. A second failure caught a WRONG explicit attaining mask:
mirroring without negating complementary non-top spins. Its traceback
is retained in paired_actual_joint_gap_attaining_mask_failure.txt; the
corrected mask now passes exact energy and direct rank/run checks. The
failure did not affect independently computed frustration or LP values.

## 7. Consequence and next precise gap

Universal joint exactness and every uniform additive O(n) correction are
excluded by a realizable all-dimensional family. However this family has

    D+K+L(H)=653T-3/2 >> 2^n/4=256T.

Thus the weaker positive-density joint-certificate conjecture survives.
The next target is a QUANTITATIVE certificate under actual scan constraints,
not exactness. An immediate necessary realizability constraint is a local
ancestor incident-load bound: variable theta_(h,p) has at most2^(h+2)
raw mixed turns with higher-coordinate ancestors, since each charges a
distinct middle vertex in its prefix subcube. Therefore its total NET
ancestor coupling magnitude is at most2^(h+2). Formalize and audit this
bound, then use it together with D,K and compatible cycles to constrain
near-zero density scans. Do not replace an all-scan proof by this example.
