# Face-local additive consistency cannot certify Gray run density

Date: 2026-10-03. Status: unpublished research and route exclusion.
Baseline: TA-TR-2026-22 v1.0, DOI
[10.5281/zenodo.23103274](https://doi.org/10.5281/zenodo.23103274).

The main target, a dimension-independent lower bound for M_n, remains OPEN.
Every permutation constructed below is explicitly **not** an additive
sweep. Its small run count is therefore **not** an RLC upper bound.

## 1. The precise relaxation under audit

Let gamma_n(x)=x XOR (x >> 1), with coordinate 0 least significant.
Use exactly the published alternating-run statistic R and its cyclic
counterpart C. The forward Gray rank is in the inherited prefix-separable
signed-tree family; this admissibility is unchanged.

Call a vertex permutation p consistent on k-faces with a positive vector a
when its restriction to every coordinate face of dimension at most k is
the strict order induced by a on that face. The SAME vector must work on
ALL faces, including every parallel translate. This definition concerns
the test order p, not a new admissibility condition on the target rank.

Local face consistency, positivity, distinct coordinate weights and
complement symmetry might appear sufficient to constrain the reflection
graph. The following countermodel shows that they are not.

## 2. All-dimensional theorem

**Theorem.** For every integer n>=k+3, k>=2, there are strictly increasing
positive integer weights a and a vertex permutation p with all of:

1. p is consistent on every face of dimension at most k with a.
2. Every strict comparison of the weak global score a dot x is respected.
3. p_(2^n-1-i) is the bitwise complement of p_i.
4. p is not induced by ANY generic real additive vector, of either sign.
   Two opposite strict comparison rows, each of support k+1, certify this.
5. For T=sum_j a_j,

\[
 R(\gamma_n\circ p)=C(\gamma_n\circ p)
 \le 4(T+1),\qquad T\le(2n)^{k+1}.
 \tag{1}
\]

Consequently, for any integer sequence k=k(n)>=2 with
k=o(n/log n), one obtains all-dimensional countermodels with

\[
 R/2^n=C/2^n\longrightarrow0,\qquad
 \log_2 R=o(n).
 \tag{2}
\]

For example k=floor(n/(log_2(2n))^2), once it is at least two, gives this
conclusion while the face dimension itself tends to infinity.
For any fixed 0<eta<1, the choice
k=floor(eta*n/log_2(2n)) instead gives
R <= 2^(eta*n+O(log n)), still of zero density.

**Proof, part A: deterministic integer weights.** Start with

\[
 (a_0,\ldots,a_k)=(1,2,\ldots,2^{k-1},2^k-1).
 \tag{3}
\]

The powers of two have distinct subset sums. An equality involving the
last seed weight can only use ALL k preceding weights, because their
total is exactly 2^k-1 and all are positive. Hence the seed has no nonzero
signed relation with coefficients in {-1,0,1} and support at most k.
It has the intended relation of support k+1.

When m weights have been chosen, let

\[
 {\cal F}_m=\left\{\sum_{j<m}\epsilon_j a_j:
 \epsilon_j\in\{-1,0,1\},\
 \#\{j:\epsilon_j\ne0\}\le k-1\right\}.
\]

Choose a_m as the least integer greater than a_(m-1) outside this finite
set. Any new zero relation of support at most k would express a_m as
a member of F_m (negate all signs if needed), so none is introduced.
There are at most

\[
 B_m=\sum_{r=0}^{k-1}2^r {m\choose r}
 \le \sum_{r=0}^{k-1}(2m)^r
 \le (1+2m)^{k-1}
\]

forbidden values. Among B_m+1 consecutive candidates there is an allowed
one, so a_m<=a_(m-1)+B_m+1.
With m<=n-1, this implies

\[
 T\le n2^k+n^2((2n)^{k-1}+1)\le(2n)^{k+1}.
 \tag{4}
\]

For the last inequality, the three summands are at most respectively
(2n)^k, (n/2)(2n)^k and (2n)^k, whose sum is at most
2n*(2n)^k since n>=5.
The greedy avoidance method is a standard kind of additive-combinatorial
construction, not a claim of a new general method.

**Part B: a central refinement with few Gray runs.** Let s(x)=a dot x.
For each integer t<T/2, list the vertices with s(x)=t by increasing
gamma_n(x), and concatenate these buckets in increasing t.
Call this first-half list H.

If the middle bucket s(x)=T/2 exists, first list its vertices with
x_(n-1)=0 by increasing gamma, then append their complements in reverse
order. This gives a central list Z, possibly empty. Define

\[
 p=H,\ Z,\ \overline{\operatorname{reverse}(H)}.
 \tag{5}
\]

Complementation changes s to T-s, so this permutation respects all
strict primary-score comparisons and is centrally symmetric.
Its restriction to every k-face is generic: two distinct vertices on
that face differ in at most k coordinates, and part A excludes a zero
score difference. The nonzero difference is preserved by (5).
This covers all smaller faces and every translate with the SAME a.

There are at most T+1 nonempty score buckets. Each lower bucket is
increasing in gamma. The elementary identity

\[
 \gamma_n(\bar x)=\gamma_n(x)\mathbin{\mathrm{XOR}}2^{n-1}
 \tag{6}
\]

means a mirrored upper bucket consists of at most two decreasing
blocks, separated by one increasing bridge. It has at most three runs.
The middle bucket has at most two runs. Concatenating q nonempty
buckets, each with at most three runs, gives R<=4q-1:
an edge joining two buckets introduces at most two new turn positions.
This bound also holds for singleton buckets by giving them the
conservative run bound one. Closing the permutation adds at most one
to R, so C<=4q<=4(T+1).

In fact the unique first two vertices are 0 and 1, since a_0=1 and all
other weights exceed one. The last two are their reversed complements.
Their first/last Gray comparison signs are respectively positive and
negative, and the closing sign is negative. Exactly one closing turn
is added to the internal turns, proving R=C. No generic-sweep endpoint
formula is being assumed for a nonadditive permutation.

**Part C: an explicit global impossibility certificate.** Set

\[
 u=2^k-1,\quad v=2^k,\quad z=2^{k+1},\quad t=2^k-1.
\]

Then s(u)=s(v)=t, and s(u OR z)=s(v OR z)=t+a_(k+1).
The seed contributes 2t to T. There are at least two further weights;
a_(k+2)>a_(k+1), so

\[
 2(t+a_{k+1})<T.
 \tag{7}
\]

Both tied pairs occur in lower buckets, where gamma is sorted upward.
Their highest differing input bit is k. Common bit k+1 is zero in the
first pair and one in the translated pair. The inherited Gray comparator
therefore gives

\[
 u\prec_p v,\qquad v\mathbin{\mathrm{OR}}z
                  \prec_p u\mathbin{\mathrm{OR}}z.
 \tag{8}
\]

Any real additive vector inducing p would have to satisfy

\[
 w_k-\sum_{j<k}w_j>0,\qquad
 \sum_{j<k}w_j-w_k>0.
 \tag{9}
\]

Adding these inequalities gives 0>0. The integer positive multipliers
(1,1), and the two opposite ternary rows of support k+1, form a complete
strict infeasibility certificate. This does not rely on a numerical
linear-programming solver or on the sign restriction on w.

Finally (1) gives log_2 R <= (k+1)log_2(2n)+O(1). Both asymptotic
conclusions follow. This completes the proof in every stated dimension.

## 3. A quadratic-range explicit three-face example

For k=3, the greedy weights have the simpler explicit form

\[
 a_0=1,\ a_1=2,\quad a_j=3j-2\ (j\ge2).
 \tag{10}
\]

They are distinct and positive. Apart from a_1=2, every weight is 1
modulo 3. A sum of two distinct such weights is 2 modulo 3 but exceeds
two, and a_1 plus another weight is 0 modulo 3. Thus no weight is the
sum of two distinct others. This proves the absence of all nonzero
ternary relations of support at most three directly.
The intended support-four relation is 1+2+4=7.

For every n>=6, use the refinement (5), with

\[
 T=(3n^2-7n+8)/2,\qquad
 C=R\le 6n^2-14n+20.
 \tag{11}
\]

Every three-dimensional face of every translate shares the same generic
vector (10), while the full scan is nonadditive. The certificate is
7 before 8 and 24 before 23, since the common translation is 16.
The exact finite counts in the receipt (e.g. 828 runs out of 262,144
vertices at n=18) are not asserted as an all-dimensional exact formula.

## 4. Consequences for the current Gray graph route

The exact graph identity from GRAY_REFLECTION_GRAPH_AUDIT.md is algebraic
in a centrally symmetric permutation. Its diagonal forced turns and
top-coordinate cancellation also hold for (5), although that permutation
is not a genuine sweep. With the identity spin choice,

\[
 E_*(p)-D(p)\ge 2^n-2C(\gamma_n\circ p)
             \ge 2^n-8(T+1).
 \tag{12}
\]

Hence complement symmetry plus agreement with a common positive vector
on all k-faces, even for growing k=o(n/log n), cannot by themselves imply
a dimension-independent net-energy deficit. Any such claimed deduction
would apply to (5) and contradict (12).

This excludes only a weakened proof premise. Full global additivity,
or global disjoint-translation consistency beyond these face dimensions,
excludes (8) immediately. The main RLC target, and the conjectured
positive density of the actual forward-Gray minimum, remain open.
The relevant next step must use this global condition quantitatively;
finite face checks are not a complete chamber reduction.

## 5. Audit, reproduction, and prior work

Run python3 verify_face_local_obstruction.py in this directory.
The integer verifier independently checks strict primary-score ordering,
the full complement pairing, all coordinate sets for the k-face
genericity certificate, direct near-vertex pairs in dimensions at most
ten, and the two-row infeasibility certificate. It checks global Gray
counts directly in eleven cases through dimension eighteen.
Coverage is 415,712 vertex entries, 4,105 coordinate sets and
244,368 directly tested unordered near-vertex pairs, with zero violations.
The all-dimensional result is the proof above, not those finite tests.

Implementation audit: an initial assertion incorrectly used q+1<=T+1
for the number q of score buckets. The correct inequality is q<=T+1;
the verifier and proof use C<=4q<=4(T+1). This was an implementation
off-by-one, not a rejected theoretical step.

Maclagan, Boolean Term Orders and the Root System B_n, Definitions 1.1
and 2.4, supplies the established disjoint-translation and coherence
framework: [author preprint](https://arxiv.org/pdf/math/9809134).
The violation (8) is already forbidden by its term-order axiom; this
framework is not new.
Greedy dissociated-set constructions are also established; see Sayan
Dutta, The Greedy Algorithm for Dissociated Sets,
[arXiv:2601.07068](https://arxiv.org/abs/2601.07068), and the dissociation
argument in De, Diakonikolas, Feldman and Servedio, Nearly optimal
solutions for the Chow Parameters Problem and low-weight approximation
of halfspaces, [author paper](https://www.cs.columbia.edu/~rocco/Public/stoc12chow.pdf).
No optimal range theorem for those constructions is used here.

An earlier moment-encoding/Prouhet idea would also separate bounded
supports, but was replaced before implementation by the simpler seeded
greedy construction above. Prouhet and Newton identities are known
tools, not proposed innovations; the checked source was Allouche and
Shallit, The ubiquitous Prouhet-Thue-Morse sequence, Section 5.1,
[author paper](https://cs.uwaterloo.ca/~shallit/Papers/ubiq15.pdf).
The research increment is the quantitative Gray-run relaxation
obstruction, the shared-vector face coverage, and the explicit global
infeasibility certificate. These targeted searches do not establish
historical priority of that application.
