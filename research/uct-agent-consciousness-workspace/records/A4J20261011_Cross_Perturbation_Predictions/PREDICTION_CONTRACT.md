# Cross-perturbation signed prediction contract

## Fixed objects

Fix one bearer population, event type, body/effector, three-action grain, response lag, scoring rule and baseline. Let `Z_R` be a randomized relation-directed disruption and `Z_F` a randomized present-fit/effort-directed disruption. For `X` in `{R,F,J}`, let

`tau_X(z) = E[X | do(z)] - E[X | do(baseline)]`.

`R` is actual current use of the retained context-to-continuation relation, `F` is a prospectively specified present coordination/fit coordinate, and `J` is A4I's event-indexed continuation judgment. None is complete organization or experience by definition.

Before looking at `J`, independently establish the intended first-stage directions

- `sign(tau_R(Z_R)) = -1`;
- `sign(tau_F(Z_F)) = -1`.

The off-target signs `sign(tau_F(Z_R))` and `sign(tau_R(Z_F))` remain unrestricted in `Omega={-1,0,+1}`. This is a fat-hand design, not a selectivity assumption.

## Scoped pure signed candidates

- `B_relation+`: on this fixed intervention family, the sign of the total effect on `J` equals the sign of the total effect on `R`; `F` has no additional route to `J` inside this scoped candidate.
- `B_fit+`: on this fixed intervention family, the sign of the total effect on `J` equals the sign of the total effect on `F`; `R` has no additional route to `J` inside this scoped candidate.

These are stronger than “may contribute.” Mixed, interactive, nonmonotone and threshold bridges are outside the comparison unless separately preregistered. The plus sign denotes a declared positive orientation; it is not supplied by C1 or by the wording alone.

## Strict prediction table

Write the observed total-effect signature as `(sign tau_J(Z_R), sign tau_J(Z_F))`.

| Signature | `B_relation+` | `B_fit+` | Decision inside the scoped comparison |
|---|---:|---:|---|
| `(-,-)` | compatible | compatible | inconclusive |
| `(-,0)` or `(-,+)` | compatible | incompatible | relation-only |
| `(0,-)` or `(+,-)` | incompatible | compatible | fit-only |
| `(0,0)`, `(0,+)`, `(+,0)`, `(+,+)` | incompatible | incompatible | reject both pure signed candidates |

Cross-effects are allowed in every row. The table works because each candidate constrains a different targeted arm, not because either intervention is pure.

## Weak sensitivity

If a targeted disruption may produce either a decrease or an exact null under its candidate, replace the fixed `-` by `{-1,0}`. Four signatures then fit both, two are relation-only, two fit-only and one fits neither. Null effects lose most of their separating force. If zero reflects inadequate precision rather than a declared equivalence margin, use no sign at all and stop.

## General sign-set criterion

Let `S_R(z)` and `S_F(z)` be independently warranted allowed sign sets. Then

`P_R = S_R(Z_R) x S_R(Z_F)` and `P_F = S_F(Z_R) x S_F(Z_F)`.

An observed signature discriminates exactly when it belongs to one set and not the other. The candidate families are globally separated only if `P_R` and `P_F` are disjoint. If no first-stage sign is warranted, all four input sign sets equal `Omega`, hence `P_R=P_F=Omega^2`: the intervention names alone identify nothing.

## Stop conditions

Stop at `INVALID_PROTOCOL` if the fixed bearer/event/grain or the intended first-stage direction is not established independently of the `J` outcome, if the intervention changes the question's referent or response code, or if loss/abstention destroys the declared total-effect estimand.

Stop at `INCONCLUSIVE_BETWEEN_PURE_CANDIDATES` for an overlap signature such as `(-,-)`. Do not regress on post-formation `R`, `F`, effort, success or memory to manufacture a residual distinction.

Use `REJECT_SCOPED_PURE_CANDIDATES`, not “no familiarity” or “no experience,” when the signature lies in neither prediction set. Mixed bridges, measurement failure and wrong first-stage assumptions remain alternatives.

No empirical `H_cont` claim is licensed unless the A4I referent contract, independent signed endpoint reliability, actual same-event route evidence and complete bearer binding are also supplied.
