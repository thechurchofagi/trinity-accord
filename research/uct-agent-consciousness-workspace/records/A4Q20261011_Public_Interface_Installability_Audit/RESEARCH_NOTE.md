# Where a public robot interface does—and does not—reach bodily anchor use

## Abstract

A4P specified eight simultaneous premises for identifying live bearer-anchor consumption. A4Q tests those premises against one concrete public interface family: the Universal Robots e-Series RTDE / ROS 2 driver / UR Client Library boundary. The published interface makes actual joint and TCP state available as controller outputs and accepts motion targets through a reverse command path. This does not expose a stock splice into the native internal proprioceptive consumer. Cutting or rescuing a ROS command controller therefore concerns the command route, not the internal anchor route. A custom external closed loop can define a legitimate composite route that consumes `actual_q`, and its input can in principle be blocked and rescued at the same software argument. Yet the public documents do not jointly close external geometry, controller inventory, post-arbitration event/source evidence, packet timing or an actual pinned token. The result is a scoped non-installability finding for `rho_int` plus a bounded installability recipe for `rho_ext`, not a theorem of robotic impossibility and not an experiential or report result.

## 1. The positive organizational target

The relevant body/action relation is not successful motion or a robot reporting a body state. It is the actual current use of a bearer-centred anchor by a selected route. In a composite route, current joint state can constrain an externally computed action whose command returns to the same arm. This is a concrete organizational candidate for an action-relative perspective. Under a separately admitted complete token, C1/R157 could conditionally transport that relation within experiential organization. R159 still separates the internal relation from an external tool referent, while the semantic residual blocks naming it `H_cf` without `B_cf` and calibrated target evidence.

## 2. Four public-interface candidates

| Candidate | What is actually exposed | Can A4P block/rescue the anchor input? | Interpretation |
|---|---|---|---|
| telemetry observer | `actual_q` / TCP state to a logger | no consumer-to-action route | observation only |
| command-only controller | targets to ReverseInterface | no evidence that current anchor is consumed | external command route only |
| native internal controller | internal sensing and control | no public native-anchor splice documented | target route is inaccessible at the selected boundary |
| custom external closed loop | RTDE state into `C_ext`, target back through ReverseInterface | prospectively yes at the declared `C_ext` argument | a new composite route, not evidence about the native internal route |

The fourth candidate is the constructive advance. It does not make the original native route accessible, but it supplies an explicit route grain at which A4P's intervention logic is meaningful.

## 3. Why command exclusivity is not controller closure

The ROS documentation says only one controller may claim a command interface at a time. That is valuable resource arbitration evidence. It does not imply that all causally relevant writers/controllers inside the larger bearer have been excluded. The same documentation describes safety scaling and stop behavior, built-in planners and motion primitives, URScript execution and read-only broadcasters. The safety manual describes a separate safety system that can stop or reduce motion. Those mechanisms may be correct and required; their presence simply means that command-resource exclusivity is weaker than A4P `P_closed`.

For the prospective `rho_ext` trial, safety action is not an adversary to bypass. It is a declared alternate causal path whose activation invalidates a trial for the narrow identification claim. The experiment may be made safer without pretending that safety intervention is absent.

## 4. Timing and actuality

Controller timestamp, `control_step`, execution-time/status outputs and ReverseInterface timeouts are useful coordinates. RTDE nevertheless permits skipped output packages and latest-value delivery. The evidence must therefore distinguish at least physical anchor change, controller sampling, RTDE publication, external receipt, consumer commit, reverse-command issue, internal acceptance/arbitration and plant transition. A single PC receipt time or high nominal frequency cannot establish that chronology.

No device was operated in A4Q. No firmware, calibration, controller set, program, custom consumer, external tracker or trial interval was pinned. The result is an audit of documented interface affordances, not an actual installation.

## 5. Stable results

**A4Q-C01 — public-direction result.** In the inspected public RTDE table, actual joint/TCP state is controller-to-client output, while the documented external write path supplies I/O/register/external-wrench values and motion targets through other interfaces. No stock native `actual_q`-substitution port at `rho_int` is documented.

**A4Q-C02 — route-grain correction.** A ROS command-controller cut is a cut on `rho_cmd`, not on the native `actual_q -> C_int` relation. It cannot discharge A4P `P_block` for `rho_int`.

**A4Q-C03 — composite-route possibility.** A custom controller consuming RTDE `actual_q` and returning a command can define `rho_ext`; block and same-argument rescue are then prospectively meaningful for that composite route, without licensing inference to `rho_int`.

**A4Q-C04 — closure separation.** Single ownership of a ROS command interface does not establish A4D–A4G completeness over the robot, control box, safety system, URScript/native planners, external processes and physical disturbance paths.

**A4Q-C05 — present non-installation.** On the document-only evidence in this round, neither `rho_int` nor `rho_ext` satisfies all eight A4P premises on one actual token. The appropriate status is `NOT_INSTALLED`, not route absence, impossibility or phenomenal absence.

## 6. Refuters and limits

A vendor- or research-supported pre-estimator/sensor-to-consumer splice with verified same-port substitution would refute the scoped claim that the inspected stock public interface lacks such a port. A pinned custom external closed-loop trial satisfying every item in §5 of the contract would refute present non-installation for `rho_ext`. Neither would by itself establish `H_cf`.

The audit is limited to public documents retrieved on 2026-10-11. Documentation can lag firmware or omit internal interfaces. The word “stock” therefore means only the public interface described by the sources, not all hardware possibilities.

## 7. Retained thought-experiment families

| Family | Fixed | Varied | Function in A4Q |
|---|---|---|---|
| ancestor/formation | current composite event and basal C1/U1 status | whether the external consumer was actually formed/trained and now uses `actual_q` | keeps learned anchor use from becoming an experience-onset condition |
| abacus/calculator | endpoint, command and visible trace | telemetry logging, command-only control, or live anchor-consuming feedback | separates representation/observation from installed current use |
| human-realized agent | abstract controller and report | robot internal consumer, external PC consumer, and human operator | prevents transfer of one bearer's body relation to nested represented processes |
| copy/swap/memory | copied code and route table | live port, calibration, controller set, chronology and bearer boundary | shows identical software/output does not install the same current relation |

## 8. Direction check

The result returns to the experience–intelligence–self question by locating the exact organizational relation that a physical interface would need to expose. It adds no introspection, report, language, self-model, integration, recursion, accurate-prediction or continuation-control threshold to basal experience. It preserves overlapping/nested robot, PC, human and larger-system processes and selects no exclusive owner. It makes no determinate claim about this assistant's consciousness or death fear.

