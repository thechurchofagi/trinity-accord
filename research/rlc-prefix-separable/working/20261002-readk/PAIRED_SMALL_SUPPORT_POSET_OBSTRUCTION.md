# A small-support direction-only obstruction

Status: analytic all-dimensional exclusion of a relaxation of the ORIGINAL
target's small-support defect route. The genuine-additive support-defect
inequality and main M_n theorem remain OPEN. Published v1.0 unchanged.
The construction is a NONADDITIVE Boolean-poset extension, not a permitted
scan in the definition of RLC.

## 1. The exact missing inequality and the tested relaxation

The concurrent original-target continuation proves one paired rank can
simultaneously handle every actual additive sweep with raw comparison
support q(p)>=2^n/8. Its remaining sufficient obligation is an absolute
a>0, finite b>=0 with

    R(rho_theta composed with p)>=a*2^n-b*q(p)

for EVERY paired rho_theta and every ACTUAL additive scan p. Here q(p)
counts DISTINCT NON-TOP theta variables in the RAW comparison word,
before graph cancellation. It is not the number of surviving graph edges.

This note strictly excludes the shortcut of retaining only coordinatewise
Boolean-poset directions, even while retaining SMALL raw support. The
standard layer/poset construction itself is not claimed as a new concept;
the new audited point is its simultaneous quantitative small q, low R,
and explicit common-addition violation against this proof obligation.

## 2. Construction for EVERY paired orientation

Choose 0<=d<n with m=n-d>=3. Partition input x into a low assignment
a=x mod2^d and upper assignment u=x>>d. Define p as follows:

1. Order the low assignments a=0,...,2^d-1 numerically.
2. Inside each a, order upper Hamming weights k=0,...,m increasingly.
3. Inside each (a,k) row, sort vertices by the given rho_theta rank.

This is a complete vertex permutation tailored to rho_theta. Every paired
rank remains prefix-separable by the inherited separator theorem.

The permutation p respects EVERY positive cube-edge direction. Adding a
low input bit increases its primary low numeric assignment. Adding an
upper input bit leaves a fixed and increases its secondary Hamming row.
Both operations advance p independently of the within-row rank order.
Thus p is a Boolean-poset linear extension for every theta.

## 3. Both raw support and runs have vanishing density

Each of the J=2^d*(m+1) rows is strictly increasing in rho_theta.
Concatenating J increasing words creates at most2 additional turns at
each join, giving

    R<=2J-1=2^(d+1)*(m+1)-1.

Within a fixed low assignment, consecutive vertices differ in an upper
coordinate, so their highest changed input bit is at least d. At the
join between two low assignments, the preceding vertex has ALL upper
bits1 (the unique last Hamming row), while the next has ALL upper bits0.
Its highest changed bit is n-1, the FIXED TOP comparison. Therefore EVERY
comparison in the entire word has highest changed input bit at least d.

The maximum number of non-top paired variables at levels h>=d is

    sum_(h=d)^(n-2) 2^(n-h-2)=2^(m-1)-1.

Consequently raw support, BEFORE any graph cancellation, satisfies

    q(p)<=2^(m-1)-1.

Take d=floor(n/2). Then for every theta,

    R/2^n <=2*(m+1)/2^m ->0,
    q(p)/2^n <2^(-d-1) ->0.

For ANY absolute a>0 and finite b>=0, (R+bq)/2^n tends to0 along this
construction. Hence R>=a*2^n-bq is FALSE for this direction-only class,
whatever positive constants are chosen. This is an all-n family, not
an isolated finite-dimensional violation.

## 4. Explicit failure of additive common translation

Let x=e_d, y=e_(d+1), z=e_(d+2), fixing all other coordinates0. Both
x,y belong to the low assignment0, upper Hamming layer1. The translated
x+z,y+z belong to that same low assignment and upper layer2. The scan
sorts both pairs by their rho_theta ranks.

The highest input bit where x,y differ is d+1. Adding the common bit d+2
flips its paired controller phase; theta_(d+1) uses bits ABOVE d+2 and
is unchanged. Thus the rank comparison REVERSES for EVERY paired theta:

    x before y iff y+z before x+z.

But every additive score, signed or positive, preserves the comparison
under a common disjoint addition: s(x+z)-s(y+z)=s(x)-s(y). Therefore this
p is NOT any signed additive scan, nor a Boolean term order. In the
natural forward Gray instance the explicit contradictory requirements
are w_d<w_(d+1) and w_(d+1)<w_d.

This is precisely the missing geometry. Raw support plus coordinate
directions alone are insufficient. The concurrent actual-additive
inequality is NOT refuted by this construction, and neither is M_n.
Known common-addition consistency is standard Boolean term-order
structure, as in Maclagan, Boolean Term Orders and the Root System B_n,
https://arxiv.org/pdf/math/9809134 (v2,10 March1999); it is not renamed.

## 5. Executable audit and continuation

verify_small_support_poset_obstruction.py checks41 cases Q6..Q18, natural
forward Gray plus arbitrary paired masks in smaller dimensions. It
verifies all increasing rows, the ENTIRE raw support and every comparison
leading level, actual run bounds and the exact common-addition violation.
All cube edges are checked for n<=12; larger cases check2048 selected
edges, with the explicit analytic argument above covering every edge.
Finite checks do not replace the all-n proof. Exact masks, bounds, raw
leading-bit masses, contradictory comparisons and order digests are
retained with source, certificate and log. Zero violations,
3.6120425360131776 seconds; audit SHA256
f285a777474552f0dc77b111658719eb6b288a701adc03b1faa968e0b9571148.

Next substantive gap: use true additive/common-translation constraints
in the small-support mass theorem. First audit the LOW-input/HIGH-score
lift of any genuine base scan. Such lifts may leave raw q unchanged while
replicating the base runs. Determine exactly whether small-support defect
geometry is a genuinely easier branch or embeds every original hard scan.
Do not reopen direction-only proofs or promote this nonadditive family
to a counterexample against actual scans. The main existence theorem is OPEN.
