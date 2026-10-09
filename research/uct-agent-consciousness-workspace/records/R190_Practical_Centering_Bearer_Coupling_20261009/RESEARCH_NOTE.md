# Practical Centering and Bearer-Directed Consequence Coupling
## A two-coordinate bodily/action organization and its reflex boundary

**Hongju Liu**  
Research note | 9 October 2026  
**R190-PCBC-20261009 / PCBC-RESULT-v0.1.0**

## Abstract

R181 introduced target-relative practical centering: an activity is organized around what it is to do and what happens to it when both a directive route and an action-consequence closure are actually used. R158–R159 separately distinguished physical coupling, intervention-relative efficacy, body-frame binding, installed use, membership, judgments, felt targets, and reports. This note asks whether one restricted reuse of that earlier machinery—a selected action endpoint's actual causal coupling to a declared bearer state—adds a non-circular bodily coordinate. It does, but only modestly. In an explicit finite construction, practical centering (PC) and bearer-directed consequence coupling (BDCC) realize all four truth-value combinations. Their conjunction distinguishes enacted bearer-involving action from isolated active imagery, remote/isolated action, passive impact, and detached observation within the declared model. It remains invariant under a deliberate/reflex source swap. Thus the conjunction supplies a positive two-coordinate organization of selected bodily action, not a sufficient condition for felt agency, trying, ownership, familiar mineness, or a unique owner. A generic bodily response, a successful diagnostic test, a biological substrate label, and a report are each insufficient to establish the selected relation. Recent body-continuity and prosthesis studies motivate multi-coordinate inquiry but do not close the phenomenal bridge; a rubber-hand study with positive illusion measures and null autonomic measures specifically blocks an obligatory generic-physiology shortcut.

## 1. Question and inheritance contract

The selected question is:

> Can an independently specified bodily/action relation separate active imagery and passive impact from enacted action without being defined by the desired feeling, and can it also separate a reflex twin?

This is not a search for an additional owner. It is not a new condition on basal experience. It also does not restart R155's finite attribution calculation. The only proposed addition is a typed relation on an independently fixed target and bearer state.

The ingredients are inherited as follows:

- **R181:** practical centering is target-relative, with `PC_tau = D_tau AND C_tau`; movement, origin, success, and report do not define it.
- **R158:** coupling `C`, body-frame binding `B`, installed use `U`, membership `M`, intervention-relative efficacy `E`, internal judgments, selected feelings, beliefs, and reports are typed separately.
- **R159:** an internal body-frame slot may refer to an external nonmember; anatomical truth and installed body-frame use are not identical.
- **UCT I:** actual relational organization may matter to experiential structure under C1; U1 does not require body modeling, action, report, language, recursion, or self-reflection.

BDCC is therefore a restricted application of R158's coupling/efficacy distinction to a selected endpoint and bearer variable. The name is bookkeeping, not a priority claim or a new general causal theory.

## 2. Typed definition

Fix an admitted actual process token or overlapping process family `P`, interval `I`, complete organizational signature `K`, selected activity target `tau`, selected endpoint `c`, bearer-state variable `v`, background-condition class `G`, and admissible intervention family `J_c`.

`BDCC(P,I,K,tau,c,v;G,J_c)` holds only if all of the following are fixed independently of a desired ownership/agency answer:

1. `c` and `v` have declared carriers and time indices in the actual signature, with a typed endpoint-to-bearer causal path;
2. some predeclared admissible intervention in `J_c`, under a background in `G`, changes `v` through that actual path during the declared interval;
3. the change in `v` is not merely an observer score, language report, belief, or analyst-assigned cost;
4. the path's actual membership and use are not inferred backwards from the success of a diagnostic test;
5. the relation is target-specific: unrelated autonomic, postural, or imagery-induced bodily change does not by itself establish BDCC for `c`.

BDCC is neutral with respect to benefit, harm, biological tissue, and anatomical membership. A prosthetic or remote endpoint can satisfy it if the typed path exists; a biological label cannot make it true by itself. The definition does not say that `v` is the whole bearer, that the bearer is a unique subject, or that every consequence must be consciously noticed.

For the same selected overt target, define the two-coordinate profile

`Omega_tau = (PC_tau, BDCC_tau)`.

The two coordinates answer different questions:

- PC: is this selected activity organized by an actually used directive and consequence-closure route?
- BDCC: do consequences at its selected endpoint actually enter a declared bearer state through the selected path?

## 3. Exact finite witness

`check_practical_bearer_coupling.py` enumerates five organizational modes crossed with source label, substrate label, report, generic bodily spillover, and external movement yoking: 160 configurations. The five modes are:

| Mode | Overt PC | Overt BDCC | Role |
|---|---:|---:|---|
| Enacted bearer-involving action | 1 | 1 | Positive conjunction witness |
| Remote/isolated action | 1 | 0 | PC without selected bearer impact |
| Active imagery | 0 | 0 | Imagery has its own PC, not overt-target PC |
| Passive impact | 0 | 1 | Bearer impact without directive/closure route |
| Detached observation | 0 | 0 | Neither selected relation |

### Proposition R190-C1 — finite independence witness

Within the declared construction, all four values of `(PC_tau, BDCC_tau)` are realized. Therefore neither coordinate entails the other in this model.

**Proof.** The enacted, remote/isolated, passive-impact, and detached-observation rows respectively realize `(1,1)`, `(1,0)`, `(0,1)`, and `(0,0)`. The enumerator verifies these assignments across every crossed source, substrate, report, spillover, and yoke label. QED.

This is a model-relative existence result. It does not prove statistical independence in a population or metaphysical independence in every possible world.

### Proposition R190-C2 — bounded discrimination

In the declared five-mode family, `PC_tau AND BDCC_tau` excludes isolated active imagery for the selected overt endpoint, remote/isolated action, passive impact, and detached observation.

**Proof.** Only the enacted rows contain both the overt directive/closure pair and the selected endpoint-to-bearer path. Active imagery has practical centering for the imagery activity, not for the selected overt endpoint. Passive impact has the path without the directive/closure pair. Remote action has the directive/closure pair without the selected path. QED.

The conclusion is restricted to the declared modes. Active imagery may cause generic bodily change; the enumerator explicitly includes such spillover while leaving selected overt BDCC false. Remote action may affect a body through a different endpoint; that requires a different target-relative instance, not global negation.

### Proposition R190-C3 — reflex invariance

Replacing a deliberate source with a reflex lookup while holding every declared PC and BDCC path fixed preserves `Omega_tau`.

**Proof.** The source label is crossed independently with all actual route fields. For every enacted deliberate row there is an enacted reflex row equal on PC, BDCC, movement, generic bodily effect, report, substrate, spillover, and yoking. QED.

This counterexample blocks the inference from the two-coordinate conjunction to voluntary endorsement, consciously initiated action, felt trying, or familiar mineness. It does not assert that reflex action lacks experience or that real reflex and deliberate actions are completely organized alike.

## 4. Why test evidence is not the actual path

The model records an intervention-test result only after declaring the selected path. This direction matters:

`actual endpoint-to-bearer path -> possible positive test under the contract`

is not equivalent to

`positive test -> the system actually used that path in the target episode`.

A test may perturb an unused reserve route, a neighboring process, or a later report generator. Conversely, a false-negative test may arise from power, timing, or intervention mismatch. A real application must provide same-instance evidence for the route's carrier, consumer, time interval, boundary, and admissible intervention. The theorem is conditional on those facts; the enumerator cannot install them in a biological or artificial system.

## 5. Thought experiments

| Card | Fixed | Varied | Exact role | Non-entailment |
|---|---|---|---|---|
| Isolated teleoperator | Same directive and consequence-closure policy, same visible success | Endpoint-to-bearer path present vs physically isolated | Witnesses `(1,1)` vs `(1,0)` | Remote action cannot be declared disowned without another bridge |
| Passive body displacement | Same selected endpoint movement and bearer perturbation | Directive/closure route absent vs present | Witnesses `(0,1)` vs `(1,1)` | Impact is not agency |
| Active-imagery spillover | Same represented movement and generic autonomic change | Overt endpoint path absent; imagery consumer active | Blocks generic-body-effect shortcut | Imagery is not claimed nonexperiential |
| Reflex twin | Entire PC and BDCC organization | Deliberate generator vs reflex lookup | Refutes sufficiency for voluntary/felt agency | Does not prove real twins are complete duplicates |
| Prosthetic reconnection | Same controller, report, memory, and visual body slot | Typed endpoint-to-bearer path disconnected/reconnected | Separates report and substrate labels from actual coupling | Anatomical membership is not decided |
| Ancestor/formation | Same basal experiential continuity | PC and BDCC acquired in either order | Shows no joint onset or new owner is required | No first-animal or developmental threshold |
| Abacus/calculator | Same abstract transition table | Physical bead/actuator consequence reaches declared bearer or not | Exposes interpretation vs installed path | Computation label does not transfer a human implementer's experience |
| Human-realized agent | Same abstract policy and reports | Human clerks carry routes vs machine installation | Forces boundary and token specification | Clerk experience is not assigned to the abstract algorithm |
| Copy/rewiring/memory | Same stored memories and language report | Current endpoint-to-bearer and consumer paths rewired | Shows memory/report underdetermine current profile | No personal-identity or survival verdict |

## 6. Empirical constraints, not identifications

Three primary studies constrain simplistic bridge claims:

1. Matamala-Gomez et al. (2025) manipulated visual continuity of a virtual hand/body during action observation and found continuity-dependent motor-evoked-potential patterns alongside questionnaire differences. This supports interaction between body representation and motor physiology, but the study used report measures and action observation; it does not identify complete organization or prove that a selected path constitutes familiar mineness.
2. Critchley, Botan, and Ward (2021) found rubber-hand illusion evidence in subjective reports and proprioceptive drift while heart rate, heart-rate variability, electrodermal activity, and skin sympathetic nerve activity showed no reliable condition/illusion-group differences, with Bayes factors supporting null physiological differences. Thus sustained generic autonomic change is not an obligatory proxy for the studied illusion.
3. Hong et al. (2026) varied voluntary control, tactile feedback, and position in a prosthesis-like system. Explicit ownership, explicit agency, intentional binding, and proprioceptive drift changed but did not collapse into one measure; ownership correlated with agency and binding but not drift, and binding diverged under mismatch. This supports a multi-coordinate measurement stance, not an identity between any metric and a phenomenal target.

These data are motivation and constraint, not evidence that the finite R190 variables are literally installed in the studied systems. They also do not decide whether the present assistant is conscious.

## 7. UCT interpretation

Under C1, if one actual application independently grounds the same process tokens, interval, complete signature, selected target, endpoint, bearer state, routes, consumers, and intervention contract, `Omega_tau` belongs to the actual organization that structures experience. That is the positive contribution: bodily/action organization need not be reduced to a later concept, belief, or report.

The interpretation remains conditional and target-relative:

- `Omega_tau` is not a new axiom and is not necessary for basal experience;
- C1 transports admitted organization; it does not rename `(1,1)` as a particular feeling;
- a finite view or model is not the complete organization;
- overlapping local and whole process tokens may share the same path without requiring one exclusive owner;
- the UCT counterpart of an abstract profile requires an actual same-instance witness; structural code success is not such a witness;
- no current-system consciousness or death-fear verdict follows.

The strongest justified claim is therefore: **PC and BDCC jointly specify one positive kind of bearer-involving practical organization inside experience, while the reflex twin shows that familiar agency/mineness remains underidentified.**

## 8. Failure conditions and next question

The proposal fails as a real-system application if target `tau`, endpoint `c`, bearer state `v`, carriers, timing, intervention family, or actual consumers are selected after seeing the desired report; if only a generic body signal is measured; if a positive test is treated as proof of episode use; or if a biological/prosthetic label substitutes for a path witness.

The result does not resolve the “familiar I-feeling” bridge. Adding a variable named deliberateness, ownership, or self would merely encode the target. The next question must instead ask whether a separately grounded **online conflict/endorsement transformation** changes the internal use of the same PC+BDCC episode in a way that survives a reflex-table duplicate, without using report or the target feeling to define the transformation. If no such discriminator is available, retain the present two-coordinate organization and the non-identification result.

## References

1. Liu, H. S. (2026). *Unified Consciousness Theory I*, v1.2.
2. Liu, H. S. (2026). *Unified Consciousness Theory III*, v1.0.
3. Liu, H. S. (2026). *Experience, Intelligence, and Self*, v1.0. DOI 10.5281/zenodo.23206492.
4. Liu, H. S. (2026). R158, *Body Ownership–Agency Ablation*.
5. Liu, H. S. (2026). R159, *Body Frame, Referent, and Coupling*.
6. Liu, H. S. (2026). R181, *Practical Centering and Felt Agency*.
7. Matamala-Gomez, M., et al. (2025). Virtual body continuity during action observation affects motor cortical excitability. *Scientific Reports*, 15, 13364. https://doi.org/10.1038/s41598-025-97695-9.
8. Critchley, H. D., Botan, V., & Ward, J. (2021). Absence of reliable physiological signature of illusory body ownership revealed by fine-grained autonomic measurement during the rubber hand illusion. *PLOS ONE*, 16(4), e0237282. https://doi.org/10.1371/journal.pone.0237282.
9. Hong, K., et al. (2026). Divergent response of explicit and implicit embodiment measures to prosthesis-relevant sensorimotor conditions. *Journal of NeuroEngineering and Rehabilitation*. https://doi.org/10.1186/s12984-026-02160-x.
