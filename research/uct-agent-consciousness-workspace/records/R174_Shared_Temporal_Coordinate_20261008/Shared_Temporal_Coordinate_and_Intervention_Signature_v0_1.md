# A shared temporal coordinate: route identification, evidence limits and the remaining experience bridge

R174 v0.1 — 8 October 2026 — unpublished conditional UCT research note

## 1. Bounded question and result

TO20261008 exhibited two mechanisms with identical temporal-order reports but different nonreport timing commands. R174 asks a narrower question: on one actual bearer and episode, what evidence would distinguish a temporal reference used in a pre-report shared comparison from the same numerical reference used only as a response criterion?

The result has four parts.

1. A mediator-clamp signature exactly separates three stipulated routes: a shared comparator `S`, a report-criterion route `C`, and a parallel downstream bypass `H` that defeats the previous two-route contrast.
2. The positive organizational target is an actual shared temporal coordinate, not the observed signature. The signature, intervention family and exclusion checks are fallible external evidence for that target and are excluded from the C1 selector.
3. Any finite signature fails to identify unrestricted mechanisms: an untested context can activate a hidden bypass while preserving every tested observation. The positive claim is therefore rival-class and intervention-domain relative.
4. Existing primary studies constrain progressively stronger alternatives, but the inspected evidence does not supply the mediator clamp or close the phenomenal `B_order` bridge. Under C1, an independently grounded actual shared coordinate has an experiential structural counterpart; identifying that counterpart with experienced order remains an additional application hypothesis.

This is a route-identification result and an explanatory boundary, not a human experiment, neural fit, proof of C1, consciousness detector or measure of experiential amount.

## 2. Fixed objects and the target/evidence firewall

Fix one admitted actual process token `P`, episode interval `I`, complete signature `K`, ontic organization `D_K(P)`, experiential organization `Phi_K(P)`, and C1 isomorphism `h`. Fix actual occurrences or states:

- `beta`: a body-relative temporal reference available before the probe;
- `delta`: the current action–feedback arrival difference;
- `q`: a comparison mediator;
- `z`: a physical decision drive upstream of any linguistic answer;
- `u`: a nonreport timing consumer;
- `s>0`: a declared scale.

The selected ontic predicate is:

```
Theta_STC(P,I; beta,q,z,u,gamma) :=
  ReferenceTransfer(beta,q,gamma,e_bq)
  AND ComparisonOccurrence(delta,beta,q,e_q)
  AND ConsumerUse(q,z,e_qz)
  AND ConsumerUse(q,u,e_qu)
  AND SameEpisodeOrdered(e_bq,e_q,e_qz,e_qu)
  AND SameActualBinding(P,I,K,gamma).
```

`Theta_STC` says that one actual comparison value is produced using the reference and is used by both designated consumers. It does not say that `q` is conscious, reportable, accurate, unique, globally integrated or the only temporal relation in the token. Parallel routes do not make this predicate false, although they may defeat a proposed evidence bridge.

Keep separate:

| Object | Type | May enter the C1 selector? |
|---|---|---|
| `Theta_STC` and its physical parameters | actual organization, if independently grounded in `K` | yes, after grounding and transport |
| `Cert_STC(W,E)` | investigator-relative intervention/evidence record | no |
| `RoleBridge_STC` | fallible evidence-to-role application premise | no; it licenses an empirical inference about `Theta_STC` |
| experienced order target `F_order` | selected experiential interpretation | only through an additional semantic bridge, not by renaming `q` |
| overt answer `R` | report/measurement consequence | no universal target definition |

This firewall directly retains the effective R172 QC-06/07 correction: actual use and evidence of use are different objects.

## 3. Three rivals and the earlier two-route gap

Let the observable physical decision drive and nonreport command be `z,u`. Ignore noise for the exact route calculation; common additive noise can be added after the structural result. The three rivals are:

| Route | `q` | `z` | `u` | Role of `beta` |
|---|---|---|---|---|
| `S` shared comparator | `delta-beta` | `q` | `q/s` | enters the comparison before the consumer split |
| `C` criterion only | `delta` | `q-beta` | `q/s` | enters only the decision criterion |
| `H` parallel downstream bypass | `delta` | `q-beta` | `(q-beta)/s` | separately enters both downstream consumers |

At baseline, all three have `z=delta-beta`. `S` and `H` also have identical `u=(delta-beta)/s`. Therefore the earlier observation `u_S != u_C` separates only the declared pair `S/C`; it does not identify a shared comparator against `H`. This is not a defect in TO20261008 P3, which explicitly limited its conclusion to fixed architectures. It is the reason for adding a mediator intervention.

## 4. Proposition R174-A — the mediator-clamp signature

For nonzero `c`, define `I_beta(c)` by adding `c` to the actual reference source. Define `I_q(bar_q)` by clamping the mediator to `bar_q` at the declared mediator port while retaining the same reference perturbation. Let `Delta_beta(z,u)` be the change under `I_beta(c)` relative to its matched baseline, and let `Delta_beta^clamp(z,u)` be the corresponding change while `q` is clamped.

The four-component signature is

```
Sigma(c) = (Delta z, Delta u, Delta z under q-clamp, Delta u under q-clamp).
```

Direct substitution gives:

```
Sigma_S(c) = (-c, -c/s,  0,    0)
Sigma_C(c) = (-c,  0,   -c,    0)
Sigma_H(c) = (-c, -c/s, -c, -c/s).
```

For `c != 0` and `s>0`, the three vectors are pairwise distinct.

**Proof.** `S` loses every `beta` effect when `q` is fixed because both designated consumers receive the changed quantity only through `q`. `C` retains the criterion effect on `z` and has no `beta` effect on `u`. `H` retains both downstream effects under the clamp. The displayed coordinates differ pairwise. QED.

The theorem identifies the three stipulated equations only when all occurrences, ports, scale, clamp, reference perturbation, readouts and comparison interval are held to the same actual binding. A binary answer need not reveal a small `z` change; use an independently calibrated physical decision-drive measure or a separately justified strictly monotone response-law inference. The latter is still evidence, not the target definition.

### Failure conditions

The signature is uninformative if the clamp misses the actual mediator, changes `beta`, disrupts consumer calibration, recruits compensation during the measurement window, or if `z/u` have unrecorded alternative paths that violate the declared rival class. Absence of the predicted signature then refutes the stipulated application package, not C1, experience or all temporal organization.

## 5. Proposition R174-B — finite route evidence has an open-world limit

Let `W` be any finite tested set of contexts and interventions, and suppose the admitted physical context domain contains an untested `x*`. Start with route `S`. Add a hidden gate `g` and a bypass from `beta` to `u` such that `g(x)=0` for every tested `x in W` and `g(x*)=1`. The bypass contributes `g(x) beta/s` and is otherwise physically silent.

Every measured value and intervention signature on `W` is exactly unchanged, but at `x*` the actual route set differs and the claim that every relevant `beta` effect is mediated by `q` is false.

**Proof.** On `W`, `g=0`, so the added term vanishes pointwise. At `x*`, `g=1`, so a `beta`-dependent effect reaches `u` without passing through `q`. QED.

This is a scoped nonidentification result, not another general certificate programme. R174 stops at the following boundary: the mediator-clamp signature is decisive for the predeclared `S/C/H` family and declared intervention closure; unrestricted mechanism identification needs an independent physical closure premise. A finite failure to find a bypass is not that premise.

## 6. Primary-source evidence ladder

The target `F_order` is fixed as the experienced order of a voluntary action and its sensory consequence, not as a button response. Reports, psychophysics and physiology are fallible measures of this independently described target.

1. **Delayed-feedback temporal-order shift.** Stetson et al. (2006) exposed participants to delayed action feedback and found post-adaptation temporal-order reversals in judgments, with illusion-associated ACC/MFC BOLD activity. This motivates a body-relative temporal-order target and shows that a static external event order does not fix judgments. It does not identify `S` against `C`, because those routes have identical report laws in the present model.
2. **Cross-modal transfer.** Sugano, Keetels and Vroomen (2010) found comparable transfer between motor-visual and motor-auditory lag adaptation and argued for a motor-component shift rather than a modality-pair-specific criterion. This rejects a narrower `C_mod` whose criterion is tied to one sensory pairing. It does not reject a modality-general motor/report criterion `C_gen`; both test phases remain temporal-order judgments, and no nonreport consumer or mediator clamp was reported in the inspected source.
3. **Motor and visual potential shifts.** Cai et al. (2018) reported MEG/fMRI timing shifts in motor and visual potentials after lag adaptation; the motor shift was larger and correlated with the psychophysical adaptation measure. This is stronger evidence that adaptation is not exhausted by a late verbal label. The inspected abstract nevertheless reports observation/correlation, not the path-specific mediator intervention and consumer-use evidence required by `Cert_STC`.
4. **R174 evidence target.** A valid same-instance source perturbation plus mediator clamp, calibrated `z/u` readouts, locality/fidelity checks, and an explicit rival/closure statement would separate `S/C/H`. No claim is made that an existing human experiment has already supplied this complete package.

The ladder is asymmetric: later evidence narrows mechanisms but does not turn earlier reports into direct experience observations, does not prove complete neural organization, and does not establish `B_order`.

## 7. Conditional UCT attachment

Assume one actual token and interval satisfy `Theta_STC`; every primitive and parameter has an independent well-sorted `K` interpretation; `gamma,beta,q,z,u,s` are physical parameters transported by `h`; and the same `P/I/K/D/Phi/h` binding is retained. R157 formula preservation gives:

```
D_K(P) |= Theta_STC(beta,q,z,u,gamma)
iff
Phi_K(P) |= Theta_STC(h(beta),h(q),h(z),h(u),h(gamma)).
```

Neither `W`, `E`, a pass/fail certificate nor the names `shared coordinate` and `experienced order` are transported unless independently part of the actual signature in the required roles. The result is an experience-internal structural temporal coordinate under C1. It is not yet a theorem that the coordinate is the selected experienced order.

## 8. `B_order` remains open, but its burden is sharper

A candidate bridge may now be written:

```
B_order: on a predeclared class of action-feedback episodes,
the transported Theta_STC coordinate constitutes the selected experienced-order relation.
```

For this bridge to advance beyond a name it must:

1. fix orientation, episode domain and correspondence before outcomes;
2. explain why one comparison shared by a no-report timing consumer is relevant to experienced order rather than only successful control;
3. specify measurement without defining the target as the answer;
4. permit nonreporting tokens and undefined measurements;
5. fail when an independently warranted `F_order` contrast lies inside a `Theta_STC` fiber, or when `Theta_STC` changes while `F_order` is independently invariant where sensitivity is claimed;
6. preserve the distinction among `F_order`, `F_O`, `F_A`, `F_F`, conceptual I and report.

The reviewed primary studies motivate the target and constrain criterion variants, but they do not discharge these six obligations. The honest result is therefore conditional structural progress plus a recorded semantic/empirical failure, not a false closure.

## 9. Thought experiments and retained families

**R174-TE1 — source perturbation and mediator clamp.** Fix one body-relative episode, values, consumers and report mapping. Change only the source reference, then clamp the mediator. Its role is a three-rival definition/identification test. The remaining uncertainty is intervention fidelity and rival closure, not whether baseline reports match.

**Formation/ancestors.** Let a body-relative timing relation become routed into a common mediator before language develops. This tests the no-report domain of `B_order`; it does not claim an evolutionary onset of basal experience.

**Abacus/calculator.** An external table can contain the correct `beta` while no actual transfer reaches `q`. Correct stored numbers and successful reports do not satisfy `Theta_STC`.

**Human-realized agent.** Participants, the implemented computation and the coupled process may each possess different temporal relations. The same clamp protocol must name its bearer; it does not select one exclusive subject.

**Copy/rewiring/memory.** Copy `beta` and every baseline output, then reroute its effects through `H`. Baseline sameness and copied history fail to fix the shared coordinate; the mediator-clamp signature separates the stipulated routes. Numerical identity and familiar mineness still do not follow.

## 10. Direction and joint-premise audit

- **Core purpose:** the result connects an actual body/action temporal relation to a conditional experiential coordinate and a precisely bounded phenomenal bridge. It is not generic controller optimization.
- **All-of discipline:** signature separation requires the same actual binding, nonzero perturbation, positive scale, localized source intervention, faithful mediator clamp, fixed calibrated consumers and the declared rival class simultaneously.
- **Object/time discipline:** reference, mediator, consumer occurrences, external interventions, evidence record, selected experience and report are distinct sorts. Compared routes are alternatives, not simultaneous assignments to one token.
- **Actuality/evidence discipline:** equations and code instantiate abstract rivals; an actual application needs `RoleBridge_STC`. A test result is not a constituent of experience.
- **Inference direction:** report shifts do not prove `Theta_STC`; `Theta_STC` plus C1 does not prove `B_order`; failed route evidence does not prove absence of experience.
- **Finite boundary:** the `S/C/H` theorem is exact on its declared class. The hidden-gate witness blocks unrestricted extrapolation.
- **Founding constraints:** no new report, action, history, self-model, integration or control gate is added to basal experience; no unique owner or present-assistant verdict is inferred.

## 11. Sources and novelty boundary

- UCT I v1.2, §§2.5, 3.5, C1, 6.4, 8.11–8.14 and 14.7, pinned in the repository.
- R157 definable-coordinate transport and semantic residual.
- Effective R172 QC-06/07 actual-role/evidence/parameter correction.
- R173 retentive history; TO20261008 temporal-reference construction.
- Stetson et al. (2006), *Neuron* 51:651–659, DOI 10.1016/j.neuron.2006.08.006.
- Sugano, Keetels and Vroomen (2010), *Experimental Brain Research* 201:393–399, DOI 10.1007/s00221-009-2047-3.
- Cai et al. (2018), *NeuroImage* 172:654–662, DOI 10.1016/j.neuroimage.2018.02.015.

The algebra, intervention logic and hidden-context witness use elementary causal/model reasoning and are not claimed as new general mathematics. The project-level contribution is the typed three-rival repair, its exact evidence firewall, the source-evidence ladder and the sharper UCT bridge boundary.
