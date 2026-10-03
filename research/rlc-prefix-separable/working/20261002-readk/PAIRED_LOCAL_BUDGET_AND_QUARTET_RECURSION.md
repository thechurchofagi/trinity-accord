# Local vertex budgets and a failed translated-quartet recurrence

Status: strict necessary realizability inequalities and a strict exclusion
of an upper-run-only recursion in an explicitly RELAXED model. The main
M_n target remains OPEN. The real all-dimensional path/cycle gap from
PAIRED_REAL_JOINT_PACKING_GAP.md remains separate. Published v1.0 unchanged.
Middle-event counting, finite-state costs and Farkas certificates are
inherited techniques, not claimed inventions.

Reconciliation: concurrent commit f78f46bbd5ca297bb42d62cf5bd64c1300c3a076
already proves the ancestor-only budget and an all-dimensional NONADDITIVE
R=2 obstruction passing local budgets, ancestor support and antipodal
symmetry. That result is credited in PAIRED_SIGNED_K5_AND_FULL_PACKING.md,
not reclaimed here. It confirms that these necessary inequalities must
be combined with genuine additive consistency. The additional accounting
here includes ALL incident couplings, cancellation and same-label counts,
and the exact endpoint identity. That commit also improves the REAL gap
family to n>=9 with density1/512, and proves full fractional cycle packing
equals half joint packing. Both are preserved as separate strict results.

## 1. Local incidence inequalities, without assuming additive coherence

For any permutation p of cube vertices, let u=theta_(h,z) be an existing
paired variable, h<n-1, z the prefix above input coordinate h+1. All
comparisons labeled u have endpoints in the SAME prefix subcube S_u,
of size2^(h+2). For a raw turn incident to u, its middle vertex therefore
belongs to S_u. Different turn positions have different middle vertices.

Write d_u for its same-label forced turns, a_u for its raw mixed-turn
incidence, k_u for the sum of cancellation minima on ALL incident edges,
and w_u for its net incident norm. Exactly a_u=w_u+2k_u. A same-label
turn contributes once to the middle-vertex count, so

    w_u + 2k_u + d_u = a_u+d_u <= |S_u|=2^(h+2).

This is stronger than the initially proposed ancestor-only bound; in
particular sum_ancestor |J_uv|<=2^(h+2). It is valid for arbitrary cube
permutations, hence necessary but very far from sufficient for additive
scan realizability. The top variable uses the whole cube size2^n.

Let l_u be the number of comparisons labeled u and e_u the number among
the first and last comparison positions (both counted if they coincide).
Every occurrence has two neighboring turns except at these endpoints;
same-label turns count twice and mixed turns once. Consequently

    a_u + 2d_u + e_u = 2l_u.

These exact balances can be enforced before using an abstract capacity
graph as a potential actual scan witness. For example, the earlier Q3
diagnostic-capacity scale on the odd-K5 seed assigns two ancestor edges
at Q10 variable462 capacity33 each. That variable has h=3,z=14 and
|S|=32, whereas net incidence is already>=66. Such a graph is impossible
for ANY cube permutation, irrespective of score feasibility.

verify_paired_local_vertex_budgets.py checks independent middle-vertex
sets, raw products, all local norms/cancellations/forced counts and the
endpoint identity. It covers every positive representative chamber Q2-Q4,
fresh Q5-Q12 scores and72 arbitrary vertex permutations.477 actual scans,
one nongeneric rejection, zero violations,0.41402420798840467s, digest
5a77886975b3cf6519e3dcdf414f2d8eecfb6e80d144a17d2f28a796d2000070.
Full certificates and parameters are retained. This does NOT prove any
positive-density lower bound.

## 2. Precise translated-quartet relaxation and candidate recurrence

For F face items, take offsets s_f and common positive gaps0<a<b. The four
events of face f have scores s_f+(0,a,b,a+b). Give it a rank interval
4B_f+{0,1,2,3}, where B is an arbitrary permutation of the F face items,
and use a two-bit forward-Gray local rank XOR an independent two-bit mask.
This captures low two-coordinate faces, but deliberately discards the
cube subset-sum constraint on s and the paired upper-rank/controller
constraints on B and the masks. Keep that relaxation explicit.

Let U be the runs of B along increasing s. A proposed lemma was

    R >= min(F+1,4U-3).

If such a lemma applied uniformly to actual paired upper ranks, its
factor4 under a dimension drop of2 would close the constant-density gap.
It is NOT proved. The relaxed version is strictly FALSE below.

## 3. Finite checks cannot be promoted to that lemma

probe_translated_quartet_recurrence.py checked255 new generic F4/F8
translated cases, exhaustively optimizing all local masks. No failure;
seed202610031235,0.29794046899769455s, digest
517c51da94511ac9e07ce6abaf8cea1cfb89a1c3f984246cf088d6687a191873.
Even the simpler local R>=F+1 shortcut fails: F8 offsets0..7,a9,b27,
identity B and zero masks give just7 runs. The upper rank here has U1;
this is a relaxation witness, not an admissible paired cube counterexample.

The stronger track-order-only version already fails at an exhibited F4
grid shuffle. The word and exact rank values are in
quartet_grid_recurrence_certificate.json. It has U2,R4, purported bound5.
Its additive infeasibility is elementary: two required order inequalities
give s2<s1+a and s1+a+b<s2+a, hence b<a, contradicting b>a.
The complete F4 audit inspects ALL24024 grid shuffles,24 face-block
permutations and256 local masks.108 grid words violate the proposed bound;
EVERY one has an exact nonnegative INTEGER Farkas infeasibility certificate
for true equal-gap scores. No real translated failure at F4 is found.
This is a finite classification in the relaxation, not an all-dimensional
lemma or all cube-weight chamber enumeration.5.6561157969990745s, digest
129a44d5de608f78d14518dc9a217e5905c653978c8c51c238954d61eb6d2f9c.

## 4. A genuine equal-gap translated failure with unbounded face count

Larger exact pressure finds a REAL equal-gap translated F32 failure:

    a=2322,b=30426,
    s=(0,1,8,12,732,739,748,757,1486,1495,1504,1511,
       2460,2464,2471,2479,3402,3408,3415,3418,3938,3942,
       3949,3950,4255,4263,4269,4274,5223,5228,5236,5243),
    B=(4,5,6,7,0,1,2,3,16,17,18,19,12,13,14,15,
       28,29,30,31,20,21,22,23,8,9,10,11,24,25,26,27).

All128 scores are distinct. EXACT local minimum R=31, attained with ALL
local masks0; U=9, while min(F+1,4U-3)=33. The full integer rank sequence
is retained. No smallest-F claim is made. The offsets have not been shown
to be cube subset sums, and B violates paired local-controller conditions;
this is not a main-target or actual cube-scan counterexample.

Exact local optimization here is particularly simple: two adjacent
INTERNAL comparison signs can only belong to the SAME face, because they
share a middle vertex. A cross-face comparison is fixed by the interval
order B and independent of all local bits. Thus every turn term is either
constant or involves the two bits of only ONE face. The optimum is a
constant plus a sum of four-state face minima. This elementary decomposition
is proved by shared-middle indexing and independently checked against128
full orientation exhaustions; it is not a general Ising innovation.

The F32 sign word has exactly15 isolated negative comparisons, with
positive first/last signs. The upper sign word has4 isolated negatives,
also positive first/last. For ANY integer k>=1 replace every face f by
k faces with offsets(k+1)s_f+t, ranks kB_f+t (0<=t<k), and scale a,b
by k+1. Old scores had integer gap>=1, so the new order replaces EACH
old event by an increasing k-clone track with no interleaving between
old events. Every old cross-event sign retains its sign; new clone
signs are positive. Isolated negatives are unchanged. Therefore for
EVERY k, F=32k,U=9 and the exact local minimum remains31. The constant
cross-turn contribution alone is31, attained by the zero masks. In fact
all adjacent seed events belong to DIFFERENT faces, and cloning preserves
that property, so no local mask can change ANY comparison sign.

This excludes EVERY putative relaxed recursion

    R >= min(cF+C,4U-3),

with fixed c>0 and finite C: eventually its right side is33, but R31.
For a further proof attempt, retaining just local Gray quartets, genuine
equal-gap translations and a scalar upper run count is insufficient.
The missing paired upper-prefix/controller restrictions matter.

Large pressure:4984 generic cases,744 rejected ties,128 independent full
orientation crosschecks, first F32 failure; seed202610031305,
0.9846691270067822s, digest
18d2cf80c1844400928b87d41ddbf2a0596e372ee8a4714fc1a6d9a01e0fdda1.
All parameters/failures are retained losslessly. The independent hard-coded
integer verifier checks all clone k through64 and certifies the all-k
order/turn proof, not merely those finite instances.

## 5. Next precise proof obligation

Investigate a two-coordinate induction retaining the actual upper paired
prefix rank and its controller phase. At level1 the local second bit is
x1 XOR y0 XOR theta1(y>>1), not an arbitrary per-face orientation. The
relaxed F32 example has increasing four-face chunks and all second-bit
phases0, violating that constraint. A repaired statement must encode this
phase relation AND additive upper subset-sum order, rather than condition
only on U. Derive a conserved multi-state deficit or a compatible-cycle
certificate for that constrained merge. The local vertex budgets supply
necessary capacity checks; neither they nor these finite positive results
settle the dimension-independent target.
