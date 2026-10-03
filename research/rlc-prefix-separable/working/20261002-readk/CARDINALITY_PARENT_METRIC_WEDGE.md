# An exact metric threshold inside a single coherent parent chamber

Date: 2026-10-03. Research theorem in a completely specified parameter
family. Main M_n constant density remains OPEN. The known geometric
idea of arrangement refinement and inherited Gray tools are reused;
this does not claim their invention or historical priority.

## 1. Family and exact optimization theorem

Keep the entire seven-bit parent scan order fixed while varying

    b(t)=(4,6,3,0,8,16+8t,28+8t),  0<=t<=1.

Insert the eighth, highest coordinate by

    c(t,A)=(A+b_0(t),...,A+b_6(t),0),  A real.

Restrict to pairs (t,A) for which every fixed-cardinality secondary
layer is generic. A sufficiently large common primary coefficient
always realizes the order by genuine positive additive weights.
Let F(t,A)=E_int-D_int for the eight-bit interior graph.

**Theorem.** For EVERY real generic pair in the specified domain,

    F(t,A)=36   if 3/4<t<=1 and 29+8t<A<23+16t;
    F(t,A)<=32 in every other generic case.

At every t outside the improving range, a fully separated insertion
attains F=32. Thus optimizing over ALL real A gives

    max_A F(t,A)=32  for 0<=t<=3/4,
    max_A F(t,A)=36  for 3/4<t<=1.

The general numerical-tail extension makes the corresponding optimal
limiting run density exactly

    7/16   for 0<=t<=3/4,
    55/128 for 3/4<t<=1.

These are restricted-family lower AND upper optima; they do not give
an unrestricted Gray optimum or any value or lower bound of M_n.
The entire parent order, not just its run count, is identical on the
whole interval t in [0,1]. Yet the best descendant density jumps at
the exact interior parameter t=3/4.

## 2. Strict parent-order certificate

The cardinality-first order of b(0) and b(1) is identical. Within each
cardinality layer its consecutive difference rows are linear forms
in b. All 120 such rows have strictly positive integer values at BOTH
endpoints. Every value at b(t) is the convex combination of these
endpoint values and stays strictly positive. Therefore all real
t in [0,1] have exactly this parent order; this assertion does not
come from checking a finite sample.

## 3. Complete real two-parameter certificate

Every changing comparison in an inserted cardinality layer is between
two faces. For |y|=|x|-1 its breakpoint is

    A=b(t) dot y-b(t) dot x = a+s*t.

There are exactly 145 distinct affine breakpoint lines. The exact
intersection parameters inside [0,1], including its endpoints, are

    0, 1/8, 1/4, 3/8, 1/2, 5/8, 3/4, 7/8, 1.

No other intersection parameter is omitted: the verifier forms ALL
adjacent-cardinality vertex differences, deduplicates their affine
lines, and computes every pairwise intersection as a Fraction.
On each of the eight open t strips between consecutive values, the
order of these lines is fixed. Exact rational representative t values
and every open A interval then cover all generic two-parameter cells.
The nine critical vertical sections are independently classified,
including their merged breakpoint lines. Nongeneric A endpoints
are excluded explicitly.

The resulting 2,092 generic interval evaluations cover 448 distinct
child orders. Each graph and spin optimum uses exact integers.
This is finite, exact arrangement coverage of a real two-parameter
domain, not an extrapolation from numerical samples. Because every
child comparison has a constant sign in each covered cell, the
verified order and graph extend throughout that entire cell.

Across the first six open t strips, the maximum net energy is 32.
It remains 32 at t=3/4. In each of the last two open strips, and at
t=7/8 and 1, exactly one A interval has net energy above 32. Its
endpoints are precisely 29+8t and 23+16t. Its graph is the same
eight-bit graph in every such cell, with D_int=18, E_int=W_int=54,
and net 36. All other covered cells have net energy at most 32.
The certificate asserts every one of these statements, rather than
only the best sampled value.

## 4. The two explicit geometric inequalities

The lower boundary comes from input integers y=80 and x=13:
|y|=2, |x|=3, and

    b(t) dot 80 - b(t) dot 13 = 29+8t.

The upper boundary comes from y=104 and x=23:
|y|=3, |x|=4, and

    b(t) dot 104 - b(t) dot 23 = 23+16t.

Their strict order leaves a nonempty insertion window exactly when
29+8t<23+16t, equivalently t>3/4. The window has width 8t-6 and can
be arbitrarily narrow while the parent order stays unchanged.
This identifies the specific missing metric information in the
parent-order-only induction. It is not an assertion that all possible
extensions depend only on these two inequalities.

## 5. Audit and continuation

Run verify_cardinality_parent_metric_line.py. It certifies endpoint
margins, all affine breakpoints and intersections, every generic
cell graph, exact spin optima, and the improving wedge. Zero
violations. Its digest is
08a165b02737ce991b276e8fec9e4ee8cb034e0e4797cc9b4e9b8a7bcce4260a.
The recorded elapsed time is in the executable receipt.

The theorem closes the specified metric-line gap. It does not remove
the n^2 denominator in the general lower bound. A useful next analytic
step is to test whether the exact improving wedge can be maintained
under repeated coherent insertions, while tracking all changed
breakpoint inequalities. Automatic doubling in the separated regime
cannot help, and the fixed nine-core single-offset route has already
been rigorously closed. Any proposed recurrence needs all-dimensional
inequalities, not only a list of successively larger finite seeds.
