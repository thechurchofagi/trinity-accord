# Exact Gray reflection graphs and an unbounded independent-edge error

Date: 2026-10-03. English research note, not a new published edition.
Baseline: TA-TR-2026-22 v1.0, DOI 10.5281/zenodo.23103274.
The published bytes are preserved. The general constant-density target is OPEN.

## 1. The proof gap addressed

A scalar parent run count cannot control arbitrary translated face merging;
the previous note already provides an all-dimensional counterexample to
constant-loss doubling. This round instead retains the entire cyclic
comparison-label pattern of a genuine additive sweep.

For a fixed vector of positive generic magnitudes, the new application below
reduces *all* weight-sign choices to one weighted signed graph on at most
\(n-1\) active vertices. It does not restrict the magnitudes to signed lex
or to a sampled chamber. We then test, and disprove in its smallest possible
dimension, the simplification that every graph edge can be optimized
independently. An explicit lift makes the resulting error grow with dimension.

The conversion of a binary sign objective to a quadratic/Ising objective,
signed-graph balance, and weighted frustration are established methods.
They are not newly named inventions. The contributions here are their exact
application to this forward-Gray rank, the cube-specific cancellation,
and the audited counterexample to the attempted simplification.

## 2. Exact reflection-orbit formula for arbitrary generic magnitudes

Put \(N=2^n\), \(\gamma_n(x)=x\oplus(x\gg1)\). Coordinates start at 0.
Let \(a=(a_0,\ldots,a_{n-1})>0\) be generic and let
\(p=(p_0,\ldots,p_{N-1})\) be its increasing additive sweep.
Use indices modulo \(N\), including the closing edge.
Define
\[
 e_i=\operatorname{sgn}(\gamma_n(p_{i+1})-\gamma_n(p_i)),\qquad
 h_i=\lfloor\log_2(p_i\oplus p_{i+1})\rfloor.
\]
For \(0\le h\le k<n\), put
\[
 J_{hk}=\sum_{i:\{h_i,h_{i+1}\}=\{h,k\}} e_i e_{i+1}.
 \tag{1}
\]
Here each turn is counted once; for \(h=k\) it belongs to that diagonal
entry. There is no extra factor of two on off-diagonal entries.
Let
\[
 D=\#\{i:h_i=h_{i+1}\},\quad
 W=\sum_{h<k}|J_{hk}|,\quad
 E_*(a)=\max_{\sigma\in\{-1,1\}^n}
          \sum_{h<k}J_{hk}\sigma_h\sigma_k.
\]

**Theorem 1 (exact sign-orbit reduction).** Every weight-sign choice
\(w_j=(-1)^{z_j}a_j\) has cyclic turn count
\[
 \boxed{
 C(\gamma_n\circ\pi_w)
   =\frac{N+D-\sum_{h<k}J_{hk}\sigma_h\sigma_k}{2},
 \qquad \sigma_h=(-1)^{(\gamma_n(z))_h}.}
 \tag{2}
\]
Moreover,
\[
 J_{hh}=-\#\{i:h_i=h_{i+1}=h\},\qquad J_{h,n-1}=0\ (h<n-1).
 \tag{3}
\]
Consequently, if \(f=\arg\min_j a_j\), then
\[
 \boxed{
 \min_z C(\gamma_n\circ\pi_{((-1)^{z_j}a_j)_j})
     =\frac{N+D-E_*(a)}2,\quad
 \min_z R(\gamma_n\circ\pi_{((-1)^{z_j}a_j)_j})
     =\frac{N+D-E_*(a)}2-\mathbf1\{f=n-1\}.}
 \tag{4}
\]
For \(n\ge2\), the optimization needs only \(2^{n-2}\) spin assignments:
fix the isolated top spin and one further spin positive.

**Proof.** The signed score at \(p_i\oplus z\) equals the positive score
at \(p_i\), minus the sum of the magnitudes whose signs were negated.
Thus the signed sweep is exactly \(p_i\oplus z\).
The Gray transform is linear over XOR:
\(\gamma_n(p_i\oplus z)=\gamma_n(p_i)\oplus\gamma_n(z)\).
The highest differing Gray bit is precisely \(h_i\). XOR with the
fixed rank mask \(\gamma_n(z)\) therefore multiplies comparison \(i\)
by \(\sigma_{h_i}\). Substituting into
\(C=\sum_i(1-e_i e_{i+1})/2\) gives the quadratic identity.
Since \(\gamma_n\) is a bijection, every spin assignment is attainable
by an actual weight-sign choice.

When two consecutive labels equal \(h\), the middle input bit \(h\)
has flipped twice and all higher bits of the three vertices agree.
The two Gray comparison signs are opposite, proving the diagonal
identity. This argument is valid for any vertex permutation.

For the top cancellation, use the additive complement symmetry
\[
 p_{N-1-i}=\overline{p_i},\qquad
 \gamma_n(\overline{x})=\gamma_n(x)\oplus2^{n-1}.
 \tag{5}
\]
The mirrored edge index is \(N-2-i\) modulo \(N\). It has the same
label \(h_i\), and its sign is \(\mu_{h_i}e_i\), where
\(\mu_h=-1\) for \(h<n-1\) and \(\mu_{n-1}=1\).
The turn joining edges \(i,i+1\) is paired with the mirrored turn
joining edges \(N-3-i,N-2-i\). If exactly one label is \(n-1\),
the two products are opposites. The turn involution has no fixed points:
\(2i=N-3\pmod N\) has no solution because \(N\) is even.
This proves \(J_{h,n-1}=0\). Thus the top spin is irrelevant.
Global inversion of all other spins leaves their pair products
unchanged, giving the stated search size.

Finally the previously proved generic Gray endpoint identity is
\(C=R+\mathbf1\{f=n-1\}\). The absolute-value minimizer \(f\) is
the same for every sign choice. This proves (4). \(\square\)

This theorem covers every generic magnitude vector, hence every actual
additive chamber. It removes the discrete sign optimization exactly,
but does not remove the optimization over positive magnitude chambers.
No step asserts that all additive sweeps are signed lex.

## 3. Frustration is necessary; the first obstruction is Q5

Let the weighted frustration be
\[
 \phi(a)=\min_\sigma\sum_{\substack{h<k,\ J_{hk}\ne0\\
               \sigma_h\sigma_k\ne\operatorname{sgn}J_{hk}}}|J_{hk}|.
\]
The standard signed-graph identity gives
\[
 E_*=W-2\phi,\qquad
 \boxed{\min_z C=(N+D-W)/2+\phi.}                    \tag{6}
\]
Optimizing the edges independently sets \(\phi=0\) without justification.
That expression is a valid lower relaxation, but it is not always the
attainable optimum.

**Exact integer counterexample.** On Q5 take
\[
 a=(2,20,16,5,12).
\]
The full positive sweep and its ordered scores are
\[
\begin{split}
 p={}&(0,1,8,9,16,17,4,24,5,25,2,12,3,13,10,11,\\
     &20,21,18,28,19,29,6,26,7,27,14,15,22,23,30,31),\\
 s={}&(0,2,5,7,12,14,16,17,18,19,20,21,22,23,25,27,\\
     &28,30,32,33,34,35,36,37,38,39,41,43,48,50,53,55).
\end{split}
\]
These strictly increasing integer scores certify genericity.
The only nonzero off-diagonal couplings are
\[
 J_{02}=-2,\qquad J_{03}=4,\qquad J_{23}=2.
 \tag{7}
\]
The diagonal entries are \(J_{33}=-4,\ J_{44}=-8\), so
\(D=12,\ W=8\). The triangle on labels \(0,2,3\) has negative
sign product. Its three desired spin products cannot all hold:
their product must equal \(1\). At least one edge is unsatisfied,
with weight at least \(2\). Taking every spin positive attains
that weight, so \(\phi=2,\ E_*=4\).
The independent-edge value is \(18\); the true minimum over all
32 signed weight vectors is \(20\). The full cyclic histogram is
\[
 \{20:16,\ 22:8,\ 26:8\}.
\]
Here \(f=0\), so the same counts are the linear run counts.

**Minimality.** This obstruction cannot occur through dimension four.
The exact generator produces all 336 positive Q4 chambers; their
nonzero off-diagonal graph has zero edges in 245 cases, one in 86,
and two in 5. Hence each is a forest and \(\phi=0\).
The dimensions 1--3 are also exhausted and have no negative cycle.
Every signed chamber is a gauge switch of its positive chamber,
which preserves the sign product around each cycle.

Coverage is not inferred from a weight sample: Maclagan's Section 4
gives the arrangement region counts \(2,8,96,5376\) for dimensions
1--4. Sign reflection gives \(2^n\) orthants of equal size. The
generator constructs that exact number of distinct, integer-realized
orders in every dimension, establishing completeness. The counts
are an explicit dependency on existing literature.

## 4. An all-dimensional growing-error family

**Theorem 2.** For every \(n\ge5\), with \(m=n-5\) and \(L=2^m\),
take
\[
 a^{(n)}=(64,128,\ldots,64\,2^{m-1},\,2,20,16,5,12).
 \tag{8}
\]
For \(m=0\) the leading list is empty. This is generic and satisfies
\[
 \boxed{D=12L,\quad W=8L,\quad\phi=2L,\quad
          \min_z C=\min_z R=20L.}
 \tag{9}
\]
The error in treating the independent-edge relaxation as an exact
optimum is therefore \(2L=2^{n-4}\). No dimension-independent
additive correction makes that simplification valid.

**Proof.** The Q5 scores range from 0 to 55, so 64-spaced lower
counter rows are disjoint. The full sweep repeats the high Q5 sweep
exactly \(L\) times. Each high vertex lies in its forward-Gray macro
rank interval; comparisons within a row, and from its last high
vertex 31 to the following first high vertex 0, have the same
signs and highest differing labels as the closed Q5 sweep, with
all labels shifted by \(m\). The same holds at cyclic closure.
The graph in (7), including its diagonal entries, is therefore
scaled by \(L\). The negative triangle has least edge weight
\(2L\), and all-positive spins attain that frustration.
Lower spins affect none of these comparisons. The smallest
absolute weight is at input coordinate \(m<n-1\), so \(R=C\)
for every reflection. Equation (9) follows. \(\square\)

This is an all-dimensional exclusion of a proof shortcut, not a lower
bound for \(G_n=\operatorname{RLC}(\gamma_n)\) across all chambers:
a different magnitude vector can have fewer runs.

## 5. Complement symmetry alone does not prove density

The top cancellation (3) is useful but cannot supply a positive deficit
by itself. For every \(n\ge2\), put \(M=2^{n-1}\), let
\(u_i=\gamma_n^{-1}(i)\), \(0\le i<M\), and consider
\[
 p=(u_0,\ldots,u_{M-1},
       \overline{u_{M-1}},\ldots,\overline{u_0}).
 \tag{10}
\]
It has precisely the additive complement symmetry (5). Its Gray ranks
are
\[
 (0,1,\ldots,M-1,\,N-1,N-2,\ldots,M),
\]
so \(R=C=2\). It also satisfies top cancellation.
For \(n\ge3\), however, the vertices \(0,1,3,2\) occur in that order.
An additive score would require \(w_0>0\) from \(0<1\) and \(w_0<0\)
from \(3<2\), an exact contradiction. Thus these are inadmissible scans.

Any attempted graph inequality that uses only central symmetry and
the cancellation in (3), omitting translation consistency across
cube faces, admits zero-density counterexamples (10).

## 6. Genuine translated-face pressure test

To test the gap beyond sign reflection, use positive magnitude seed
\((1,14,4,12,20)\), the absolute values of the established 5/16 ceiling.
Keeping these five magnitudes fixed, add one arbitrary positive
magnitude \(t\). Cross-face score ties occur precisely at the 48
distinct positive differences of parent subset sums. Their complement
in \(t>0\) has 49 open intervals. One rational midpoint in each interval
(and one point in the last unbounded interval), scaled to integers,
exhausts every generic translated merge in this specified one-parameter
family. Enumerate all assignments of the six magnitudes to coordinates
and optimize their signs by Theorem 1.

There are 34,560 distinct positive Q6 chambers in this family.
Their largest \(E_*-D\), and also largest \(W-D\), are both 24.
Thus their minimum cyclic count is 20. The complete generation parameters
and chamber digest are saved with the pressure script.
This is a one-parameter coverage result, not coverage of all Q6 chambers
or of a full five-dimensional parent cone. It recovers the expected
local behavior, supplies no all-dimensional lower bound, and does not
improve the existing Gray ceiling.

## 7. The precise uniform gap and theoretical impact

For arbitrary positive generic magnitudes, (4) implies
\[
 F_n=\frac12\left(N-
     \max_{a>0\ {\rm generic}}[E_*(a)-D(a)]\right).
 \tag{11}
\]
The unresolved Gray target is exactly a dimension-independent
energy deficit:
\[
 \exists\varepsilon>0,\ n_0:\quad
 E_*(a)-D(a)\le(1-\varepsilon)2^n
 \quad\text{for every }n\ge n_0
 \text{ and every positive generic }a.
 \tag{12}
\]
If (12) holds, \(G_n\ge\varepsilon2^{n-1}-1\), giving the primary
constant-density target through the already-proved strict prefix
separability of the Gray tree rank. A sufficient, stronger candidate
inequality is \(W-D\le 2^{n-1}\), which would give \(C\ge2^{n-2}\);
this inequality is currently neither proved nor refuted here.
Frustration must be retained when that relaxation is too weak.
The actual proof obligation is the geometry of realizable magnitude
chambers, not a generic theorem about arbitrary signed graphs.

The strongest next step is to derive a quantitative restriction on
\(W-D-2\phi\) from translation consistency of all face restrictions,
or to construct a genuine additive family approaching the full energy
budget. The central-symmetry relaxation and independent-edge equality
have now been rigorously separated from that task.

This round gives a reusable exact reduction, a minimal counterexample,
and two all-dimensional route exclusions. It does not remove the
\(n^2\) denominator in the general bound or establish a new optimal
Gray constant. It is a structural research increment, not a solution
of the main conjecture or evidence of top-journal readiness.

## 8. Verification and sources

Run verify_gray_reflection_graph.py with Python 3; it uses only the
standard library and exact integers. It checks every signed additive
sweep through Q4 (5,482 scans), all 32 reflections of the Q5 certificate,
320 explicit row-lift reflections through dimension 14, and 16,256
additional reflections of sampled generic magnitudes through dimension
12. The sampled magnitude tests are not chamber-complete.
It checks the central-symmetry counterexamples through dimension 12.
Analytic all-dimensional claims rest on the proofs, not these finite checks.
The separate pressure script records genuine one-parameter Q6 coverage.

The baseline comparator, face reversal, endpoint identity, and row lifting
are inherited from the preceding audited notes.
The known chamber-complement symmetry and region counts are in
Diane Maclagan, *Boolean Term Orders and the Root System B_n*,
Order 15 (1998), 279--295, Sections 2 and 4,
[primary preprint](https://arxiv.org/pdf/math/9809134),
DOI [10.1023/A:1006207716298](https://doi.org/10.1023/A:1006207716298).
Signed-graph balance originates in Frank Harary,
*On the notion of balance of a signed graph*, Michigan Math. J. 2
(1953/1954), 143--146,
[publisher record](https://projecteuclid.org/journals/michigan-mathematical-journal/volume-2/issue-2/On-the-notion-of-balance-of-a-signed-graph/10.1307/mmj/1028989917.full),
DOI [10.1307/mmj/1028989917](https://doi.org/10.1307/mmj/1028989917).
The publisher PDF was blocked during this round; the balance criterion
used here is proved directly by multiplying spin products.
Targeted primary-source searches on 2026-10-03 did not establish
historical priority for this Gray-specific application. Priority is
unconfirmed; established quadratic optimization and signed-graph
concepts must not be advertised as new theory.
