# Joint fractional certificates: finite exactness and structural exclusions

Status: two finite rational-certificate audits and two analytic
all-dimensional unsigned-minor obstructions. No universal joint-packing
exactness or constant-density M_n theorem is proved.

## 1. Exact audit of the compatible half path/cycle certificate

For a half graph H, enumerate every simple terminal path and every simple
negative cycle. Put nonnegative mass on these objects, constrain the
SUM of their loads at each edge by its actual capacity, and maximize
P+2C. Its dual assigns nonnegative lengths y_e, with length at least 1
on every terminal path and at least 2 on every negative cycle.

probe_paired_joint_fractional_packing.py uses an LP solver ONLY to generate
candidate rational masses and dual lengths. It then reconstructs every
number using Fraction and independently checks every capacity, every
dual inequality, and equality of the two rational objectives. An integer
ancestor optimum supplies the full frustration for comparison. Thus each
reported packing optimum is strictly verified without floating tolerances.
Enumeration-limit cases would not certify an optimum.

It covers all 336 positive Q4 representative metrics, four specific Q5
seeds, 256 fresh Q5 candidates, 128 Q6 and 32 Q7 candidates, with seed
202610031145. Positive-only geometry is sufficient for this finite chamber
comparison because rank reflection closure is already established; the
higher-dimensional samples are not chamber enumeration. Of 756 candidates,
one was nongeneric and 755 yielded exact rational optima. Every one has
max(P+2C)=phi, and every D+K+max(P+2C)>=N/4. This is evidence for a target,
not its all-dimensional proof. Runtime .7624563650024356 seconds, digest
9e01a2896803896efbebbb21a29c6d035a00eb89ff68a87c09b70ebb45a0595d.

The lossless report paired_joint_fractional_pressure.json.gz decompresses
to 735526 bytes, SHA256
188566f3e332684021895012dc68d1b3636b7003cdc792c0d3248141d8cca667.
The source regenerates the plain and compressed reports; the run log is
paired_joint_fractional_run.log. The gzip round trip was verified.

## 2. A stronger signed-support hypothesis and its separate audit

A sufficient way to make ordinary negative-cycle packing exact is to
prove a signed support is weakly bipartite. This is established signed
graph theory, not a new RLC method. Guenin's 2001 characterization says
the negative-cycle covering polyhedron is integral exactly when the
corresponding signed odd-K5 obstruction is absent. Geelen and Guenin's
2002 paper supplies half-integral packing results. Relevant primary
sources, checked 2026-10-03:

* B. Guenin, A characterization of weakly bipartite graphs, JCT B 83
  (2001), 112-168, DOI https://doi.org/10.1006/jctb.2001.2051.
* J. F. Geelen and B. Guenin, Packing odd circuits in Eulerian graphs,
  JCT B 86 (2002), 280-295, https://doi.org/10.1006/jctb.2002.2128.
* The author's statement and bibliography:
  https://www.math.uwaterloo.ca/~bguenin/covering.html.

That literature does not prove our scan supports satisfy the hypothesis,
nor does cycle-cover integrality itself prove a quantitative RLC density.
The terminal-path-plus-cycle LP has additional constraints and cannot
be identified with the cited cycle-only polyhedron without a reduction.

probe_paired_weak_bipartite_support.py tests the FREE negative-cycle-cover
integrality hypothesis on signed supports of genuine scans. It assigns
alternative capacities, first all 1 and then fresh integers 1,...,5,
and compares exactly certified fractional cycle packings with independently
computed integer free frustration. These modified capacities are diagnostic
graphs, not their actual scan couplings; a gap would refute support
idealness but would not by itself refute a scan lower bound.

With seed 202610031202 it tests 385 genuine scans in dimensions 6,...,12.
There are 716 exact rational primal/dual equalities and 54 enumeration-limit
cases, with no gap among the completed cases. The enumeration cutoff is
200000 DFS calls per path/cycle phase; skipped cases remain unproved.
Runtime 24.43566293299955 seconds, digest
fc17acbce8c546ba1c6b3125b4a70d7bb5c2c7fa9943589e3b912881d12dfb21.
The lossless paired_weak_bipartite_support_pressure.json.gz decompresses
to 2844228 bytes, SHA256
202db1315383f615f5661211b165d8c11e3fead6b6c15f79be7c10800e4ab71f.
The run log is paired_weak_bipartite_support_run.log. No support-idealness
theorem follows from these samples. Recorded minimum-degree fill widths
are heuristic upper bounds on treewidth, not exact treewidth certificates.

## 3. A genuine K4 minor excludes uniform series-parallel structure

For positive generic Q6 weights

    (36014,4119,36488,65387,58395,45969),

the half graph has four connected, disjoint branch sets

    {16,24}, {28,17,18}, {30,25}, {31}.

Connections within these sets are 16-24, 28-17, 28-18 and 30-25. All six
required inter-set connections exist, as witnessed by

    16-28, 24-30, 16-31, 17-30, 18-31, 25-31.

Contracting the three nontrivial branch sets and deleting unwanted edges
gives an unsigned K4. This is an explicit minor certificate, not an
inference from a greedy fill width. Hence generic scan half graphs are
not uniformly series-parallel or of treewidth at most two. No minimality
claim about dimension 6 is made: lower dimensions were not exhaustively
classified for this minor.

## 4. A genuine K3,3 subgraph excludes uniform planarity

For positive generic Q8 weights

    (3998575,4578511,42715,7899299,2129239,2794740,3504965,7382886),

take the two vertex sets

    A={126,127,124}, B={97,98,103}.

Every one of their nine cross edges is nonzero. Their signed capacities,
with A in the displayed order and B likewise, are

| A vertex | 97 | 98 | 103 |
|---|---:|---:|---:|
| 126 | 1 | 1 | -2 |
| 127 | -1 | -2 | -1 |
| 124 | 1 | 1 | -1 |

Deleting all other edges leaves K3,3. Therefore even genuine positive
generic scan half graphs need not be planar. This blocks using planarity
as a blanket way to invoke cycle-cover integrality. A nonplanar graph
can still be weakly bipartite: neither this certificate nor the K4 minor
is a signed odd-K5 certificate.

## 5. Analytic support preservation in every higher dimension

Here is a general low-tail lift, extending the previously used block
lifting method with an exact support/sign formula. Start with ANY positive
generic d-coordinate weights w and let S=sum(w), L=S+1. In n=d+m dimensions
put new LOW coordinates of weights (L,2L,...,2^(m-1)L) below the old core.
Let T=2^m. Tail score rows are spaced by L>S, so the scan is T complete
copies of the core scan. Every adjacent comparison, including between
rows, has its highest differing coordinate in the old core; the old
paired label u becomes u+delta, delta=2^(n-1)-2^(d-1), and its forward
Gray sign is unchanged within each copy. In particular no new low
variable is active in a comparison.

Positive genericity implies a unique smallest coordinate j and core
endpoints 0 and all-ones. Its first comparison has sign +. If j<d-1,
its last has sign -, and each row boundary has sign -. Writing f,l for
the first and last paired labels and b for the old top, each boundary
therefore adds +1 at (l,b) and -1 at (f,b). When j=d-2, f=l is the root,
so these increments cancel exactly. When j<d-2, f and l are distinct,
so each edge receives an increment of magnitude at most one. When
j=d-1, both endpoint labels are top; there are two extra forced turns
per boundary and no mixed-edge increment. Thus, on shifted labels,

    J_n = T*J_d + (T-1)*B,

where each nonzero B entry is +/-1, or B=0 in the two exceptional cases.
For every old integer nonzero J_d(e),

    |T*J_d(e)| >= T > T-1 >= |(T-1)*B(e)|.

Consequently every old coupling remains nonzero with its original sign.
The complementary half's old nodes have the same depth/prefix labels,
so their shifted embedding remains in the new half. Old unsigned minors
and subgraphs persist. Applying this to the two explicit seeds proves

    genuine half graphs with K4 minors exist for EVERY n>=6;
    genuine nonplanar half graphs exist for EVERY n>=8.

verify_paired_support_minor_lift.py checks the complete graph formula,
score order, signs, half embeddings, all branch-set connections and all
nine K3,3 edges through Q18 (24 dimension-family cases). It records
paired_support_minor_lift_certificate.json and
paired_support_minor_lift_run.log. Zero violations, 1.3347272190003423
seconds; digest a7b3f4aedf6f6d1a4adc6555ac096453a5e20952462599c97457c35ea3f6cdfe.
The local boundary formula and strict sign inequality prove arbitrary
n; finite checks only audit implementation.

## 6. Reconciled evidence and the next precise gap

Concurrent canonical commit 3554a71bde802f884618fd75bf6be869eb646a11,
PAIRED_PERIODIC_OVERLAP.md, proves a different quarter-sharp overlapping
family with D+K+lambda=4, all couplings bounded by two, growing negative
cycle packing, and an arbitrary signed slow-row extension subject to a
gap condition. It credits the earlier constant-active-graph obstruction
2f9601940107c026a154e11d86b17ab0635c28c7. Both results are retained with
their distinct scopes; no route exclusion or shared method is reclaimed
as novelty. Its completed jobs should not be repeated here.

The current new exclusions concern unsigned structural shortcuts, and
the LP audits give reproducible evidence rather than a claimed theorem.
The next structural gap is signed odd-K5 exclusion or an exact witnessed
obstruction on a REAL scan support. Even a proof of support idealness
would leave the quantitative requirement D+K+P+2C>=c*N over every generic
scan. Keep structural exactness, quantitative density and the primary
M_n extremal problem separate. Published v1.0 is unchanged.
