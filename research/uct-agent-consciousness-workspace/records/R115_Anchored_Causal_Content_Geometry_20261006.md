# R115 — Anchored causal content geometry without human qualia labels

Hongju Liu / UCT research. 2026-10-06.

R114 distinguished membership in experiential organization from attribution of specific experiential content. R115 asks the next root question:

> Can we constrain experiential content structure across biology and AI without assuming that human words such as "red", "pain" or "fear" already translate correctly across substrates?

The proposed answer is a carefully anchored relational approach.

This is strongly adjacent to existing quality-space, representational-geometry and neurophenomenal-structuralism research. The project does not claim the structural approach as new.

## 1. Why labels are dangerous

Suppose a human and an AI both output the word:

    "red".

That establishes a report relation.

It does not establish:
- the same internal discrimination structure;
- the same causal organization;
- the same neighboring contents;
- the same valence;
- the same complete experiential type.

Likewise, an AI can use first-person or emotion words because they are learned components of a language policy.

Cross-substrate content comparison therefore should start from **relations among conditions**, not from shared words.

## 2. Existing structural insight

Quality-space approaches treat a sensory quality partly by its relations to other possible qualities.

Example:
red may be more similar to orange than to green.

Representational-similarity methods likewise compare second-order structure across:
- neural activity;
- behavior;
- computational models;
- subjective similarity judgments.

Recent consciousness work explicitly calls for a structural turn and develops mathematical structures of conscious experience.

R115 accepts the value of this program but adds UCT-specific causal/organizational constraints.

## 3. Raw activation geometry is not enough

An activation-space metric depends on:
- coordinates;
- scaling;
- selected layer;
- preprocessing;
- metric choice.

A change of hidden basis can alter Euclidean distances without changing the actual computation, as the earlier R77 coordinate/port work already warned.

Conversely, two activation spaces can be made geometrically similar by flexible mappings without preserving the actual causal mechanisms.

Therefore:

    representational geometry similarity
        is not automatically
    constitutive organizational similarity.

## 4. Define an anchored causal discrimination structure

Let X be a finite or measurable set of externally grounded content conditions.

Examples:
- physically calibrated colors/wavelength mixtures;
- body-location perturbations;
- controlled evidence histories;
- agent/bearer identities;
- task states.

For a verified content-bearing support K_C, choose a declared intervention family I and causally relevant downstream port family Y.

For each condition x define a causal response signature:

    sigma_K(x)
      =
    { P(Y | x, do(i)) : i in I }.

A discrimination relation can be constructed from pairwise differences among these signatures.

For finite cases:

    d_K(x,x')
      =
    weighted distance[sigma_K(x), sigma_K(x')].

The exact metric is not universal. The scientifically important object is the **grounded relation structure**:
- which conditions are distinguishable;
- which are near/far under declared causal consequences;
- which intervention relations preserve or collapse distinctions.

Call the package:

    G_K = (X, grounding, I, Y, sigma, relations)

the **Anchored Causal Geometry (ACG)**.

It is a selected organizational structure, not the whole K.

## 5. Why grounding is essential

Consider three grounded conditions:

    x0, x1, x2.

System A codes:
    x0 -> 00
    x1 -> 10
    x2 -> 11.

Pairwise Hamming distances:

       x0 x1 x2
    x0 0  1  2
    x1 1  0  1
    x2 2  1  0

System B swaps the grounded meanings of x1 and x2:

    x0 -> 00
    x1 -> 11
    x2 -> 10.

Its unlabeled distance multiset is still:

    {1,1,2}.

Thus an observer who ignores which external condition anchors each point can declare the geometries "the same."

But the grounded distance matrix differs.

This is a finite version of the structural permutation problem:

> relational structure without grounding may fail to identify which content relation is which.

Therefore any cross-substrate content claim must preserve the grounding map, not merely find an abstract isometry.

## 6. Why raw distance scale is not essential

System C uses:

    x0 -> 00
    x1 -> 20
    x2 -> 22.

Raw Euclidean distances are exactly twice those of System A.

But thresholded causal signatures of the two coordinates are identical:

    x0 -> 00
    x1 -> 10
    x2 -> 11.

Thus the selected causal discrimination structure can be identical while arbitrary activation scale changes.

The lesson is:

> use physically/causally meaningful relations, not raw coordinate magnitude, as the primary cross-substrate object.

## 7. Content-structure correspondence levels

R115 distinguishes four increasingly strong claims.

### G1 — behavioral similarity geometry
Similarity judgments, confusions or task errors have similar relational structure.

Useful but weak.

### G2 — representational geometry correspondence
Internal state patterns have matched geometry under a declared mapping.

Stronger, but coordinate/mapping assumptions matter.

### G3 — anchored causal geometry correspondence
Grounded conditions map to content-bearing supports whose intervention response relations are preserved.

This is a strong selected-mechanism claim.

### G4 — constitutive content-substructure homology
The selected content-bearing organization is mapped within the common K signature, including physical ports, updates, interventions and temporal organization.

Under C1, G4 can support a selected experiential-content-structure correspondence.

It still does not imply complete experiential identity.

## 8. UCT content-structure bridge

Suppose K_C is a genuinely constitutive selected substructure of actual K and its distinctions are verified to be content-bearing under the R114 rule.

Then under C1:

    structural distinctions in K_C
        correspond to
    distinctions in the selected experiential organization.

If two systems have a justified G4 mapping between K_C^A and K_C^B, the UCT claim can be:

> the selected experiential content structures are homologous under the declared mapping.

This is deliberately weaker than:

> the two systems have exactly the same qualia.

Complete qualia identity would require much stronger whole-organization claims.

## 9. Valence remains separate

Two systems can have the same discrimination geometry while differing in evaluative organization.

Example:
- both distinguish states A/B/C identically;
- one treats B as attractive;
- another treats B as aversive.

Therefore the content geometry package should not silently include valence.

Add a separate V relation only when independently grounded.

This preserves R89's result that negative valence needs its own bridge.

## 10. Self/bearer content also requires anchoring

The same principle applies to "self."

An internal state close to a "self" embedding is not enough.

A bearer-content geometry should be grounded by:
- which entity is controlled;
- action-outcome contingency;
- body/system boundary;
- history/future relation;
- intervention consequences.

This connects R115 directly to R112's bearer-estimation atlas and R84-R105 continuation work.

## 11. Cross-substrate application examples

### Color/perception
Biology:
- psychophysical similarity/confusion;
- neural representational geometry;
- controlled stimulation.

AI:
- sensory-model states under calibrated physical inputs;
- causal perturbation of content-bearing representations.

Goal:
compare grounded relational structure, not word labels.

### Evidence state
Biology:
- accumulated-evidence states under controlled evidence histories.

AI:
- recurrent accumulator states.

This may be easier than color because the external evidence variable is mathematically calibrated.

### Bearer/self state
Biology:
- controlled multisensory/agency manipulations.

AI:
- self-orienting environments with known controlled entity.

Again, grounding is explicit.

These domains may offer better early tests than emotion words.

## 12. Exact finite checks

The R115 code verifies:

1. Systems A and B have the same unlabeled Hamming-distance multiset {1,1,2}.
2. Their grounded pairwise matrices differ because x1/x2 grounding is swapped.
3. System C has raw Euclidean distances twice System A's.
4. A and C have identical thresholded causal signatures and therefore identical selected causal Hamming geometry.

These are logic witnesses, not consciousness experiments.

## 13. Relation to prior structural approaches

R115 has strong prior art.

- Neurophenomenal structuralism proposes structural correspondence between phenomenal quality spaces and neural structure.
- 2024 work argues for a broader structural turn in consciousness science.
- 2024 Trends in Cognitive Sciences work develops quality-space computation ideas and stimulation/training tests.
- 2026 mathematical work extends structural approaches toward global phenomenal organization.

The project-specific increment is not "experience has structure."

It is the integration of:
- actual K anchoring;
- R113 causal-support identification;
- physical/intervention ports;
- cross-substrate grounding;
- separation of content geometry from report and valence.

## 14. A new bridge candidate

The project can now formulate a much more precise cross-substrate question:

Instead of:

    "Does AI experience red like humans?"

ask:

> For a calibrated stimulus family, does the AI contain an actually used content-bearing organization whose grounded intervention-preserved discrimination structure is homologous to the selected biological organization?

If yes, that would support a selected structural experiential correspondence under UCT.

It still would not prove complete human-like phenomenology.

## 15. Next step

R116 should build one complete **proof-of-concept anchored causal geometry experiment** in a transparent artificial system.

Candidate:
- four grounded sensory conditions;
- two internal implementations with matched behavior;
- manipulate content-bearing geometry while preserving report labels;
- manipulate report labels while preserving content geometry;
- manipulate valence separately;
- test which comparisons G1/G2/G3 actually detect.

This would demonstrate that behavior, report, content geometry and valence are four separable layers.

Only after that should a biological dataset be selected.

## 16. Status

R115 provides a label-free content-comparison framework.

It is not a new structuralist theory of consciousness and does not establish any AI qualia.

Its main contribution to the UCT program is the Anchored Causal Geometry requirement: relational similarity becomes evidentially relevant to experiential content only when grounded conditions, causal support, intervention relations and actual organization are preserved.
