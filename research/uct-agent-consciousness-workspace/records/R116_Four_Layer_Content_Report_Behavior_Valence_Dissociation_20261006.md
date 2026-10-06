# R116 — Four-layer proof of concept: task behavior, report, content geometry and valence

Hongju Liu / UCT research. 2026-10-06.

R115 proposed Anchored Causal Geometry (ACG). R116 builds a transparent finite system in which four commonly conflated layers can be manipulated independently:

1. selected content geometry;
2. task behavior/policy;
3. report labels;
4. evaluative/valence ordering.

The experiment is deliberately simple. Its purpose is logical/mechanistic separation, not artificial-consciousness measurement.

## 1. Grounded condition set

Use four externally grounded conditions:

    X={x0,x1,x2,x3}.

Base selected content-bearing code:

    x0 -> 00
    x1 -> 01
    x2 -> 11
    x3 -> 10.

Grounded Hamming geometry is a four-cycle.

Task target:

    x0,x1 -> 0
    x2,x3 -> 1.

Report labels:

    x0 -> L0
    x1 -> L1
    x2 -> L2
    x3 -> L3.

Valence:

    V(x0)=-1
    V(x1)=-0.5
    V(x2)=+0.5
    V(x3)=+1.

The selected code is causally used by a task readout in the toy construction.

## 2. Variant G — change content geometry, preserve task behavior/report/valence

Permute the grounded internal code:

    x0 -> 00
    x1 -> 11
    x2 -> 01
    x3 -> 10.

Adjust the task readout so the same grounded task target is still produced.

Keep:
- task behavior identical;
- report labels identical;
- valence identical.

Result:

    task behavior equal = true
    report equal = true
    valence equal = true
    grounded content geometry equal = false.

The unlabeled Hamming distance multiset remains:

    {1,1,1,1,2,2}.

Thus an ungrounded geometric comparison can still miss the change.

This is the strongest R116 witness:

> same task behavior and same report do not identify the same selected content geometry.

## 3. Variant R — change report only

Keep:
- base content geometry;
- base task policy;
- base valence.

Swap report labels for x1 and x2:

    x1 -> L2
    x2 -> L1.

Result:

    content geometry equal = true
    task behavior equal = true
    valence equal = true
    report equal = false.

Thus report is independently variable relative to the selected content support and task behavior.

This is the finite constructive form of the no-report/report-head distinction.

## 4. Variant B — change task behavior only

Keep:
- base selected content geometry;
- base report labels;
- base valence.

Invert the task policy:

    target 0 -> output 1
    target 1 -> output 0.

Result:

    content geometry equal = true
    report equal = true
    valence equal = true
    task behavior equal = false.

Therefore selected content structure does not uniquely determine a particular task policy without specifying downstream policy/readout organization.

This matters because behavior is not simply "experience made visible." It is generated through additional organization.

## 5. Variant V — change valence only

Keep:
- base content geometry;
- base task behavior;
- base report labels.

Flip evaluative ordering:

    V'(x) = -V(x).

All six unordered condition pairs reverse preference.

Result:

    content geometry equal = true
    task behavior equal = true
    report equal = true
    valence equal = false
    pairwise preference disagreement = 6/6 = 1.0.

Thus perceptual/discrimination content geometry and valence are distinct organizational structures.

This directly supports keeping R89's valence bridge independent from content geometry.

## 6. Detection matrix

Relative to Base:

| Variant | Task behavior | Report | Grounded content geometry | Valence |
|---|---|---|---|---|
| G | same | same | different | same |
| R | same | different | same | same |
| B | different | same | same | same |
| V | same | same | same | different |

No single observable layer reconstructs all four.

## 7. Consequence for AI consciousness research

A current AI can:
- behave like a human on a task;
- use the same words;
- even show similar representational geometry;

while still differing in:
- grounded content organization;
- report mapping;
- policy mapping;
- valence/evaluative organization.

Conversely, report or behavior differences do not automatically establish content-geometry differences.

This makes "behavioral synchrony" a badly underspecified consciousness question.

## 8. Consequence for UCT

Under C1, if the selected content-bearing code corresponds to actual constitutive K relations, changing that content geometry changes the selected experiential organization.

But the downstream task/readout/valence layers are also parts of complete K.

Therefore:

- Variant G: selected content experiential structure changes.
- Variant R: complete experiential type changes because report organization changes, while selected content substructure can be preserved.
- Variant B: complete experiential type changes because policy organization changes, while selected content substructure can be preserved.
- Variant V: complete experiential type changes because evaluative organization changes, while selected discrimination content structure can be preserved.

This is the precise way to say:
different aspects of experience/organization can change independently.

It does **not** mean there are four metaphysically independent consciousness modules.

## 9. Content geometry is not valence geometry

A useful formal separation is:

    G_content = grounded causal discrimination structure
    G_valence = ordering/evaluative relation.

Two systems can share G_content but have opposite G_valence.

Thus:

    "what state is this?"
and
    "how good/bad is this state?"

are different organizational questions.

This matters directly for:
- pain;
- fear;
- reward;
- self-preservation.

A system can represent termination accurately without negative valence.
A system can avoid a state instrumentally without fear.
These earlier R84–R105 conclusions are consistent with R116.

## 10. Behavior should be split into channels

R116 also clarifies that "behavior" is not one variable.

At least distinguish:
- task action;
- report/communication;
- preference choice;
- motor/tool output.

Two systems can match on one behavioral channel and diverge on another.

Thus cross-substrate comparisons should always name the output channel.

## 11. G1/G2/G3 test

The variants expose the limits of the R115 evidence levels.

### G1 — task behavior
Cannot distinguish Base from G, R or V.

### G2 — ungrounded representation geometry
Can miss the Base/G distinction if only abstract distance multiset/isometry is used.

### G3 — anchored causal geometry
Distinguishes Base and G because grounded x-to-content relations differ.

But G3 alone does not detect Variant V, because valence is deliberately kept outside content geometry.

Therefore even a strong G3 content match is not a complete experiential match.

## 12. A stronger decomposition of complete experiential organization

Within the selected research view, complete E can contain relational substructures corresponding to:

    content discrimination
    temporal access/memory
    self/bearer organization
    policy/action
    report
    evaluative/valence organization
    and other constitutive relations.

This should not be mistaken for a complete taxonomy of experience.

It is a research decomposition of K/E relations already motivated by the project.

## 13. Exact finite checks

The exact script verifies:

Base vs G:
- same task behavior;
- same report;
- same valence;
- different grounded content geometry;
- same unlabeled distance multiset.

Base vs R:
- same content geometry/task/valence;
- different report.

Base vs B:
- same content geometry/report/valence;
- different task behavior.

Base vs V:
- same content geometry/task/report;
- opposite valence;
- all 6 pairwise preferences reversed.

## 14. Next step

R117 should ask whether the four-layer decomposition can be turned into a **minimal cross-substrate experiment design**.

Choose one non-emotional domain first, likely:
- calibrated visual color/shape;
- spatial evidence state;
- controlled bearer identity.

The experiment should measure:
1. task behavior;
2. report;
3. anchored causal content geometry;
4. evaluative preference separately.

Then perturb one layer while matching the others as far as possible.

This would be the first direct cross-substrate test of the architecture developed in R106–R116.

## 15. Status

R116 is a transparent logical/mechanistic proof of concept.

The separability of representation, action, report and value has broad prior art. The project-specific result is their integration into the UCT cross-substrate evidence architecture.

No AI phenomenology is measured.
