# Complete audit of the six-dimensional cardinality-layer subclass

Date: 2026-10-03. Research draft and exact finite subclass theorem.
The constant-density lower bound for M_n remains OPEN. This is NOT an
exact value for unrestricted Gray G6, or for the extremal M6.

## 1. Genuine scan class and theorem

Write x=(y,z), y in Q5 and z in {0,1}, with z the highest coordinate.
For secondary real coefficients s=(s_0,...,s_4), order first by |y|,
then by z, then by s dot y. Require that the secondary scores in each
fixed-cardinality y layer are distinct. This is a genuine additive order:
after subtracting the smallest s_j and adjusting the common coefficient,
choose positive t larger than every within-layer secondary span and
choose B with B-t greater than every adverse inter-layer secondary gap.
Then weights (B+s_0,...,B+s_4,t) induce exactly that order.
The highest magnitude t is its unique minimum. Include every input
reflection, equivalently every sign choice of these magnitudes.

**Theorem.** Across this entire class and every reflection,

    min R = 29,       min C = 30.

The integer weights (-29,-31,28,25,33,12) attain both minima.
This proves the earlier counterexample is optimal WITHIN this precisely
specified class. It does not cover other interleavings of cardinality
layers, different secondary models, or all six-dimensional chambers.

## 2. Complete reduction of secondary chambers

The five secondary coefficients are distinct, since otherwise singleton
layer scores tie. Sort them, subtract the smallest, and write

    (0,a,a+b,a+b+c,a+b+c+d),       a,b,c,d>0.

Disjoint pairs of secondary subsets with equal cardinality determine
all relevant inequalities. Cardinality-three comparisons are complements
of cardinality-two comparisons, and cardinality-four comparisons are
complements of singleton comparisons. In the pair layer, comparisons
of overlapping pairs reduce to coefficient order. For four distinct
sorted indices i<j<k<l, two of the three disjoint-pair comparisons are
forced by that order; only s_i+s_l versus s_j+s_k can vary.
The five choices of four indices give precisely

    c-a,  c+d-a,  d-a,  d-a-b,  d-b.

No additional equal-cardinality comparison can change without changing
one of these five signs or a positive gap. Every generic secondary order
therefore belongs to one of their 32 strict sign patterns.

Twelve patterns have positive integer gap witnesses. The other twenty
have explicit positive-row zero-sum certificates. For any proposed
pattern, use the four strict gap rows e_i and the five normal rows with
the proposed signs. Each excluded pattern has a positive integer
combination of at most five such rows equal to zero, which would require
0>0 if that pattern were realizable. This is a strict infeasibility
certificate over ALL real gaps, not an integer-grid exclusion.

For example, c-a>0 but c+d-a<0 is impossible because the strict rows
d>0, c-a>0, and a-c-d>0 sum to zero. All twenty certificates are retained
and independently checked exactly by rational elimination.
The grid is used only to find feasible integer witnesses.

The region reduction and positive dependency certificates are standard
linear-inequality methods. The new finite claim is their complete
application to this Gray scan class; historical priority is unconfirmed.

## 3. Every coordinate assignment and every sign

The twelve feasible patterns and 5! coordinate assignments generate
1,440 distinct positive full orders. Since the signed reflected order
is obtained by xor of all vertices with its reflection mask, all
64 reflections are covered. For independent verification each of
these 92,160 actual signed integer vectors is sorted anew. No chamber
sampling is used.

The reflection graph independently predicts the cyclic minimum of every
base order. Direct full-sequence counts of all actual reflected scans
agree with that minimum and with the endpoint identity R=C-1.
The complete histogram of base-order cyclic minima is:

| Minimum C | Positive orders |
| --- | --- |
| 30 | 8 |
| 34 | 124 |
| 36 | 160 |
| 38 | 192 |
| 40 | 240 |
| 42 | 168 |
| 44 | 264 |
| 46 | 84 |
| 48 | 184 |
| 52 | 16 |

Thus every member of the class has C>=30 and R>=29, and the explicit
witness gives equality. Coverage rests on the normal reduction and
the twenty strict certificates; the numerical grid is not its premise.

## 4. Reproducibility and continuation

Run verify_cardinality_layer_chambers.py. It uses only Python's standard
library and the previously audited reflection-graph code. There is no
floating solver. The certificate includes all feasible gap seeds,
all infeasible patterns and their integer row multipliers, and the
1,440 costs, graph values and minimizing reflection masks in deterministic
generator order. The aggregate order-hash chain and independent scan
digest make the result replayable without storing every expanded order.
Its packing was checked against the initial full record array without
rerunning completed mathematics.

The final receipt reports 92,160 independently sorted scans, zero
violations, and elapsed 3.315 seconds. Certificate identity and verification
digest are recorded in cardinality_layer_chamber_verification.json.

The next theoretical gap is the varying-dimension coherent cardinality
model: pair/triple equal-cardinality comparisons proliferate when there
are more than five secondary coordinates. The exact six-dimensional
classification gives a pressure tool, not an induction. A viable general
bound must control the off-diagonal couplings of those globally coherent
secondary orders, or quantitatively charge failures of numerical-prefix
pairing to forced diagonal turns. Merely knowing that the highest
magnitude is tiny is now disproved as a sufficient half-density condition.
