# The minimum-highest half-density conjecture is false in all dimensions

Date: 2026-10-03. Unpublished exact research result; published v1.0 unchanged.
The main dimension-independent M_n lower bound remains OPEN.

This note supersedes the conjecture left open in
minimum_top_bit_probe_receipt.json. Unstructured random pressure checked
4,772 genuine vectors without finding a violation. A targeted layered
construction now supplies a strict integer counterexample and an
all-dimensional, arbitrarily separated family.

## 1. Precisely rejected statement

The proposed subcase was: for every generic positive magnitude vector a
whose unique smallest entry is the highest coordinate, its Gray reflection
graph satisfies E_*(a)<=D(a), equivalently every sign choice has
C(gamma_n o pi_w)>=2^(n-1).

It was UNPROVED, never an accepted lemma of the published paper.
The following theorem disproves it. It even disproves the same assertion
under an arbitrarily large fixed ratio between every other magnitude
and the highest-coordinate magnitude.

## 2. Explicit six-dimensional chamber family

Let s=(4,6,3,0,8). For every integer B>=20 set

\[
 a(B)=(B+4,B+6,B+3,B,B+8,12),\qquad
 v(B)=(-B-4,-B-6,B+3,B,B+8,12).
\]

**Lemma.** The positive order pi_(a(B)) is generic and independent of B,
and the signed order pi_(v(B)) is its input reflection by z=3.
For that signed order R=29 and C=30.

**Proof of genericity and chamber invariance.** Group the first five
coordinates by their Hamming weight k. The secondary subset scores in
the six groups are:

| k | Sorted secondary scores |
| --- | --- |
| 0 | 0 |
| 1 | 0,3,4,6,8 |
| 2 | 3,4,6,7,8,9,10,11,12,14 |
| 3 | 7,9,10,11,12,13,14,15,17,18 |
| 4 | 13,15,17,18,21 |
| 5 | 21 |

All scores inside a group are distinct. Its secondary width is at most
11<12, so all vertices with highest bit zero precede the identical
highest-bit-one group shifted by 12. Between successive k groups the
worst secondary deficit is 7. Their separation is at least B-12-7>=1.
The positive score order is therefore exactly by
(k, highest bit, secondary score), regardless of B>=20. No limit or
sampling is involved.

Input reflection by z=3 negates precisely the first two magnitudes and
adds only a constant to every score. The exact integer vector at B=25 is
v=(-29,-31,28,25,33,12). Its full 64-vertex order and the independently
computed comparison statistics are retained in the certificate.

The graph certificate for the positive order is especially short:

    D=8;
    J_(1,2)=-4, J_(1,3)=-4, J_(2,3)=+4;
    all other off-diagonal couplings are zero.

These four integer quantities are checked by independently reading every
cyclic adjacent triple of the 64-vertex order. Taking spins
sigma_1=-1, sigma_2=sigma_3=+1 satisfies all three nonzero couplings.
Thus E_*=W=12, and the inherited exact identity gives

\[
 \min_z C=\frac{64+8-12}{2}=30.
\]

All 64 actual signed weight vectors are independently sorted and checked.
Their cyclic minimum is 30 and their linear minimum is 29. The explicit
reflection z=3 attains both. Chamber invariance extends these exact
statistics to every B>=20. End of proof.

The finite certificate is an audit of ONE explicitly specified order,
not a claim of exhaustive six-dimensional chamber coverage or minimal
counterexample dimension.

## 3. Arbitrary magnitude separation and all-dimensional lift

**Theorem.** For every n>=6 and every real K>0, there is a generic positive
magnitude vector a with a_(n-1) the unique minimum and
a_j>K a_(n-1) for every j<n-1, such that

\[
 \min_z C(\gamma_n\circ\pi_{(-1)^z a})=\frac{15}{32}2^n,\qquad
 \min_z R=\frac{15}{32}2^n-1,\qquad
 E_*(a)-D(a)=\frac1{16}2^n.
\]

**Proof.** Choose an integer B>=20 with B>12K. Put m=n-6,
L=2^m, and A=sum a(B)+1=5B+34. Use lower magnitudes A*2^j
for 0<=j<m, followed by the six high magnitudes a(B). The signed witness
uses the same lower magnitudes followed by v(B).

The high score range is sum a(B)=A-1. Each low-coordinate row is therefore
disjoint from the next, and has the same high order. All full scores
are distinct. The highest magnitude is still 12, and every other one
is greater than 12K.

Inside a row, every edge changes a high seed coordinate; at its boundary,
the last high vertex is followed by the first high vertex of the next
row, so again its highest differing coordinate is high. The highest-bit
labels and Gray comparison signs are exactly the seed cyclic word,
repeated L times. Lower bits cannot decide any comparison. Consequently
D and every nonzero coupling are scaled by L, with their indices shifted
by m. The isolated lower spins do not affect the optimization:

    D_n=8L, W_n=E_n=12L, E_n-D_n=4L=2^n/16.

The cyclic optimum is 30L. The inherited endpoint identity for a unique
minimum magnitude in the highest coordinate gives R=C-1 for every sign
choice, so the linear optimum is 30L-1. The displayed signed integer
vector realizes both. End of proof.

Even arbitrarily small highest weight relative to each individual other
weight does not control the spacing between their subset sums. This is
why a magnitude-only dominance argument in this subcase fails.

## 4. Verification and what remains open

Run verify_minimum_highest_counterexample.py. It audits all 64 signs
for B in {20,25,100,10000,10^12}, checks every exact secondary bucket,
and tests separated lifts through n=18 at B=25 and through n=10 at
the other specified B values. The all-dimensional claim rests on the
proved chamber invariance and row graph scaling, not those finite lifts.

The discovery replay probe_layered_minimum_highest.py uses seed
202610030755. It tested 400 generic cases in each of n=4,5 before the
140th case in n=6 violated the conjecture. Its first large seed was
(953242,983318,936098,862068,1052123,476207). The small chamber family
above replaces it with a much simpler exact certificate.

No new permutation statistic, graph optimization concept, reflection
identity, or row-lift method is claimed as an invention. The contribution
relative to the current audited notes is the explicit refutation of their
remaining minimum-highest conjecture, including arbitrary magnitude
separation. Historical priority is unconfirmed.

This ceiling 15/32 is larger than the existing unrestricted Gray ceiling
5/16. Therefore it does not improve the global upper bound or resolve
the main positive-density lower question. It rules out a proposed
sufficient condition, and underscores that full subset-difference
constraints, not comparisons of individual magnitudes alone, must enter
the general proof. The next useful pressure route is to analyze
cardinality-layer orders and their reflection couplings with the actual
shared secondary vector, preserving all translated comparisons.
