# Formation-intervention contract

## Required declaration

Before endpoint inspection, declare:

1. the actual bearer, action grain, formation interval, test interval, apparatus and consumer route;
2. the formation assignment `F` and its fidelity evidence;
3. every candidate control's timestamp and causal role;
4. whether the estimand is total, controlled direct, or route specific;
5. the `J_H` wording/coding and the fixed `H_way` interpretation target;
6. the positivity, missingness and selection criteria;
7. the exact result that defeats the candidate bridge.

## Variable classes

| Class | Definition | Permitted primary use |
|---|---|---|
| `C0` | Fixed or measured before formation assignment | Stratification/precision adjustment under the declared assignment assumptions |
| `T` | Actual formation-dependent trace/consumer route | Organizational target; never replaced by a fitted score or report |
| `Z` | Ease, success, value, expectation, source/agency or other descendants measured at test | Outcome, diagnostic or mediator; not a primary matched confounder |
| `J_H` | Fallible coded judgment about the fixed target | Endpoint only under A3X/A3Z content and coding contracts |
| `H_way` | Selected phenomenal target | Not an observed covariate and not identified by causal adjustment alone |

## Estimand routes

- **Route T:** estimate `E[J_H(1)-J_H(0)]`; adjust only for pre-formation `C0` in the primary contrast.
- **Route C:** estimate `E[J_H(1,z)-J_H(0,z)]` only when `do(Z=z)` is a coherent physical intervention in both arms, has joint support, and preserves the declared route question.

Observed equality or regression adjustment on a post-formation `Z` is not Route C.

## Feasibility verdict for the proposed five-way match

- Motor success, reward value, and some expectations can receive explicit experimental manipulations, but their joint cross-arm support must be shown.
- Subjective ease and source/agency feeling currently have no independently specified clamp that is known to preserve `T` and avoid directly changing the selected target or its report.
- Therefore the complete five-way residual contrast is **NOT YET INSTALLABLE AS A CONTROLLED DIRECT-EFFECT TEST**.
- A randomized total-effect formation study is installable and informative at the organizational/judgment level.

## Stop rule

If an effect exists only after descendant matching, if joint support fails, or if a clamp changes `T` or `J_H`, do not call it a residual formation effect on `H_way`. Retain the failure and report the narrower organizational result.
