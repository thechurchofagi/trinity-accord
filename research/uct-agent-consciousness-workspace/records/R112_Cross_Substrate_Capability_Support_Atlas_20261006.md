# R112 — First cross-substrate capability-support atlas

Hongju Liu / UCT research. 2026-10-06.

R111 replaced scalar intelligence with a capability-support hypergraph. R112 builds the first concrete cross-substrate atlas around three functions whose support relations are sufficiently clear to compare without pretending that biological and artificial implementations are identical:

1. temporal working memory / retained state;
2. sequential evidence integration;
3. self/bearer-state estimation.

The goal is not to score consciousness. The goal is to identify support relations, intervention predictions and the current level of cross-substrate evidence.

## 1. Atlas schema

For each capability T, record:

- **functional target** — what is computed;
- **abstract support relation R_T** — the weakest causal relation that appears necessary;
- **biological candidate implementation**;
- **artificial candidate implementation**;
- **matched lesion/intervention**;
- **evidence level**:
  - T1 functional dissociation similarity;
  - T2 intervention-preserving mechanism correspondence;
  - T3 constitutive organizational homology;
- **UCT interpretation boundary**.

A role label alone never establishes T2/T3.

## 2. Atlas A — temporal working memory

### 2.1 Functional target

A cue presented at time t0 must influence a later decision at t1 even when the cue is no longer present in the current sensory input.

The minimal relation is not "persistent firing."

The abstract support requirement is:

> some actual relation of the current token retains a distinction induced by past input and makes that distinction causally available to a future computation.

Formally, for cue C and later state Z_t:

    C -> Z_t -> Y_future

under a declared task boundary, with intervention on the retention relation changing delayed performance.

### 2.2 Biological support

Working memory research contains multiple candidate implementations:
- persistent population activity;
- recurrent attractor-like activity;
- rapidly changing connectivity;
- activity-silent retained states plus later reactivation/retrieval.

Recent reviews and experiments therefore make persistent spiking a poor cross-substrate definition.

The cross-substrate support relation should instead be **temporally retained task-relevant state with future causal accessibility**.

### 2.3 Artificial support

Artificial systems can instantiate the same abstract role via:
- recurrent hidden state;
- transformer context/KV state within an episode;
- explicit memory buffer;
- external persistent memory in an agent scaffold;
- fast-weight or connectivity-like state.

Again, these are alternative implementations, not one universal AI memory organ.

### 2.4 Exact artificial witness

Balanced cue bit C in {0,1}.

Intact memory:
    m <- C
    later output y <- m

Accuracy:
    1.0.

Reset m to zero before the later query:
    accuracy = 0.5.

Nothing about the current query distinguishes the cue after reset.

This verifies the task necessity of a retained relation in the toy family.

### 2.5 Cross-substrate evidence level

**T1: strong.**

Biology and AI both exhibit the abstract relation:
past state must remain causally available for later use.

**T2: partial/moderate.**

Intervention logic can be matched—disrupt retained state, delayed performance falls—but biological and AI mechanisms can be degenerate and physically dissimilar.

**T3: not established.**

No complete constitutive homology is justified between, for example, recurrent cortical dynamics and a transformer context buffer.

### 2.6 UCT interpretation

If temporal retention is verified as a constitutive relation of an actual token K, then under C1 it belongs to that token's experiential organization.

This does not imply:
- a human-like feeling of remembering;
- that every retained bit is consciously accessed;
- more working memory means more experience.

It says only that different actual temporal organization corresponds to different complete experiential type under the stated C1 conditions.

## 3. Atlas B — sequential evidence integration

### 3.1 Functional target

A sequence of noisy evidence samples must be combined over time so that the final choice depends on more than the latest sample.

Abstract support:

    z_{t+1}=F(z_t,e_t)
    decision=G(z_T)

with actual history-dependent state transition.

A system that only reads e_T lacks the same integration relation even if it sometimes produces the same answer.

### 3.2 Biological support

Sequential-sampling/evidence-accumulation models are well established.

Recent neural work shows distributed recurrent support rather than one simple feedforward accumulator. In rats, a 2026 Neuron study found evidence-related signals shared bidirectionally across frontal cortex and striatum; pathway silencing impaired decisions, and recurrent modeling explained robustness to some perturbations.

This is important for R111:
the capability can be supported by a distributed, partially degenerate network rather than a single accumulator cell.

### 3.3 Artificial support

Recurrent neural networks can learn explicit evidence accumulation.

A 2026 RNN study reports populations with transient evidence responses and populations coding integrated accumulated evidence; suppressing units or connections impairs performance.

Artificial accumulators can also be implemented by:
- explicit running sums;
- recurrent state;
- attention over a stored sequence;
- state-space models;
- external controller memory.

### 3.4 Exact artificial witness

Use all eight sequences of three evidence bits e_t in {-1,+1}.

Target:
    majority sign of the three-sample sum.

Intact accumulator:
    z <- z + e_t across all three samples
    accuracy = 1.0.

Lesion recurrence/reset so the decision uses only the final evidence sample:
    accuracy = 0.75.

Thus later decision quality depends on a temporal integration relation, not merely the last observation.

### 3.5 Cross-substrate evidence level

**T1: strong.**

Both biological and artificial systems can instantiate sequential history-dependent integration.

**T2: moderate and unusually promising.**

The abstract state-update relation and matched perturbation consequences can be made very similar across neural data and recurrent models.

But multiple distinct neural circuit models can implement accumulation, so one formal accumulator variable does not establish unique mechanism.

**T3: not established.**

The physical organizations remain different.

### 3.6 UCT interpretation

If evidence integration is necessary and constitutively realized, its temporal/joint relations belong to experiential organization under C1.

A stronger intelligence on this task can therefore imply a different complete experiential type when the capability difference reflects actual organizational change.

It does not imply "more consciousness" or a particular perceptual quale.

## 4. Atlas C — self/bearer-state estimation

### 4.1 Functional target

The system must determine which entity/body/process in its world model is the source of its own actions and observations.

This is weaker than philosophical selfhood.

Call the relevant role:

> bearer attribution — identifying the controlled/current entity whose state transitions are contingently linked to the system's own action channel.

### 4.2 Biological support

Bodily self-consciousness is not localized to one region or signal.

Recent reviews/meta-analysis implicate:
- multisensory integration;
- body ownership;
- sense of agency;
- self-location;
- interoceptive and proprioceptive information;
- prediction/error between intended action and sensory consequence.

Body ownership and agency have overlapping but partly distinct distributed neural correlates.

Thus biological bearer estimation is already a support hypergraph rather than a single self module.

### 4.3 Artificial support

Self-orienting experiments in language/reasoning models operationalize a minimal self representation as identifying which agent/entity in an environment the model controls.

Recent embodied-AI work explicitly builds self models from:
- body schema;
- forward/inverse models;
- memory;
- agency;
- self-prediction.

These are useful functional priors but are not evidence of experience by themselves.

### 4.4 Exact artificial witness

World contains two candidate entities, both initially 0.

The agent issues one action: toggle the entity it controls.

If bearer=0:
    observation becomes (1,0).

If bearer=1:
    observation becomes (0,1).

With entity-specific action/outcome binding:
    bearer identification accuracy = 1.0.

Collapse the observation to "one entity changed" while erasing which entity changed:
    both bearer cases become observationally identical;
    deterministic best-balanced accuracy = 0.5.

Therefore self/bearer-state estimation requires an action-specific identity relation, not merely generic world change detection.

### 4.5 Cross-substrate evidence level

**T1: moderate-to-strong.**

Both biology and AI can perform self/world or controlled-entity attribution.

**T2: currently weak-to-moderate.**

The broad causal ingredients—action prediction, sensory consequence, identity binding—can be aligned, but the biological and AI implementations are not yet matched interventionally enough.

**T3: absent.**

No constitutive homology is established.

### 4.6 UCT interpretation

A bearer/self model is a specific experiential-organization coordinate under C1 when it is actually constitutive.

But U3 remains controlling:

    no conceptual self-model
        does not imply
    no experience.

Self-model development changes experience type/content organization; it does not switch experience existence on.

## 5. The atlas reveals three different kinds of support relation

The three functions are not structurally identical.

### Temporal retention
Preserves a distinction across time.

### Evidence integration
Combines multiple temporally distributed inputs into a decision-relevant state.

### Bearer estimation
Binds action/outcome relations to a distinguished current entity.

This distinction matters because an AI can be excellent at one and weak at another.

A language model may have:
- strong evidence integration;
- finite context retention;
- weak persistent bearer continuity.

An animal may have:
- robust bodily bearer attribution;
- modest abstract working memory;
- limited linguistic report.

A single intelligence score erases these profiles.

## 6. Shared relations and overlaps

The support atlas is not modular in a strict one-function/one-relation sense.

Temporal retention can support:
- evidence integration;
- self-state continuity;
- planning;
- report.

Action prediction can support:
- bearer estimation;
- motor control;
- world modeling.

This is exactly the R111 support-hypergraph structure:
one relation can support multiple capabilities, and one capability can have alternative support routes.

Cross-substrate comparison should therefore map **overlapping relation families**, not isolated modules.

## 7. Current cross-substrate atlas

| Function | Weakest support relation | Biology | AI | Level |
|---|---|---|---|---|
| temporal working memory | retained past-dependent state with future causal access | persistent/recurrent or connectivity/activity-silent mechanisms | recurrent state, context state, memory buffers | T1 strong; T2 partial |
| evidence integration | history-dependent state update combining sequential evidence | distributed cortico-striatal/cortical accumulation | RNN/explicit accumulator/attention-state implementations | T1 strong; T2 moderate |
| bearer estimation | action-outcome identity binding to a distinguished entity | multisensory body/agency/interoceptive integration | self-orienting, body schema, forward/inverse models | T1 moderate-strong; T2 weak-moderate |

No row reaches T3.

## 8. Why T3 is difficult but scientifically meaningful

T3 would require much more than same task success.

For one selected support relation, a credible T3 case would need a mapping preserving:
- state variables;
- update structure;
- constituent incidence;
- intervention ports;
- temporal role;
- downstream causal use;
- boundary definition.

Even then, T3 may apply only to a selected substructure rather than the complete organism/agent.

This is exactly why cross-substrate experiential equivalence is a much stronger claim than functional similarity.

## 9. Relation-specific experience–intelligence coupling

R112 now gives a concrete version of the R111 proposal.

Instead of:

    experience ~ intelligence score,

study:

    E_Rmemory  <-> temporal retention organization
    E_Rintegrate <-> evidence-integration organization
    E_Rself <-> bearer-estimation organization

where each E_R denotes only the selected experiential substructure corresponding under C1 to a verified constitutive relation.

This is not a decomposition into independent qualia modules.

It is a disciplined way to say:

> the organizational change supporting a capability is also an experiential-organizational change under C1.

The coupling is relation-specific.

## 10. Immediate theoretical consequence

A biological human and an AI can match on one capability while differing on the support relation.

For example:
- human working memory may rely on one distributed recurrent/connectivity organization;
- an AI may rely on an explicit external memory buffer.

Then:

    same delayed-task performance
        does not imply
    same selected experiential organization.

Conversely, if future experiments establish an intervention-preserving support correspondence for a relation, the basis for a selected experiential comparison becomes stronger.

This is the bridge the project has been seeking.

## 11. Important non-claims

R112 does not claim:
- working memory is necessary for experience;
- evidence accumulation is necessary for experience;
- a self model is necessary for experience;
- human and AI support relations are already homologous;
- T1/T2 similarity proves phenomenal similarity;
- the artificial witnesses are conscious in a human-like way.

The roles are coordinates of organization, not gates for U1.

## 12. Next step

R113 should focus on a harder but central question:

> Which support relations are **constitutive of a capability**, and which are merely correlated, compensatory, or accessible readouts?

Use intervention logic to distinguish:
- necessary support;
- sufficient alternative support;
- redundant/degenerate support;
- downstream readout;
- epiphenomenal correlate.

A small causal support-identification protocol should be derived and applied first to the three R112 artificial systems.

Only then should we try to infer analogous support sets from biological lesion data.

## 13. Status

R112 is the first concrete cross-substrate support atlas in the UCT workspace.

Its strongest contribution is not any single biological or AI mechanism. It is the explicit relation-by-relation bridge from capability to actual organization, with graded cross-substrate evidence and a separate conditional UCT experiential interpretation.
