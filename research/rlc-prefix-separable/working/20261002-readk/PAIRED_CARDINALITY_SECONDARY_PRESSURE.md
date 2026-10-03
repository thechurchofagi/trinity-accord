# Arbitrary cardinality-secondary pressure and a matching-scope counterexample

Status: finite exact pressure; no new all-dimensional lower bound is claimed.
This follows the proved PAIRED_CARDINALITY_NUMERIC_QUARTER.md theorem.

The numerical raw matching cannot simply be reused when secondary coordinate
priorities change. Already at n=3 take secondary coefficients (2,1,4) and
primary coefficient B=8, hence genuine generic weights (10,9,12). The
one-bit layer is (2,1,4), so the prescribed A triple (1,2,4) is not
consecutive in the stipulated order. All subset scores are distinct. This
is a counterexample to reuse of the certificate, not to the segment bound:
the exact family minimum here is 6 (D=4,K=1,W=0), attained by mask 0.
The full order is (0,2,1,4,3,6,5,7). The dimension is the smallest
allowed by the theorem. An arbitrary within-layer perturbation proof needs
a different matching or a quantified repair.

probe_paired_cardinality_secondary.py uses exact ancestor optimization and
direct integer run checks. It exhausts all secondary superincreasing
coordinate priority permutations for n=3,...,7 (5910 scans), and adds 1150
generic signed-secondary integer draws with seed 202610031037 in n=5,...,10.
Two nongeneric proposals were rejected, giving 7060 checked scans. Each
scan has w_j=B+b_j with B=1+sum(abs(b_j)); these are positive, generic and
cardinality-priority whenever the secondary layer values have no ties.

Among those finite permutation sweeps the minimum R values are
(4,7,12,25,49), and the minimum D+K values are (3,6,10,18,34).
The n=7 minimizer of R can differ from the minimizer of D+K. None of the
7060 scans violates R>=N/4+2 or D+K>=N/4+1. This absence proves neither
inequality for general dimensions or all secondary chambers.

The result file preserves exact minimum witnesses, attaining masks,
parameters, scan and DP digests; every evaluated result contributes to the
overall digest 3bf9cdde27a82dac8d9e7910ee92a4bf0a07e1ae213eebb30d9b8b5af4835815.
Runtime 215.614266 seconds. Full per-scan rows are reproducible from the
deterministic generator; they are not described as a complete chamber audit.
Independent recursion is additionally checked through n=7.

Next route: use the exact complement-symmetric half-graph reduction rather
than extend numerical adjacency by assumption. Check whether half graphs
are balanced, and if they are use a standard integer root-to-top minimum
cut; if they are not, retain the negative-cycle obstruction explicitly.
