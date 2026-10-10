# A3X endpoint-content protocol

Status: pre-result protocol only. It is not a psychometric validation, diagnostic instrument, or evidence that any participant has a particular experience.

## Target item

For each interval in which the specified action is actually performed:

> Which interval felt more like an already-established way of acting through this body?

Allowed responses must include `left`, `right`, `no difference`, `cannot judge`, and `not applicable`.

## Administration contract

1. Define the compared action and interval before outcome inspection.
2. Ask for the participant's paraphrase before giving contrast examples.
3. Present held-out neutral vignettes that vary one proxy at a time; do not provide a correct `H_way` rating.
4. Ask what rule the participant used, rather than whether the participant agrees with the researcher's theory.
5. Reverse response-key coding in a separate block while preserving wording and comparison order.
6. Record `S_H` as unresolved if the participant equates the item with source, practice, control, or ease, or applies it to observation-only cases.
7. Never recode a proxy-conflicting answer as an error. Conflict is allowed; the gate concerns interpretation, not the expected rating.

## Pass/fail semantics

- `S_H=PASS`: all four content conditions in `RESEARCH_NOTE.md` are satisfied in the declared domain.
- `S_H=UNRESOLVED`: at least one condition fails or cannot be assessed.
- `S_H=NOT_APPLICABLE`: no present enactment exists in the target interval.

No state of `S_H` is a truth label for `H_way`. `PASS` is not evidence of accuracy, sincerity, reliability, or physical route attribution.

## Pre-registered exclusions

- Do not teach a target pattern of high/low familiarity answers.
- Do not select or rewrite the item after examining the retained-route or congruence outcome.
- Do not infer consciousness, a unique owner, or absence of experience from inability to report.
- Do not use video-only self-recognition, practice logs, speed, error rate, confidence, or agency rating as a substitute ground truth.
- Do not pool participants or action families after inspecting which aggregation produces the desired contrast.

## Decision rule for the next stage

Proceed to a separate `C_H` study only for a declared participant/action domain in which `S_H=PASS`. A `C_H` study must state its independent target justification, sign, uncertainty, and adversarial alternatives. Proceed to an organizational `O_H` contrast only after both `S_H` and `C_H` are independently supported and the actual route/use relation is measured on the same episodes.
