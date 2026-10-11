# Three-link actual anchor-route contract

Version: A4R-TLARC-v0.1.0  
Status: disabled conditional certificate; no physical installation or phenomenal calibration.

## 1. Frozen bearer, event and selected route

Fix one actual candidate bearer `P`, one event interval `I`, one physical bearer-anchor occurrence `a`, one sampled value at port `x`, one declared current consumer `C`, one pre-arbitration command occurrence `u`, one post-arbitration plant-write occurrence `w`, one external target/tool geometry, one transform signature and one route grain. For A4Q's candidate, `P` is explicitly the robot–controller–PC composite and the route is `rho_ext`; it is not the native internal route `rho_int`.

The contract distinguishes three relations:

```text
L_s(P,I,a,x): the sampled value x is currently caused by the selected physical anchor a under the frozen transform.
L_c(P,I,x,C,u): the declared consumer currently reads x and that read occurrence contributes to u.
L_w(P,I,u,w): the selected u occurrence is a current source of the post-arbitration plant write w.
```

Define `ActualAnchorRoute := L_s AND L_c AND L_w`, with every occurrence bound to the same `P`, `I`, event and signature. Availability of a state interface is not `L_c`; a computed command is not `L_w`; a value numerically equal to an anchor reading is not `L_s`.

## 2. Local blinded challenge–block–rescue obligations

Each link receives a separately declared, information-scoped test:

1. **Anchor-to-sample (`T_s`).** Independently track the physical perturbation and external geometry; apply a fresh anti-current anchor challenge; require the sampled innovation with the predeclared sign and latency; block the selected sensor/provenance path and rescue at the same sampling port.
2. **Sample-to-consumer (`T_c`).** After input-source validation and before consumer calculation, inject a fresh route-local innovation unknown to alternative consumers at their relevant commitment time; require a corresponding pre-arbitration command innovation; cut the consumer read and rescue at the same argument.
3. **Command-to-write (`T_w`).** Apply a fresh command innovation after the consumer calculation; require a source-specific post-arbitration/pre-plant witness and plant change; cut the selected writer and rescue through the same command interface.

For each test, challenge generation, commitment order, read access, clocks, queues, replay, reset and alternate routes must be inventoried. A test is `INCONCLUSIVE`, not positive, if an admitted alternative can observe the challenge before commitment, replay the expected response, inject after the probe, suppress the witness, alter its time, or reproduce it through a shared root.

## 3. Conditional identification result

The finite audit represents each actual link by `L_i` and any admitted alternative that can reproduce that local test by `B_i`. The observed local result is `Q_i=L_i OR B_i`.

The all-positive signature `(Q_s,Q_c,Q_w)=(1,1,1)` has 27 worlds in the unrestricted six-bit model and contains all eight actual-link patterns, including `(0,0,0)`. Thus even three attractive local responses do not identify the route while bypasses remain admitted.

If, for the same event, independent source/timing evidence closes all three declared bypass classes (`B_s=B_c=B_w=0`), the same all-positive signature has one world, `(L_s,L_c,L_w)=(1,1,1)`. This is a finite conditional certificate, not a universal theorem that every unknown alternative has been excluded.

## 4. Positive organizational interpretation

When the conjunction is actually installed, the present action is not merely correlated with a body-state stream. Its sampled control coordinate is physically anchored in the bearer, currently consumed in forming the command, and carried into the present plant event. This supplies a precise candidate for the organization referred to by A4N's `BearerPerturbationDependence` and `SameRouteUsesFrame`.

Under C1, if `P` and the complete relevant organization are independently admitted, the three-link relation has an experience-internal structural counterpart. The further interpretation as `H_cf`—the fit of action unfolding through an established body/action manner—remains the open bridge `B_cf`. The certificate neither creates experience nor establishes a conceptual self, report reliability, exclusive owner or consciousness verdict.

## 5. Thought-experiment attacks

| Family | Fixed | Varied | Result |
|---|---|---|---|
| Ancestor/formation | physical perturbation and successful action | inherited sensor–consumer–writer coupling versus a late yoked bypass | formation history does not replace current three-link use |
| Abacus/calculator | correct answer and visible motion | bead-position sample read by the practiced carry operation versus a result lookup that merely moves beads | output equality does not identify `L_c` |
| Human-realized agent | algorithm, spoken command and device motion | whether the human implementer reads the declared body-relative sample and whether that command is the current writer | program identity does not transfer the relation to every nested process |
| Copy/swap/memory | copied sample value, output and report | physical anchor provenance, consumer occurrence and writer occurrence | value equality preserves none of the three actual relations by itself |

## 6. Stop rule

Do not enter `H_cf` comparison unless all three link tests and their same-event bypass closures are independently warranted on one actual token. Failure of any link denies the declared conjunction for that trial; missing fidelity or closure yields `INCONCLUSIVE`. No result changes C1/U1 or introduces an experience-existence gate.
