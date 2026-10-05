# R79 — Preservation versus tradeoff in a learned organization

Hongju Liu / UCT agent-consciousness research. 2026-10-05. Secondary analysis of archived R78 checkpoints. No additional training or model API call; published A/B/C unchanged.

## 1. Result

A learned representation can support more robust binary decisions while failing to preserve some decisions supported before learning. Counting usable distinctions or tasks therefore does not establish enrichment. The correct restricted comparison asks whether every old decision remains available, not merely whether the number of available decisions increases.

On R78 seed 3, with hidden-state perturbations bounded in Euclidean norm by epsilon=0.5, the initial representation supports 4 of the 16 binary labelings of the four inputs; the trained representation supports 8. Nevertheless the two task sets are incomparable. The old code preserves the second input; the new code loses that robust distinction but gains equality/parity. These are properties of a specified interface and perturbation family, not amounts of experience.

This round supplies a necessary-and-sufficient criterion for this finite robust decision comparison, computes all change regimes of the archived models, and records the scope in which the ordering can change. The mathematics has direct common-information/confusability and partition-order antecedents. It is a project-specific application, not a new consciousness theorem or a claim of historical priority.

## 2. Why this follows the A/B/C route

A v1.2 §9 distinguishes strict enrichment from more general transformations, including specialization, compression and reweighting. C1/U1 does not require any of these mechanisms, or introspection, to switch experience on. B requires an independently anchored physical view, fixed bridge rules and explicit residual assumptions. C separates actual task performance, full organizational type and finite observations.

R78 already showed learned interaction at fixed parameter count, with two complete task successes and six incomplete solutions. It also found a geometric tradeoff in the two successes. R79 turns that tradeoff into a full finite decision comparison instead of creating more training runs or returning to linguistic self-report.

R61 already proved noiseless partition-factorization criteria; R65 already distinguished a preserved core from preserved whole organization. The present addition is the error-set-aware comparison and its complete evaluation on actually trained checkpoints, including unequal task counts with non-inclusion.

## 3. Definitions fixed for this analysis

Let H be the four allowed input histories, indexed

    0=(-1,-1), 1=(-1,+1), 2=(+1,-1), 3=(+1,+1).

For a fixed checkpoint, let e(h) be its recorded two-dimensional hidden activation. Declare nonempty uncertainty/perturbation sets U(h). In the numerical application they are closed Euclidean balls B(e(h),epsilon). A binary task f:H->{0,1} is robustly realizable when some deterministic decoder d satisfies

    d(z)=f(h) for every h and every z in U(h).             (1)

The decoder class is unrestricted: cost, linearity, memory and training constraints are not imposed. Availability under (1) therefore does not mean the actual trained readout already realizes the task. All four input histories remain allowed; we do not select a favorable communication codebook.

Two distinct interpretations of U must remain separate:
- Epistemic uncertainty about a measured activation changes what an observer can identify. It does not alter the process or its experience.
- Actual bounded perturbations applied at a declared internal interface define a robustness property of the computational organization. R79 computes that counterfactual property but does not execute new physical perturbations.

Neither interpretation identifies a scalar experiential amount. The original R78 experiment is unchanged.

## 4. Robust realizability criterion and proof

Construct the overlap graph on H: connect h and h' exactly when U(h) intersects U(h'). Let Pi_U be its connected-component partition.

**Criterion.** A binary task is robustly realizable iff it is constant on each component of Pi_U.

Necessity: for any edge, a shared possible state z must receive one decoder value, so f(h)=f(h'). Equality propagates along paths. Sufficiency: if f is constant on components, assign to any z in the union of the sets the value of a component containing a compatible h. Distinct components cannot share such a z; hence this is well-defined. Decoder values outside the union are irrelevant.

Consequently, if Pi_U has k components, exactly 2^k binary labelings satisfy (1). For Euclidean balls of a common radius, an edge exists iff ||e(h)-e(h')||<=2epsilon.

**Preservation criterion.** Write T_old,T_new for the two task sets. Then

    T_old subseteq T_new
    iff Pi_new refines Pi_old.                            (2)

If Pi_new refines Pi_old, any function constant on old components is constant on new ones. Conversely, if a new component joins members of distinct old components, a binary indicator of one old component belongs to T_old but not T_new. Strict inclusion holds precisely for strict refinement, for this unrestricted binary task family.

This is a restricted robust capability order. It is not an embedding of the complete old physical organization, and does not alone certify full experiential enrichment under A. Its proof is a standard partition/common-function argument.

## 5. Applying the criterion to all R78 checkpoints

The analysis includes all 16 original runs (8 full training and 8 readout-only controls). It compares initial and final hidden tables. For each pair, all six pairwise distances on each side determine the complete set of possible graph changes as epsilon varies. The implementation retains all 112 joint regimes, plus a ten-value display grid. It tests every one of the 16 binary labelings; no task was selected for the counts after seeing a favorable result.

This is a secondary, exploratory analysis of existing checkpoints, not a new preregistered training outcome. The model outputs were already known from R78. Squared-distance comparisons use 200-digit Decimal arithmetic on the exact archived binary64 centers. This improves numerical graph decisions but does not recover an ideal infinite-precision neural computation or measure physical activation noise. Narrow numerical intervals are marked; the reported illustrative epsilons are well away from critical boundaries.

### One trained checkpoint has several different restricted orders

For successful seed 3:

| epsilon | Initial components | Final components | Binary task counts old/new | Set relation |
|---:|---|---|---:|---|
| 0 | 0 / 1 / 2 / 3 | 0 / 1 / 2 / 3 | 16 / 16 | Equal availability |
| 0.01 | 0 / 1 / 2 / 3 | 0 / 12 / 3 | 16 / 8 | Old strictly contains new |
| 0.50 | 02 / 13 | 0 / 12 / 3 | 4 / 8 | Incomparable |
| 0.65 | 0123 | 0 / 12 / 3 | 2 / 8 | New strictly contains old |
| 1.00 | 0123 | 0123 | 2 / 2 | Equal; only constant tasks |

Here 12 denotes the set {1,2}, not the number twelve. The task counts include two constant tasks, so a count of 2 does not mean two informative distinctions or two experiences.

At epsilon=.5, the initial components 02 and 13 retain the second input. Its labels (0,1,0,1) are constant on those components. The new component 12 joins two different values of that input, so this task is lost. Equality/parity has labels (1,0,0,1); it is constant on the new components but not the old ones. Of the task sets, two constants are shared, two old tasks are lost and six new tasks are gained. More tasks therefore coexists with loss of old tasks.

The new equality/parity task is not only available to an imaginary decoder at epsilon=.5: the actual trained linear readout has the R78 sufficient margin radius .696108, so it is robust throughout this error ball. At larger epsilons, ideal decoding availability and this particular readout must still be distinguished. For example, a task-availability statement at epsilon=.8 does not establish that the existing readout is robust there.

Successful seed 6 displays the same types of comparison at different scales: at epsilon=.01 old strictly contains new; at .7 they are incomparable; at .8 new strictly contains old. These are not claims that the physical experience changes when the analyst changes epsilon. They show that the comparison property being asked about changes.

All eight readout-only controls preserve the hidden tables and have equal task sets throughout every regime. The six incomplete full-learning runs are retained. At epsilon=.5 they lose robust task possibilities relative to their initial codes and do not robustly support the target equality task. Their optimization failures are not removed from the conclusion.

## 6. Coordinate consistency

If an invertible coordinate map T is applied, transport U(h) to T(U(h)). Then

    U(h) intersects U(h') iff T(U(h)) intersects T(U(h')).

The overlap graph, component partition and task-set order are unchanged. This follows from bijectivity, without requiring T to preserve Euclidean distances. Replacing the transported sets with same-radius isotropic balls in the new chart generally changes the question. R77's rule of transporting the full interface therefore extends to the perturbation model.

The code checks inversion for a componentwise affine chart example; the arbitrary-bijection statement rests on the proof, not that one check. No new coordinate-dependent consciousness score is introduced.

## 7. What “organization is richer” may and may not mean here

The result permits three precise statements, each with a different burden:

1. Better realized task performance: R78 measured the existing output mechanism on the specified task.
2. Larger robust task repertoire: R79 counts tasks for an unrestricted decoder under fixed error sets; this may accompany non-preservation.
3. Preservation plus addition: (2) certifies that every old task remains realizable and at least one new task is available, at that scope.

Even (3) is not a full constituent-preserving physical embedding. It supplies neither a unique subject count nor all temporal, internal or maintenance relations. Calling it full experiential enrichment would exceed the result. Within C1, verified constitutive relationships still belong to experiential organization, independently of self-report; the additional challenge is identifying exactly which relationships the finite view establishes.

It would also be wrong to identify experience with the overlap components themselves. With purely observational error, the same physical token is assigned different observable partitions at different resolutions; C1 does not license different arbitrary experiences for that identical organization. With an actually implemented noise process, a different larger token may need to be analyzed, with its own constitutive organization. Neither case makes observational ambiguity an absence of experience.

For the inorganic-to-cell-to-AI question, this prevents a simplistic ladder based on a count. Material coupling, retained distinctions, coordinated use and self-maintenance require separate relation families and justified actual boundaries. A system can gain a useful coordinated operation without preserving every earlier distinction. The present data concern one artificial computational organization, not biological evolution or subjective experience in cells.

## 8. Prior art, reading scope and limits

Gacs and Korner (1973), Common Information Is Far Less Than Mutual Information, Problems of Control and Information Theory 2(2), 149–162, directly study common functions and component/block structure in joint distributions. This round visually inspected the author-hosted PDF's first three printed pages (149–151): introduction, definition and setup of the ergodic decomposition. The later asymptotic proof was not audited. PDF text extraction produced no text, so page images were used. Source: https://cs-web.bu.edu/faculty/gacs/papers/commoninf.pdf . The finite set-valued overlap proof here is supplied independently; it is not claimed to reproduce their entire stochastic theorem.

Shannon's 1956 zero-error-capacity literature was located at bibliographic/search level only; its full text was not read this round. The present task is not Shannon capacity: all inputs must be accommodated and label compatibility follows connected components, rather than selecting an independent codebook. Do not cite a codebook-capacity theorem as if it directly proved (2).

R61 already uses partition factorization and discusses Blackwell comparison; R77 already handles coordinate/intervention consistency. A v1.2 §9 was directly reread here. The remaining A/B/C dependency passages were read in preceding rounds and are not claimed to have been freshly audited in full.

The work has a modest project-level contribution: applying a complete error-set-aware task order to retained learned checkpoints, exposing a concrete 4-to-8 task gain without preservation, and distinguishing epistemic resolution from constitutive organization. Historical novelty and a UCT-exclusive prediction have not been established. No subjective, human, animal or new pretrained-model data were obtained.

## 9. Failure ledger and next step

- “More robust tasks means preservation”: disproved by seed 3 at epsilon=.5.
- “One network has one noise-independent richness ranking”: disproved for this task-set order by the regime table; no claim of changing experience with the analyst's resolution.
- “The current readout realizes every available task”: not implied, and the original hidden code already illustrates the gap.
- “Finite partition refinement establishes complete ontic enrichment”: unsupported; retain the distinction from A and R65.

Next move from this observation/robustness order back to the actual constitutive organization: select a small declared family of update, retention and consumer-use relations, and determine whether the trained checkpoints preserve that family. Do not expand the noise grid or task counts as a substitute for the physical relation question. A useful positive result would state which old implemented relations survive and which newly implemented relation appears, without mistaking an ideal decoder's availability for an installed computation. No new large training or self-report scoring is warranted by this round.

Conclusion: task-count increase and strict preservation are separable in the actual retained learning results. This supplies a precise limited ordering, while explicitly rejecting its use as a universal experiential ruler. Major-breakthrough status: not met.

## 10. Reproduction

Extract the companion package preserving paths and run `python r79_robust_task_order.py` from its root. The package includes the exact archived input `r78_results/R78_Summary.json`, the analysis code, complete result JSON, summary CSV, execution log and worklog. This is deterministic checkpoint reanalysis; it does not retrain a model. The result records the input SHA-256. The archived binary64 coordinates, rather than unrounded analytical training trajectories, define the numerical comparison. Decimal arithmetic at precision 200 protects the finite distance comparisons; interval widths below 1e-12 are flagged rather than interpreted as meaningful physical scales.
