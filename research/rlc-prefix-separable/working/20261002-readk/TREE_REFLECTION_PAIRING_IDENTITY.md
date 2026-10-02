# Reflection pairing for balanced-tree ranks

Date: 2026-10-03. Status: research note; not a published revision.
Baseline: TA-TR-2026-22 v1.0, DOI 10.5281/zenodo.23103274.

## Setup

Put \(Q_n=\{0,1\}^n\), number coordinates from 0 (least significant)
to \(n-1\), and put \(N=2^n\).  A balanced-tree rank \(\rho\) is
obtained from the fixed coordinate hierarchy that splits coordinate
\(n-1\) at the root, then \(n-2\), and so on.  Every internal node may
choose either child first, with no restriction on how that choice depends
on the complete higher-coordinate prefix.  These are exactly the ranks in
the signed-tree family used in the published proof.

For \(z\in Q_n\), define
\[
  \pi_z=(z\mathbin\oplus0,z\mathbin\oplus1,\ldots,
         z\mathbin\oplus(N-1)).
\]
This is a generic additive sweep.  Indeed, the integer weights
\[
  w_j(z)=(1-2z_j)2^j
\]
satisfy
\[
  w(z)\cdot x=C_z+\sum_{j=0}^{n-1}2^j(x_j\mathbin\oplus z_j),
\]
so increasing score gives exactly \(\pi_z\).

## The reflection-pairing theorem

**Theorem.** For every \(n\ge1\), every balanced-tree rank \(\rho\), and
every \(z\in Q_n\),
\[
 \boxed{R(\rho\circ\pi_z)+
        R(\rho\circ\pi_{z\oplus1})=2^n.}
\]
Consequently
\[
 \boxed{\operatorname{RLC}(\rho)\le2^{n-1}.}
\]
Equivalently, the mean run count over all \(2^n\) signed binary sweeps is
exactly \(2^{n-1}\).

**Proof.**  For the sweep \(\pi_z\), write
\[
 e_i(z)=\operatorname{sgn}\bigl(\rho(z\oplus(i+1))-
                                  \rho(z\oplus i)\bigr),
 \qquad 0\le i\le N-2.
\]
The binary increment \(i\to i+1\) changes coordinates
\(0,1,\ldots,k_i\), where \(k_i=\nu_2(i+1)\).  Hence \(k_i\) is the
highest coordinate on which the two endpoints differ.  In a balanced
tree their rank comparison is decided at the node that splits coordinate
\(k_i\), using only their common coordinates above \(k_i\), the direction
of their crossing at \(k_i\), and that node's fixed orientation.

Replace \(z\) by \(z\oplus1\).  If \(k_i=0\), the increment changes only
coordinate 0, so the two endpoints are exchanged and
\(e_i(z\oplus1)=-e_i(z)\).  If \(k_i>0\), complementing coordinate 0 in
both endpoints changes neither their highest differing coordinate, their
common higher prefix, nor their crossing direction there.  Therefore
\(e_i(z\oplus1)=e_i(z)\).

For each possible turn position \(0\le i\le N-3\), exactly one of
\(i+1,i+2\) is odd.  Thus exactly one of \(k_i,k_{i+1}\) equals zero.
Under \(z\mapsto z\oplus1\), exactly one of the two adjacent comparison
signs is negated.  The turn indicator is therefore complemented:
\[
 \mathbf1\{e_i(z)\ne e_{i+1}(z)\}+
 \mathbf1\{e_i(z\oplus1)\ne e_{i+1}(z\oplus1)\}=1.
\]
Summing over the \(N-2\) turn positions and adding the initial run in
each sequence gives \(R_z+R_{z\oplus1}=2+(N-2)=N\).  One member of each
pair has at most \(N/2\) runs, and both sweeps are generic additive
sweeps.  This proves the corollary.  The case \(n=1\) is the same identity
with no turn positions. \(\square\)

The proof also works if the coordinates above 0 are placed in any order
of signed lexicographic significance, provided coordinate 0 remains the
fastest coordinate.

## Scope and effect on the main problem

The theorem allows every node orientation to depend arbitrarily on the
entire higher prefix.  It therefore covers ordinary block tensors,
prefix-dependent finite-state substitutions, the forward-Gray rank, and
all other ranks in the fixed balanced coordinate-tree family.  It is not
an upper bound for all prefix-separable ranks: a general prefix-separable
order need not have a single compatible balanced-tree representation.

This is a universal constant-density ceiling for the construction family,
not a disproof of the target \(M_n\ge c2^n\).  A balanced-tree family could
still prove that target with any \(c<1/2\).  The exact remaining challenge
inside this family is to produce one orientation whose run count is
bounded below by \(c2^n\) for every additive sweep, including non-lexicographic
subset-sum interleavings.  The theorem shows that signed binary sweeps can
never certify a larger constant and supplies an obligatory equality test
for any proposed recursive proof.

Alternating runs and signed-tree representations are established notions.
A targeted search found no statement of this cube-reflection pairing
identity, but this is not an exhaustive priority claim.

## Verification

Run `python3 verify_tree_reflection_pairing.py`.  The verifier constructs
tree traversal ranks independently of the proof's LCA description.  It
exhausts every node orientation for dimensions 1 through 4 and every
reflection, then checks seeded orientations in dimensions 5 through 10.
It also verifies the integer score realization and the stronger
turn-by-turn complementation identity.  All arithmetic is integral.
