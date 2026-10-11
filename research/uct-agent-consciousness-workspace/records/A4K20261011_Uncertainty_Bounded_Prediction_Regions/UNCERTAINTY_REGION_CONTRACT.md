# Pre-outcome uncertainty-region contract

## Fixed objects

Fix one bearer population, just-enacted continuation event, body/effector, three-action grain, response lag, response coding and baseline. Let `Z_R` and `Z_F` be the randomized relation-directed and present-fit-directed interventions from A4J. For `X` in `{R,F,J}`, let `tau_X(z)` be the randomized total effect relative to baseline.

Before unblinding `J`, freeze compact intervals

- `D_RR` for `tau_R(Z_R)` and `D_RF` for `tau_R(Z_F)`;
- `D_FR` for `tau_F(Z_R)` and `D_FF` for `tau_F(Z_F)`;
- one readout orientation interval `A` for the fixed `J_cont` coding;
- positive pure-candidate gain intervals `G_R` and `G_F`.

The intervals may be deterministic physical bounds or uncertainty sets from a disjoint/blinded calibration. If probabilistic, their simultaneous coverage event and selection rule must be declared. Marginal confidence levels are not silently treated as joint coverage. No interval may be widened, shifted or sign-selected after inspecting `J`.

## Scoped quantitative candidates

For `c` in `{R,F}`, define the common scale interval `M_c=A*G_c`. The quantitative pure candidate says that one common scale `m_c in M_c` links its named coordinate to both arm effects:

`(tau_J(Z_R),tau_J(Z_F)) = m_c (d_cR,d_cF)`, with `d_cR in D_cR` and `d_cF in D_cF`.

Thus its exact prediction region is

`P_c={m(d_R,d_F): m in M_c, d_R in D_cR, d_F in D_cF}`.

The shared scale is a substantive invariance premise. Allowing an unrelated scale in every arm produces a Cartesian rectangle but weakens the candidate. Mixed, interactive, threshold and nonmonotone bridges remain outside this comparison.

## Exact propagation and compatibility

When `M_c=[m_L,m_U]` is strictly positive, each marginal hull is the ordinary interval product `M_c*D_ci`. Their Cartesian product is a conservative outer rectangle, not generally the exact joint region, because the same `m` is used in both coordinates.

For two candidates `a,b`, let `Lambda=M_b/M_a=[m_bL/m_aU,m_bU/m_aL]`. Their exact regions intersect iff some positive `lambda in Lambda` satisfies, for both arms `i`,

`L_ai <= lambda U_bi` and `lambda L_bi <= U_ai`.

These are linear inequalities in one scalar. They give an exact feasibility check without pretending that overlapping outer rectangles imply overlapping exact regions.

For an outcome uncertainty box `O=O_R x O_F`, candidate `c` is compatible iff some `m in M_c` satisfies, for both arms,

`L_Oi <= m U_ci` and `m L_ci <= U_Oi`.

Disjointness means rejection of that scoped quantitative candidate, conditional on the frozen intervals, outcome uncertainty rule and all candidate premises. Intersection means compatibility, not confirmation.

## Orientation and stop rules

- If `A` is strictly positive, signs are preserved. If it is strictly negative, recode `J` prospectively and rerun with `-A`.
- If `0 in A`, both candidate regions contain `(0,0)` whenever their gains are positive. Global separation is impossible, and A4J's strict sign transfer is not warranted.
- If the allowed orientation has both signs but is not one frozen signed interval, analyse the branches separately; do not average them into an oriented bridge.
- If either targeted first-stage interval is not bounded strictly below zero as preregistered, the corresponding strict A4J sign promise is not installed.
- If the first-stage, orientation, common-scale, same-event referent, loss or response-coding contract fails, stop at `INVALID_ORIENTATION_OR_CALIBRATION`.
- If `P_R` and `P_F` overlap at the observed uncertainty box, use `INCONCLUSIVE_BETWEEN_QUANTITATIVE_PURE_CANDIDATES`.
- If the observation box intersects neither, use `REJECT_SCOPED_QUANTITATIVE_PURE_CANDIDATES`, not “no familiarity,” “no experience,” or “C1 false.”

No post-formation adjustment for `R`, `F`, effort, success, memory or report policy is used to manufacture narrower intervals.
