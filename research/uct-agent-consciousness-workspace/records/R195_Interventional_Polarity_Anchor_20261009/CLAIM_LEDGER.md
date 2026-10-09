# R195 claim ledger

## R195-C1 — Interventional latent-pole relabelling

- **Type:** exact finite theorem; standard latent-variable relabelling application.
- **Statement:** every one of the 256 deterministic binary SCMs has a distinct complemented model with the same `(M1,M2,Y)` distribution under both `do(Q)` values; the models form 128 pairs.
- **Domain:** the five-variable deterministic binary domain in `RESEARCH_NOTE.md` §2.
- **All premises:** fixed equations, intervention family, observed variables and arbitrary complete consequence kernel.
- **Proof/source:** algebra in §3 and exhaustive `check_interventional_anchor.py` / `EXACT_RESULTS.json`.
- **Counterexample/scope:** a target-directed asymmetric restriction not closed under the complement transform is outside the theorem.
- **Status:** `PROVED_IN_DECLARED_DOMAIN`; candidate map node disabled.
- **Thought-experiment role:** TE1 is the direct witness.

## R195-C2 — Route sensitivity does not by itself orient polarity

- **Type:** exact scoped nonidentification result.
- **Statement:** even with `z(0)!=z(1)` and a known reversed second marker, the 64 admitted models remain in 32 complement pairs.
- **Domain:** R195-C1 plus the two displayed restrictions.
- **All premises:** the restrictions are fixed prospectively; no target-direction bridge is added.
- **Proof/source:** exhaustive checker.
- **Counterexample/scope:** an ordered outcome relation can orient a functional pole only by an extra restriction.
- **Status:** `PROVED_SCOPE_BOUNDARY`.
- **Thought-experiment role:** TE2–TE3 block source-label and multi-marker shortcuts.

## R195-C3 — Functional anchor orientation

- **Type:** positive conditional identification result.
- **Statement:** the explicit full-table restriction `Y=Z` selects one functional orientation; its complement is exactly the opposite restriction `Y=1-Z`.
- **Domain:** the complete finite consequence table, not merely observed success on one realized state.
- **All premises:** `Y` has an independently fixed ordering and the `Y`–`Z` direction is declared before inference.
- **Proof/source:** exact 16/16 enumeration and complement bijection.
- **Counterexample/scope:** changing task value can reverse `Y` without changing familiar mineness.
- **Status:** `CONDITIONAL_FUNCTIONAL_RESULT`.
- **Thought-experiment role:** TE8 supplies the prospective defeater.

## R195-C4 — Functional polarity is not phenomenal polarity

- **Type:** typed semantic non-entailment.
- **Statement:** an outcome-oriented structural pole does not entail the positive `F_fam` pole without a distinct `B_dir` premise.
- **Domain:** R195's selected familiar-mineness application under TA25 D5/R157/R173.
- **All premises:** functional target and phenomenal target remain different sorts; C1 does not assign ordinary-language names to selected coordinates.
- **Proof/source:** R157 T2 plus the explicit complement interpretation.
- **Counterexample/scope:** an independently warranted phenomenal direction-transfer bridge would make the inference conditional rather than invalid.
- **Status:** `OPEN_BRIDGE_EXPOSED`.
- **Thought-experiment role:** TE2 and TE8 distinguish success from familiar mineness.

## R195-C5 — Prospective interventional anchor contract

- **Type:** methodological synthesis / candidate adequacy contract.
- **Statement:** a substantive anchor must jointly discharge target declaration, same-instance actuality, ontic intervention, installed use, functional direction, phenomenal direction transfer, reliability/rivals and a defeater.
- **Domain:** future named familiar embodied/action-mineness applications.
- **All premises:** all eight fields concern the same bearer, interval, signature, route and target.
- **Proof/source:** failures in R157/R173/R193/R194 plus C1–C4.
- **Counterexample/scope:** satisfying structural fields without `B_dir` yields functional orientation only.
- **Status:** `PROPOSED_METHOD_CONSTRAINT_PENDING_REVIEW`.
- **Thought-experiment role:** TE1–TE8 stress each field.

## R195-C6 — Conditional UCT placement

- **Type:** conditional UCT application.
- **Statement:** with actual complete-signature grounding and all same-instance R157 premises, C1 transports the intervened organizational relation into experiential organization; neither the intervention nor its success names `F_fam` or gates experience.
- **Domain:** admitted actual tokens only.
- **All premises:** C1, actual token, complete signature, grounded formula, sorted witnesses and parameter transport.
- **Proof/source:** UCT I C1/U1 and R157 T1/T2.
- **Counterexample/scope:** a finite SCM or successful diagnostic does not discharge actual admission or completeness.
- **Status:** `CONDITIONAL_THEORY_INTERPRETATION`.
- **Thought-experiment role:** TE4–TE7 protect actual-history, boundary and implementation distinctions.
