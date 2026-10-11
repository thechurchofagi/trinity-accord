# From a state stream to a bearer-anchored action: a three-link conditional certificate

Version: A4R-TLARC-v0.1.0  
Status: disabled research application; conditional finite result, not an installed robot or phenomenal finding.

## Abstract

A4Q showed that a public robot interface can expose joint state to an external controller without exposing the native internal state consumer. This note asks what positive evidence would make the external composite route relevant to body/action organization. The answer is a three-link factorization: physical anchor to sample, sample to current consumer computation, and consumer command to current plant write. Overall success, interface access, a correct command, or any single cut/rescue cannot substitute for the conjunction. An exact 64-world model gives 27 worlds with the all-positive observed signature and all eight actual-link patterns when local bypasses are admitted. Closing all three bypass classes leaves one world, the full conjunction. This yields a locally falsifiable conditional certificate and failure localization, not a universal closure theorem or experience measurement.

## 1. Problem and net contribution

A4P supplied an eight-premise end-to-end route contract; A4Q separated `rho_int`, `rho_cmd` and the external composite `rho_ext`. The remaining ambiguity is internal to `rho_ext`: a current state can be physically genuine but unused, a consumer can use a value that lacks the claimed physical provenance, and a computed command can fail to cause the present plant event.

A4R's net result is the factorization and its exact nonidentification/conditional-identification audit. It corrects the tempting inference:

```text
public state access + successful controller output + observed motion
  => bearer-anchored current action.
```

The valid target is instead one same-event conjunction `L_s AND L_c AND L_w`, with a separate blinded local challenge/block/rescue and closure obligation for each link.

## 2. Exact finite result

Let `B_s,B_c,B_w` denote admitted alternatives able to reproduce the respective local test. An observed pass is `Q_i=L_i OR B_i`. Enumerating all 64 assignments gives:

- the target observed signature `(1,1,1)` in 27 worlds;
- all eight actual-link signatures inside that fibre;
- explicit twins for physical-sample-not-used, used-sample-not-physical, command-not-current-write and fully bypassed cases;
- after setting every `B_i=0`, exactly one target world, `(1,1,1)`.

This proves only the declared finite implication. The closure claims must be independently grounded; calling a bypass “closed” does not close it.

## 3. Why the factorization matters for self-related organization

UCT I §8.12 describes body-centered organization as actual relations involving body position, action state and self-generated consequences, not an inner observer. A4R makes one such relation more precise. When `L_s` holds, the coordinate is physically about this bearer's current state rather than only label-equal to it. When `L_c` holds, that coordinate is part of the current action computation rather than passive telemetry. When `L_w` holds, the computation contributes to this action event rather than to a discarded command.

This is a positive explanation of how a bearer-relative action relation can exist within experience under C1. It is not yet an explanation of why the relation has the selected `H_cf` character, and it is not a basal-experience condition. Conceptual self-reference and verbal report remain later, separate organizations.

## 4. Counterexamples and limits

1. **Access without use:** RTDE state is correct and logged, but a fixed or hidden controller produces the command.
2. **Use without anchor provenance:** the declared consumer reads an injected/yoked value numerically compatible with posture, not the selected physical anchor occurrence.
3. **Command without plant provenance:** the controller computes the expected command, but arbitration, safety logic or another writer produces the plant event.
4. **Triple replay:** three bypasses reproduce every local pass; the fully bypassed world shares the observed signature.
5. **Challenge leakage:** a hidden controller reads the challenge before commitment. The local test is invalid, not evidence for the link.
6. **Late witness:** a log produced after arbitration or derived from the target writer is circular or temporally downstream of the fact it purports to establish.

## 5. Relation to inherited work and originality status

The decomposition inherits causal mediation, intervention fidelity, writer provenance and information-isolation ideas from A4D–A4Q and established causal/control practice. A4R does not claim invention of mediation analysis, challenge–response testing or provenance. Its proposed reusable increment is their explicit three-link application to the UCT body/action-frame question, together with the 64-world fibre result and the rule that each link needs its own same-event falsifier and closure evidence. External priority beyond the bounded source comparison is unverified; independent paper release remains HOLD.

## 6. Status

No actual robot, controller, tracker, custom consumer or event is installed. No formal graph node or rule is promoted. The result advances the design from an undifferentiated end-to-end route to a precise conditional certificate, but every actual premise and `B_cf/H_cf` remain open.
