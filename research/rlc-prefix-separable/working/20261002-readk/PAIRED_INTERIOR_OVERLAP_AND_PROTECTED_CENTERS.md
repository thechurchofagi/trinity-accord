# Interior-overlap loss and protected face centers

Status: an analytic all-dimensional REAL counterexample to lossless face
merging, followed by an analytic positive-density theorem for a broader
restricted weight class. The unrestricted M_n constant-density target remains
OPEN. Published TA-TR-2026-22 v1.0 is unchanged. No new DOI is authorized.

This follows the latest master version44. The independently saved complete
paired Q5 theorem and endpoint-only overlap lemma are credited to
RLC_Five_Face_Endpoint_Overlap_20261003.md, not reclaimed here. This round
extends beyond endpoint-only overlaps, with a smaller guaranteed constant.
Trimming endpoints and counting retained turns are elementary techniques;
the increment is the exact all-dimensional scan class and obstruction.

## 1. Not all lost internal turns can be compensated

One tempting extension of endpoint-swap compensation is

    R_merge >= R_A+R_B-1

for two faces with identical additive scores differing by a translation,
disjoint rank intervals, and actual paired rank restrictions. This is FALSE.

### A genuine Q4 seed

Use positive weights w=(4,6,8,9) and paired mask6, root phase0. The order is

    (0,1,2,4,8,3,5,9,6,10,12,7,11,13,14,15).

Its rank values are

    (0,1,3,7,13,2,6,12,4,14,10,5,15,11,9,8).

The complete word has8runs. Restricting to bit3=0 or1 gives respectively

    (0,1,3,7,2,6,4,5),
    (13,12,14,10,15,11,9,8),

each with5runs. Both faces use the same core scores(4,6,8), translated by9;
their rank intervals are0..7 and8..15. Thus8<5+5-1. This respects the
genuine paired controllers, not independent arbitrary face permutations.
The interval9 is below the endpoint-only threshold18-4=14, so there is
no contradiction with the saved endpoint-only theorem.

### A linear-loss extension in every n>=4

Let n=4+m, T=2^m. Add m LOW input coordinates with HIGH score coefficients
28,56,...,28*2^(m-1), followed by(4,6,8,9). Write x=(u<<m)|t. The core
span is27, so the actual scan is T complete copies of the core order, one
per numeric t. Every score is a distinct integer.

Let r4 be the displayed paired seed rank and let g_m(t)=t XOR(t>>1). Define

    r_n(x)=T*r4(u) + [g_m(t) XOR((T/2)*(u&1))], m>0,
    r_4(x)=r4(x), m=0.

The bracket changes only the top of the new low rank bits. These are exactly
the baseline paired bits x_h XOR x_(h+1) on the new coordinates, with all
their theta values0. The old theta mask6 shifts by2^(n-1)-8. Thus the
complete rank is paired, and the inherited paired separator theorem proves
strict affine separation of every proper prefix in EVERY dimension.

Core comparisons are determined by r4 because their block difference is
at least T and low rank terms lie in[0,T-1]. Full core rows have7turns and
endpoint signs+,-. Their row join is descending from block8 to block0,
and adds exactly one turn. Hence

    R_full=7T+1+(T-1)=8T.

Partition by the old core bit3, now coordinate m+3. Each restricted first
face row has4turns and endpoint signs+,+; its descending join from block5
to0 adds2turns. Second face rows have4turns and endpoint signs-,-, and
their ascending join from block8 to13 also adds2turns. Therefore

    R_A=R_B=4T+1+2(T-1)=6T-1,
    (R_A+R_B-1)-R_full=4T-3=2^n/4-3.

The two (n-1)-faces still have IDENTICAL restricted score orders and a
constant translation9, and their rank intervals remain disjoint. This is
an actual all-dimensional linear loss, not a proposed nonadditive merge.
It does not refute constant density: R_full=2^(n-1), and the individual
face run counts were not claimed to be optimized minima. In particular
this does not refute compensation for a CAPPED fixed-core minimum budget.

verify_paired_interior_overlap_loss.py independently checks every score,
rank-mask identity, face translation, all three run formulas and complete
orders on n4..18; prefix separators are checked through n6. It also
regenerates the seed search in3655 cases, stopping at its first failure;
this is not a claim of smallest dimension or complete Q4 metric coverage.
Zero violations,5.7657276739919325seconds, audit SHA256
4c9fb4727671ab3686c57e3641db89d462724fd4a5125f0e41b7e34c523dc83e.
The initial score-translation check indexed a sorted score tuple by vertex;
it was corrected to dict(zip(order,scores)) before certification. The rank
and theoretical formulas were unchanged. Full certificate and log retained.

## 2. A protected-center lemma that tolerates interior overlaps

Fix the LOWEST d INPUT coordinates as the core (their scoring coefficients
may have arbitrary priorities), with q=2^d distinct normalized subset scores

    0=s0<s1<...<s_(q-1)=S.

Normalize signed core weights by input reflection, which preserves the paired
rank family. Complement symmetry gives s_i=S-s_(q-1-i). Suppose a certified
fixed-core bound says EVERY induced paired rank on that core has at least
Lruns, including either root phase. The proof below needs this exact fixed
core fact, not all weight chambers in dimension d.

Choose k<q/2. If EVERY consecutive outer subset-score gap exceeds S-s_k,
then in every face its middle q-2k vertices, with local score indices
k,...,q-k-1, form one contiguous block in the COMPLETE scan.

Proof. For a face with offset a, the last score of any preceding face is
at most a-gap+S<a+s_k. The first score of any following face is at least
a+gap>a+S-s_k=a+s_(q-k-1). Earlier or later nonneighbor faces obey the
same inequalities. Hence no other face vertex can enter its center.
This proof permits overlaps among its discarded end vertices, arbitrary
outer priority, signed outer weights, and arbitrary dimension. It does
not need row overlap to consist of endpoint swaps.

Deleting a vertex from an END of a rank word deletes one comparison and
loses at most one turn. Deleting k from each end therefore leaves at least

    max(0,L-1-2k)

turns inside the center. These are complete-scan turns and centers of
different faces cannot share a turn. Thus for every paired mask,

    R >= 1+max(0,L-1-2k)*2^(n-d).

This is the new all-dimensional restricted-scan lemma. A positive retained
budget proves positive density on this class, not RLC over all weights.
There is no assumption about local block rank ordering at the joins.

### An adaptive version

Different faces can have different numbers of trimmed initial and final
vertices. For face f, choose l_f,r_f such that the preceding gap exceeds
S-s_(l_f) and the following gap exceeds S-s_(r_f); a missing outer neighbor
needs no trim. Whenever l_f+r_f<q, the same argument gives

    R >= 1+sum_f max(0,L_f-1-l_f-r_f),

where L_f is any certified lower bound for that face's restricted runs.
The fixed-k statement follows by taking l_f=r_f=k. This refinement is
analytic here; the current verifier audits the fixed-k version only.

## 3. A concrete interior-overlap class outside two-face coverage

The fixed five-coordinate core b=(65,66,68,72,80) has paired minimum12.
This round INDEPENDENTLY checks all32768 normalized theta masks directly,
including attaining ranks, and cross-checks the ancestor integer optimizer.
Root phase1 is obtained by complementing all output rank bits, preserving
runs and the family. Signed input reflections are covered by the inherited
paired-family reflection identity.

Here S351 and the smallest scores are0,65,66,68,72. With k3 the threshold
is351-68=283 and the retained budget is12-1-6=5. Therefore for all n>=5,
ANY generic outer weights whose consecutive subset-score gaps exceed283
have, for EVERY paired mask,

    R >= 1+5*2^(n-5) = 1+(5/32)*2^n.

In particular take outer coefficients(284,568,1136,...). Every boundary
genuinely interleaves interior vertices: relative to the old row, the new
first scores284,349,350 occur before old last scores285,286,351 in part.
Thus this family lies outside the earlier endpoint-only condition gap>286.
The center contains26vertices and is protected. Scores are generic because
the core has no score difference284, while two row spacings568 exceedS.

There are NO contiguous adjacent-coordinate two-faces in this family,
in EVERY dimension:

* Two free core coordinates span three cardinality layers. Core increments
  above65 per bit total26<65, so cardinality layers are strictly ordered.
  Their middle layer has at least5vertices, all between the face endpoints.
  Four consecutive global vertices therefore cannot be this face.
* A free core coordinate4 and outer coordinate5 have span80+284=364.
  The lowest corner has core score c<=271. The first row's five weight-four
  vertices and its top vertex, with scores at least271 and at most351,
  all lie between the endpoints c and c+364. At least6vertices intervene
  in the interval, so it cannot consist of four consecutive vertices.
* Two free adjacent outer coordinates with weights w,2w, w>=284, have
  span3w. The intermediate row at offset w has protected center scores
  w+68,...,w+283, entirely between the lowest corner c<=351 and the
  highest corner c+3w. Its26vertices rule out contiguity.

For n5 only the first case applies. This proof is specific to the concrete
positive family; the signed audits test the lower-bound class, not this
extra no-two-face statement.

verify_protected_face_centers.py validates every center as a contiguous
global block and counts its retained turns on72 specified mask/scans
Q5..Q13 and48 signed/permuted genuine cases Q6..Q11. It independently
optimizes the full rank family on the concrete weights through Q10 and
evaluates each attaining mask directly. Complete core exhaustion plus
actual weights/centers suffice for this result; no prior Q5 archive is
required. The separately saved universal Q5 minimum9 would also give
coefficients3/16,1/8,1/16 for k1,2,3 respectively, but is not re-audited
or reclaimed here. Its package access returned a transient502 twice;
the fixed-core theorem above avoids that dependency entirely.

The certificate and log retain runtimes, exact minima, all tested weights,
seeds, core histogram, optimizer table hashes and order hashes.

## 4. Remaining proof gap

For arbitrary weights there may be no positive-length protected center and
the trimming sum can vanish. Thus this theorem does NOT prove a single
paired rank has RLC>=c*2^n, nor M_n>=c*2^n. It proves a new positive-weight
CLASS in every dimension for ALL paired masks, allowing some interior
overlaps and preserving an exact constant.

The lossless compensation shortcut is now rigorously excluded. The next
valuable route is a CAPPED per-face budget: first pay from protected centers,
then compensate only its remaining minimum-budget deficit by disjoint
crossing turns and genuine paired controller penalties. The general deficit
identity in PAIRED_QUARTET_CONTROLLER_POTENTIAL.md and the exact exterior
fields in PAIRED_TRANSLATION_AND_SCALAR_OBSTRUCTIONS.md remain the intended
tools. The main target is still unrestricted generic additive scans.
