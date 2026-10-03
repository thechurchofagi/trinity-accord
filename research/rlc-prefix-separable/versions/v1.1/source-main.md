---
title: "Exponential Run Complexity of Prefix-Separable Orders on the Boolean Cube"
author: "Hongju Liu"
date: "3 October 2026"
lang: en
documentclass: article
fontsize: 11pt
geometry: margin=1in
header-includes:
  - '\usepackage{amsmath,amssymb}'
  - '\usepackage{microtype}'
---

Independent researcher, Shenzhen, China

**Report:** TA-TR-2026-22 · **Version:** 1.1 · **DOI:** __DOI_RESERVED_AT_RELEASE__

**Publication status:** Mathematical preprint; not externally peer reviewed.

## Abstract

Let \(Q_n=\{0,1\}^n\). An order on its vertices is prefix-separable if every proper nonempty initial segment is strictly separated from its complement by an affine hyperplane, with a different hyperplane permitted for each segment. For a rank function \(\rho\), let \(\operatorname{RLC}(\rho)\) be the minimum number of maximal consecutive monotone runs obtained by reading \(\rho\) along any generic linear-functional ordering of the vertices. We prove that prefix-separable orders can have \(\operatorname{RLC}(\rho)=\Omega(2^n/n^2)\). More precisely, if \(M_n\) is the maximum of this minimum over prefix-separable orders, then \(\liminf n^2M_n/2^n\ge \log2/(2\log3)\), where \(\log\) denotes the natural logarithm. The proof combines a fixed balanced signed-tree construction, a deterministic bound on repeated comparison labels, the established read-k tail theorem, and the number of linear sweep chambers. Tree representations, alternating-run statistics, and concentration tools are existing ingredients; the result concerns their quantitative combination under the cube prefix condition and a simultaneous quantifier over every linear sweep. We also prove constant-density bounds on two specified scan classes using a paired-tree family, including a compatible extension that preserves any chosen upper rank. An all-dimensional row-lift identity rules out a uniform exponential-tail shortcut. The unrestricted dimension-independent positive-density lower bound remains open.

**Keywords:** Boolean cube; prefix separation; pseudo-sweep; alternating runs; separable permutations; linear ranking; probabilistic method.

## 1. Introduction

An order can be simple at each threshold while resisting approximation by a single additive ranking. The threshold statement is that every initial segment can be cut out by a strict affine inequality. The global comparison considered here is the number of times the rank sequence changes direction after the vertices are sorted by one linear functional. The weights in that functional may be chosen optimally and may have either sign.

The prefix condition belongs to an established geometric framework: a pseudo-sweep permutation has every initial segment equal to a strictly separated k-set [1, Section 6.1]. In the setting of Boolean term orders and qualitative probability, nonrepresentable orders whose initial segments are threshold complexes already provide a qualitative separation between individual cuts and a common additive representation [2, 3]. We do not claim this qualitative phenomenon or the prefix condition as new.

Our question is quantitative. Write \(N=2^n\). Must some prefix-separable cube order still make \(\Omega(N/\log^2N)\) monotone runs even after the best linear-functional ordering is chosen? We answer this question affirmatively. The construction uses random signs on a fixed balanced binary tree with its leaves identified with the cube in a fixed coordinate hierarchy. Its tree representation and least-common-ancestor comparison rule are standard for separable permutations [4]. The key estimate controls the chance of few runs for any fixed ordering of those leaves, without assuming that the resulting composed permutation remains separable.

A potential difficulty is that one tree sign may govern many adjacent comparisons of the chosen sweep. A direct concentration estimate based only on the number of independent signs can therefore be too weak. We use a deterministic alternative: if one sign governs too many edges, the sequence already has many runs; otherwise all bounded-difference constants can be controlled by the proposed low-run threshold. This yields a probability bound that can be summed over all linear sweeps.

The paper gives the complete proof of the general bound and an explicit finite inequality. It makes no claim of an exact extremal value, an optimal asymptotic constant, or a positive-density bound \(M_n\ge c_0 2^n\). Version 1.1 strengthens the leading coefficient by a factor of \(4\log2\), adds two simultaneous restricted-sweep theorems, and gives exact obstructions to proposed proof routes. The supplementary file separates exhaustive verification from sampled pressure tests and records the version changes.

## 2. Definitions and main results

For a sequence \(p=(p_1,\ldots,p_m)\) of distinct real numbers with \(m\ge2\), define

\[
R(p)=1+\sum_{i=1}^{m-2}
\mathbf 1\{(p_{i+1}-p_i)(p_{i+2}-p_{i+1})<0\}.
\]

Equivalently, \(R(p)\) is the number of constant-sign blocks in the word of adjacent differences. The runs partition the edges of the sequence; adjacent runs share their turning vertex. This is the classical alternating-run or birun statistic [5], rather than the number of increasing runs alone.

A rank function is a bijection \(\rho:Q_n\to\{0,\ldots,N-1\}\). It is **prefix-separable** if, for every \(1\le k<N\), there are \(a_k\in\mathbb R^n\) and \(b_k\in\mathbb R\) such that

\[
\rho(x)<k\ \,\Longrightarrow\, a_k\cdot x<b_k,
\qquad
\rho(x)\ge k\ \,\Longrightarrow\, a_k\cdot x>b_k.
\]

The separating weights need not agree for different \(k\). This condition is denoted \(B_{\mathrm{ind}}(\rho)=1\) in the accompanying research records.

A weight \(w\in\mathbb R^n\) is **generic** if the \(N\) numbers \(w\cdot x\), \(x\in Q_n\), are distinct. Let \(\pi_w=(x_1,\ldots,x_N)\) list the vertices in increasing score order. Set

\[
\operatorname{RLC}(\rho)=
\min_{w\text{ generic}}R(\rho(x_1),\ldots,\rho(x_N)),
\qquad
M_n=\max_{\rho\text{ prefix-separable}}\operatorname{RLC}(\rho).
\]

Generic weights exist. Only finitely many distinct sweep orders occur, so the minimum is attained by an ordering chamber. The maximum is over a finite set of rank functions. For \(n\ge1\),

\[
1\le M_n\le 2^n-1.
\]

**Theorem 2.1 (exponential run complexity).** For every fixed
\(0<c<\log2/(2\log3)\), all sufficiently large \(n\) admit a prefix-separable rank function \(\rho\) on \(Q_n\) such that every generic weight satisfies

\[
R(\rho\circ\pi_w)>\left\lfloor\frac{c2^n}{n^2}\right\rfloor.
\]

Consequently,

\[
\liminf_{n\to\infty}\frac{n^2M_n}{2^n}
\ge\frac{\log2}{2\log3},
\qquad
\lim_{n\to\infty}\frac{\log_2 M_n}{n}=1.
\]

There is also a finite sufficient condition. Write

\[
H_n=\frac{3^n-1}{2},\qquad
S_n=2\sum_{j=0}^{n-1}\binom{H_n-1}{j},
\]

with \(\binom aj=0\) for \(j>a\).

**Theorem 2.2 (finite bound).** Let \(n\ge2\) and let \(K\) be an integer with \(1\le K<2^{n-1}\). Put
\[
D(q\Vert p)=q\log(q/p)+(1-q)\log((1-q)/(1-p)),\qquad
T_{n,K}=\frac{2^n-2}{2K}D\left(\frac{K-1}{2^n-2}\Big\Vert\frac12\right),
\]
with \(0\log0=0\). If \(S_ne^{-T_{n,K}}<1\), then \(M_n\ge K+1\). The fair signed-tree construction has \(\operatorname{RLC}>K\) with probability at least \(1-S_ne^{-T_{n,K}}\) when that expression is positive.

The all-weight bound remains of order \(2^n/n^2\). The additional theorems below concern specified scan classes, and do not replace the minimum over all generic weights in the definition of \(M_n\).

## 3. A prefix-separable signed-tree family

Fix a full balanced binary tree of depth \(n\). Its root splits the cube by coordinate \(n-1\), the next level by coordinate \(n-2\), and so on down to coordinate \(0\). A node at coordinate \(j\) fixes all higher coordinates and has two children indexed by the value of \(x_j\). The canonical leaf order is the ordinary binary integer order, with coordinate \(0\) the least significant bit.

Assign each internal node \(u\) a sign \(\xi_u\in\{-1,+1\}\). Sign \(+1\) means that child 0 is traversed first; sign \(-1\) means that child 1 is traversed first. Recursively concatenate the two child orders in this chosen order. Let \(\rho_\xi(x)\) be the position of leaf \(x\), starting from 0. Each child subtree occupies a consecutive interval of ranks. There are \(N-1\) internal nodes, and we sample all their signs independently and uniformly.

This is a special fixed-shape signed-tree representation of a separable permutation. The usual direct/skew-sum description and ancestor comparison rule appear in [4, Definitions 2.8--2.9 and Observation 2.10]. We use a particular cube labeling so that the whole family satisfies the required geometric prefix condition.

**Lemma 3.1 (explicit strict separators).** Every \(\rho_\xi\) is prefix-separable.

**Proof.** Fix \(1\le k<N\), and let \(z\) be the first excluded leaf, so \(\rho_\xi(z)=k\). For each coordinate \(j\), let \(u_j(z)\) be the node on the path to \(z\) that splits coordinate \(j\). Define the integer affine form

\[
L_z(x)=\sum_{j=0}^{n-1}3^j\xi_{u_j(z)}(x_j-z_j).
\]

For \(x\ne z\), let \(j\) be its highest differing coordinate from \(z\). Both leaves pass through \(u_j(z)\), and this is their first split. The sign of their rank difference is

\[
\operatorname{sgn}(\rho_\xi(x)-\rho_\xi(z))
=\xi_{u_j(z)}\operatorname{sgn}(x_j-z_j).
\]

The \(j\)-th term of \(L_z(x)\) dominates all lower terms because

\[
3^j>\sum_{h<j}3^h=\frac{3^j-1}{2}.
\]

Thus \(L_z(x)\) has that same sign. Its integer value is at most \(-1\) on the prefix and at least \(1\) on the other excluded leaves; also \(L_z(z)=0\). The threshold \(L_z=-1/2\) strictly separates the two sets. This holds for every prefix. \(\square\)

## 4. Comparison labels and their multiplicities

Fix an arbitrary permutation \(\pi=(x_1,\ldots,x_N)\) of the leaves. It need not be an additive sweep. For \(1\le i<N\), let \(u_i\) be the least common ancestor of \(x_i,x_{i+1}\). At that node they are in opposite children. Define \(\eta_i=+1\) if they cross from child 0 to child 1, and \(\eta_i=-1\) for the reverse crossing. Both \(u_i\) and \(\eta_i\) depend only on \(\pi\) and the fixed tree.

The adjacent rank comparison sign is therefore

\[
s_i=\operatorname{sgn}(\rho_\xi(x_{i+1})-\rho_\xi(x_i))
=\eta_i\xi_{u_i}.
\]

For a node \(u\), define its comparison multiplicity by

\[
m_u(\pi)=\#\{i:u_i=u\},\qquad
\sum_u m_u(\pi)=N-1.
\]

These multiplicities are deterministic once \(\pi\) has been fixed.

**Lemma 4.1 (mean run count).** For every fixed leaf permutation \(\pi\),

\[
\mathbb E_\xi R(\rho_\xi\circ\pi)\ge N/2.
\]

**Proof.** If \(u_i\ne u_{i+1}\), the two signs use independent fair spins, so the probability of a turn is \(1/2\). If \(u_i=u_{i+1}\), the three leaves cross the same split twice. Their child memberships alternate, giving \(\eta_{i+1}=-\eta_i\), so a turn is forced. There are \(N-2\) possible turns. In fact, if \(J=\#\{i:u_i=u_{i+1}\}\), then

\[
\mathbb E_\xi R(\rho_\xi\circ\pi)
=1+J+\frac{N-2-J}{2}=\frac{N+J}{2}.
\]

The asserted lower bound follows. \(\square\)

**Lemma 4.2 (multiplicity forces runs).** For every sign assignment, every fixed \(\pi\), and every internal node \(u\),

\[
m_u(\pi)\le R(\rho_\xi\circ\pi).
\]

**Proof.** The two children of \(u\) occupy disjoint rank intervals, one entirely below the other. Within a strictly increasing run, an edge labeled \(u\) must cross from the lower interval to the upper one. Once this crossing has occurred, the run cannot later return to the lower interval, so a second such edge is impossible. The decreasing case is the same with the directions reversed. This remains true if other leaves outside the subtree occur between crossings. Partition all sequence edges into their constant-sign blocks. Each block contains at most one edge labeled \(u\), proving the inequality. \(\square\)

## 5. Read-degree concentration for a fixed leaf ordering

We apply the known read-k theorem of Gavinsky, Lovett, Saks and Srinivasan [9, Theorem 1.1]. If Boolean functions \(Y_1,\ldots,Y_\ell\) of independent inputs read each input at most \(d\) times, and their average marginal is \(p\), then for \(0\le q<p\),
\[
\Pr\left\{\sum_iY_i\le q\ell\right\}
\le\exp[-(\ell/d)D(q\Vert p)].
\]
The tail inequality is prior work. Its application to the cube comparison word supplies the improved coefficient.

**Proposition 5.1.** For every fixed leaf permutation \(\pi\), \(n\ge2\), and integer \(1\le K<N/2\),
\[
\Pr_\xi\{R(\rho_\xi\circ\pi)\le K\}
\le\exp\left[-\frac{N-2}{2K}
D\left(\frac{K-1}{N-2}\Big\Vert\frac12\right)\right].
\]

**Proof.** If some fixed comparison multiplicity \(m_u>K\), Lemma 4.2 makes the event impossible. Otherwise each tree sign occurs in at most \(2m_u\le2K\) turn indicators. Indicators with equal successive labels are constant 1; all others have marginal \(1/2\), so their average marginal \(p\ge1/2\). Apply [9] to the \(N-2\) indicators with read degree \(2K\) and \(q=(K-1)/(N-2)<1/2\). For \(p<1\),
\[
\frac{\partial}{\partial p}D(q\Vert p)=\frac{p-q}{p(1-p)}\ge0,
\]
so replacing \(p\) by \(1/2\) weakens the bound. If \(p=1\), the event is impossible. The multiplicities depend only on \(\pi\); the independent spins have not been conditioned on a low-run event. \(\square\)

More precise sweep-specific bounds follow by deleting the forced indicators. If \(J\) is their number, \(\ell=N-2-J>0\), and \(d_\pi\) is the maximum number of remaining indicators reading one spin, then for \(0\le K-1-J<\ell/2\),
\[
\Pr(R\le K)\le\exp\left[-\frac{\ell}{d_\pi}
D\left(\frac{K-1-J}{\ell}\Big\Vert\frac12\right)\right].
\]
For \(K-1<J\) the probability is zero. Other thresholds may be bounded trivially by 1.

## 6. Counting sweeps and the improved all-weight theorem

Score ties lie on the central hyperplanes with normals
\(d\in\{-1,0,1\}^n\setminus\{0\}\), modulo overall sign. There are exactly
\(H_n=(3^n-1)/2\) such hyperplanes. A central arrangement of \(H\) hyperplanes
in dimension \(n\) has at most \(2\sum_{j=0}^{n-1}\binom{H-1}{j}\) regions:
adding a hyperplane induces the Pascal recurrence on its restriction, and
coincident restrictions can only reduce the count. Thus the number of generic
signed additive sweeps is at most \(S_n\), and
\[
\log S_n\le(\log3)n^2+O(n),\qquad S_n\le3^{n^2}\quad(n\ge2).
\]
For the second inequality, encode every subset of size at most \(n-1\)
of \(H_n-1\) symbols as its increasing list padded to length \(n-1\) by a
spare symbol. Hence \(S_n\le2H_n^{n-1}\le3^{n^2}\).

Union bounding Proposition 5.1 over this fixed family proves Theorem 2.2.
Fix \(0<c<\log2/(2\log3)\) and \(K=\lfloor cN/n^2\rfloor\). Since
\(D(q\Vert1/2)\to\log2\) as \(q\to0\), the failure probability is at most
\[
\exp\left[\left(\log3-\frac{\log2}{2c}+o(1)\right)n^2\right]\longrightarrow0.
\]
Every sample is prefix-separable. Letting \(c\) increase to
\(\log2/(2\log3)\) proves Theorem 2.1. The upper bound \(M_n\le2^n-1\)
still gives \(\log_2M_n/n\to1\). The improved liminf coefficient is
\(0.3154648767\ldots\), compared with \(1/(8\log3)=0.1137799033\ldots\)
in v1.0; the ratio is \(4\log2=2.772588722\ldots\). \(\square\)

## 7. A paired family and a simultaneous support theorem

Write the output bits of a rank as
\[
\rho_h(x)=x_h\oplus x_{h+1}\oplus\theta_h(x\gg(h+2))\quad(h<n-1),
\qquad \rho_{n-1}(x)=x_{n-1}.
\]
The \(2^{n-1}-1\) phase bits \(\theta\) are free. Given higher input bits,
the displayed equations recover each lower input bit from the rank, so the
map is bijective. It is a signed-tree traversal: at a node splitting
coordinate \(h<n-1\), the orientation bit is
\(x_{h+1}\oplus\theta_h(x\gg(h+2))\). Lemma 3.1 therefore gives a strict
separator for every prefix. The top phase is fixed; it need not be randomized.

For a vertex permutation \(p\), label each consecutive comparison by its
highest differing input coordinate \(h\) and, when \(h<n-1\), the prefix
\(u=x\gg(h+2)\). Its sign is the sign for the baseline rank
\(x\oplus(x\gg1)\), multiplied by \((-1)^{\theta_h(u)}\). Let \(q(p)\)
count the distinct non-top labels in this RAW comparison word, before any
coefficient cancellation. At least one top comparison occurs.

**Lemma 7.1 (support counting).** Under independent fair phases, for every
vertex permutation and integer \(1\le K\le N-1\),
\[
\Pr_\theta\{R(\rho_\theta\circ p)\le K\}
\le2^{-q(p)}\sum_{j=0}^{K-1}\binom{N-2}{j}.
\]
**Proof.** A turn-transition word together with any one comparison sign
determines all comparison signs. At an observed top comparison that sign is
fixed. Recover each active phase from one of its occurrences. Thus the
transition word is injective on the \(2^{q(p)}\) equally likely active
assignments. At most \(K-1\) turns allow the displayed number of binary
transition words. No independence of turn indicators is assumed. \(\square\)

**Theorem 7.2.** For every \(n\ge12\), one paired rank simultaneously satisfies
\[
R(\rho\circ\pi_w)>N/128
\quad\text{for every generic signed }w\text{ with }q(\pi_w)\ge N/8.
\]
**Proof.** Let \(K=N/128\), \(\ell=N-2\). The binary entropy bound
\(\sum_{j=0}^t\binom{\ell}{j}\le2^{\ell H_2(t/\ell)}\), for
\(t\le\ell/2\), follows by weighting the binomial expansion with
\(p=t/\ell\). Also
\(H_2(p)\le p\log_2(e/p)\), so
\(H_2(1/128)<17/256\); use \(\log_2e<3/2\), equivalently \(\log2>2/3\).
The latter follows from the first term of
\(\log2=2\sum_{j\ge0}(1/3)^{2j+1}/(2j+1)\).
Each bad-sweep probability is therefore less than \(2^{-15N/256}\).
At \(n=12\), \(3^{144}<2^{240}\). The ratio \(2^n/n^2\) increases
for \(n\ge3\), so \(3^{n^2}2^{-15\,2^n/256}<1\) for every \(n\ge12\).
A union bound selects ONE rank for EVERY sweep in the stated class. \(\square\)

## 8. Conditional extensions preserving an arbitrary parent

Add a new lowest input coordinate to ANY fixed paired rank in dimension
\(n-1\). Keep all its higher phase bits, and independently randomize only
the \(2^{n-2}\) fresh phases \(\theta_0(u)\). Let \(L(p)\) count consecutive
comparisons changing ONLY input bit 0. Two such comparisons cannot be
adjacent: they would repeat the first vertex. Every affected turn consequently
depends on one fresh phase and a fixed higher comparison.

Group the affected costs by phase:
\[
R=C_0+\sum_uY_u(\theta_0(u)),\qquad C_0\ge1,
\qquad Y_u(0)+Y_u(1)=k_u\le4.
\]
One fresh phase controls two bit-0 edges, each touching at most two turns.
If \(e\in\{0,1,2\}\) counts fresh comparisons at the ends of the linear
comparison word, then
\[
\sum_uk_u=2L-e,\quad \mu=\mathbb ER=C_0+L-e/2\ge L,
\quad \sum_u A_u^2\le8L,\qquad A_u=Y_u(0)-Y_u(1).
\]
Indeed \(A_u^2\le k_u^2\le4k_u\). The independent fresh-bit mgf and
\(\cosh z\le e^{z^2/2}\) give
\[
\mathbb E e^{-\lambda(R-\mu)}
=\prod_u\cosh(\lambda A_u/2)\le e^{\lambda^2L}.
\]
Markov's inequality with \(\lambda=1/4\) yields
\[
\Pr_{\rm fresh}\{R\le L/2\}\le e^{-L/16}.
\]
This bound holds for ANY vertex permutation and ANY fixed paired parent.

**Theorem 8.1.** For every \(n\ge15\) and every specified paired parent,
there is ONE child preserving it such that
\[
R(\rho\circ\pi_w)>N/16
\quad\text{for EVERY generic signed }w\text{ with }L(\pi_w)\ge N/8.
\]
**Proof.** Failure implies \(R\le L/2\), and hence has probability at most
\(e^{-N/128}\). Union over at most \(3^{n^2}\) chambers is below one.
For an explicit base, \(\log3<9/8\), because the first five Taylor terms
of \(e^{9/8}\) sum to more than 3. At \(n=15\),
\(2^{15}/128=256>(9/8)15^2\); monotonicity of \(2^n/n^2\) proves the
claim thereafter. \(\square\)

Successive choices starting from any dimension-14 parent give a SINGLE
compatible family satisfying this theorem in every dimension \(n\ge15\).
It is supplied by a separate existence argument from Theorem 7.2. The
union of the two scan classes is not currently protected by a single proved
family; combining separate existential statements would be invalid.

## 9. Exact row lifts and an obstruction to uniform tails

Define the cyclic turn count \(C\) by adding the last-to-first comparison
and counting sign changes cyclically. If \(b\) is the closing comparison
sign and \(a_1,a_{D-1}\) are the linear endpoint signs, put
\(B=\mathbf1\{a_1\ne b\}+\mathbf1\{a_{D-1}\ne b\}\in\{0,1,2\}\).
Then \(C=R-1+B\).

Fix generic signed core weights \(v\) on \(d\) highest input coordinates.
Add \(m\) lower coordinates with weights \(H,2H,\ldots,2^{m-1}H\), where
\(H>\sum_j|v_j|\). The true additive order consists of \(T=2^m\) copies
of the core order. A signed-tree rank projects to a fixed upper core rank,
and its high rank intervals dominate every comparison between distinct
core vertices. Thus all within-row signs copy the core, and every row join
has sign \(b\), independently of all lower tree orientations. Exactly,
\[
R_{\rm lift}=T C_{\rm core}-B+1,\qquad C_{\rm lift}=T C_{\rm core}.
\]
For actual additive core orders the extreme vertices are complements, so
joins use the top label. In the paired family the raw non-top labels are
simply shifted by \(m\); consequently \(q_{\rm lift}=q_{\rm core}\).

**Corollary 9.1.** For the compatible family in Section 8, fix any
\(d\ge15\) core with \(L(\pi_v)\ge2^d/8\). Every such actual row lift
to dimension \(n\ge d\) has \(R\ge2^n/16-1\), even though its raw
support divided by \(2^n\) tends to zero as \(n\to\infty\).
**Proof.** Integrality and Theorem 8.1 give \(C_{\rm core}\ge2^d/16\).
Apply the exact lift identity and \(B\le2\). \(\square\)

**Proposition 9.2 (uniform-tail obstruction).** In the independent fair
signed-tree model of Section 3, no fixed \(a,c>0\) can give
\(\Pr(R\le cN)\le e^{-aN}\) for ALL additive sweeps in all sufficiently
large dimensions.
**Proof.** Set \(k=2^d\), and choose the core binary-weight order on the
top \(d\) coordinates, with lower weights \(k2^j\). When all \(k-1\)
top tree signs are positive, all core comparisons increase; when all are
negative they decrease. In either event \(C_{\rm core}=2\), \(B=2\),
and \(R=2N/k-1\), independently of lower signs. The two disjoint events
have total probability \(2^{-(k-2)}\). For a fixed \(c>0\), choose a fixed
power of two \(k\ge2/c\) and let \(n\to\infty\). The positive constant
probability contradicts the proposed exponentially vanishing tail. \(\square\)

This excludes that unconditioned proof strategy; it does not exclude
exceptional good ranks or the original extremal constant-density conjecture.
Similarly, any eventual bound \(R\ge aN-bq\) for EVERY paired rank and
EVERY actual sweep would, after arbitrary row lifting and division by \(T\),
force \(C_{\rm core}\ge a2^d\) for EVERY paired core. Its quantifiers are
stronger than the existence statement defining \(M_n\).

## 10. An actual obstruction to exact conditional doubling

A proposed missing inequality was
\(\mathbb E_{\rm fresh}C(\text{child},w)\ge2\min_vC(\text{parent},v)\)
for every paired parent and actual additive child sweep. It fails.
In dimension 4, use normalized phase mask 50, where the index of
\(\theta_h(u)\) is \(2^3-2^{3-h}+u\) for \(h=0,1,2\).
Its exact cyclic minimum over all signed additive chambers is 6.
For the dimension-5 weights \((16,1,10,8,12)\), all subset scores are distinct,
and no consecutive comparison, including the closing edge, changes only
the lowest bit. Every one of the 256 fresh assignments therefore gives
\(R=C=10<12\). The supplement supplies the full integer order and finite
certificate. Chamber completeness for the parent uses the known Q4 region
count [2]; no extrapolation to higher dimensions is involved.

Allowing losses remains a possible route. Cyclic bottom-bit accounting gives
\(\mu_C=F+L\) and \(\sum_uA_u^2\le8L\le4N\). Hence
\[
\Pr_{\rm fresh}(C\le\mu_C-t)\le e^{-t^2/(2N)}.
\]
With \(t=2n\sqrt N\), union over \(3^{n^2}\) chambers selects one child
within this loss of every conditional mean. If one could establish
\(\mu_C\ge2z(\text{parent})-a_n\), where \(z=\min_wC\), and verify
a seed with
\[
\frac{z_{n_0}}{2^{n_0}}>
\sum_{j>n_0}\left(\frac{a_j}{2^j}+\frac{2j}{2^{j/2}}\right),
\]
then telescoping would prove a positive density for a compatible family.
The uniform mean inequality and a sufficient PAIRED seed are both unproved.
The general signed-tree lower bound is not automatically a paired seed.

## 11. Relation to existing results

**Prefix separation and noncoherence.** The present admissibility condition agrees with the prefix k-set condition for pseudo-sweep permutations [1]. Maclagan studies coherence and flips of Boolean term orders [2]. Edelman, Gvozdeva, and Slinko explicitly discuss an order that is not additively representable even though all its initial segments are threshold complexes [3, Example 1]. These works already establish the qualitative obstruction. Our target is a growing lower bound on the minimum run count over all linear sweeps.

Version 1.0 used bounded differences [6]; the present all-weight coefficient uses the known read-k theorem [9]. Neither concentration inequality is claimed as new.

**Signed trees.** The representation in Section 3 uses an established permutation construction. In particular, the ancestor sign rule used in Section 4 is [4, Observation 2.10]. We locate the quantitative argument in the multiplicity bound, the low-run tail estimate for arbitrary reordered leaves, and its combination with cube sweep counts, rather than in the tree representation itself. The read-k concentration theorem in this revision is explicitly credited to [9].

**Alternating subsequences.** Pinsky [8, Theorem 1] proves that the mean longest alternating subsequence length for a uniformly random separable permutation of size \(N\) is asymptotic to \((2-\sqrt2)N\). With either initial direction permitted, that length equals \(R+1\) for every sequence of distinct values of length at least 2. Thus the statistics have a direct relationship. The relevant differences are the probability model and the simultaneous requirement: our tree shape and cube labeling are fixed, every sampled rank has strictly separable cube prefixes, and the theorem tests all additive sweeps of that same rank.

The existing mean theorem cannot simply be applied after each sweep. A combinatorially separable permutation need not have separable cube prefixes, and composing an admissible rank with a linear sweep need not produce a combinatorially separable permutation. The supplement gives two explicit \(Q_2\) examples. These examples rule out the direct substitution of that mean theorem; they do not rule out other possible reductions.

**Scope of the contribution claim.** The closest sources were checked at their pertinent definitions and theorem statements, with additional citation-chain searches. This establishes substantial antecedents and identifies the specific quantitative statement proved here. It is not a certificate of exhaustive historical priority. The manuscript presents a mathematical theorem and a bounded comparison with prior work, without claiming a new definition, a new concentration inequality, or a new theory of signed trees.

## 12. Interpretation, limitations, and further questions

The theorem measures a gap between thresholdwise linear representability and a single linear score ordering. Every initial binary classification problem for the constructed rank has an explicit strict separator. Yet a single additive score cannot order the vertices so that their ranks have few monotone pieces. This is a precise combinatorial limitation of a common linear ranking, even when the common weights are chosen optimally.

The result does not by itself give a statistical learning guarantee, a lower bound for a particular nonlinear model, or an empirical claim about biological landscapes. Its immediate value is as an extremal statement about orders and linear sweeps. Connections to ordinal modeling or preference representations would require additional model-specific arguments.

Several questions remain. First, can the \(n^2\) denominator be removed, so that \(M_n\ge c_0 2^n\) for a fixed \(c_0>0\)? Second, can a deterministic explicit family achieve the general lower bound proved here by the probabilistic method? Third, what are the sharp order of growth and constant for \(M_n\)? The finite sufficient inequality can also be sharpened by using more information about actual cube chambers or comparison-label multiplicities. The present revision improves the general coefficient and proves the restricted-class results above. It does not settle these unrestricted questions.

## 13. Verification and author disclosure

The general proof in Sections 3--6 and restricted-class proofs in Sections 7--9 are analytic and cover their stated dimensions. Finite computation is supplied as an independent implementation check of its local statements, not as a replacement for that proof. The supplement specifies the verification coverage, software, and machine-readable receipts. No experimental dataset or external participant data is used.

Hongju Liu is the human author of record and responsible depositor. Substantial assistance from ChatGPT (OpenAI) under human direction was used for mathematical development, literature retrieval, proof auditing, computation, drafting, editing, and publication preparation. The checks reported here are internal mathematical and computational checks; no independent external peer review or separate final human line-by-line verification is claimed. DOI registration and archival timestamps identify a version and its bytes, rather than establishing correctness or priority.

This is adjacent first-party research hosted in the author's existing research repository. It does not amend the Trinity Accord or its Bitcoin Originals. Newly written material is released under CC BY 4.0 to the extent the depositor holds rights; cited third-party works retain their own rights.

## References

1. A. Padrol and E. Philippe. *Sweeps, polytopes, oriented matroids, and allowable graphs of permutations*. Combinatorica **44**, 63--123 (2024). DOI: [10.1007/s00493-023-00062-3](https://doi.org/10.1007/s00493-023-00062-3). [Author preprint](https://arxiv.org/html/2102.06134v3).
2. D. Maclagan. *Boolean term orders and the root system \(B_n\)*. Order **15**, 279--295 (1998). DOI: [10.1023/A:1006207716298](https://doi.org/10.1023/A:1006207716298). [Author preprint, revised 1999](https://arxiv.org/pdf/math/9809134).
3. P. H. Edelman, T. Gvozdeva, and A. Slinko. *Simplicial complexes obtained from qualitative probability orders*. SIAM J. Discrete Math. **27**(4), 1820--1843 (2013). DOI: [10.1137/110844568](https://doi.org/10.1137/110844568). [Author preprint](https://arxiv.org/pdf/1108.3700).
4. F. Bassino, M. Bouvel, V. Féray, L. Gerin, and A. Pierrot. *The Brownian limit of separable permutations*. Ann. Probab. **46**(4), 2134--2189 (2018). DOI: [10.1214/17-AOP1223](https://doi.org/10.1214/17-AOP1223). [Author preprint](https://arxiv.org/html/1602.04960v3).
5. I. M. Gessel and Y. Zhuang. *Shuffle-compatible permutation statistics*. Adv. Math. **332**, 85--141 (2018). DOI: [10.1016/j.aim.2018.05.003](https://doi.org/10.1016/j.aim.2018.05.003). [Author preprint](https://arxiv.org/pdf/1706.00750).
6. C. McDiarmid. *On the method of bounded differences*. In J. Siemons (ed.), *Surveys in Combinatorics, 1989*, London Mathematical Society Lecture Note Series **141**, Cambridge University Press, pp. 148--188 (1989). DOI: [10.1017/CBO9781107359949.008](https://doi.org/10.1017/CBO9781107359949.008).
7. R. P. Stanley. *Valid orderings of real hyperplane arrangements*. Discrete Comput. Geom. **53**, 951--964 (2015). [Author manuscript](https://math.mit.edu/~rstan/papers/vis.pdf).
8. R. G. Pinsky. *Mean and variance of the longest alternating subsequence in a random separable permutation*. arXiv:2310.08664v2 (2023), preprint. [Full text](https://arxiv.org/pdf/2310.08664).

9. D. Gavinsky, S. Lovett, M. Saks, and S. Srinivasan. *A Tail Bound for Read-k Families of Functions*. arXiv:1205.1478 (2012), Theorem 1.1. [Primary preprint](https://arxiv.org/pdf/1205.1478); [ECCC TR12-051](https://eccc.weizmann.ac.il/report/2012/051/).
