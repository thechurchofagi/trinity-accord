# Real scan supports contain signed odd-K5 minors in all higher dimensions

Status: strict, independently verified obstruction to universal signed-support
idealness, with explicit capacity-gap certificates. The main M_n lower-bound
problem remains OPEN. Neither the exhibited actual scan nor its low-tail
lifts are counterexamples to a positive-density paired-rank bound.
Published v1.0 is unchanged.

## 1. Why this is a new gap after the unsigned minor audit

The preceding real K4 and K3,3 examples exclude series-parallel and planar
shortcuts, but not weak bipartiteness. Guenin's characterization of signed
cycle-cover idealness uses a signed odd-K5 minor, which those unsigned
examples do not supply. Here is such a certificate on a REAL additive scan.
The known theorem and the existing joint P+2C bound are inherited tools;
the new result is their explicit, realizable obstruction and its diagnostic
capacity separation. Primary literature checked 2026-10-03:

* B. Guenin, A characterization of weakly bipartite graphs, JCT B 83
  (2001), 112-168, https://doi.org/10.1006/jctb.2001.2051.
* The author's formulation and references:
  https://www.math.uwaterloo.ca/~bguenin/covering.html.

The explicit capacity-gap proofs below independently show nonidealness;
the conclusion does not require trusting a theorem from an abstract alone.

## 2. The genuine ten-dimensional integer scan

Use positive weights in numerical input-coordinate order

    (5240019,1679282,2213845,9099962,3696556,
     3855589,7554388,484042,1218448,8372834).

All 1024 subset scores are distinct. Build its existing paired-sibling
comparison graph and complementary half H, with source/root a=510 and
top r=511. The full graph has D=354,K=274,W=120 and phi=21, giving an
exact fixed-scan family minimum of 650. Its half's fixed-root maximum
energies are (46,32), norm 60. The actual half joint-packing LP optimum
is EXACTLY 21: a rational primal and dual match, with every inequality
checked over all 664 simple terminal paths and 2204 negative simple cycles.
Its actual additive capacity vector therefore does NOT refute joint
exactness or any quarter bound. Save this distinction throughout.

## 3. Five disjoint branch sets with an explicit switching certificate

Take

    B0={448,449,496},
    B1={456,457,459,463,482,486,497,498,505,508},
    B2={462,499,510}, B3={504}, B4={511}.

Switch precisely the vertices {456,463,486,508,510}. Every other listed
vertex has gauge +1. The following spanning-tree edges then become
POSITIVE; their unions within the five branch sets are connected:

    B0: 448-496,449-496;
    B1: 456-505,457-505,459-505,463-505,482-508,
        486-508,505-508,498-505,497-508;
    B2: 462-499,462-510; B3,B4: empty trees.

For every branch pair choose this bridge. EACH bridge becomes NEGATIVE
under the SAME gauge, not separately chosen gauges for different edges:

| Branch pair | Original edge |
|---|---|
| 0,1 | 496-508 |
| 0,2 | 449-510 |
| 0,3 | 448-504 |
| 0,4 | 496-511 |
| 1,2 | 463-499 |
| 1,3 | 497-504 |
| 1,4 | 456-511 |
| 2,3 | 510-504 |
| 2,4 | 499-511 |
| 3,4 | 504-511 |

Delete unwanted edges and contract the positive branch trees. The result
is K5 with all ten edges negative, i.e. a signed odd-K5 minor. This is a
complete integer certificate on a genuine scan support. Dimension 10 is
an exhibited seed, not a claimed least possible dimension.

## 4. Persistence for every n>=10

Apply the already proved low-tail support lift from
PAIRED_JOINT_PACKING_AND_MINOR_AUDIT.md. Put L=1+sum(the ten weights),
add n-10 LOW coordinates of weights L,2L,...,2^(n-11)L, and shift each
old graph label by delta=2^(n-1)-512. The actual scan is 2^(n-10) complete
core copies. Its exact graph formula is

    J_n=T*J_10+(T-1)*B, T=2^(n-10), |B_e|<=1.

Since every old nonzero coupling is an integer, its sign is strictly
preserved. The old half and the SAME branch/gauge certificate embed on
shifted labels. Consequently genuine additive half supports contain
signed odd-K5 minors for EVERY n>=10. A uniform weak-bipartite-support
lemma is false, and invoking Guenin's idealness theorem for all scans
without extra restrictions is invalid.

## 5. A small exact capacity gap, separate from actual scanning weights

Retain the 13 positive branch-tree edges and 10 negative bridges. Give
each tree edge diagnostic capacity 11 and each bridge capacity 1; delete
other edges. These are explicitly MODIFIED capacities, not score weights.
An optimum cannot violate a tree edge: that costs 11, while a constant
assignment on each branch costs at most 10. Thus free signed frustration
reduces to the all-negative K5, whose maximum cut is 6 of its 10 edges.
The free frustration is exactly 4.

Its fractional negative-cycle packing optimum is 10/3. For the primal,
lift each of the ten K5 triangles through the unique paths in the positive
branch trees and give it mass 1/3. Each bridge is used by three triangles
and has load 1; all tree loads are at most 10/3<11. For the dual, assign
length 1/3 to every bridge and zero to tree edges. A negative cycle uses
an odd number of negative bridges and cannot use only one; hence at
least three. Every negative cycle has dual length at least 1. Total dual
cost is 10/3, proving exactness and a strict 4-10/3=2/3 gap.

The complementary two-copy full frustration is 8: with r fixed, either
choice of a still allows an optimal K5 bipartition of sizes 2 and 3,
so both half frustrations equal 4. Nevertheless the joint half packing
max(P+2C) is exactly 7. Put unit path mass on the lifted bridge B2-B4,
the path (510,462,499,511). For each terminal branch in {B2,B4}, and
each pair of the other branches {B0,B1,B3}, lift that triangle with mass
1/2. The six cycles have total mass 3 and use each of the nine OTHER
bridges with load 1. Their COMBINED tree loads with the unit path are
below 11. Thus P+2C=1+6=7.

For the joint dual, put length 1 on bridge B2-B4, length 2/3 on every
other bridge, and zero on trees. A terminal path with just one bridge
must use B2-B4; every other terminal path uses at least two bridges.
Thus all path lengths are at least 1. Every negative cycle uses at least
three bridges and has length at least 2. Total dual cost is 1+9*(2/3)=7.
This proves the joint gap 8-7=1 independently of an LP solver.

## 6. Strictly positive integer capacities on the entire original support

The diagnostic can retain EVERY original half edge with a positive
capacity. Set each of the 13 selected tree capacities to 1100, each
of the ten bridge capacities to 100, and each of the remaining 15
original edge capacities to 1, keeping ALL original signs.

Any tree violation costs 1100; a branch-constant assignment costs at
most 1000+15=1015. Therefore every optimum satisfies the trees and an
exact enumeration of only five branch spins determines the optimum.
The independently computed half frustrations at the two root signs are
(404,406), so the complementary full frustration is 810.

For free cycle packing, the previous bridge dual lengths 1/3, zero tree
lengths and length 1 on every extra edge form a feasible dual. Negative
cycles using an extra edge already have length at least 1; all remaining
ones have at least three bridges. Its cost is

    100*(10/3)+15=1045/3 < 400 <= min(404,406).

This strictly refutes idealness using POSITIVE integer capacities on
the full original support, not just a graph deletion.

For joint packing put the prior joint lengths on the selected edges
and length 2 on every extra edge. Any path/cycle using an extra edge
is already covered; otherwise the previous proof applies. This bounds
the joint optimum by 100*7+2*15=730<810. The exact rational LP primal
and dual improve that upper bound and MATCH at 1425/2=712.5. Every
capacity and all 2868 object inequalities are independently checked.
The exact arbitrary-capacity joint gap is

    810-1425/2=195/2=97.5.

Neither positive diagnostic capacity vector is asserted realizable by
an additive scan. The same ORIGINAL score scan still has actual
max(P+2C)=phi=21. Failure of support-wide exactness therefore does not
disprove actual-capacity joint exactness, a uniform weaker density
bound, or the primary M_n target.

## 7. Reproduction and failed-route ledger

probe_paired_odd_k5_minor.py reuses the saved support-pressure weights,
avoids duplicating those LP jobs, and searches signed contractions with
bounded state counts. It reached 303 scans: 291 have a width-at-most-three
unsigned K5 exclusion certificate, seven searches ended without a
witness, four reached the explicit 20000-state limit, and the final
Q10 search found the witness in 421 states. Absence of a witness in
these searches is not used as a theorem. Runtime 13.829598735988839
seconds; digest 5a1465ee46bf9533339dd043c3ac0e67a05d594788ed9bf582ffa97a00deebeb.
The lossless report and run log are paired_odd_k5_minor_pressure.json.gz
and paired_odd_k5_minor_run.log.

verify_paired_odd_k5_obstruction.py uses hard-coded branch sets, gauges,
trees and bridges, independently of the search. It verifies every
signed connection, all lifts through Q18, both explicit diagnostic
primal/dual proofs, positive-capacity LP optima and all actual-capacity
LP inequalities. No claim rests on floating arithmetic. Zero violations,
1.3301637179974932 seconds; digest
b292ee3211680d5d1c97af831dc83e349e962f52500997666f14d771cd97aaec.
Files: paired_odd_k5_obstruction_certificate.json,
paired_odd_k5_obstruction_run.log and
paired_odd_k5_actual_joint_certificate.json.gz. The actual certificate
decompresses to 488874 bytes, SHA256
bfbddea5550b0621e1c514a213a1c105c73121d95a74e5f0f8706afef63f65f9.
To regenerate its candidate, use solve(BASE,retain=True) from
probe_paired_joint_fractional_packing.py; the independent verifier checks
the saved certificate's entire object list, rational packing, dual and
separate integer energy recursion.

The first final verifier invocation failed only while serializing an
integer-valued Fraction after its mathematical assertions passed.
paired_odd_k5_obstruction_serialization_failure.txt records that failure.
Conversion of this reporting value to int fixed serialization; it did
not change any exact proof arithmetic. The final run added and passed
the independent full actual-capacity certificate audit.

## 8. Next gap: actual coupling geometry, not universal graph exactness

Three blanket structural shortcuts are now false on real half supports:
series-parallel structure, planarity, and weak bipartiteness. An exact
joint-packing theorem cannot be justified merely by allowing arbitrary
capacities on these supports. A viable route must use additive scanning
restrictions on the ACTUAL raw counts/net couplings, or prove a weaker
packing-density bound that tolerates these signed obstructions.

The next concrete pressure target is an actual metric perturbation of
the Q10 witness, rebuilding its genuine scan graph each time, and testing
whether actual max(P+2C)<phi can occur. A gap at this stronger exactness
target still would not reject a positive-density certificate. If the
couplings never enter the nonideal capacity cone, derive a precise
translation-consistency inequality that separates that cone, rather than
reusing unconstrained graph integrality or interpreting sampled equality
as an all-dimensional theorem.
