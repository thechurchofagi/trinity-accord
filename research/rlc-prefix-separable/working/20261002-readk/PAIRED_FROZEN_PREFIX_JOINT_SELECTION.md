# Joint selection with a protected prefix

Status: analytic all-dimensional conditional selection theorem. The
original all-weight M_n >= c 2^n problem remains OPEN. Published v1.0
is unchanged. This is a conditioned refinement of the existing raw-support
entropy lemma, not a new entropy method or new tree representation.

## 1. Conditional injection, with exact frozen-label cost

Fix a root phase and ANY set F of non-top paired labels, at arbitrary
fixed values. Randomize every remaining label independently and uniformly.
For a complete vertex permutation p write S(p) for its RAW active non-top
label set, before any graph cancellation, q=|S(p)| and
q_f=|S(p) minus F|. Only q_f fresh labels affect its comparison-sign word.

**Lemma.** For every K>=1,

    P(R<=K | fixed F) <= 2^(-q_f) sum_(j=0)^(K-1) binom(N-2,j),
    q_f >= q-|F|.                                  (1)

Proof. A comparison sign is its deterministic forward-Gray sign times
the spin of exactly one label. Every active fresh label occurs at least
once; changing it changes that comparison sign. Thus all2^q_f fresh
assignments give distinct sign words. A complete cube permutation has a
top-leading comparison somewhere, and its sign is fixed by the root.
A transition word and this known sign reconstruct the whole sign word.
Consequently the transition words are also distinct. R<=K means at most
K-1 ones among N-2 transition positions, giving the integer count in(1).
Fresh inactive labels do not change the result and can be averaged out.

Fixing the root, or another known comparison phase, is necessary for this
injection as stated. Complementing EVERY label and the root flips all
comparison signs while retaining the transition word. The Q2 certificate
records this two-to-one failure if the phase is incorrectly left free.

This conditions the previously proved unconditioned lemma of checkpoint50;
the important new use is legitimate joint existence after choosing and
retaining a protected finite prefix. It does not select a different rank
for each scan or for each success condition.

## 2. Explicit entropy estimate

For N=2^n and K=N/128, the inherited elementary binomial entropy estimate
gives sum_(j<=K-1) binom(N-2,j) < 2^(17N/256). Indeed

    H_2(1/128)=7/128+(127/128)*log_2(128/127)<17/256,

using log2>2/3 and log(1+t)<t. The same bound with N instead of N-2
is conservative. The upper count3^(n^2) includes ALL generic signed
additive order chambers. These counting and entropy tools are inherited.

If only the upper five-bit prefix is frozen, |F|=15. For EVERY scan with
q>=N/8, equation(1) therefore gives

    P(R<=N/128) < 2^(15-15N/256).                    (2)

The union over all such signed chambers is below one for every n>=13:
using log3<9/8 and log2>2/3 its logarithm is at most

    (9/8)n^2 + 10 - 5N/128 < 0.

The base n=13 is checked with integers, and N/n^2 increases thereafter.
Thus an ARBITRARY fixed five-bit paired prefix can be retained while
choosing one full rank handling the entire large-q class. A particular
protected prefix is not an independent existential witness to be combined
after the fact: it is fixed BEFORE all remaining labels are sampled.

## 3. The SAME rank covers three proof classes

Retain the explicit five-bit prefix mask2 with normalized root0 from
checkpoint59. It has cyclic minimum12 and linear minimum11 over ALL
signed five-dimensional additive scans, independently certified.

For each n>=18 there exists ONE paired rank retaining that prefix such
that, simultaneously, for EVERY generic SIGNED additive scan:

* if q>=N/8, then R>N/128;
* if m_0+m_1>=N/8, then R>N/32;
* if the lower-coordinate subset-score gaps exceed the signed five-core
  diameter, then C>=3N/8 and R>=3N/8-1, for ANY generic five-core weights.

The third guarantee holds for EVERY lower-label choice by59's exact row
proof, so it adds no random failure event. The second uses58's conditional
single-level bound: one level has m_h>=N/16, and conditioning on all
other labels gives failure at most exp(-N/512). Conservatively allow two
level-specific events. They use the SAME independent fresh labels as(2).

For N>=320,2^(15-15N/256)<=exp(-N/128), using log2>2/3. Thus the total
failure probability is at most

    3^(n^2) [ 2 exp(-N/512) + exp(-N/128) ]
       <= 3 * 3^(n^2) exp(-N/512) < 1, n>=18.

At18,(9/8)+(9/8)*18^2<2^18/512; the normalized exponential margin grows.
This is a rigorous joint union bound. It resolves the fixed-core
compatibility question left open in59. It does NOT show that the same
two-level guarantee can be imposed at every step of a compatible path.

The simpler joint selection covering q>=N/8 and m_0>=N/8, with respective
R>N/128 and R>N/16, already works at n>=15: bound the two failure terms
by2*3^(n^2)*exp(-N/128), and use
1+(9/8)*15^2<2^15/128. The protected row guarantee again comes for free.

## 4. A uniform four-coordinate extension, preserving ANY parent

**Theorem.** For every n>=18 and EVERY fixed paired parent of dimension
n-4, one four-bottom-level child simultaneously handles ALL signed
scans with q>=N/8 at R>N/128 and ALL scans with m_0+m_1>=N/8 at R>N/32.
The parent's root phase and all upper labels are preserved.

There are |F|=2^(n-5)-1=N/32-1 frozen non-top labels. Hence q_f>=3N/32
on the large-q class, and the entropy failure bound is at most

    2^(-7N/256) <= exp(-7N/384) <= exp(-N/128).

The first two bottom levels are fresh, so the same conditional two-level
bound and joint union argument apply. The guarantee is uniform in the
parent; no unproved conditional mean-doubling inequality is used.
If the parent also retains protected core mask2, the row theorem holds
for this SAME child. Repeating in steps of four gives a compatible path
with these guarantees at its four-step endpoints; it does not imply
them at every intermediate dimension. The all-weight target remains open.

## 5. Exact audit and precisely what is still missing

verify_frozen_prefix_entropy.py checks ALL24 Q2 and ALL40,320 Q3 arbitrary
vertex permutations. For EACH it freezes EVERY label subset at EVERY
assignment, enumerates EVERY active fresh state, verifies distinct sign
and transition words, and checks EVERY run threshold against its exact
binomial integer count. Q3 coverage:1,088,640 frozen contexts,
1,847,680 fresh states and7,620,480 threshold checks. It also proves the
explicit n13,n15,n18 bases with exact Fraction arithmetic and retains the
phase-free injection counterexample. Root0 is the enumerated phase;
the analytic injection proof handles any fixed phase. Zero violations,
6.971875821996946s; stream
6d2bd0ec59e07527091d4a3d1bc6c9cc7c78f0c75b2dc3f63f252bddaff8d64d;
receipt6362bb368ba599cd33ea7227e0ab3bb3915e9c63c412600e71c27554def1f38d.
Receipt:frozen_prefix_entropy_certificate.json; log:frozen_prefix_entropy_run.log.

The main remaining class is now explicitly q<N/8 AND m_0+m_1<N/8,
without separated protected-core rows. The already proved q<=2 universal
bounds and other universal restricted-scan lemmas still apply, but do not
cover that entire remainder. Low-run nonadditive poset orders cannot stand
in for genuine scans. No finite or sampled Q6 result is substituted for
an all-dimensional conditional mean or support theorem. Next analyze the
actual equal-translation duplicate projections on this joint remainder,
or a selected-parent mean inequality with summable normalized loss.
