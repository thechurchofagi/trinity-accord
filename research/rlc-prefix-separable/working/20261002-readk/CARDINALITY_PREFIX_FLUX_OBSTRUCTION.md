# Few primary buckets do not imply small coherent reflection flux

Date: 2026-10-03. Unpublished all-dimensional route exclusion and
specified-family lower bound. The main constant-density RLC target is OPEN.

The concurrent ARBITRARY_SECONDARY_ENERGY_OBSTRUCTION.md at commit
97504d38f31ca2b5bdc77c9141d4a517dc8dd506 already excludes polynomial
coupling for arbitrary secondary orders using a simpler four-bit core.
This note adds a multi-edge companion and explicit forced-turn payment;
it does not claim a new priority for that exclusion.

The numerical-bucket theorem proves W<=2q for its precise tie rule. The
following genuine coherent family shows that this estimate cannot be
extended to arbitrary additive secondary vectors, even when q=n+1.
This is not a counterexample to positive Gray run density.

## 1. An exact integer seed

On seven coordinates take primary weights all equal to one and secondary
weights

\[
 b=(16,59,15,4,49,11,7).
\]

Their sum is 161. The generic positive actual vector

\[
 w=162\,(1,1,1,1,1,1,1)+b
  =(178,221,177,166,211,173,169)
\]

orders first by Hamming weight and then by the secondary additive score.
There are q=8 primary buckets. Enumerating the 128 integer score pairs
proves joint genericity; the supplied standard-library verifier gives a
complete reproducible finite certificate.

For interior triples, the counts of positive and negative mixed-label
products are:

| Labels | Positive | Negative | Net coupling |
| --- | ---: | ---: | ---: |
| 2,4 | 4 | 8 | -4 |
| 2,5 | 12 | 0 | 12 |
| 2,6 | 19 | 19 | 0 |
| 4,5 | 0 | 6 | -6 |
| 4,6 | 5 | 5 | 0 |
| 5,6 | 4 | 4 | 0 |

There are 28 interior forced diagonal turns. The full graph has D=30
and exactly J24=-4, J25=12, J45=-6, so W=22>2q=16. These three edges
are jointly satisfiable, giving E_*=22. All 128 signed actual vectors
were independently sorted and have minimum R=C=68. Thus this is a
strict failure of W<=2q, while its minimum cyclic count exceeds N/2.

## 2. Every-dimensional family

For every n>=7, put m=n-7 and extend b by the rungs

\[
 b_j=162\,2^{j-7}\quad(j\ge7).
\]

Let L=162*2^m and w_j=L+b_j. The secondary sum is L-1, so w is positive
and generic and orders exactly by (Hamming weight, secondary score).
Each higher secondary weight exceeds the sum of all preceding ones.
Thus in any primary bucket, the higher-coordinate prefixes form
contiguous blocks, with their restricted seed orders unchanged.
There are still only q=n+1 buckets.

All seed interior triples with labels 2,5 are reproduced once per
higher-coordinate assignment. Their Gray comparison products are
unchanged because these labels depend only on seed bits through bit six.
Consequently

\[
 J_{25}^{\mathrm{interior}}=12\,2^{n-7}.
\]

All other contributions to this coupling arise at the q designated
cyclic bucket joins, involving at most 2q triples. It follows that

\[
 W\ge |J_{25}|
   \ge12\,2^{n-7}-2(n+1)
   =\frac{3}{32}2^n-2(n+1).
 \tag{1}
\]

In particular W/q tends to infinity, and W>2q for every n>=9.
Thus no dimension-independent estimate W=O(q) holds over all coherent
secondary refinements, even with a positive integer primary score having
only n+1 values. This is an analytic family theorem based on an exact
finite seed, not an extrapolation from the tested dimensions.

## 3. Large flux can still be paid for by forced turns

The same family illustrates why D must not be discarded. For interior
mixed triples with maximum label at least six, the controller coordinate
lies above the free seed block, where secondary prefixes are contiguous.
The protected transport involution from PREFIX_TRANSPORT_DEFECT.md
cancels them. All remaining interior graph couplings are therefore the
three seed couplings repeated 2^m times. Bucket joins contribute at most
2q in total absolute weight, giving

\[
 W\le22\,2^m+2q.
\]

The 28 forced seed interior turns also repeat without interruption, so
D>=28*2^m. Hence EVERY coordinate-sign choice satisfies

\[
 C\ge\frac{2^n+D-W}{2}
   \ge2^{n-1}+3\,2^{n-7}-(n+1),
\]
\[
 R\ge\frac{67}{128}2^n-n-2.
 \tag{2}
\]

This proves a specified-family asymptotic density lower bound exceeding
one half despite W=Omega(2^n). It reinforces the actual global target,
which concerns E_*-D, rather than insisting that W alone be small.
Neither (1) nor (2) covers every generic additive sweep.

## 4. Verification and limits

Run python3 verify_cardinality_prefix_flux.py. It checks seed genericity,
all 128 actual signed seed orders, interior and full coefficients, and
specified lifts in every dimension from seven through fifteen. Every
lift is independently sorted using exact integer actual weights. It
checks the copied interior coupling vector, the 28 copied forced turns,
(1), and (2). The finite record is not an asserted exact formula for all
lifted minimum counts.

The discovery probe used seed 202610030832 for unrestricted cardinality
secondary pressure; a compact-seed search used 202610030843 and found
the retained vector on trial 534. The discovery domain and receipt are
saved. No absence of a sampled cost counterexample is treated as a
coverage theorem. In particular the unrestricted cardinality-secondary
half-density statement with a boundary loss remains OPEN here.

This note changes no published edition, DOI, timestamp or archive.
