# A sharp quarter lower bound for all signed lexicographic scans

Date: 2026-10-03. All-dimensional restricted-scan theorem.
Main M_n constant density remains OPEN. This extends the saved natural
top-face row theorem to every coordinate significance order. Prefix
trees, Gray comparisons, raw cancellation and spin optimization are
existing tools reused here, without historical-priority claims.

## 1. Statement

Let n>=2, N=2^n, and let rho be ANY member of the paired-sibling family
from PAIRED_SIBLING_RANKS.md. Let pi be ANY signed lexicographic cube
scan: coordinates may have any significance order and any signs.
Equivalently, pi is an input reflection of a binary integer order after
an arbitrary coordinate permutation. Such orders are genuine generic
additive scans, realized by coefficients +/-2^r.

Then its paired-variable graph satisfies

    D+K >= N/4,

where D counts forced same-variable turns and K counts opposite raw
mixed products canceled at each unordered variable pair. Consequently

    R(rho composed with pi) >= N/4+1.

No negative-cycle or frustration lower bound is needed for this scan
class. The bound is sharp over the family for every n>=3: the earlier
three-bit natural-top-face row construction attains N/4+1. At n=2 the
lower bound is two, also attained. This is not a theorem for arbitrary
generic weights and therefore does not settle RLC or the main M_n goal.

## 2. Disjoint four-vertex certificates

Let j be the fastest scan coordinate and k the second fastest. Partition
the scan into N/4 consecutive four-vertex blocks. Each block visits

    x, x XOR e_j, x XOR e_k, x XOR e_j XOR e_k,

with every other coordinate fixed. Signs of the scan coefficients may
make the first free bit value one rather than zero, but this does not
change the cases below. Each block contributes two internal turn
positions. These positions are all disjoint between blocks.

Recall: a comparison with highest input difference h has the Gray sign
times its paired variable theta_(h,prefix above h+1). At equal h, two
consecutive comparisons have opposite Gray signs and the same variable.

### Case A: j>k

All three comparison labels in a block have highest difference j and
the same paired variable. Their crossing directions alternate. Thus
both internal positions are forced turns. Over all blocks,

    D >= 2*(N/4)=N/2.

### Case B: k=j+1

The highest differences are j,k,j. The two j-comparisons have the same
variable, since the changing controller k is dropped from its prefix.
Their Gray signs are opposite, because the value of bit j+1 changes
between the first and last edge. The middle comparison has its fixed
k-variable. The two mixed products are therefore opposite contributions
to the SAME unordered variable pair. Match these two raw products in
each block. This gives N/4 disjoint cancellation pairs and hence

    K >= N/4.

### Case C: j<k-1

Coordinate j+1 is slower than j,k. Pair each four-vertex block with its
translate obtained by flipping the fixed controller j+1. This pairs
the blocks without fixed points. In corresponding j-comparisons the
paired-variable label is unchanged, since the controller is excluded
from its prefix, but the Gray sign negates. In the middle k-comparison,
flipping j+1 changes neither the highest differing bit k nor any
controller or prefix above it, so both its label and sign are unchanged.

Thus EACH of the two mixed products in one block is opposite to the
corresponding product in its translated partner at the SAME unordered
variable pair. Match them separately. There are N/8 block pairs and
two raw cancellation pairs per block pair, giving

    K >= 2*(N/8)=N/4.

## 3. Why other comparisons cannot undo the certificate

At an unordered variable pair {u,v}, let P,Q be the counts of positive
and negative raw products. Its cancellation contribution is min(P,Q).
The matching above uses distinct raw turn positions, so if it supplies
t pairs at {u,v}, then t<=P and t<=Q. Other internal or between-block
products only increase P or Q; they cannot reduce min(P,Q).

Likewise forced-turn indices counted in Case A are distinct and remain
forced regardless of all spins. The exact identity from the preceding
ancestor note gives

    R_min=1+D+K+phi >=1+D+K >=N/4+1.

This applies simultaneously to every rank mask. Every signed scan was
already included in the direct four-vertex argument; alternatively the
family's reflection closure reduces it to positive lexicographic order.
No finite sampling is used in the proof.

## 4. Audit and exact limitations

Run verify_paired_all_lex_quarter.py. It retains explicit disjoint raw
cancellation matchings, verifies their variable pairs and opposite
products, checks that every matching load is bounded by min(P,Q), and
independently forms the whole graph. It exhausts 5,912 positive
coordinate orders through n=7. Every sign choice is also audited through
n=5. Fresh signed integer scans through n=12 verify the full actual
score ordering and random admissible ranks. Exact ancestor optimization
checks sharp genuine attainers through n=12.

The certificate contains every exhausted coordinate permutation with
its D,K and matching digest, explicit representative pair lists, signed
integer weights/rank masks, and sharp attainers. There are 4,184
additional signed audits, zero violations, 2.271 seconds; digest
da13ae7cfe73473ef842094c7003524981ff98193db458b5d53440a3e79ca7d0.

This is a real expansion of an all-dimensional protected scan class.
It still leaves generic subset-sum interleavings outside the proof, and
does not remove the n^2 denominator of the published general theorem.

## 5. Immediate next gap

The four-vertex proof does not depend on the ORDER of the slow-coordinate
faces, only on every such face being a consecutive block with its common
two-coordinate additive order. Extend it to all scans with separated
two-coordinate faces, and quantify the loss if some parallel faces are
fragmented. Before treating that loss as small, test cardinality-first
scans: each such two-face spans three cardinality layers and may contain
many other vertices between its corners. A theorem covering only block
faces cannot by itself imply an all-weight result.
