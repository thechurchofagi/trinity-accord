# Conditional extension of arbitrary paired parents

Status: analytic all-dimensional restricted-scan theorem, with exhaustive
small-dimensional integer checks. The original existential M_n >= c 2^n
problem remains OPEN. Published v1.0 is unchanged. The fresh single bottom
bit theorem in master checkpoint 55 is prior work and is credited here.
This note extends it to any single level and to a bottom block.

## Definitions and exact influence bounds

Use the existing forward-Gray paired rank: output bit h is
x_h XOR x_(h+1) XOR theta_(h,x>>(h+2)) for h<n-1; the top bit is
x_(n-1) XOR a fixed root phase. For a complete vertex permutation p let
m_h count adjacent comparisons whose highest changed input bit is h.
Comparison signs at level h depend on exactly the indicated theta label,
regardless of changes in lower output bits. R is one plus the number of
sign changes in the comparison-sign word. It is not the number of runs
in the vertex permutation itself.

Two successive level-h comparisons have the same prefix label, because
their shared middle vertex fixes all input bits above h. Their signs are
opposite: x_h changes twice, while the controller x_(h+1) stays fixed.
Thus their turn is forced and independent of theta. For any label u at h,
all turns affected by its spin have their middle vertex in u's prefix
cylinder. Middle vertices are distinct and that cylinder has 2^(h+2)
vertices. This proves an exact affected-turn bound 2^(h+2), without
assuming independent turns or assuming an additive scan.

## Single fresh level, all other labels fixed

Fix EVERY label except level h, including both higher and lower levels.
Choose the remaining spins independently and uniformly. Let D_h be the
number of consecutive comparison pairs both leading at h, and e_h the
number of word endpoints leading at h (at most two). The exact identity is

    R = C_0 + D_h + sum_u Y_u(theta_u),       C_0 >= 1.

Y_u counts boundary turns with exactly one level-h comparison. If k_u is
the number of such positions, Y_u(0)+Y_u(1)=k_u. In particular

    sum k_u = 2 m_h - 2 D_h - e_h,
    E R = C_0 + m_h - e_h/2 >= m_h.

Put A_u=Y_u(0)-Y_u(1). The cylinder charge above gives

    sum A_u^2 <= sum k_u^2
                <= 2^(h+2) sum k_u <= 2^(h+3) m_h.

Writing each centered two-state term as A_u times an independent fair
sign divided by two, the cosh moment bound gives
P(R<=E R-t)<=exp(-2 t^2/sum A_u^2). Zero variance is interpreted
deterministically. Consequently, for m_h>0,

    P(R <= m_h/2) <= exp(-m_h/2^(h+4)).       (1)

At h=0 this is the checkpoint-55 result, not a new discovery. At h>0 it
is a conditional extension; upper labels are not randomized or replaced.

## Several fresh bottom levels

Fix ANY upper paired parent in dimension n-H, where 0<H<n. Retain its
root and all its labels as the upper levels, and randomize only levels
0,...,H-1. Let m_low=sum_(h<H) m_h. A turn touching a fresh comparison
has expectation at least 1/2: two different fresh labels, or a fresh and
a fixed label, give exactly 1/2; identical labels give a forced turn.
There are at least m_low-1 such turn positions. Hence E R>=m_low/2.

Let C_u count affected turns in which label u appears and the other
comparison has a different label. Changing u changes R by at most C_u.
The same middle-vertex charge gives C_u<=2^(h+2)<=2^(H+1), and counting
fresh-edge incidences gives sum C_u<=2m_low. Therefore

    sum C_u^2 <= 2^(H+2) m_low.

The standard bounded-differences inequality, applied to independent
fresh labels (not to turns), gives

    P(R <= m_low/4) <= exp(-m_low/2^(H+5)).  (2)

This uses a known concentration theorem. One primary reference is
Lutz Warnke, "On the method of typical bounded differences," arXiv:1212.5796,
v1 (23 December 2012), Theorem 1, applied to -R:
https://arxiv.org/pdf/1212.5796 . The new calculation here is the exact
paired-label cylinder bound and parent-preserving conditional application.

## Uniform two-level corollary with explicit constants

**Theorem.** For EVERY n>=18 and EVERY normalized paired parent of
dimension n-2, there is ONE bottom-two-level child such that EVERY generic
SIGNED additive scan with m_0+m_1 >= 2^n/8 satisfies R>2^n/32.
The same statement holds for an arbitrary fixed root phase.

Proof. If m_0+m_1>=N/8, one of these two counts is at least N/16.
Condition on all other fresh labels and apply (1) to that level.
Averaging over the conditioned labels retains the same bound. Failure
of R>N/32 for the scan has probability at most exp(-N/512).
Using the inherited upper bound 3^(n^2) on all signed additive order
chambers, the conservative union bound is

    2 * 3^(n^2) * exp(-2^n/512) < 1.

Indeed log 2<1 and log 3<9/8, and at n=18,
2^18/512=512 > 1+(9/8)*18^2. The ratio 2^n/n^2 increases for n>=3,
so the inequality persists. This chooses a single extension for all
qualifying scans. The upper parent is not required to be randomly chosen.
For a fixed root-1 parent, global output complementation transfers the
root-0 statement, with the corresponding label complementation.

The weaker general block estimate (2) also yields a simultaneous
extension if 3^(n^2) exp(-delta*2^n/2^(H+5))<1. No claim is made that
this covers scans of smaller m_low or that it is compatible with an
independently selected rank from the large-raw-support entropy argument.

## Independent exact pressure checks and remaining gap

verify_bottom_block_extension.py uses integer ranks and actual comparison
signs. It checks every signed chamber, every upper parent, every fresh
assignment for (n,H)=(3,2),(4,2),(4,3): 16,224 contexts and 1,377,024
full-rank words. It additionally checks all 40,320 arbitrary Q3 vertex
permutations, with all eight fresh assignments each. Every possible
conditioning on other levels is audited for the single-level affine
formula, mean, two-state differences and variance bound. Root phase zero
is the enumerated case; arbitrary root phase follows analytically above.

Receipt: bottom_block_extension_certificate.json; log:
bottom_block_extension_run.log. Zero violations, 28.17572228499921 seconds;
audit stream f144cd0fd6498d27ca097c31710e088f1542a47325a33f7861d6aba692f905ff;
receipt digest 25a6c2822bc85112d40c340865601539a446d5b19e3e9218977c65aac78a2f6b.
The finite checks support but do not replace the proof for all n.

The exact main gap is the low-bottom-comparison-mass class, and the
existence of compatible parents protecting their constrained translated
duplicate projections. Checkpoint 57 supplies a genuine ZERO-fresh-edge
counterexample to exact conditional mean doubling; it does not refute
the weaker controlled-loss reduction or the original existential goal.
Simply combining two separate existential ranks is invalid. A useful
next test is whether the conditional mean loss has polynomial size or
can be amplified to a fixed fraction of N on genuine scans while the
parent's *minimum over every signed additive scan* is retained.
