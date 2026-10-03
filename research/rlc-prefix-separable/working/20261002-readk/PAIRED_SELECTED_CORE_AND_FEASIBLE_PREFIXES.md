# Selected five-bit core and genuinely incompatible optimal prefixes

Status: exact finite selected-parent theorems, an all-dimensional
restricted-scan lower theorem, and an all-dimensional branch-specific upper
certificate. The original M_n >= c 2^n target remains OPEN. Published v1.0
is unchanged. Numerical pressure is not an all-weight or all-n proof.

## 1. Objects, provenance, and exhaustive finite domains

Use the existing forward-Gray paired rank and normalized root phase zero.
In dimension five, mask2 means that only theta_(0,1) is set, in the
repository's existing label indexing; all other paired labels are zero.
Its upper four-bit parent is mask0. This is a prefix-separable rank by the
existing strict separator theorem in PAIRED_SIBLING_RANKS.md and
verify_paired_sibling_ranks.py. No new interpretation of Gray order is used.

C is the number of turns in the CYCLIC comparison-sign word; R is the
linear monotone-run count. Always |C-R|<=1, but they are not interchangeable.
For an upper parent define z(parent)=min_(all signed actual scans) C.
Define t(parent)=min_(all signed next-dimensional actual scans) E_fresh C,
where only the new lowest-level labels are averaged. The same fixed
parent is used in both minima. Expectations over different parents
cannot be combined to claim a single feasible extension.

The finite chamber source is inherited, not new: the certified sorted
Q5 component has546 Boolean term orders,516 coherent and30 noncoherent.
Only the516 coherent orders, each with a generic integer weight certificate,
enter this exact scan audit. Their120 coordinate permutations and32 input
sign reflections give1,981,440 signed Q5 chambers. Completeness is the
previous audited Q5 result using the primary counts and certificates;
this note does not infer completeness from a random grid. Primary reference:
Diane Maclagan, *Boolean Term Orders and the Root System B_n*,
arXiv:math/9809134v2,10 March1999, https://arxiv.org/pdf/math/9809134.
The inherited source paired_boolean_term_orders_certificate.json.gz has
SHA256 e00dba962c76e8ad0031c53f4ed2e9a643f8ae0312e3a7531c8415cacd63933c.

## 2. Exact selected-parent distinction

Across ALL128 normalized Q4 paired parents, the complete signed Q4 cyclic
minimum z and complete signed Q5 conditional minimum t are:

| Count of parents | z | t | 2z-t |
| ---: | ---: | ---: | ---: |
| 72 | 4 | 8 | 0 |
| 32 | 6 | 12 | 0 |
| 24 | 6 | 10 | 2 |

Thus the genuine checkpoint-57 loss for parent50 is real, but not a
universal obstruction to choosing a better parent. Parent0 is an explicit
choice with t=2z=12. The32 choices are retained in the exact certificate.

The conditional computation is integer-exact. In a cyclic actual scan
let L count comparisons changing ONLY the new lowest input bit. Two such
comparisons cannot be adjacent: they would repeat a vertex. Every turn
touching one has expectation1/2. Every remaining comparison compares the
fixed upper-parent ranks. Therefore E C=F+L, where F counts the fixed
turns with two nonfresh comparisons. The program checks each of128
reported minimizing weights against ALL256 fresh assignments. Signed
reflections are transferred by the exact paired-rank reflection identity;
a root-one transformed rank is normalized by globally complementing ALL
output bits, hence ALL15 or7 labels as appropriate, not just a root bit.

probe_selected_parent_conditional_minima.py:61,920 positive chambers,
6.570810641002026s, zero violations, stream
a669ff55241f3d8de98e46119d317199ae0257618c39f779a3cf523126db4ae9,
receipt69c419a2c9af29638a1968c450d780e86e5392fd48f658e99952c84064502e49.
Development assertions caught a root-normalization bitmask typo and an
unsupported assumption that a conditional mean must be even; corrected
before certification. The error log is retained.

## 3. A fixed child, rather than an average guarantee

Among ALL256 Q5 children retaining parent0,50 have exact signed cyclic
minimum12. In particular child mask2 satisfies

    min_(all generic signed additive scans) C = 12,
    min_(all generic signed additive scans) R = 11.

The latter gives RLC(rho_2)=11 and therefore M_5>=11. It does not give an
asymptotic M_n lower bound. The paired CYCLIC minimax Z_5 equals12:
the lower bound is this child; the inherited normalized minimax row-lift
inequality Z_5/32<=Z_4/16 and complete Z_4=6 give the upper bound.
No assertion that unrestricted M_5 equals11 is made.

Two independent implementations audit the lower bound. The first uses
direct rank tables for the2,048-rank reflection closure of all256 children.
The second uses NO NumPy and does NOT call the rank routine to check
chambers: it builds integer baseline forward-Gray sign words, toggles whole
label-incidence bit sets, and counts cyclic/linear turns by XOR/popcount.
For mask2 its32 reflected ranks give1,981,440 exact checked sign words.
The independent cyclic attainer is(1,6,-4,12,20); the linear attainer is
(-1,12,-16,20,6). Full vertex and rank words are retained in the receipt.

probe_fixed_natural_parent_children.py:21.88857669600111s, stream
94e5dea7ad5158c90a06a767f7bef4606679eecc5410d12c114e3ce51e972a3c,
receipt0c604e89f2c67f81d9f9bf84100a676fb7ec29f3b0e3626ce8b03258cd65e581.
verify_selected_child_bitwords.py:3.8767351580027025s, stream
209b142a159c78273b04567773d05c55dfaf2d2566f53a668adde2f4794d1620,
receiptb3dd254f043daca07d278d96f689e9c6ce2b4e0879458df3b33dc563131cf86f.

## 4. An all-dimensional protected class, with sharp3/8 constant

**Theorem.** For every n>=5, every normalized-root-zero paired rank
retaining upper five-bit parent mask2, with ARBITRARY labels at all lower
levels, has

    C >= 3*2^n/8,          R >= 3*2^n/8 - 1

on EVERY generic signed additive scan w=(u,v) such that v consists of
the five upper-input weights and the distinct subset scores of the n-5
lower-input weights u have consecutive gaps exceeding
S(v)=sum|v_j|. The five-bit core v may be ANY generic signed weights.

Proof. Write d=n-5,T=2^d. The condition makes the actual scan exactly
T translated rows of the SAME signed five-core order, sorted by the
lower-coordinate subset scores. Within a row, different upper-core
ranks determine the full rank comparison sign; no lower label matters.
Each row join goes from the last core vertex to its first, which are
antipodal for a generic additive scan. Their highest changed input bit
is the global top bit. Consequently every join sign is exactly the
closing sign of the core word, whatever the lower assignment changes.
The full CYCLIC sign word is T copies of the same core cyclic word.
Thus C=T C_core>=12T. If a is the core cyclic sign word and
beta=[a_(Ncore-2)!=a_(Ncore-1)]+[a_(Ncore-1)!=a_0], then

    R = T C_core + 1-beta >= 12T-1.

This is the inherited row identity, not a newly named row construction.
The new ingredient is the FIXED core's complete ALL-signed lower bound12,
which handles ALL admissible five-core weights simultaneously. Raw
non-top support is copied with shifted label indices; joins are top
comparisons, hence q_full=q_core<=15. The covered scans therefore have
bounded raw support even as n tends to infinity.

Sharpness on this class: take v=(-1,12,-16,20,6), with C_core=12,
R_core=11,beta=2, and u=(56,112,...,56*2^(d-1)). The lower subset-score
gap56 exceeds S(v)=55. Every choice of all lower labels then gives
R=12T-1 in every dimension n>=5. Sharpness is for this protected scan
class, not for the unrestricted M_n.

The theorem also survives GLOBAL output complementation. The earlier
draft overclaim allowing the root alone to be changed is FALSE:
mask2,root1 with v=(1,-14,-4,12,-20) has R=C=10. The full finite child
classification exposed this error; the final theorem fixes root0 and
the exact counterexample is retained. Root complementation and global
rank complementation must not be confused.

verify_selected_core_separated_rows.py checks320 mixed-sign and genuinely
nonbinary outside-order cases through Q12 plus11 sharp cases through Q15,
including arbitrary lower masks. Zero violations,1.3641334620042471s,
receipt48e087754d4ce44c4ec8416b1d93ca5c705f4e705d0443377e1b4bf6a17c03f3.
The analytic argument, not these finite dimensions, supplies all-n scope.

## 5. Combine with fresh-bottom extension using the SAME chosen rank

Start at the explicit upper five-bit mask2. Select any intermediate
extensions through dimension14. Thereafter use the checkpoint-55
single-fresh-bottom theorem at each dimension: ANY parent admits ONE
child simultaneously covering all signed scans with m_0>=N/8, with
R>N/16. Every chosen child still retains mask2. Therefore ONE compatible
infinite family handles BOTH the protected row-separated class of
Section4 in every n>=5 and the high-m_0 class in every n>=15.
This combines the results legitimately because Section4 holds for
EVERY lower-label extension, not merely a separately selected rank.

At each FIXED n>=18, checkpoint58 likewise allows a bottom-two-level
child preserving any upper parent that retains mask2 and simultaneously
handling all m_0+m_1>=N/8 scans with R>N/32. Section4 still holds for
the same child. This fixed-dimensional statement does NOT assert a
single compatible path with that two-level guarantee at EVERY n.
Compatibility with the independently selected large-q entropy rank
remains unproved.

## 6. Even finite-optimal parents need future compatibility

Positive-only bottom-weight slices of2,500 specified five-core orders
give117,980 genuine Q6 orders with no mean loss found for the50 finite
optimal children. This limited pressure is not a complete Q6 theorem.
A separate audit of all46,080 signed permuted-binary scans followed by
100,000 generated signed weights (29,019 ties rejected) found FIVE
strict rejections among117,061 genuine scans:

    five-bit parents48,100,118,137,155: z(parent)=12,
    some actual six-bit scan: E_fresh C=22<24,
    and m_0=0, so EVERY fresh assignment has C=22.

For example parent137 with weights(8,1,2,4,16,32) has R=C=22 for
ALL65,536 new-bottom assignments. None need be individually enumerated:
every raw comparison leads above the new bit, so every sign is fixed
by the certified parent. Thus being optimal in the current dimension
does not ensure a lossless next extension.

**All-n branch certificate.** Retain ANY one of these five normalized
five-bit parents as the upper five bits, and let n>=6 with d=n-6.
Use its displayed rejecting six-core weights v and prepend low-input,
high-score weights L,2L,...,2^(d-1)L with L=sum|v_j|+1. Inside every
six-core row all comparisons still lead above its fresh lowest bit;
row joins lead at the global top bit. Hence ALL labels below the fixed
five-parent are irrelevant, and for EVERY descendant rank

    C=22*2^d=(11/32)2^n,
    R=22*2^d+1-beta <=(11/32)2^n+1.

For parent137 the core beta=1, so R=(11/32)2^n exactly. Thus these
currently optimal prefixes cannot achieve asymptotic density3/8, even
with arbitrarily chosen future labels. This is branch-specific. It does
NOT disprove existence of some smaller positive c or give an upper
bound on unrestricted M_n. That distinction is essential.

Signed pressure seed202610031647,12.84150941799453s, receipt
8f33ba940a790db6c75651879d695a02b9efe10cbcffb16e8acfdfc25246aa12.
The all-n branch verifier checks100 integer instances through Q15,
retaining exact lower masks and the failed root-only claim;2.843919603008544s,
receipt4dae602237370ac54e556048a36508db48fec0eac995287d14d2e54d8c2626a9.

## 7. The exact unresolved proof gap and next action

The protected scan union above is not all generic additive scans.
What remains is low-bottom-mass scanning without separated five-core
rows, along with compatibility against the large-q entropy class.
Mask2 has no mean-doubling rejection in the recorded Q6 pressure;
that is not a theorem. The useful next analytic target is a conditional
mean lower bound or summable controlled loss for selected upper
prefixes, expressed on the ACTUAL shifted-duplicate projections.
Finite-optimal parents must also retain future guarantees; five explicit
branches now demonstrate why current optimality alone is insufficient.
No general c>0 or all-dimensional exact Gray constant is claimed here.
