# Double selectivity for a named proprioceptive consumer

**Record:** A3S20261010_Area3a_Selectivity  
**Status:** bounded negative/feasibility result; disabled map candidate; no new human or animal experiment.

## 1. Result

Area 3a is a materially better named-consumer candidate than the generic human consumer in MPC/CBI/EIP/DVC. Macaque mapping and neural responses support a proprioceptive role; microstimulation has guided behaviour; a 2026 methods study placed chronic arrays at the base of the central sulcus in two rhesus macaques and recorded spikes for more than one year. These facts remove the claim that the consumer is wholly inaccessible.

They do **not** jointly identify that a selected natural proprioceptive carrier was actually read by area 3a in one probe epoch. The evidence packages were obtained in different animals, species, interventions and readouts. The closest methods satisfy different margins of a two-axis contract:

1. **source selectivity:** changing the declared carrier must not change a collateral writer into the same consumer under the admissible alternatives;
2. **consumer selectivity:** the readout must distinguish the declared consumer from neighbouring or pooled consumers under the same intervention;
3. **event binding:** source issue, arrival, local response/read event and downstream endpoint must be bound to one epoch with declared timing and background.

The main negative conclusion is therefore not “area 3a cannot be tested.” It is: **the reviewed literature does not yet instantiate both selectivity axes and event binding in one actual package.** For non-invasive human imaging, the first proof-critical failure is consumer-specific causal read identification. For macaque local recording under mixed or broad peripheral stimulation, source selectivity fails first. For area-3a microstimulation, the direction is write-to-consumer rather than read-from-selected-natural-source. For the 2026 chronic implant, access is achieved but the reported study does not execute the full source/read intervention.

## 2. Exact finite model

Let the latent use vector be

\[
x=(x_{SA},x_{QA},x_{SN},x_{QN})^\top,
\]

where `S` is the selected source, `Q` a collateral source, `A` the named area-3a consumer and `N` a neighbouring/pooled consumer. A declared linear observation package has matrix `H` and observation `y=Hx`. The target is `x_SA`.

**A3S-C1 — target-coordinate row-space criterion.** On the unrestricted real latent domain, `x_SA` is identifiable from `y` exactly when the coordinate functional `e_SA` lies in the row span of `H`.

*Proof.* If `e_SA=aH`, then `x_SA=ay`. Conversely, if `e_SA` is not in the row span, the null space of `H` contains a vector `v` with `e_SA v != 0`; `x` and `x+v` have the same observation and different target coordinate. This is standard finite-dimensional linear algebra, not new mathematics.

**A3S-C2 — one-axis and two-margin insufficiency.** Consumer-only `H=[1,1,0,0]`, source-only `H=[1,0,1,0]`, and their two-row combination all omit `e_SA` from the row span. Exact binary twins in `EXACT_RESULTS.json` preserve every declared observation while switching `x_SA`. Thus two marginal contrasts do not automatically identify their interaction. A direct target-selective row `[1,0,0,0]` identifies the coordinate in this model.

The model is deliberately minimal. It does not claim neural responses are linear sums. Its role is to expose an inference error that also survives many nonlinear packages: separate evidence about the source margin and consumer margin need not identify the selected source-by-consumer event.

## 3. Feasibility ladder

| Package | What it adds | First unmet proof premise | What it cannot establish |
|---|---|---|---|
| Human high-resolution fMRI during kinesthetic/motor stimulation | Region compatible with 3a activation | consumer-specific causal read event | selected carrier use, exclusivity, `H` |
| Macaque peripheral nerve stimulation plus area-3a LFP | local consumer-region response | source selectivity under mixed recruitment | selected natural writer, single-neuron consumption |
| Macaque area-3a ICMS guiding behaviour | writable access and downstream behavioural availability | read-from-selected-natural-source direction | natural afferent read, ownership/agency |
| 2026 chronic area-3a array | stable physical access and local spiking readout candidate | executed source-linked intervention/event package | actual selected-source read in this methods study |
| Required future crossed package | identified source intervention + local ensemble event + neighbour controls + epoch timing | empirical execution and validation | still does not by itself name a self-related feeling |

This ladder is a correction to an overly coarse “human probe infeasible” conclusion. Invasive macaque access is now demonstrated. The remaining problem is the conjunction of source selectivity, consumer selectivity and event binding, not access alone.

## 4. Positive UCT relevance

If a future package grounds one actual process token, interval and complete signature, identifies the selected carrier-to-area-3a relation and demonstrates its local use, then C1 transports that organizational relation to a structural counterpart within the experience of that admitted process. This is a positive organization-to-experience conditional: body-related input use belongs inside experience rather than being assigned to an extra owner.

That conditional does not identify agency, ownership, familiar mineness, conceptual self or report. `B_min/B_fam` and measurement remain separate. Failure of the probe package is failure of this application inference, not absence of basal experience. Area 3a can overlap with other actual processes and need not be the unique subject.

## 5. Thought-experiment attacks

- **Copy/switch:** hold the local 3a response and behaviour fixed while switching the causal writer from a selected spindle channel to a collateral cutaneous/central writer. It defeats source identity inferred from local activation alone.
- **Human-realized agent:** hold the program output and report fixed while replaying a pooled 3a-like signal to a display read by the group. It distinguishes actual biological consumer use from a matching external record.
- **Ancestor/formation:** vary the maturity of a proprioceptive cortical field while preserving basal actual processes. It motivates graded organization but supplies no new onset proof and no exclusive owner.
- **Abacus/calculator:** equal position estimates can be produced by a local proprioceptive loop or an external lookup. Capability equality does not identify the consumer relation or experiential target.

## 6. Failure and stopping rule

No reviewed package satisfies all three premises in one instance. Stop the actual-read claim when any source mapping, local read event, neighbour control or epoch binding is missing. Do not substitute more literature enumeration, region labels, imaging activation, behavioural success or device access for the missing conjunction.

The next concrete question is whether the 2026 chronic-array platform has, or can support, a predeclared randomized peripheral-source contrast with identified receptive fields, local spike-event timing, neighbouring-site controls and matched movement/touch consequences. If not, retain the exact failed premise rather than generalizing to impossibility.
