# Public-interface contract for an anchor-consuming action route

Version: A4Q-PIIA-v0.1.0  
Status: document-grounded interface audit; no robot token, trial or phenomenal target is installed.

## 1. Frozen candidate bearer and route grains

The bounded device candidate is one Universal Robots e-Series arm, its control box and safety controller, one external PC running the official ROS 2 driver and UR Client Library, one declared tool, and one bounded command event. Software, protocol, calibration, tool configuration, controller set, program and network path would have to be pinned for a real trial; this round has no such hardware or version witness.

Three routes must not be conflated:

1. `rho_int`: joint sensing and internally calibrated state are consumed inside the robot controller before a motion output;
2. `rho_cmd`: an external target is sent through a ROS controller / ReverseInterface / URScript path to the robot controller;
3. `rho_ext`: `actual_q` is exported by RTDE, consumed by a custom external controller, and a resulting target is returned through the reverse command path.

Only `rho_ext` exposes a candidate anchor-consumer input that an experimenter could block and rescue in the same custom consumer. That would be a relation of the composite robot-plus-PC bearer. It would not identify `rho_int`. Merely exercising `rho_cmd` supplies no evidence that the external program consumes the current joint anchor.

## 2. Documented public directions

The official RTDE table types `actual_q`, `actual_qd`, `actual_TCP_pose` and controller timestamp as controller outputs. Its public controller inputs are I/O values, general-purpose registers and an external wrench field; the table does not expose `actual_q` as a controller input. The ReverseInterface accepts joint position, velocity, trajectory, Cartesian velocity/pose and torque command vectors. ROS controller exclusivity states that only one controller may claim a command interface at a time, while read-only broadcasters do not claim the resource.

This supports a directional distinction:

```text
internal sensed/calibrated state --RTDE output--> external observer or consumer
external target/command --------ReverseInterface--> internal motion stack
```

It does not document a splice that overwrites the internal sensed-state value at the native `rho_int` consumer. This is an inference from the published field directions and controller semantics, limited to the inspected public interface; it is not a claim that no vendor-internal or custom research interface could exist.

## 3. Port and timing table

| A4P obligation | `rho_int` through stock public interface | `rho_ext` with a custom external consumer | Current audit result |
|---|---|---|---|
| `P_same` | native consumer and exact anchor port are not named | bearer/consumer can be declared but are not actually installed or hashed | not discharged |
| `P_ext` | internal TCP estimate is downstream of internal sensing and calibration | needs an independent external target/tool tracker | external extension required |
| `P_anchor` | current joint/TCP state is observable but not writable at the native consumer | physically change posture/base relation, verify independently, and read `actual_q` | feasible schema, not installed |
| `P_block` | stopping a ROS controller cuts `rho_cmd`, not the native anchor edge in `rho_int` | custom code can cut the `actual_q` argument after receipt and before consumption | custom instrumentation required |
| `P_rescue` | commands do not enter the native sensed-state interface | custom code can substitute a calibrated value at that same external argument while the native feed stays cut | custom instrumentation required |
| `P_closed` | ROS command-resource exclusivity does not inventory internal safety, scaling, URScript, native planning or physical/human paths | same unresolved internal paths remain, plus external process and network paths | not discharged |
| `P_event` | timestamps and status are observable, but no source-specific post-arbitration/pre-plant witness is documented | add a fresh challenge, post-consumer command probe, controller/thread status and common-control negative tests | not discharged |
| `P_readout` | RTDE provides joint/TCP outputs, but outputs may be skipped and TCP is internally computed | predeclare frames, tolerances, controller timestamp/control step and packet-skip policy; retain an independent external readout | conditional support only |

RTDE may publish at up to the controller loop frequency, but the controller may skip output packages and send only the latest state. Therefore network receipt order is not, by itself, proof of native issue–consume–arbitrate–plant chronology. ReverseInterface timeouts bound command freshness but do not identify which internal state relation generated or consumed a command.

## 4. Cut-location result

Let `A -> C_int -> T_int` denote the selected internal anchor, its native consumer and an internal transform. Let `X -> C_cmd -> U` denote the external command path. Disabling a ROS controller intervenes on `X -> C_cmd`; it is not a cut on `A -> C_int`. A same-command-interface rescue therefore tests the command route, not the native anchor route. Re-labelling that cut after observing motion would change the route grain and violate `P_same`.

For `rho_ext`, the cut can be placed at `actual_q -> C_ext` and rescue can use the same `C_ext` argument. That makes a legitimate prospective anchor-consumption experiment for the composite route, provided all eight A4P premises are independently satisfied. The public documentation alone does not satisfy them.

## 5. Minimum installable extension

An admissible `rho_ext` trial would require all of the following on one token:

1. pin robot, controller, safety configuration, firmware, calibration, tool, PC, OS, driver/library commits, RTDE protocol and custom consumer hash;
2. define the composite bearer and the exact `actual_q` argument consumed by the custom controller;
3. use an independent external tracker to hold or measure target/tool geometry and to verify the sign and timing of the physical anchor perturbation;
4. cut the received anchor after timestamp/sequence validation and before the consumer calculation; rescue only at that same argument while native input remains cut;
5. bind a fresh anti-current challenge to a post-consumer command vector and a post-arbitration/pre-plant witness under A4D–A4G;
6. inventory every motion-capable ROS controller, URScript thread, built-in planner, force/freedrive/manual path, dashboard/program path, safety limiter, network/process writer and physical disturbance inside the boundary;
7. treat every safety intervention, packet skip, clock ambiguity, unlisted writer or route switch as invalid/inconclusive rather than as support for route use;
8. freeze the coordinate transform, latency window, tolerance and comparison strata before observing results.

If this package succeeds, the conclusion is only device- and event-relative use of the external composite anchor route. `rho_int`, complete UCT actuality, C1, a specific `H_cf`, report reliability and an exclusive owner remain separate.

## 6. Stop and return rule

Stock public documentation is insufficient to install A4P on `rho_int`. A custom `rho_ext` design remains a prospective candidate but is not installed here because controller closure, event/source witnessing, independent geometry and actual same-instance binding are absent. The robotics branch therefore stops at a scoped interface result and returns the next research step to finding a genuinely inspectable sensor-to-consumer splice or building the one bounded `rho_ext` witness package. No interface success or failure changes U1 or supplies a consciousness verdict.

