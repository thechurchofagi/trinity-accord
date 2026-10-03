# Actual additive capacities have a joint packing gap in every n>=9

Status: an exact counterexample to universal ACTUAL-CAPACITY joint packing
exactness, with an analytic all-dimensional extension. The constant-density
M_n target remains OPEN. This is not a counterexample to a positive-density
run or packing bound. Published TA-TR-2026-22 v1.0 is unchanged.

## 1. The new distinction

Concurrent commit 50072f8d3591a0885cf359cfd2efbadbe5bd7111 already supplies
real signed odd-K5 supports and gaps for MODIFIED capacities, while its
actual scan packing remains exact. PAIRED_SIGNED_K5_AND_FULL_PACKING.md
adds a compact nine-coordinate support obstruction, an exact original
capacity lift, and proves the unconditional fractional reduction

    max compatible half (P+2C) = full fractional negative-cycle packing.

Concurrent commit e57c2bfd08ac482550cc0ec06940e95128fd7afb,
PAIRED_REAL_JOINT_PACKING_GAP.md, has now independently established a REAL
all-dimensional gap from a ten-coordinate seed, of size 2^n/1024-1/2.
That route exclusion is credited there, not reclaimed here. The present
independent increment is a smaller nine-coordinate seed, a gap
2^n/512-1/2, compact explicit affine certificates, and the general
half/full fractional packing reduction in the companion note. No least
dimension or largest possible gap is claimed. All capacities below are
the exact comparison counts of genuine scans, not freely selected weights.

The inherited paired-sibling identities used here are
R_min=1+D+K+phi and E_full=F_++F_- for the complementary half, with r fixed
positive and a fixed respectively positive/negative. These do not compute
M_n or a single rank's RLC over all scan weights.

## 2. The genuine nine-coordinate counterexample

Use the positive integer coefficients

    v=(432,492,488,884,496,1284,9,1202,256).

All 512 subset scores are distinct, with minimum consecutive gap one.
The complete graph is built from this EXACT order, not a proposed support.
Its raw terms are D=56,K=184,W=86. The half has a=254,r=255, norm 43,
16 active vertices and 32 edges, saved explicitly in the certificate.

Its conditioned half energies are F_+=21,F_-=19. Therefore E_full=40,
phi=(86-40)/2=23 and the rank-family minimum is 264. All 147 simple a-r
paths and all 437 negative simple cycles are independently enumerated.
A rational primal and dual match at

    max(P+2C)=45/2=22.5 < phi=23.

Every capacity constraint and ALL 584 dual inequalities are checked with
Fraction arithmetic. The LP solver only supplied candidate masses; the
independent final verifier calls no LP solver. It also checks two separate
integer ancestor optimizers and exhaustively verifies the finite boundary
energy table used below. Thus the exact half-unit gap is certified without
floating tolerances or an incomplete cycle search.

## 3. Exact one-coefficient wall search and its limits

Start from w=(216,246,244,442,248,642,6,601,128) and vary ONLY coordinate 6
in the open range (0,128), fixing the other eight coefficients. Their 256
subset sums are distinct. Two full scores can change order only at a
positive difference of those fixed subset sums. List every such difference
in (0,128), adjoining endpoints 0 and 128; this yields 124 genuine open
intervals. Use their exact rational midpoints, multiplying all coefficients
by two. Every midpoint is strictly generic. Every graph signature in this
slice is distinct.

110 intervals yielded fully certified rational joint LP optima; 14 hit
the explicit enumeration limit and certify no LP optimum. Among the
completed cases, interval (4,5) yields the gap above, at coefficient 4.5
before scaling. This is exhaustive ORDER-INTERVAL coverage only for this
one bounded coefficient slice, not a complete Q9 chamber classification
or complete LP coverage. It is no assertion about the skipped 14 cases.

probe_paired_coordinate6_walls.py regenerates the audit. The completed run
took 13.765806865005288 seconds. Its exact original report is losslessly
stored as paired_signed_k5_coordinate6_wall_audit.json.gz.base64: base64
decode, then gzip decompress. The result is 954425 bytes, SHA256
ba7b8baa00c94d83fbc020856bc42a40f03cb1ac872133e8297236eca708faff.
The archive round trip was checked; the original run output is retained.

## 4. A real scan in every higher dimension

For n=9+m, T=2^m and L=1+sum(v)=5544, use

    v_n=(L,2L,...,2^(m-1)*L,432,492,488,884,496,1284,9,1202,256).

The new coefficients occupy the m LOW input coordinates; their list is
empty at n=9. Row spacing L exceeds the old total range 5543. The actual
order is exactly T complete copies of the core, with vertex
(x<<m)|t for row t and core x. Every dimension is strictly generic.

By the previously proved low-tail formula, every active variable shifts
by delta=2^(n-1)-256 and

    J_n=T*J_9+(T-1)*B,
    B_(252,255)=-1, B_(253,255)=+1, other entries zero.

The least old coefficient is coordinate 6; the first/last comparison
labels are 252/253. These two increments reinforce the old signs.
The half H_n therefore has the SAME signed topology, with capacities

    cap(H_n)=T*cap(H_9)+(T-1)*1_(252,255).

Equivalently it is cap(H_9)+(T-1)*cap(H_infinity), where H_infinity has
the old capacities plus ONE extra unit on (252,255). All other edges
scale exactly. The complete raw quantities are

    D_n=56T, K_n=184T, W_n=88T-2.

## 5. Exact joint primal and dual for every T

The following half packing lists ALL its positive objects. Shift every
vertex by delta. Every displayed cycle is negative; path sign is unrestricted.
Every mass is nonnegative for T>=1.

| Object | Mass |
|---|---:|
| path (254,240,252,255) | T-1/2 |
| cycle (194,254,243,207,255) | T |
| cycle (199,252,255) | T |
| cycle (200,242,202,255,252) | T |
| cycle (201,242,203,255) | T |
| cycle (205,243,254) | T/2-1/4 |
| cycle (205,243,255) | T/2+1/4 |
| cycle (205,252,240,254) | T/2+1/4 |
| cycle (205,252,255) | T/2-1/4 |
| cycle (206,243,252) | T |
| cycle (240,252,241,254) | T |
| cycle (240,252,243,254) | T/2+1/4 |
| cycle (241,254,242,255) | T |
| cycle (242,252,255) | T |
| cycle (243,252,255) | T/2-1/4 |

Its total masses are P=T-1/2 and C=11T, hence objective 23T-1/2.
Capacity feasibility follows without an infinite enumeration. At T=1
the saved packing fits H_9. The coefficient of T in the table is another
feasible packing on H_infinity, with path mass one, integral cycle masses
one or half, and objective 23. Their sum, base+(T-1)*slope, fits
cap(H_9)+(T-1)*cap(H_infinity) for every T>=1. Both finite load checks
are exact and include their COMBINED path and cycle loads.

For the matching dual assign the following lengths to half edges;
unlisted lengths are zero. Shift labels in higher dimensions.

| Length | Edges |
|---:|---|
| 3/2 | 199-252,203-242,241-252 |
| 1 | 194-254,200-242,205-243,205-252,206-243,241-255,242-252,243-252 |
| 1/2 | 201-242,202-242,205-254,205-255,207-243,240-252,242-254,242-255,243-254,243-255,252-255 |

Every simple terminal path has length at least one and every negative
cycle at least two; all 147/437 possibilities are checked exactly in the
fixed core. Higher lifts have exactly the same topology and signs, so
these inequalities remain valid. Its base cost is 45/2 and its length on
the sole changing half edge (252,255) is 1/2. Its cost in H_n is therefore

    T*(45/2)+(T-1)/2=23T-1/2.

Primal and dual match. Thus the exact joint fractional optimum is
23T-1/2 in EVERY dimension. By the general half/full reduction, this
also equals the full fractional negative-cycle packing optimum.

## 6. Exact integer frustration and the size of the gap

In the core fix r=+1, a=s and b=spin(252). Exhaustive integer enumeration
of the other thirteen active spins gives this entire boundary table:

| a spin | b=+1 | b=-1 |
|---|---:|---:|
| +1 | 19 | 21 |
| -1 | 19 | 17 |

The full actual core optimum 40 is independently checked by the existing
NumPy and standard-library ancestor optimizers. After lifting, only the
half edge (252,r) has a boundary increment. Consequently the exact
conditioned energies are

    F_+(T)=max(19T-(T-1),21T+(T-1))=22T-1;
    F_-(T)=max(19T-(T-1),17T+(T-1))=18T+1.

The inequalities hold for all T>=1. Complementary-half decomposition
then gives E_full(T)=40T and

    phi_n=(88T-2-40T)/2=24T-1.

An explicit attaining rank has negative spins on the shifted vertices

    {202,208,214,215,216,221,243,245,246,252,253},

and positive spins everywhere else. Its base energy is 40; the two new
boundary terms cancel since spins 252 and 253 are both negative and r
positive. Its energy is exactly 40T and its actual run count is 264T.

The resulting all-dimensional conclusions are

    phi_n=24T-1;
    joint/full fractional packing=23T-1/2;
    phi_n-packing=T-1/2=2^n/512-1/2 > 0;
    fixed-scan rank-family minimum=264T=(33/64)*2^n.

This is a genuine additive capacity gap of POSITIVE linear density,
not just a fixed half-unit discrepancy extrapolated from Q9. The gap's
proof uses the complete graph formula, an affine primal, a fixed dual
and the exact finite boundary table.

## 7. What is excluded and what remains open

The stronger hypothesis max(P+2C)=phi for EVERY actual generic score scan
is false, even after adding all possible simple terminal paths and all
negative cycles fractionally. Ordinary full fractional negative-cycle
packing has the same limitation. Graph support idealness and actual
capacity exactness are both unavailable as universal shortcuts.

The weaker quantitative target is NOT refuted. Here

    D_n+K_n+max(P+2C)=263T-1/2,

which remains far above the quarter budget 128T. The rank minimum itself
has density 33/64. The primary extremal M_n conjecture and a uniform
positive-density certificate bound over ALL generic weights remain OPEN.
An approximate packing bound or a different certificate could still
prove the desired density despite a systematic exactness gap.

The next proof work should pursue such a quantitative bound using genuine
additive restrictions. Do not continue trying to prove universal joint
exactness, and do not interpret this family as an upper bound on M_n.

## 8. Independent verification

paired_actual_joint_gap_compact_certificate.json saves the real graph,
base primal/dual, slope primal and finite boundary table.
verify_paired_q9_joint_gap.py calls no LP solver. It reconstructs the
genuine score graph, re-enumerates all 584 objects, matches their ordered
list hash, verifies every rational load/dual constraint, independently
exhausts all four boundary states, checks the two integer optimizers and
audits actual lifts Q9..Q18 with full graph identity, full cycle lifting,
attaining energy and actual rank runs. The infinite result follows from
the analytic formulas, not from that finite audit.

Zero violations, 6.036838265004917 seconds; audit digest
b848d360f25902f98e1b83c5e996437832c5476dce71f037220c77e7d2cb0c16.
The full verification report and log are paired_actual_joint_gap_verification.json
and paired_actual_joint_gap_run.log. All own jobs recorded here are complete.
