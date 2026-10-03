# Complete next-insertion exclusion over an improving parent wedge

Date: 2026-10-03. Exact restricted-family theorem with executable certificate.
The dimension-uniform M_n constant lower bound remains OPEN. Published v1.0
is unchanged. Hyperplane arrangement refinement and Gray reflection graphs
are established tools reused here; no historical-priority claim is made.

## Statement

Let

    c(t,A)=(A+4,A+6,A+3,A,A+8,A+16+8t,A+28+8t,0),
    3/4<t<=1, 29+8t<A<23+16t.

As certified in CARDINALITY_PARENT_METRIC_WEDGE.md, every such eight-core
has the same cardinality-first order and the same interior graph:
D_int=18, E_int=54, F=E_int-D_int=36. Extend it by

    d(t,A,H)=(H+c_0(t,A),...,H+c_7(t,A),0).

For EVERY generic real triple (t,A,H) in this domain, the nine-core
interior net energy satisfies

    E_int(d)-D_int(d) <= 72.

For each fixed allowed (t,A), the separated-offset insertion lemma attains
72 for all sufficiently large H. Consequently, the minimum asymptotic
run density after appending dominant numerical tails is exactly

    (512-72)/1024 = 55/128.

Thus inserting another highest secondary coordinate cannot improve the
eight-core's normalized limit anywhere in this continuous metric wedge.
This statement classifies three real parameters, rather than merely
testing a few parent vectors or integer offsets. It does not classify
the entire parent chamber, other insertion positions, or arbitrary scans.

## Exact covering proof

The wedge closure is the triangle with vertices

    (t,A)=(3/4,35),(1,37),(1,39).

Write c(t,A)=b_0+t*b_1+A*b_2 where

    b_0=(4,6,3,0,8,16,28,0),
    b_1=(0,0,0,0,0,8,8,0),
    b_2=(1,1,1,1,1,1,1,0).

Only a cross-face comparison inside a nine-dimensional cardinality layer
depends on H. Its equality is H=c(t,A) dot (y-x), with old vertices
|y|=|x|-1. Enumerating ALL such differences gives precisely 422 distinct
affine breakpoint planes H=u+v*t+w*A. Same-face orders remain fixed.

The ordering of these 422 breakpoints can change only on pairwise plane
comparison lines. Compare each difference at all three triangle vertices.
A linear form crosses the interior exactly when these values have both
signs. After primitive integer normalization, exactly nine such lines
remain, represented by (u,v,w) with equation u+v*t+w*A=0:

    (7,-8,0), (22,16,-1), (26,12,-1), (30,8,-1),
    (36,0,-1), (37,0,-1), (38,0,-1),
    (51,24,-2), (53,24,-2).

Exact Fraction polygon clipping by these lines gives 16 positive-area
cells. Their exact areas sum to the triangle's area. In each cell all
pairwise breakpoint comparisons have a fixed sign. Thus between any
two consecutive breakpoint planes, the entire child order is fixed.
Every cell has 423 open H intervals, including the two unbounded ones.
One exact rational representative per interval therefore determines the
graph for the whole cell-interval region. This covers 6,768 regions.

The certificate stores all cell vertices, nine line signs, rational
representatives, all breakpoint values, every D_int/E_int/net triple,
order hash chains, and optimizing spin certificates. For every region,
the exact integer reflection-graph optimizer gives F<=72. Each of the
16 cells attains maximum 72, also independently realized by a genuine
signed integer score scan sorted from scratch.

Boundary points create no extra generic orders. If the child order at a
point on a refinement line or on t=1 is generic, its finitely many strict
within-layer comparisons remain strict in an open neighbourhood. The
allowed open wedge is dense in its closure along these allowed points,
so a nearby point off all nine lines has the identical child order.
Therefore the interior cell bound applies at every allowed generic
boundary point. Parent-tie edges A=29+8t, A=23+16t and t=3/4 are excluded
from the stated hypothesis.

Finally, the earlier all-dimensional core-tail reduction converts this
finite core net into the limiting run density. The lower bound 55/128
here is only for this stated core-tail family; it is not a lower bound
on RLC over all linear scans of a fixed ranking or on M_n.

## Audit and next precise gap

Run verify_cardinality_wedge_next_insertion.py. It uses no floating-point
LP, evaluates every spin exactly and retains an independent actual
score-sort realization of each cell optimum. There are 802 distinct
child orders. Zero violations were found. Detailed digest and elapsed
time are stored in cardinality_wedge_next_insertion_certificate.json and
cardinality_wedge_next_insertion_run.log.

Next: preserve the same full parameter covering, but test all nine
possible numerical positions of the inserted coordinate. Reuse each
distinct child order once and permute the position of its insertion bit;
do not repeat the real-parameter partition. A success would give another
restricted all-dimensional upper example through core-tail reduction;
a failure would exclude this entire insertion route, but would still
not prove the desired general constant lower bound.
