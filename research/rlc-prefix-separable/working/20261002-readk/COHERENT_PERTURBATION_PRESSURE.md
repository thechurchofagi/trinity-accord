# Genuine perturbations and a sorted-weight density obstruction

Date: 2026-10-03. Unpublished research audit. The primary constant-density
lower bound for M_n is OPEN. Published v1.0 is unchanged.

## 1. Closing the local countermodel's missing condition

The preceding FACE_LOCAL_COHERENCE_OBSTRUCTION.md constructs a permutation
that respects a weak integer score and every small-face order, but fails
two opposite translated comparisons. It is not an additive sweep.

For any positive integer primary vector a in dimension n, put B=2^n and

    w_j=B a_j+2^j.

Then w dot x=B(a dot x)+x, where x on the right denotes the ordinary binary
integer, NOT forward Gray. If two primary scores differ, their integer
difference is at least one, while the difference between two vertex integers
has magnitude at most B-1. Therefore this generic additive scan orders by
(primary score, numerical vertex). Within a primary tie, the numerical
vertex orders strictly. No floating perturbation or limit is used.

This standard lexicographic perturbation is a tool, not a novelty claim.
It repairs global translated-difference consistency; it does not preserve
the earlier Gray-sorted bucket refinement.

The exact audit checks three primary families for each n=5,...,18:

1. All a_j=1.
2. a_j=j+1.
3. a=(1,2,4,7,10,...,3n-5), the previous k=3 greedy family.

For all 42 genuine scans, the direct Gray run density is at least 1/2.
For n<=12 the exact reflection graph minimizes over EVERY weight sign;
these finite minima are also at least 1/2. An independently realized
signed integer witness attains every computed minimum. This is finite
pressure, not a theorem about untested dimensions or arbitrary secondary
weights. No all-dimensional half-density assertion is made for these
families.

At n=18 the k=3 genuine scan has R=C=131,136; the inconsistent central
refinement had only 828. Hence this specified numerical perturbation did
not carry the apparent zero-density countermodel into the actual domain.

## 2. Sorted positive magnitudes do not ensure half density

**Theorem.** For every n>=5, the strictly increasing positive integer vector

    (1,6,8,12,16,64,128,...,64*2^(n-6))

(with no entries after 16 when n=5) is generic and has, under the FORWARD
Gray rank gamma_n(x)=x XOR (x>>1),

\[
 R(\gamma_n\circ\pi_w)=C(\gamma_n\circ\pi_w)
      =14\,2^{n-5}=\frac7{16}2^n.
\]

**Proof.** In dimension five the exact score order is

    0,1,2,3,4,5,8,9,6,7,16,17,10,11,12,13,
    18,19,20,21,14,15,24,25,22,23,26,27,28,29,30,31.

Its 32 distinct integer scores are independently checked by the verifier.
Direct evaluation of the adjacent Gray comparisons gives R=C=14.
The first comparison has sign + and the last sign -.

Every appended magnitude is greater than the sum of all earlier ones:
the seed sum is 43<64, and 43+64(2^r-1)<64*2^r. Thus the new score
order is the concatenation of the old order p and its identical upper-face
copy. If L=2^d and A_i=gamma_d(p_i), additive complement symmetry gives
the upper rank list B=L+reverse(A). Its sign word is -reverse(e), where e
is the lower sign word. The inter-face edge is positive. Since the old
first sign is + and last is -, the two internal sign words each contribute
R-1 turns and the bridge contributes exactly one. The child has 2R runs.
Its first and last signs remain + and -, and its cyclic closing sign is -,
so C=R. Induction proves the formula and genericity. End of proof.

This refutes the proposed half-density bound even in the sorted-positive
magnitude subclass in every larger dimension. It does NOT improve the
existing unrestricted Gray upper ceiling 5/16, and it does NOT give an
upper bound for M_n.

The smallest possible obstruction dimension for this sorted-magnitude
claim is five. The sorted positive arrangement has 1, 2, and 14 chambers
in dimensions 2, 3, and 4. They are generated exactly and every reflected
sign orbit has cyclic minimum at least 2^(n-1). Their coverage follows by
quotienting Maclagan's established signed chamber counts 8, 96, and 5,376
by n! 2^n. This prior-source count is not a contribution.

## 3. Exponentially long individual runs and a crossing shortcut

The proposed bound of O(n) on each individual monotone segment is false.
Let E={0,2,4,...} be the even coordinates and O={1,3,5,...} the odd ones,
put B=1+sum_(j in E) 2^j, and assign

    w_j=2^j       for j in E,
    w_(2r+1)=B*2^r.

All subset scores are distinct: even-coordinate subsets give distinct
scores below B, and odd-coordinate scores are different multiples of B.
The first contiguous score block has all odd bits zero, and has
2^ceil(n/2) vertices in increasing even-coordinate binary order.
On this face,

    gamma_n(x)=x_0 + sum_(j in E, j>0) (2^j+2^(j-1))*x_j.

The highest differing free coordinate decides both its binary order and
its Gray order, with positive direction. Hence the entire initial block
is Gray-increasing. Individual monotone runs can contain at least
2^ceil(n/2)-1 edges in a genuine generic scan. This excludes the suggested
longest-run shortcut, not any bound on the aggregate number of runs.

A separate exact Q6 integer vector
(133155,187135,633646,896257,867970,597105) has coordinate crossing counts
(29,27,29,29,31,27). Thus it is also false that every generic scan has a
coordinate crossed at least 2^(n-1) times. This finite counterexample is
checked exactly; no asymptotic conclusion follows.

## 4. Reproducibility and exact remaining gap

Run verify_coherent_perturbations.py. Its JSON receipt records all integer
weights, order hashes, genuine perturbation run counts, exact sign minima
through n=12, the sorted small-chamber coverage, and the separated witness
through n=18. It also checks the controller-frozen face construction
through n=18 and the Q6 crossing certificate. There is no floating solver.

Exploratory pressure first exposed a sorted positive Q5 counterexample
(1522,194122,315647,431098,555729). Exact integer search replaced it by the
short seed above; the large seed is not needed for the proof.
The replay script explore_sweep_variation.py and its separate exploratory
receipt retain seeds, domains, observed results and failed hypotheses.
No general density result is derived from random observations.

The needed statement remains a positive net-energy deficit for all genuine
generic magnitude chambers, or a new prefix-separable rank family. Sorting
magnitudes by coordinate and numerical refinement do not resolve it.
The next construction route is coordinate-adaptive trees; their unconditioned
tail must be audited before using the same union-bound method.
