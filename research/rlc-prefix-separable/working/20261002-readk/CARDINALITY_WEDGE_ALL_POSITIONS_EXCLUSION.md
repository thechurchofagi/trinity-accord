# Exact exclusion of every insertion position over the metric wedge

Date: 2026-10-03. Research theorem for a restricted continuous family.
Main constant-density M_n remains OPEN; published v1.0 is unchanged.

## Theorem and scope

Use the parent wedge and insertion family of
CARDINALITY_WEDGE_NEXT_INSERTION_EXCLUSION.md. Move the inserted ninth
coordinate from position 8 to any position j=0,...,8, preserving the
relative numerical order of the eight old coordinates. For ALL allowed
generic real (t,A,H), the interior net F=E_int-D_int is at most the
position-specific value in this table. Each value is attained.

| Insertion position j | Maximum F | Minimum core-tail limiting density |
| --- | --- | --- |
| 0 | 70 | 221/512 |
| 1 | 70 | 221/512 |
| 2 | 28 | 121/256 |
| 3 | 10 | 251/512 |
| 4 | 8 | 63/128 |
| 5 | 66 | 223/512 |
| 6 | 58 | 227/512 |
| 7 | 72 | 55/128 |
| 8 | 72 | 55/128 |

Therefore none of these nine insertion positions can improve on 55/128.
The density statements follow from the previously proved arbitrary
core-tail reduction. They concern exactly these constructed scans, not
RLC against all generic scans and not M_n. Arbitrary permutations of the
old coordinates, other parent metric directions and the entire parent
chamber remain outside the theorem.

## Proof by exact covering and coordinate relabeling

The source certificate covers all real parameters by 16 rational polygon
cells and 6,768 cell-offset regions, including generic boundary orders
through their open neighbourhoods. It contains exactly 802 distinct
highest-insertion child orders. An order-preserving coordinate embedding
maps a vertex x to

    low=(x mod 2^j),
    high=floor((x mod 256)/2^j),
    y=low + 2^(j+1)*high + 2^j*floor(x/256).

This is a bijection. Permuting the weights with the same map preserves
every comparison, so the entire child order for position j is obtained
by applying this map to the base order. In particular, a metric change
that leaves the base order unchanged leaves every positioned order
unchanged. No extra partition of the real parameter domain is needed.

The verifier checks all 802 base orders and all nine embeddings, giving
7,218 exact position-order evaluations. It independently verifies the
complete vertex-order permutation for each one. Exact reflection-graph
spin optimization gives the displayed maxima; representative rational
parameters, integer secondary vectors, exact graphs and optimizing
reflections for all nine maxima are retained in the certificate.

Every attained maximum is also checked by independently sorting a genuine
generic signed integer score scan. On each such actual scan, the verifier
directly counts sign changes on all 494 interior triples and checks the
identity 2*changes=494+D_int-E_int. This count does not use the graph to
produce the observed signs.

## Evidence and restart point

Run verify_cardinality_wedge_all_positions.py. Result: zero violations,
12.276 seconds, digest
a656e01ee4432bc6989f6e66887316e62ca1c8915fc23eee26808673fef95257.
All 802 order representatives and all nine cost vectors are retained in
cardinality_wedge_all_positions_certificate.json; stdout is retained in
cardinality_wedge_all_positions_run.log. The source partition certificate
is read rather than recomputed or sampled.

This excludes the complete stated insertion route, not the main positive
lower bound. Stop searching the same wedge for a tenth equivalent sample.
Return to a dimension-uniform structural argument. A complementary route
to audit is bounding the longest monotone segment of forward Gray ranks:
first look for coherent face blocks with exponentially many vertices,
before asserting a polynomial maximum segment length.
