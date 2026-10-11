# Redundant same-event port-participation contract

Version: `A4X-RPP-v0.1.0`
Status: disabled bounded application contract; not a general definition of actual causation, not an actual installation, and not a phenomenal bridge.

## 1. Fixed target and consumer boundary

Fix one candidate actual process `P`, interval `I`, complete-signature obligation `K`, event `e`, target activity `tau`, downstream consumer occurrence `m`, two named input ports `p_1,p_2`, route occurrences `r_1,r_2`, and a declared intervention family `J`. `m` is the boundary under test. If an upstream compiler consumes both routes and sends one wire to `m`, the compiler—not `m`—is the possible two-route consumer.

Values, logs, port labels and output equality do not identify occurrence, lineage, read or consumer boundary. Counterfactual trials are distinct admissible tokens or executions; they are not one token with contradictory values.

## 2. Candidate relation

For `i in {1,2}`, define the disabled candidate `SameEventPortParticipation_i(P,I,K,e,tau,m,p_i,r_i;J)` (`SEPP_i`) by the conjunction:

```text
BIND_i AND LINEAGE_i AND READ_i AND FROZEN_m
AND FACTORIAL_J AND CONTINGENT_SENSITIVITY_i AND EXCLUSION_J.
```

1. **BIND.** `P/I/K/e/tau/m/p_i` refer to one declared actual event and one fixed consumer boundary.
2. **LINEAGE.** the occurrence at `p_i` descends from the named live route `r_i` in that event; a value-equal copy, stale item or analyst label is insufficient.
3. **READ.** the actual mechanism of `m` samples or otherwise consumes that occurrence before the declared target state is fixed. A passive recorder or an unused physical wire fails.
4. **FROZEN.** the consumer mechanism, port semantics, target rule, event grain and readout remain fixed across the admitted challenges.
5. **FACTORIAL.** `J` independently reaches the required port combinations at the same boundary, including the two off-diagonal rows when the sibling projection is not known in advance. Reachability by changing consumer identity or event grain fails.
6. **CONTINGENT SENSITIVITY.** for at least one sibling-port value declared before outcome inspection, changing only `p_i` changes the relevant internal/output coordinate of frozen `m`. This is port-specific functional relevance under a contingency, not the demand that `p_i` be but-for necessary at every actual row.
7. **EXCLUSION.** intervention labels, hidden mode switches, alternate writers/readers, replay, and direct target bypasses that could manufacture the contrast are independently excluded within the declared finite boundary.

For A4W's target, replace its intentionally weak `Participates_tau(r_i,m,e)` placeholder only prospectively by `SEPP_i`; then the bounded candidate is

```text
RPP-JOINT := ConcurrentBCR2 AND SEPP_1 AND SEPP_2.
```

Every conjunct must hold on the correctly typed same binding. Two distinct `SEPP` relations are non-exclusive and do not select one owner.

## 3. Ontic relation versus evidence

`LINEAGE AND READ` concerns the actual event. `FACTORIAL AND CONTINGENT_SENSITIVITY` supplies bounded evidence that the port belongs to the consumer's mechanism rather than being a decorative read. `FROZEN AND EXCLUSION` limits inference from the challenges. None can replace the others:

- functional dependence of an abstract table does not prove a port was physically present or read;
- an actual read does not show relevance if the consumer discards the value;
- an output contrast does not identify the named port if the test mode or a bypass can read intervention labels;
- absence of simple actual-row but-for dependence in a redundant context does not establish nonparticipation.

The contract therefore uses the modest phrase **mechanism-bound participation**. It does not decide the broader philosophical question of actual causation. Structural-model causation with declared contingencies is established prior art; A4X applies a narrower port audit and does not claim that machinery as new.

## 4. Exact Boolean scope

Let `h(u,v)` be a deterministic Boolean consumer and require A4W normal correctness: `h(0,0)=0`, `h(1,1)=1`. Exactly four functions remain: projections `u`, `v`, AND and OR.

Port-specific contingent relevance is

```text
Dep_u(h) := exists v*: h(0,v*) != h(1,v*)
Dep_v(h) := exists u*: h(u*,0) != h(u*,1).
```

AND and OR satisfy both predicates; each projection satisfies exactly one. AND has its witness when the sibling is `1`; OR when the sibling is `0`. Yet AND at actual `(0,0)` and OR at actual `(1,1)` have no single-port but-for dependence for either port. Consequently, requiring both ports to be but-for necessary at every normal row rejects all four correct functions. Both off-diagonal challenges are needed to rule out both unknown projections.

This theorem is elementary Boolean classification. The net contribution is its scoped use to repair A4W's open participation predicate and its explicit separation of actual event read/lineage from counterfactual mechanism evidence.

## 5. Compiled one-port equivalents

On the normal diagonal, `k(x)=x` reproduces AND, OR and both projections. That behavioral compilation does not establish which organization is installed. Under full factorial port access, no function of `u` alone or `v` alone equals AND or OR on all four rows. If a compiler `q(u,v)` feeds a one-port `m`, challenges may establish two-port participation at `q`; they do not establish it at `m`. Consumer-boundary relocation is a different claim, not a refutation.

## 6. Stop rule and UCT placement

If any actual-binding, reachability, freeze or exclusion clause is unavailable, report `NOT_INSTALLED` for `SEPP` and retain A4W's participation edge as open. Do not add more generic control layers.

If one complete actual organization independently satisfies `ConcurrentBCR2 AND SEPP_1 AND SEPP_2`, C1/R157 can conditionally transport those relations as experience-internal structural relations. `B_pc^family` and the further `H_cf` interpretation remain separate open bridges. `SEPP` is not a basal-experience gate, self-model, report, language, prediction-accuracy, integration, recursion or continuation-control requirement; it gives no subject count and no verdict about any current assistant.
