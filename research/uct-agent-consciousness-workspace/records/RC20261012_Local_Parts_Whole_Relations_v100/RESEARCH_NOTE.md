# Local Parts, Whole Relations — technical research checkpoint

**UCT-RC-2026-01 v1.0.0 · 12 October 2026**

Prepared manuscript: *Local Parts, Whole Relations: A Constructive Audit of Composition in Structural Consciousness Models*. Human author of record: Hongju Liu, independent researcher, Shenzhen, China. Substantial GPT-6 Astra Pro research, proof, coding, execution, and drafting assistance is disclosed. English theoretical/methods preprint, 14 pages, 10 references. Not peer reviewed. No DOI reserved or published, no OTS submission, and no Arweave payment or archive.

## 0. Scope and persistence

The user requested actual progress on local process persistence and whole organization, using thought experiments and measurement-aware reasoning, until a defensible standalone preprint contribution exists. This checkpoint preserves the complete core constructions and proofs, not a claim to have solved phenomenal combination or empirically confirmed UCT.

The full 50,126-byte manuscript, rendered PDF, source/claim audit, metadata, and complete preparation package remain in the originating conversation's downloadable files. This repository note is a technical checkpoint, **not a verbatim mirror of that manuscript or its PDF**. The accompanying verifier and exact JSON are separately saved when their commits succeed. Obtain the actual manuscript/package for publication; do not reconstruct missing files and call them the reviewed edition.

The inherited completed map is UCT-MAP-v1.1.2; publication coverage entry was UCT-PUB-v1.0.33. No full semantic review of the 913-node map was performed. All candidate RC claims remain PENDING_MAP, disabled as established UCT premises. Existing papers and Originals are unchanged. No PR, CI run, main merge, or deployment is requested. Branch head checked immediately before persistence: 38a65a362d90fc55b8e11ea7a097ed5067f3059b, which preserves the preceding XRT work.

## 1. Why this is not a repetition of UCT I

UCT I v1.2, Section 6.3, already derives a conditional nonproduct conclusion under C1 in a declared common product comparison. Section 6.1 explicitly leaves general gluing of overlapping processes unestablished. A4W already distinguishes several local centred routes from actual joint downstream use; A5L already shows that a grounded role coordinate need not identify a selected feeling. These are inherited, not RC discoveries.

The new application asks which local records determine a whole, which cross-relations remain unrecorded, and whether an assumed local/whole distance relation can coexist with genuine forgetting. It directly audits Lee-Youngzie et al. (2026), *Towards a Mathematical Structure of Global Phenomenal Consciousness*, Entropy 28(6):615, DOI 10.3390/e28060615, especially Definition 1, Section 4.1.3 and Appendix A15. Its DIS category assumes symmetry and zero diagonal but **not** triangle inequality. All metric conclusions below explicitly add that assumption.

## 2. RC1: finite gluing existence does not entail uniqueness

Let W={l,m,r} with topology T={empty,{m},{l,m},{m,r},W}. For each open U, F(U) assigns a bit to each vertex in U. A further bit b describes one relation supported on {l,r}, and is present exactly when both endpoints lie in U. Restrictions forget coordinates not carried by the smaller open.

**Proposition.** This presheaf has gluing existence for every cover of every open, including the empty cover of the empty open, but not uniqueness.

**Proof.** Coordinate projection preserves identities and composes. A compatible family fixes consistent vertex values on its union. If a patch contains both endpoints, its b value is fixed; two such patches agree on b because their intersection also contains both endpoints. If no patch contains both, either b value extends the family. Thus an amalgamation always exists. In the cover {l,m},{m,r}, each of the eight consistent vertex triples has exactly two amalgamations, b=0 and b=1. The empty section is unique. This proves the general cover statement, not merely one successful fixture. QED.

Appendix A15 of the cited paper defines gluing as existence, then states that finiteness makes locality/uniqueness automatic. RC1 refutes that literal implication. If gluing is instead defined to include uniqueness, no counterexample to that different convention is claimed. Giving all section spaces zero dissimilarity also makes this a formal DIS-valued counterexample; that zero-distance device is not a model of distinguishable qualia.

Several mathematical completions do not mean that an actual experience is indeterminate, that no whole exists, or that multiple subjects have been counted.

## 3. RC2: exact relational completion

Fix labeled carriers V and relation atoms Omega, each with a nonempty declared support supp(alpha) contained in V. A global structure is a free binary assignment z in {0,1}^Omega. A patch U retains exactly those atoms whose entire support lies in U. Given compatible induced patch descriptions, let k be the number of atoms whose support is contained in no observed patch.

**Proposition.** Every compatible family has exactly 2^k completions in the free binary class. Local data uniquely determine every global assignment exactly when k=0.

**Proof.** Compatibility fixes every visible atom to one common value. Each hidden atom is unconstrained and independently takes two values. Product counting gives 2^k. If k=0 there are no choices; if k>0 toggling one hidden atom gives two distinct completions. QED.

A physically admissible subclass A filters this fiber: A intersect {z: every restriction matches}. It may contain zero, one, or several structures. The free count is not a count of realizable brains, experiences or subjects. It is for fixed labeled assignments. An allowed automorphism quotient can identify assignments, so physically grounded ports and label symmetries must be declared before interpreting differences.

## 4. RC3: a constructive incidence repair

Extend the base from vertices to B=V disjoint-union Omega. Order v <= alpha when v is incident to alpha; use downsets as opens. An open that contains a relation field therefore contains its endpoints. On an open O, assign values to every carried vertex/relation field and restrict by forgetting fields.

**Proposition.** These assignment sections glue uniquely across every cover of fields.

**Proof.** Every field in the union appears in a member of the cover. Matching fixes a common value wherever a field appears more than once. Assign that value fieldwise. This constructs a unique union section. QED.

Covering all vertices is not necessarily covering B: the previously missing cross-relation remains a genuinely missing field. The repair changes an incomplete representation; it does not assume the physical relation previously failed to exist. This is the classical sheaf of assignments applied to a relation-incidence base, not newly invented sheaf mathematics. Additional physical constraints can still obstruct gluing and must be checked separately.

For ongoing local loops feeding a larger consumer, the whole can acquire relations absent from the retained local description without thereby deleting the local records. Under C1/P3/U1, experiential interpretation additionally requires actual process persistence and independently grounded constitutive relations. Coupling can alter local boundary dependence and local experience; unchanged selected local records do not prove unchanged complete local organization.

## 5. RC4: constructive geometry and the forgetting obstruction

Let r_i:X->X_i be local views, d_i pseudometrics, and beta:X->Z an independently grounded relation descriptor with pseudometric d_Z. Then

D(x,y)=max(max_i d_i(r_i x,r_i y), d_Z(beta(x),beta(y)))

is a pseudometric, every r_i is nonexpansive, and D is a metric exactly when the common zero classes separate points. Nonnegativity and symmetry are immediate. For triangle, apply each component's triangle inequality and then max(a_i+b_i)<=max(a_i)+max(b_i). Joint separation gives the last statement. This is a constructive consistency witness, not a claim that max is the universal phenomenal geometry.

In contrast, a universally expansive map satisfies d_X(x,y)<=d_Y(rx,ry). Therefore d_Y(rx,ry)=0 implies d_X(x,y)=0. If d_X is a metric, r is injective. Such a map cannot genuinely forget a globally discriminated feature. Context-retaining local states are an alternative, so this does not show DIS is inconsistent or attention empirically forgets that feature.

**Counterexample to silently adding triangle.** On X={00,01,10,11}, put c(x,y)=0 when either coordinate agrees and c(x,y)=1 otherwise. This symmetric zero-diagonal dissimilarity obeys both expansive projection bounds. But c(00,11)=1 while c(00,01)+c(01,11)=0. Hence connected chains of zero local distinctions do not force global collapse in the actual nonmetric DIS category. A singleton zero-distance empty-region target would force collapse, but this is an explicit boundary-case condition, not an asserted choice made by the source paper.

## 6. RC5: exact pseudometric compatibility

Now explicitly assume a broad **pseudometric** on a finite comparison set, on a common calibrated [0,1] scale. Let c be symmetric upper caps with zero diagonal and ell symmetric nonnegative lower requirements with zero diagonal. Define c-star(x,y) as the shortest c-weighted path from x to y.

**Theorem.** A pseudometric d satisfying ell<=d<=c exists if and only if ell<=c-star. Moreover c-star is the greatest pseudometric pointwise below c.

**Proof.** For any d<=c, repeated triangle inequalities show d(x,y)<=sum of c along every path, hence d<=c-star. Conversely nonnegative shortest-path distance is a pseudometric and c-star<=c via the direct edge. If ell<=c-star, choose d=c-star. These arguments also prove maximality. QED.

A connected zero-cap graph forces c-star=0. For a two-factor square, pairs can be joined by two one-coordinate-change edges with allowance eta, giving a whole-distance cap min(1,2 eta); the construction by shortest-path closure attains it. This is conditional on the square, local identification and metric assumptions, not a universal brain-resolution law.

## 7. RC6: exact minimum uniform relaxation

Replace each off-diagonal cap by c_delta(x,y)=min(1,c(x,y)+delta). The exact smallest nonnegative delta for compatibility is

max(0, max_{x!=y} max_{simple paths p:x->y} [ell(x,y)-sum_{edge e in p} c(e)] / |p|).

**Proof.** Before clipping, ell<=shortest-path(c+delta) is equivalent to every path satisfying ell(x,y)<=sum c(e)+|p| delta. Rearranging all these inequalities gives the displayed maximum. Nonnegative costs allow cycles to be removed, so simple paths suffice. Clipping an edge to 1 cannot create a violating path because any such path already costs at least 1>=ell(x,y); paths with no clipped edges are unchanged. Thus the same maximum remains exact after clipping. QED.

This uses classic shortest-path mathematics, not a claimed new generic algorithm. In raw DIS without triangle only direct pairwise deficits matter. With three points, c(0,1)=c(1,2)=0 and c(0,2)=ell(0,2)=1, the direct pairwise requirement is satisfied at delta=0, while the pseudometric requirement needs delta=1/2. The distinction is essential.

## 8. RC7: restriction is not automatically an attentional intervention

A same-context restriction of an episode and a new episode after selectively attending to part of a stimulus are different objects. Physical stimulus constancy does not prove context or experiential constancy. A measured cross-attention map needs independent calibration/transport assumptions. Objectwise isomorphisms under C1 do not alone prove a chosen cross-context map commutes with externally interpreted phenomenal restrictions.

For a direct expansive claim, measured difference d_hat_whole-d_hat_local greater than epsilon_whole+epsilon_local+eta contradicts the scoped claim on the defended simultaneous confidence event. Here eta must cover allowed map distortion and attention-transport uncertainty, not only instrument noise. A nonsignificant local difference is not zero. This is a prospective test rule, not an executed experiment or an independent bridge from neural responses to a particular feeling.

## 9. Executed evidence

Python 3.13.5, standard library, exact Fraction arithmetic. General conclusions rest on the proofs above and in the full manuscript, not finite induction. The result JSON reran byte-for-byte.

- Five-open three-point topology: 32 covers, 326 matching families; all have amalgamations, 32 families are nonunique.
- Eight-open discrete extension: 256 covers, 3,382 matching families; 280 are nonunique. Restriction functoriality: 595 section/inclusion-chain instances.
- Incidence repair: 10 opens, 100 ordered binary covers, 847 matching families; all unique.
- Four binary-coordinate states: 729 dissimilarities; nine obey the expansive bounds, only one is also a pseudometric. All 729 shortest-path closures agree with complete simple-path enumeration.
- Three-state lower/upper pairs: 729 cases; exact relaxation formula agrees with closure thresholds. 534 require positive slack; 21 require strictly more than every direct pairwise deficit.
- Directed four-vertex relation assignments: 4,096 per cover. Disjoint pairs hide eight relation atoms, leaving 256 completions per local pattern. Overlapping triples hide two, leaving four. Adding those two relation fields uniquely distinguishes all 4,096 assignments.
- An eight-state relation-bit geometry verifies local nonexpansion and whole discrimination.

No human or language-model experiment, actual neural process realization, IIT Phi computation, validated qualia distance, or subject count is supplied.

## 10. Prior-art and publication decision

Primary references: Lee-Youngzie, Tsuchiya, Robinson, Dietz and Monti (2026), DOI10.3390/e28060615; Stacks Project Section6.7 tag006S; Floyd (1962), DOI10.1145/367766.368168 (classic algorithm attribution only); UCT I v1.2 DOI10.5281/zenodo.23131575; A4W/A5L; IIT4.0 DOI10.1371/journal.pcbi.1011465. Feature binding has established antecedents including Treisman and Gelade (1980). Schneider/Komlos (2008) and Anton-Erxleben/Abrams/Carrasco (2010) represent opposing primary results about attention and appearance; the paper does not resolve that empirical debate.

A close lead, Otaviano Lucas Duarte Santos, *Frustration and holonomy in sheaves of qualia structures: quantitative local-to-global principles for phenomenal unity*, DOI10.5281/zenodo.22135251, was found in a secondary discovery record. Primary text/API could not be retrieved. Its alleged findings are not relied on, its peer-review status is not inferred, and worldwide priority for all RC formulas is unverified. The package records exact source access limitations.

Decision: the specific correction, constructive relation-completion repair and exact scoped tolerance criterion form a coherent standalone theoretical/methods preprint. Preparation for DOI is justified; no current claim of empirical UCT superiority, refutation of IIT, or solution to the hard/combination problem is warranted. New research claims remain disabled in the UCT map pending full integration/audit. Do not increase the published-work count before an actual publication receipt.

## 11. Exact prepared-file identities

- manuscript.md: 50,126 bytes; SHA256 bfadf777f7a7ff31814ee5418651218357c1e9a32e75487d117ec15e94078181.
- Local_Parts_Whole_Relations_v1.0.0.pdf: 127,038 bytes, 14 pages; SHA256 803835006c0afe7e388738e451acb84f55c3dcae9d46cd8aad1dacf1f2acb8ff.
- code/verify_composition.py: 11,738 bytes; SHA256 99be71917957c3d56922dad38738526ade706f0db29ef88ea2a92d977ff8fd0a.
- results/exact_results.json: 3,707 bytes; SHA256 bbf674aebc846c9c670b2d04629684fa7a0041dc8804c1c392a2e740e90a0cb3.

Original package directory: /mnt/data/UCT_Relational_Composition_v1.0.0/. Local paths are not durable public URLs. Preserve previous editions and obtain actual files before any deposit. After author-approved publication follow the existing exact-byte DOI -> OTS -> verified proof -> Arweave workflow; never treat this research checkpoint as a deposit.
