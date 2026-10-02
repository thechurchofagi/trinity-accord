# Exact signed-lex Gray counts and the remaining interleaving gap

Date: 2026-10-03. Research note; published v1.0 is preserved.
Baseline: TA-TR-2026-22, DOI 10.5281/zenodo.23103274.

## 1. Definitions and comparison rule

Coordinates are numbered from 0 (least significant) to \(n-1\), and
\(\gamma_n(x)=x\oplus(x\gg1)\) is the forward-Gray rank map. For distinct
vertices \(x,y\), put \(h=\lfloor\log_2(x\oplus y)\rfloor\) and set \(x_n=0\).
The highest rank bit that differs is \(h\); hence
\[
 \operatorname{sgn}(\gamma_n(y)-\gamma_n(x))
 =(-1)^{x_{h+1}}(y_h-x_h).                                      \tag{1}
\]
The orientation is determined by the next input bit, not by all higher
bits. This is not the inverse BRGC rank map.

For completeness, under a highest-coordinate extension the two face rank
sequences are \(A\) and \(2^d+\operatorname{reverse}(A)\), when both are
read in their common lower-coordinate score order. Indeed
\(\gamma_d(\overline{x})=\gamma_d(x)\oplus2^{d-1}\), and complementation
reverses an additive score order. The complete scan merges these faces
according to one translated score list. Reversing this rank sequence and
complementing each numeric rank are different operations.

For a permutation \(p=(p_0,\ldots,p_{n-1})\) of the coordinates, define
\[
 P_p(i)=\sum_{t=0}^{n-1}2^{p_t}i_t,\qquad
 \pi_{p,z}(i)=z\oplus P_p(i)\quad(0\le i<2^n).
\]
Here \(p_0\) is the fastest coordinate. These are precisely the signed-lex
orders with arbitrary significance permutations. The integer weights
\[
 w_{p_t}=(1-2z_{p_t})2^t
\]
realize them. More generally the same order is realized whenever their
magnitudes satisfy \( |w_{p_t}|>\sum_{s<t}|w_{p_s}|\).

## 2. Exact formula for every signed-lex scan

**Theorem 1.** Let \(N=2^n\), \(f=p_0\).
If \(f=n-1\), then
\[
 R(\gamma_n\circ\pi_{p,z})=N-1.
\]
If \(f<n-1\), let
\[
 \ell=\min\{t\ge1:p_t>f\}.
\]
Then, for every reflection \(z\),
\[
 \boxed{R(\gamma_n\circ\pi_{p,z})=N(1-2^{-\ell}).}                 \tag{2}
\]
Thus the count is independent of all reflection signs, and for \(n\ge2\),
\[
 \boxed{\min_{p,z}R(\gamma_n\circ\pi_{p,z})=2^{n-1}.}              \tag{3}
\]

**Proof.** If \(f=n-1\), every binary counter increment changes coordinate
\(f\), the highest coordinate; its direction alternates. Formula (1)
therefore gives an alternating sign word and \(N-1\) runs.

Assume \(f<n-1\). Put \(B=2^\ell\), \(L=N/B\), and view the counter
cyclically. Break it into \(L\) blocks of \(B\) vertices. Inside each block
every increment changes coordinate \(f\), while all other changed
coordinates are less than \(f\). Also coordinate \(f+1\) is fixed within the
block. By (1), each block's \(B-1\) internal signs alternate, contributing
\(B-2\) turns. Its first and last internal signs are equal since \(B-1\)
is odd.

Let \(q\) be the counter position of coordinate \(f+1\). Then \(q\ge\ell\).
For each boundary, consider the two turns joining the preceding block's
last sign, the boundary sign, and the following block's first sign. Write
their sum as \(D\in\{0,1,2\}\). At a nonclosing boundary let
\(k=\nu_2(i+1)\); at the closing boundary all coordinates change.

If \(k\ge q\), or at the closing boundary, coordinate \(f+1\) changes.
Consequently the two adjoining internal signs are opposite, and \(D=1\).
If \(k<q\), coordinate \(f+1\) does not change. Pair this boundary with the
one obtained by reflecting counter bit \(q\). The carry support is
unchanged, and its highest input coordinate \(h\) satisfies \(h>f+1\).
The boundary comparison sign is unchanged by this reflection, by (1),
whereas both adjoining internal signs are negated. Therefore the paired
values satisfy \(D+D'=2\). This pairs all boundaries of the latter type
without fixed points. Summing over all \(L\) boundaries yields
\(\sum D=L\).

The cyclic turn count is therefore
\[
 C=L(B-2)+L=N(1-2^{-\ell}).
\]
The first and last nonclosing edges both change only coordinate \(f\).
Their starting vertices have complementary \(f+1\) bits, so their rank
comparison signs are opposite. On deleting the closing edge, exactly one
of the two turns adjoining it disappears. Thus the linear run count equals
the cyclic count \(C\), proving (2). Since \(\ell\ge1\), (3) follows, with
equality for \(p_0=0\). \(\square\)

This is a lower bound for a fully specified scan subclass, not for all
generic additive weights. The previous reflection-pairing theorem concerns
all balanced-tree ranks and reflected binary orders; (2) uses the special
next-bit structure of forward Gray and classifies every significance
permutation and reflection exactly.

## 3. A minimal obstruction to reducing all scans to signed lex

The integer vector \(w=(1,6,4,8)\) gives the Q4 order
\[
 (0,1,4,5,2,3,8,9,6,7,12,13,10,11,14,15)
\]
and forward-Gray values
\[
 (0,1,6,7,3,2,12,13,5,4,10,11,15,14,9,8).
\]
It has exactly 6 runs, whereas every Q4 signed-lex scan has at least 8.
Therefore minimizing over signed-lex scans is not a valid reduction of
RLC. The dimension four obstruction is minimal: on Q2, all generic scans
are signed lex. On Q3, positive sorted weights \(0<a<b<c\) have only the
two chambers \(c>a+b\) and \(c<a+b\). Their signed/permuted orbits contain
all 96 generic scans, each with at least 4 forward-Gray runs. The verifier
regenerates these chambers from \((1,2,4)\) and \((2,3,4)\) and checks them.

These finite claims supply an exact counterexample to a proposed reduction.
They are not evidence sufficient to prove any all-dimensional lower bound.

## 4. No scalar doubling recurrence with fixed loss

**Theorem 2.** There is no dimension-independent constant \(A\) such that
every generic extension by a highest coordinate satisfies
\[
 R(\gamma_{d+1}\circ\pi_{(v,t)})
 \ge 2R(\gamma_d\circ\pi_v)-A.
                                                                    \tag{4}
\]
This failure occurs even when both orders are signed lex with positive
integer weights.

**Proof.** For each \(d\ge2\), take
\[
 v^{(d)}=(4\cdot2^0,\ldots,4\cdot2^{d-2},1),\qquad t=2.
\]
The \(d-1\) entries preceding the final 1 are \(4\cdot2^j\),
\(0\le j\le d-2\). They and the extension have distinct subset sums.
The parent's highest coordinate \(d-1\) is fastest, so Theorem 1 gives
\(R_d=2^d-1\). In the child the fastest coordinate is \(d-1\), and the
first subsequent larger coordinate is the new coordinate \(d\), at
counter position 1. Therefore \(R_{d+1}=2^d\). The loss is
\[
 2R_d-R_{d+1}=2^d-2\longrightarrow\infty.
\]
This contradicts any fixed \(A\). \(\square\)

This rejects a same-weight parent recurrence, not a recurrence involving
dimension-wise minima or a richer state. It is distinct from the earlier
failed lemma that assumed a dominant parent highest weight: here that
parent weight is the smallest.

## 5. A precise asymptotic target from cyclic row lifting

For any rank sequence \(a=(a_0,\ldots,a_{N-1})\), close it by the edge
\(a_{N-1}\to a_0\), and let \(C(a)\) count sign changes cyclically.
If \(b=\operatorname{sgn}(a_0-a_{N-1})\) and \(e_0,e_{N-2}\) are the first
and last nonclosing signs, then
\[
 C(a)=R(a)-1+
       \mathbf1\{e_{N-2}\ne b\}+\mathbf1\{b\ne e_0\},
 \qquad |C(a)-R(a)|\le1.                                      \tag{5}
\]
This is the ordinary cyclic version of the alternating-run statistic,
not a new statistic or a novelty claim.

For the forward-Gray rank there is a sharper endpoint statement. A generic
additive sweep starts at \(z_j=\mathbf1\{w_j<0\}\) and ends at its complement.
If \(f=\arg\min_j|w_j|\), its first and last edges both change only coordinate
\(f\). Formula (1) gives opposite first/last signs when \(f<n-1\), so the
endpoint penalty in (5) is one. When \(f=n-1\), both signs agree with the
direction from the first rank to the last, so that penalty is two. Hence
\[
 C(\gamma_n\circ\pi_w)=R(\gamma_n\circ\pi_w)
                      +\mathbf1\{f=n-1\}.                         \tag{5a}
\]
In particular cyclic closure never decreases the forward-Gray count.

Put
\[
 G_n=\operatorname{RLC}(\gamma_n),\qquad
 F_n=\min_{w\ {\rm generic}}C(\gamma_n\circ\pi_w).
\]
**Theorem 3.** For every \(n\ge d\ge1\),
\[
 F_n\le 2^{n-d}F_d.
                                                                    \tag{6}
\]
Consequently \(F_n/2^n\) is nonincreasing, and
\[
 \boxed{\lim_{n\to\infty}G_n/2^n
        =\lim_{n\to\infty}F_n/2^n
        =\inf_{d\ge1}F_d/2^d=:\alpha_G,\quad 0\le\alpha_G\le5/16.}     \tag{7}
\]

**Proof.** For a minimizing \(d\)-dimensional sweep \(\tau\), put it on
the high \(d\) input coordinates. Choose the remaining weights as a binary
counter separated by a constant exceeding the high score range. The full
sweep is \(2^{n-d}\) copies of \(\tau\), one in each row. High ranks occupy
the exact Gray macro intervals. Closing the full sweep makes the row sign
word periodic, including its boundary sign. Thus its cyclic turn count is
exactly \(2^{n-d}C(\gamma_d\circ\tau)\), proving (6).
The limit exists by monotonicity and nonnegativity. Equation (5a) gives
\(G_n\le F_n\le G_n+1\), proving equality of limits. The five-dimensional
certificate has cyclic count 10, so \(\alpha_G\le10/32=5/16\).
\(\square\)

The exact unresolved forward-Gray gap is therefore \(\alpha_G>0\), versus
\(\alpha_G=0\). A bound on all signed-lex scans proves only (3); it does not
prove positivity in (7). A finite chamber improvement in (7) persists in
every higher dimension, but establishing zero requires improvements
arbitrarily close to zero. If \(\alpha_G>0\), the published strict
separability of this signed-tree family implies the main target
\(M_n\ge c2^n\) for some \(c>0\). If \(\alpha_G=0\), other prefix-separable
families remain possible.

The same projection argument gives a family-wide version. If \(T_n\) is
the largest RLC among all fixed-hierarchy balanced-tree ranks and
\(H_n\) is the largest minimum cyclic count among those ranks, then
\[
 H_n\le2^{n-d}H_d,\qquad |H_n-T_n|\le1.
\]
Every high projection is itself a \(d\)-dimensional balanced-tree rank,
and the repeated row comparison word is independent of all lower node
orientations. Taking the maximum after the individual projection bound
proves the displayed inequality. Thus \(T_n/2^n\) also has a limit.
This does not give such a limit for the full extremal quantity \(M_n\):
general prefix-separable ranks need not admit this tree projection.

## 6. Evidence, literature and next step

Run the script verify_gray_sweep_recursion.py with Python 3. It constructs
actual rank sequences independently from the proof, exhausts every
signed-lex permutation and reflection through dimension 7, checks the
paired boundary costs, tests the comparison and cyclic endpoint identities
with exact integers, verifies (4)'s counterexamples through dimension 16,
and tests row lifts with independently chosen lower-subtree orientations.

Foundational notions are established: Boolean term orders and coherence
are treated by Diane Maclagan, *Order* 15 (1998), 279--295,
DOI [10.1023/A:1006207716298](https://doi.org/10.1023/A:1006207716298),
[author preprint](https://arxiv.org/abs/math/9809134); alternating runs are
a classical permutation statistic. Targeted searches on 2026-10-03 for
Gray ranks, signed-lex sweeps and alternating runs did not locate formula
(2) or a resolution of (7). This is not an exhaustive historical priority
claim. The Gray transform, cyclic closure, and the already-proved
interleaving identity are reused ingredients.

The earlier Q4 pressure script's completeness now has an explicit source
dependency: Maclagan's Section 4 table gives
\(\chi_{H_4}(t)=(t-1)(t-11)(t-13)(t-15)\); Zaslavsky's region formula yields
\(\chi_{H_4}(-1)=5376\). Since the generator supplies 5,376 distinct generic
integer orders, it covers the whole Q4 universe. The chamber count itself
is existing literature, not a contribution of this research.

The next useful recursion must retain information about which parent
turns can disappear under translated face merging; the scalar parent
count and the two endpoint signs alone do not certify doubling.
Any finite-state reduction must prove coverage of all subset-sum chambers.
A promising pressure test is to minimize the cyclic cost over
translation-consistent face merges, using rational/integer witnesses for
every feasible transition and exact exclusions for infeasible ones.
This round gives an exact subclass lower bound, a refuted recurrence and
an asymptotic dichotomy; it does not improve the current general lower
bound or solve the constant-density problem.
