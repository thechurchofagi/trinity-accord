# R80 — Information preservation does not preserve constituent organization

Hongju Liu / UCT agent-consciousness research. 2026-10-05. Research note, not a published-paper revision.

## 1. Result and contribution

The retained R78 networks expose a useful three-way distinction. Their hidden vectors can preserve all four input identities, their individual computational units can change from single-input to joint-input dependence, and their installed output mechanism can use those new dependencies. Information recoverability, constituent organization and implemented use are therefore different claims.

This round proves a restricted obstruction to preserving the old constituent organization, connects it to R78's loss bound, and executes activation interventions on all initial and final checkpoints. It does not infer an amount of experience from a score or make introspection a condition for experience. R79's robustness tradeoff remains valid: exact invertibility and poor noise robustness can coexist.

The mathematical ingredients and intervention methods have direct precedents. The contribution is a precise application and limitation of the UCT organization-first interpretation, not a historically new theorem or independent validation of C1.

## 2. Foundation, actual process and comparison scope

UCT I v1.2 section 3.5 requires a pointed comparison that preserves inputs, constituent slots, interventions, update, output and time. Section 6.3's conditional product result needs the specified constituent product and the strong tokenwise C1, not just a weak equivalence of labels. Section 9 distinguishes enrichment from transformation. These passages were reread this round from the previously retrieved published source. UCT II's finite-view limitations and UCT III's intelligence/type distinction remain dependencies from the preceding direct audits; they were not fully reread here.

Take an executed, bounded forward evaluation with loaded parameters as the target computational process. Its finite description has input registers x, two hidden array entries h, a logit register l, the ordered evaluations of h and l, and explicit activation replacement before computing l. The parameters are held fixed within an evaluation. Training updates are a different, longer process. Checkpoint files alone are not executions of the network they specify.

This software-level description is justified by the executed operations. It is not the complete physical organization of the CPU, memory and surrounding equipment. Conditional experiential interpretation requires actual tokens M_old and M_new and a common complete signature K, with these software-level relations independently justified as part of its description. A finite model alone does not certify completeness or select a unique subject boundary.

The network is

    h = tanh(Wx+b),       l = v^T h+c,

with two inputs, two hidden units and nine parameters. x ranges over the four pairs in {-1,+1}². The initial W is diagonal with nonzero diagonal entries. The input ports remain fixed; permitted constituent relabelings act separately and bijectively on the two hidden slots, optionally with a consistently declared slot permutation. Mixing the two slots while leaving their intervention meanings unchanged is not permitted.

All eight full-training runs and all eight frozen-hidden/readout-only controls from R78 are included. No new training, model API, biological data or subjective data were acquired.

## 3. Two preservation questions and their proofs

### 3.1 Recovering the input from the whole vector

For real arithmetic, finite preactivations and invertible W,

    x = W^{-1}(atanh(h)-b).

Hence the whole hidden vector retains every input distinction. Between two such encoders, the old hidden vector is recoverable from the new one by

    F(h_new) = tanh(W_old W_new^{-1}(atanh(h_new)-b_new)+b_old).

This is a bijective relation between the ideal encoder images. It is not proof that the trained model contains or uses this decoder. Nor does it preserve same-radius noise balls. Finite precision and tanh saturation can make inversion unstable, so the actual recorded finite domain is checked separately.

### 3.2 Preserving the old constituent dependence pattern

Initially, changing x2 with x1 fixed leaves h1 unchanged, and changing x1 with x2 fixed leaves h2 unchanged. After training, if all four entries of W are nonzero, strict monotonicity of tanh implies that changing either input with the other fixed changes each hidden unit in the ideal model.

Suppose a bijection phi_j acting only on hidden slot j restored the initial encoder. Hold that unit's original input fixed and change the other input. The two initial values coincide; the two new values differ. An injective phi_j cannot map the latter to the same former value. Contradiction. A slot permutation does not help when both new slots depend on both inputs. This is a port-preserving obstruction, not a prohibition on arbitrary global coordinate maps.

On the archived four-point tables the same obstruction has a finite witness: each initial unit takes two distinct values; each fully trained unit takes four. A bijection on that unit's values cannot turn four distinct values into two while preserving all input assignments. A noninvertible lookup could still recover some old labels; that is an abstraction or decoder, not preservation by local relabeling.

Consequently, global recoverability can coexist with loss of old constituent independence. The formula in 3.1 does not contradict 3.2: it can mix the units and would require transporting their interventions and readout. Applying such a map only to observational values does not establish organizational equivalence.

## 4. When better performance forces an installed joint route

Let s=x1*x2, and let expectations be uniform over the four inputs. R78 proved, for binary logistic loss L,

    d=E[s*l],       L >= log(1+exp(-d)).

Therefore L<log(2) implies d>0. With the stipulated affine consumer,

    d = sum_j v_j E[s*h_j].

There must be a unit j with nonzero v_j E[s*h_j]. A unit depending on at most one input has E[s*h_j]=0, so at least one unit must have joint dependence used by the existing readout. Relative to the initial separate encoders, this rules out preservation solely by constituent-local bijections.

This necessity result is architecture- and task-specific. It does not say every intelligent computation requires this circuit, or that d is an experience measure. R78 already supplied the loss inequality; the present step makes its consequence for the declared constituent comparison explicit.

To locate implemented use, hold the other input at context a and change xi from -1 to +1. For unit j define

    A_ij(a)=v_j [h_j(xi=+1,a)-h_j(xi=-1,a)].

Evaluate the changed input but clamp unit j to its original activation before the actual readout. The decrease in logit is exactly A_ij(a). Thus this contrast is realized by an intervention on the installed mechanism, rather than inferred from a fitted probe. Moreover,

    [A_ij(+1)-A_ij(-1)]/4 = v_j E[s*h_j],

and summing over j gives d for either input i. The equality follows by expanding the four terms. It depends on the affine consumer and does not assign unique importance under arbitrary reparameterizations.

## 5. Executed checks and results

The code recomputed both initial and final states for all 16 runs, performed all base/source/unit activation replacements (32 per checkpoint), and performed input-flip clamping at both contexts (8 per checkpoint). This gives 32 checkpoints, 1,024 activation replacements and 256 route clamps. These are small deterministic evaluations of archived trained networks; the counts are coverage, not independent experimental sample sizes.

| Property | Eight initial full-model checkpoints | Eight final full-model checkpoints | Eight frozen-hidden controls |
|---|---|---|---|
| Effective input-to-hidden dependence | Two diagonal dependencies | Four dependencies | Same two dependencies |
| Distinct values per hidden unit, four inputs | 2 and 2 | 4 and 4 | 2 and 2 |
| Whole-vector finite input identities | All four distinct | All four distinct | All four distinct |
| Joint hidden contribution used by affine output | Zero | Nonzero for both units | Zero |
| Exact old unit-local organization retained | Reference | No, under the declared comparison | Hidden encoder retained; readout changes |

Changing a zero coefficient to nonzero changes effective functional dependence. It does not create a new physical wire or add a matrix-multiplication instruction: those slots and operations existed before training. Effective dependence and implementation topology must not be conflated.

All final full-training W matrices were nonsingular; numerical determinants range from 0.802511 to 19.983030. Maximum inverse reconstruction error on the finite archived inputs was 2.80e-8, reflecting saturation and floating-point arithmetic. The ideal invertibility result is analytic; this numerical check does not establish unlimited physical precision. Maximum activation-replacement identity error was 4.25e-15.

For successful seed 3, the two route contributions are 4.11787656 and 4.11114177, summing to d=8.22901833. For successful seed 6, they are 4.04591060 and 4.12372974, summing to 8.16964035. The six incomplete solutions also have used joint routes, with d between approximately 4.726 and 4.773, but their original 50%/75% accuracy failures remain. A used joint route is necessary under the theorem's hypotheses but insufficient for perfect task performance.

## 6. Counterexamples and failed stronger claims

**Dependence without use.** Re-evaluating seed 3 with v=0 leaves its hidden joint dependence intact but makes every logit constant. This rejects any inference from internal encoding alone to downstream use. It does not reject experience of the hidden process within UCT.

**Dense dependence without the relevant combination.** With W=[[1,2],[2,1]], b=0, v=(1,1), every hidden unit depends on both inputs. Nevertheless odd symmetry gives E[s*h_j]=0 and hence d=0. The executed finite check confirms this. Counting dependencies does not certify task-relevant joint organization.

**A nonlinear consumer invalidates hidden-route necessity.** With separate h=x and l=h1*h2, the equality task has loss log(1+exp(-1))<log(2), despite no mixed hidden unit. Combination occurs in the consumer. This analytic counterexample is evaluated in the code. Removing the affine-readout premise would make section 4 false.

**No acquired within-inference recurrent memory.** Each evaluation overwrites h from its current x and fixed weights; there is no h(t) term in a subsequent hidden update. Learned weights carry effects of training, and temporary activation storage supports the present evaluation, but these are not evidence of newly acquired online recurrence, self-maintenance, future-self representation or fear. A hardware process has additional physical history; the finite graph does not deny that history.

**No independent-aggregate baseline for the entire initial network.** Both initial channels already feed a shared output. It would be false to call the whole initial computation a pile of unrelated objects. The proved change concerns its input/hidden constituent relations at a declared interface. Rock piles also have physical interactions; a literal zero-coupling caricature would not describe them.

## 7. Conditional experiential interpretation and biological comparison

Within UCT's C1/U1, experience of an actual valid token is not switched on by joint dependence or downstream use. If the established causal relations are genuine constituents of its complete organization K, they also belong to its experiential presentation. The restricted result supplies a specific difference in organization without requiring that the process access or report itself.

It does not establish that each trained model has more experience, a more unified subject, cell-like self-maintenance or human-like fear. Global information preservation plus changed local relations establishes transformation in this finite comparison. Strict whole-process enrichment needs a separately justified preservation relation covering the relevant operations, not merely the existence of an inverse for input values.

For the inorganic-to-cell-to-agent program, the useful question is which actual relations have changed: interactions, coordinated transformations, temporal retention, maintained boundaries or control of continued operation. Those families must be assessed separately. The present artificial model gives a worked example of changed transformation and consumption relations without acquiring the other listed organizations. It is not a reconstruction of cellular evolution or a measure of cellular experience.

For language models, this also blocks both shortcuts: arithmetic implementation does not imply mere unrelated aggregation, and successful language output does not identify the full organization or a human emotion. This experiment uses a four-input equality task and provides no evidence of a world model in a language model.

## 8. Direct precedents and reading scope

Rubenstein et al. (2017), *Causal Consistency of Structural Equation Models*, UAI, supplies an established intervention-preserving transformation framework. Read scope this round: targeted section 4.3, Definition 3, Lemmas 4–5 and Theorem 6/proof (PDF pages 4–5); not the entire paper or appendix. Their exact transformations permit abstraction and should not be equated with the more restrictive local bijections used here. https://staff.fnwi.uva.nl/j.m.mooij/articles/camera_ready_uai2017.pdf

Geiger et al. (2021), *Causal Abstractions of Neural Networks*, NeurIPS 34, already separates probe recoverability from causal use and applies interchange interventions. Read scope: abstract, introduction, related work, Figure 1 explanation and opening of section 3 (PDF pages 1–4); later experiments and appendices not audited. Our activation replacements are an elementary application of established interventions, not their invention. https://proceedings.neurips.cc/paper/2021/file/4f5c422f4d49a5a807eda27434231040-Paper.pdf

No third-party full text is redistributed in the package. A's port-aware signature, R65's preservation caveat, R77's coordinate warning and R78's interaction bound are direct project precedents. R80 adds the input-invertibility/local-preservation comparison and route audit on existing learned checkpoints. It does not establish historical priority, a UCT-exclusive empirical prediction or an independent phenomenal bridge.

## 9. Reproduction, conclusion and next step

Run `python r80_constituent_audit.py` with the archived R78 input at `r78_results/R78_Summary.json`. Only NumPy and the standard library are required. The package includes that exact input, input SHA-256 in results, all intervention values, counterexamples, CSV, source scope, code and execution log. A second execution followed the addition of the two analytic scope counterexamples; no model optimization or selection occurred.

Conclusion: all original input identities can remain recoverable while local causal organization changes and new joint dependencies become used by the installed consumer. This is a positive organizational result, accompanied by precise restrictions, rather than a scalar consciousness ranking. It is not a major breakthrough.

Next examine a relation-preserving extension and a matched replacement under the same boundary/input/intervention specification: can an added implemented consumer preserve the old update and readout operations while using a new combination? Reuse the trained encoder as a fixed component where useful. First derive commuting preservation conditions and identify feedback or shared-resource counterexamples; execute a small witness only if needed. Do not substitute another task-count grid, self-report benchmark, or large training run. Audit R65's existing core-preservation construction before claiming this next step as new.
