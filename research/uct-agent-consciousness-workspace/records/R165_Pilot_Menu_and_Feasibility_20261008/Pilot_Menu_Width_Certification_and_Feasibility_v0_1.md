# Finite Pilot Menus, Width Certificates, and Honest Feasibility Triage

Version 0.1, 8 October 2026. Research checkpoint; not a published edition, executed pilot, ethics approval, recruitment plan, apparatus validation, or sample-size recommendation.

## 1. Question and result

R164 proved exact finite-sample simultaneous coverage for a bounded, non-identically distributed finite-design mean when each component uses one pilot-frozen constant bet. It left a narrower design question: how may an independent pilot choose a bet/predictor plan for precision without changing the target, using confirmatory outcomes, or falsely declaring a design impossible?

R165 gives five bounded results.

1. A finite, predeclared menu of constant-bet/constant-center plans preserves the R164 unweighted target. Any pilot-measurable deterministic selector from that menu preserves R164's planwise coverage because every menu element already has the conditional guarantee.
2. Pilot independence is enough for coverage transport but not for width prediction. Two independent deterministic pilot/confirmatory laws can reverse which center minimizes residual width.
3. A finite-menu width certificate therefore needs an explicit pilot-to-confirmatory residual-risk transport radius. Under that premise, a Hoeffding union bound yields simultaneous lower and upper bounds for every component of every menu plan.
4. Minimizing the upper certificate gives a finite regret bound relative to the best plan in the fixed menu. The confidence level used for width certification is separate from the confirmatory coverage level; it is not added to alpha because planwise coverage holds for every selected plan.
5. A binary feasible/infeasible pilot rule is invalid. The correct rule has three outcomes: `FEASIBLE_CERTIFIED`, `PILOT_INCONCLUSIVE`, and menu-relative `DESIGN_NOT_FEASIBLE`. Failure of an R161 physical/measurement gate remains `PILOT_INVALID_PROTOCOL`, not a width result.

This closes one design-selection hole. It does not supply an apparatus, transport evidence, human data, bodily mineness, familiar ownership, C1 validation, complete organization, or an exclusive owner.

## 2. Frozen finite menu and width target

Fix familywise confirmatory error `alpha`, component count `m`, width-certification error `beta`, pilot size `n_P`, a maximum confirmatory size `N_max`, and a finite menu `Q` declared before pilot outcomes. Every admissible plan `q in Q` contains:

- a confirmatory size `N_q <= N_max`;
- one constant bet `lambda_jq in (0,1)` for each component;
- one constant center `c_jq in [0,1]` for each component;
- the unchanged R161 component definitions, signs, order, normalization, margin, gate logic, missingness target and decision code.

Constant centers are used here to keep order out of the planning object. A future predictable running-center menu needs a separately frozen order-sensitive risk definition.

For scaled confirmatory observations `X^C_ij in [0,1]`, define the average expected residual risk

`rho^C_jq = N_q^{-1} sum_i E[(X^C_ij-c_jq)^2]`.

Let `L_alpha = log(2m/alpha)` and `g(lambda)=-log(1-lambda)-lambda`. Before clipping the interval to `[-1,1]`, R164 gives component half-width

`h_jq = 2 L_alpha/(N_q lambda_jq) + [2 g(lambda_jq)/lambda_jq] * bar R^C_jq`,

where `bar R^C_jq` is the realized average squared residual. Its expectation is

`B_jq(rho^C_jq) = a_jq + d_jq rho^C_jq`,

with `a_jq=2L_alpha/(N_q lambda_jq)` and `d_jq=2g(lambda_jq)/lambda_jq`. Define the declared planning objective

`H(q)=max_j B_jq(rho^C_jq)`.

This is the maximum component **expected untruncated half-width**. It is not the realized maximum width, statistical power, effect clearance, or the R161 decision itself. Those would require additional declared theorems.

## 3. Pilot selection preserves coverage, not precision

### Theorem R165-P1: finite-menu planwise selection invariance

Let `P` be the pilot record and let `S(P)` be a measurable selector taking values in the fixed menu or a no-run status. Suppose every `q in Q` satisfies all R164 planwise premises for its confirmatory procedure:

`Pr{theta_Nq,j in I_jq(C) for all j | P, S(P)=q} >= 1-alpha`.

Then, conditional on executing a selected plan,

`Pr{theta_Nq,j in I_j,S(P)(C) for all j} >= 1-alpha`.

**Proof.** Condition on the pilot record. The selected plan is frozen and has coverage at least `1-alpha` for every record that selects it. Integrating the conditional probability over pilot records preserves the bound. Every menu element uses a constant bet over confirmatory participants, so the R164 target remains the unweighted finite-design mean. No union over menu size is charged to confirmatory alpha because only one independently selected plan is executed. `square`

Finiteness is not needed for this tower argument by itself. It is needed below for a finite simultaneous pilot certificate and makes the selection range auditable.

### Same-confirmatory-data warning

The theorem does not permit looking at confirmatory outcomes and then choosing the smallest interval, most favorable center, target, or report. R162's exact two-test witness shows the point: two fixed tests of size `.05` can yield adaptive size `.10` when the same outcome selects whichever test rejects. With independent rejection events the corresponding value is `1-.95^2=.0975`. A method that uses confirmatory outcomes to choose among menu elements needs its own valid simultaneous or adaptive theorem.

## 4. Independence does not transport residual width

### Proposition R165-P2: no width guarantee without a transport premise

Pilot/confirmatory independence alone does not bound `rho^C_jq` from pilot residuals.

**Counterexample.** Use one component, one common constant bet, and two centers `c_0=0`, `c_1=1`. Let every pilot value be deterministically `X^P=0` and every confirmatory value be independently and deterministically `X^C=1`. Pilot residual risks are `(0,1)`, so the pilot selects `c_0`; confirmatory residual risks are `(1,0)`, so the true width oracle selects `c_1`. Both samples are independent, every plan retains exact R164 coverage and the target is unchanged. Only the precision ranking fails.

Thus `independent pilot` has two different roles:

- it blocks same-confirmatory-data method selection and transports planwise coverage;
- it does not establish that pilot nuisance risks resemble confirmatory nuisance risks.

Any width certificate must state a transport/stability premise or use a worst-case range-only bound that makes pilot data irrelevant.

## 5. Simultaneous pilot residual-risk certificate

For pilot participant `r`, component `j` and plan `q`, let

`R^P_rjq=(X^P_rj-c_jq)^2 in [0,1]`,

`hat rho^P_jq=n_P^{-1} sum_r R^P_rjq`, and let `rho^P_jq` be its finite-pilot-design expected mean. Pilot participants may be non-identically distributed; they must be independent at the declared participant-vector level. Dependence among components and among candidate residuals computed from the same participant is allowed.

Declare before pilot outcomes a nonnegative transport radius `tau_jq` satisfying

`|rho^C_jq-rho^P_jq| <= tau_jq`.

This is an empirical/design premise, not a consequence of independence, C1, the finite menu, or the concentration inequality.

Set

`b=sqrt[log(2m|Q|/beta)/(2n_P)]`.

Hoeffding's inequality and a union bound imply that with probability at least `1-beta`, simultaneously for every `j,q`,

`|hat rho^P_jq-rho^P_jq| <= b`.

On that event and under the transport premise, define

`ell_jq=max(0,hat rho^P_jq-b-tau_jq)`,

`u_jq=min(1,hat rho^P_jq+b+tau_jq)`.

Then `ell_jq <= rho^C_jq <= u_jq` for all `j,q`. Hence

`H_L(q)=max_j [a_jq+d_jq ell_jq] <= H(q) <= max_j[a_jq+d_jq u_jq]=H_U(q)`.

The menu-wide union bound is paid only in `beta`, the width-certification error. It does not alter the confirmatory `alpha` guarantee in Theorem R165-P1.

## 6. Upper-certificate selector and regret

Let `q_hat` minimize `H_U(q)` over deterministically admissible plans, with a frozen lexical tie-break. Let `q_oracle` minimize the unknown `H(q)` over the same menu.

### Theorem R165-P3: finite-menu regret certificate

On the simultaneous pilot event and under all transport radii,

`H(q_hat)-H(q_oracle) <= Delta(q_oracle)`,

where

`Delta(q)=max_j [4 g(lambda_jq)/lambda_jq * (b+tau_jq)]`.

**Proof.** Selection gives `H(q_hat)<=H_U(q_hat)<=H_U(q_oracle)`. For every component, `u_jq-rho^C_jq<=2(b+tau_jq)` before clipping at one, so `H_U(q)-H(q)` is at most the displayed `Delta(q)`. `square`

The bound is menu-relative and can be loose. It does not show that the menu contains a scientifically good center, that the transport radii are true, or that expected half-width implies high-probability realized width.

## 7. Honest three-way feasibility triage

Fix a predeclared maximum acceptable planning width `w_max`. First apply deterministic protocol and resource rules.

- If an R161 fidelity/washout/sensitivity gate fails, output `PILOT_INVALID_PROTOCOL`.
- If the protocol is valid but no menu plan satisfies the frozen resource envelope (including `N_q<=N_max`), output deterministic menu-relative `DESIGN_NOT_FEASIBLE`.

Otherwise compute `H_L,H_U` and use exactly one of three states:

1. `FEASIBLE_CERTIFIED` if `min_q H_U(q) <= w_max`. Execute the frozen minimizer `q_hat`.
2. `DESIGN_NOT_FEASIBLE` if `min_q H_L(q) > w_max`. With width-certification confidence at least `1-beta`, every plan in the declared menu violates the declared expected-width threshold.
3. `PILOT_INCONCLUSIVE` otherwise. Some plan is not ruled out, but no plan is certified. Do not switch interval families after seeing confirmatory outcomes. A larger/new pilot, altered menu, relaxed threshold or new transport radius is a new preregistered protocol version.

An upper confidence bound exceeding `w_max` does **not** prove infeasibility. That common binary shortcut is the central correction. Likewise, `DESIGN_NOT_FEASIBLE` is relative to the fixed menu, transport model, objective, resource envelope and confidence level; it is not impossibility of all studies, no bodily role, no mineness, or no experience.

### Worked synthetic audit point

For `m=8`, `alpha=.05`, `N=120`, `n_P=2000`, `beta=.05`, `|Q|=4`, common `tau=.02`, and a four-plan illustration with `(lambda,rho)` values `(.25,.04),(.5,.06),(.75,.12),(.9,.20)` repeated across components, `b=0.04229248`. The true planning widths are approximately `.39661,.23863,.33180,.73019`; the `.5` plan is the oracle. Using pilot estimates equal to the displayed pilot risks:

- `w_max=.30` is `FEASIBLE_CERTIFIED`;
- `w_max=.22` is `PILOT_INCONCLUSIVE`;
- `w_max=.18` is menu-relative `DESIGN_NOT_FEASIBLE`.

These are formula checks, not observed human values or recommendations for `n_P`, `N`, `tau`, lambda, or width.

## 8. Relation to the R161 decision

The width objective is subordinate to the fixed scientific protocol. A selected plan may be executed only if:

1. every R161 physical/measurement gate passes;
2. the same eight signed components, normalization, order, epsilon and target remain frozen;
3. every menu element uses a constant confirmatory bet and a declared center;
4. pilot and confirmatory participants are disjoint for this theorem;
5. participant-vector independence and boundedness hold for the R163 target;
6. missingness and undefined outcomes retain their R163/R164 types;
7. the selector, tie-break, beta, transport radii, width objective and all three statuses are frozen before pilot outcomes.

Even a certified expected half-width does not guarantee confirmation or exclusion when the true parameter is near a decision boundary. `UNRESOLVED` at the maximum sample remains a valid confirmatory result.

## 9. Retained thought-experiment roles

- **Ancestor/formation.** A prelinguistic body-regulation process can remain the target while investigators change pilot menus. Better precision is not a new experience threshold.
- **Abacus/calculator.** A pilot on one stable calculator and confirmation on another can reverse the best predictor center despite independence; transport, not intelligence or report, is the missing premise.
- **Human-realized agent.** Coordinated people can violate participant-vector independence, while disjoint recruitment alone says nothing about residual-risk transport.
- **Copy/swap/memory.** Copy the confirmatory target and observations, then swap only the pilot sample or transport radius. Coverage may remain exact while feasibility labels change, proving that the label belongs to a design certificate rather than to the experience token.

## 10. Relation to UCT and the beginner principle

R165 is an auxiliary evidence-design result for one proposed body/tool protocol. It protects the research from post-hoc rescue and false impossibility claims. It does not identify an actual installed body-frame relation or provide the positive bridge from that relation to felt mineness.

C1 remains a consciousness-specific explanatory postulate. Basal experience is not made conditional on pilot precision, a finite menu, a report, language, a self-model, integration, recursion, accurate prediction or continuation control. Actual processes may remain nested and overlapping; no necessarily unique additional owner is introduced. Population design certificates, actual process organization, a particular experience and a linguistic report remain differently typed.

## 11. Failures, boundaries and next question

- The transport radii are declared sensitivity premises; R165 does not estimate or validate them.
- Hoeffding pilot bands can be too wide to classify feasibility.
- The criterion is expected untruncated component half-width, not realized width or decision power.
- The regret result is relative to the finite menu and fixed transport model.
- Pilot/confirmation independence and protocol fidelity remain empirical obligations.
- Missingness identification, undefined post-abort outcomes, actual apparatus, `B_min` and `F_O` remain open.

The next research question should return to the main theoretical line: **what independently specified organization-level evidence would make a valid R161 physical role profile support an actually installed body-frame relation inside one token, rather than merely a population effect, without using ownership report as its definition or turning that relation into a basal-experience gate?**

## 12. Sources and attribution

- Hoeffding, W. (1963), “Probability inequalities for sums of bounded random variables.” Used for the finite pilot residual-risk union band; this is established mathematics, not claimed as new.
- Waudby-Smith and Ramdas, “Estimating means of bounded random variables by betting.” Provides the R164 bounded predictable-plug-in lineage; R165 does not alter their theorem or attribute this protocol-specific menu to them.
- Fixed R162 note, especially §§5–9. Supplies the external-pilot freeze, planwise conditional-coverage premise, tower argument, same-data-selection counterexample and status boundaries.
- Fixed R163–R164 records. Supply the bounded finite-design target, range-only fallback, constant-bet theorem, rare-spike obstruction and missingness endpoint boundary.
- UCT I v1.2 fixed source and the current master guide. Supply the physical-witness, declared-target, no-rescue and self/experience interpretation boundaries, not the statistical results.
