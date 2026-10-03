# Coherent translated lex cones and a protected quarter-density scan class

Research draft, 2026-10-03. The published v1.0 and its DOI are preserved.
The original all-scan constant-density problem remains open.

## 1. Definitions and the finite exact statement

Retain the normalized five-bit paired rank \(\sigma=\rho_{5,2}\), whose
minimum cyclic run count on all genuine signed upper scans is 12 by the
independent complete certificate of checkpoint 59. A six-bit child has
arbitrary fresh lowest-level labels. Let \(C\) count cyclic sign changes,
and \(R\) count linear monotone runs. Always \(R\ge C-1\).

For a six-bit weight vector \((a,v_0,\ldots,v_4)\), assume genericity and
that the absolute upper weights are superincreasing in **some** coordinate
order: every weight after the first exceeds the sum of its predecessors.
The signs and coordinate order are arbitrary; \(a\) is any nonzero value.

**Finite theorem (exact certificate).** For every such genuine scan,
the mean cyclic count over all fresh lowest labels obeys
\[
 \mathbb E C\ge24. \tag{1}
\]
Equality is attained by the genuine signed weights
\((24,1,6,-20,40,12)\). When the upper weights themselves are positive and
superincreasing in their original coordinate order, the minimum is 28.
These statements concern conditional means and a specified cone union;
they do not assert a selected child handling all generic six-bit weights.

## 2. A complete covering certificate, independently verified without LP

The positive numeric upper-order cone is exactly
\(v_0>0\), \(v_j>\sum_{h<j}v_h\) for \(j=1,\ldots,4\). Take \(a>0\).
The scan merges the ordered chains \(s_i\) and \(s_i+a\), where
\(s_i=v\cdot i\). The consumed counts satisfy \(i\ge j\). Choosing the
first or second chain imposes the strict linear inequality that its next
score is smaller. The first half determines the second by antipodality.
Its last vertex must be below the central score \((\sum v_h+a)/2\), another
strict homogeneous inequality. These tests enumerate every genuine scan
in this cone: an admitted chain word gives its full scan, and a rejected
inequality system excludes exactly that branch. Conversely every genuine
generic scan follows one enumerated branch and passes the central test.

There are 9134 admitted chambers. The cover has 10338 rejected branches.
Every admitted branch has an integer weight witness satisfying all its
strict inequalities. Every rejected branch has a nonzero nonnegative
integer combination of its required difference vectors summing to zero.
Thus its infeasibility follows from \(0>0\). Numerical LP discovers these
objects; the independent verifier trusts only integer arithmetic, rebuilds
every inequality, and checks that all branches are covered. No LP status or
floating-point margin is accepted as a proof. The independent cover replay
visits 39100 nodes. The compressed certificate retains the entire cover.

All 120 upper coordinate permutations and all 32 sign reflections transfer
this **same** geometric cover. They are applied directly to the parent's
rank table; permuting a scan is not treated as permuting its fixed paired
hierarchy. This checks all 35074560 map/chamber pairs. Lowest-coordinate
reflection merely reparametrizes the fair fresh labels, so \(a<0\) has the
same mean bound. The minimum of all these means is exactly 24.

Common addition, coherence, antipodality and lex cones are known concepts,
not new terminology. The cube difference constraints exclude the relaxed
mean-18 witness of checkpoint 61. The new ingredients are the complete
selected-parent cone certificate and the transfer below.

## 3. All-dimensional translated-core rows

For \(n=6+d\), retain the upper five-bit seed \(\sigma\), with root zero.
Use coordinate 0 as the new translated core coordinate and the highest
five coordinates as its upper core. Coordinates \(1,\ldots,d\) select rows.
Assume their distinct subset scores have consecutive gaps exceeding
\[
 S=|a|+\sum_{h=0}^4|v_h|.
\]
They can be signed and need not have binary weights. The full genuine scan
is \(T=2^d\) separated copies of the six-bit core order. Lower paired labels
outside the retained seed may be arbitrary.

Let \(L\) be the number of core comparisons changing only coordinate 0,
including the cyclic closing comparison, and \(F\) the number of core turns
between two fixed upper comparisons. The inherited fresh comparison
identity gives \(\mu_{\rm core}=F+L\ge24\). The closing edge changes the top
core bit, so it is fixed. Every row boundary has exactly this closing sign;
the first and last core vertices are antipodal. Consequently
\[
 m_0=TL,\quad C\ge TF,\quad
 \mathbb E[C\mid\text{all higher labels}]=T(F+L)\ge\tfrac38N. \tag{2}
\]
The last identity holds for **every** fixed assignment of all higher labels,
not just a separately chosen parent. Uniform fresh lowest labels suffice.
When \(d\ge1\), labels may be shared between two rows differing in coordinate
1. No row independence is assumed or needed; fixed turns and unbiased
fresh comparisons prove (2).

An immediate deterministic dichotomy holds for every lower assignment:
\[
 L<8\ \Longrightarrow\ R\ge17T-1;
 \qquad L\ge8\ \Longrightarrow\ m_0\ge N/8. \tag{3}
\]
This already combines legitimately with checkpoint 60's **same-rank**
bottom-mass guarantee. Unlike the old protected five-core class, coordinate
0 may have an intermediate score and interleave the two upper chains.

## 4. A stronger uniform quarter-density selection

Condition on all higher labels and randomize only the lowest labels.
The cyclic count has an affine independent two-state decomposition
\(C=C_0+\sum_u A_u\theta_u\). Fresh comparisons cannot be adjacent. A lowest
label has at most four middle-vertex turn incidences and the total number
of incidences is \(2m_0\). Hence the already established cyclic influence
bound is
\[
 \sum_u A_u^2\le8m_0\le4N.
\]
The standard product moment bound for independent fair bits, together with
(2), yields
\[
 \Pr(C\le N/4\mid\text{all higher labels})
 \le \exp(-N/128). \tag{4}
\]
This is a known concentration argument with a new protected-core mean
input, not a new concentration theorem. Dependence between turns and
between rows has not been ignored.

There are at most \(3^{n^2}\) signed generic additive scan orders, by the
inherited arrangement bound. For every \(n\ge15\),
\(3^{n^2}e^{-2^n/128}<1\). Therefore **every** paired parent in dimension
\(n-1\) retaining the seed has **one** lowest-level child satisfying
\(C>N/4\), and thus \(R\ge N/4\), on **all** separated six-core row scans
described above. The integer step uses \(R\ge C-1\). This is an
all-dimensional theorem on a restricted scan class. It does not cover
arbitrary interleaving weights or prove the original \(M_n\) claim.

The inherited single-bottom mass event has the same exponential failure
bound. Combining both gives \(2\cdot3^{n^2}e^{-N/128}<1\) already for
\(n\ge15\): using \(\log3<9/8\) and \(\log2<1\), the base is
\(1+(9/8)15^2<2^{15}/128\), and the margin increases thereafter.
Thus one compatible family, retaining the seed at every dimension, has
the new row guarantee and the inherited \(m_0\ge N/8\) guarantee for every
dimension from 15 onward. Other classes are not silently added to this
one-bottom compatible-family assertion.

At fixed \(n\ge18\), freeze the 15 seed labels and sample all others.
Equation (4) holds after every conditioning on higher labels. Thus it can
be added to checkpoint 60's joint entropy/two-bottom events under the
**same** probability measure. Their total failure probability is at most
\[
 4\cdot3^{n^2}e^{-N/512}<1.
\]
Indeed \(2+(9/8)18^2<2^{18}/512\), and the margin grows. One ranking then
simultaneously handles the large-support class, the two-bottom-mass class,
the old protected five-core rows, **and** the new six-core row class at
\(R\ge N/4\). This is a legitimate shared-rank conclusion.

## 5. Evidence and remaining gap

`enumerate_numeric_core_translates.py` creates the compressed integer cover.
`verify_numeric_core_translate_certificate.py` independently replays it
without a solver, then checks every signed/permuted upper map. Generation
took 107.918 seconds; the independent exact replay and all map checks took
8.376 seconds. All cuts and chamber witnesses are retained.

`verify_translated_core_row_dichotomy.py` tests 128 actual mixed-sign,
nonbinary-row cases through dimensions 6--13. It independently verifies the
row count, fixed-turn floor, both fresh endpoint counts, every active
fresh-label coefficient by integer sign-word XOR/popcount, and the exact
influence-square bound. These finite tests audit the all-dimensional proof;
they are not substituted for it.

The precise main remainder still includes general non-superincreasing upper
cores and scans whose six-core rows are not separated. The certificate does
not show the selected parent has mean at least 24 on all genuine six-bit
scans, nor give summably controlled selected-parent losses in all dimensions.
Those are still the needed bridges to a positive unrestricted asymptotic
density. Lower and upper bounds do not presently match.

Primary provenance: Diane Maclagan, *Boolean Term Orders and the Root System
Bn*, arXiv:math/9809134v2 (10 March 1999), Definition 2.1, Corollary 2.3 and
Definition 2.4; the equal-length interval representation is a standard
semiorder representation, e.g. Pouzet and Zaguia, *Interval orders,
semiorders and ordered groups*, arXiv:1706.03276. A targeted search did not
establish priority for every equivalent run-complexity formulation.
