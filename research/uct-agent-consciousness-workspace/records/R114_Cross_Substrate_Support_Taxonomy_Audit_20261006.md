# R114 — Support taxonomy applied to working memory, evidence integration, and bearer estimation

Hongju Liu / UCT research. 2026-10-06.

R113 established that "causal support" is not one category. R114 applies that taxonomy to the three R112 atlas functions and asks:

> In biology and AI, which observed relations are plausible content-bearing support, which are access/permissive relations, which are degenerate alternatives, which are readouts, and which are only correlates?

The result is an evidence audit, not a final mechanistic identification.

## 1. Temporal working memory

### 1.1 Content-bearing support

The capability requires some relation that preserves task-relevant distinctions over a delay.

Biology:
- persistent population activity is one candidate content-bearing implementation;
- rapidly modulated connectivity / activity-silent states are another candidate implementation;
- episodic or long-term retrieval can sometimes substitute under some conditions.

AI:
- recurrent hidden state;
- transformer context/KV state;
- explicit memory buffer;
- external scaffold memory;
- fast-weight/connectivity state.

The correct content criterion is therefore not "is activity persistent?" but:

> does the relation preserve the cue distinction, and does intervention on that retained distinction alter delayed performance?

### 1.2 Access/permissive support

A memory trace may exist yet fail to influence current decision.

Biology:
- retrieval/control mechanisms can determine whether retained information becomes behaviorally available.

AI:
- a memory buffer can contain the right value while a routing/access gate prevents the policy from reading it.

R110's access-gate witness is the exact artificial version.

Thus memory content and memory access must be separated.

### 1.3 Degenerate alternatives

Biological memory is a strong candidate for degeneracy:
- persistent active traces;
- connectivity-based retention;
- retrieval from longer-term stores.

Not every study establishes that these are interchangeable within one organism/task, so R114 labels them **alternative candidate supports**, not universally proven degenerate routes.

AI degeneracy can be made explicit:
- the same delayed task can be solved by recurrent state or external memory.

### 1.4 Readout

Motor response and verbal report are downstream of memory content.

A memory task can fail at report while retained information persists.

Biological CMD/LIS/no-report cautions make this especially important.

### 1.5 Correlates

A sustained neural signal or activation pattern may track remembered content but need not be causally used.

Likewise in AI, a probe-decodable activation is not necessarily the operational memory path.

Therefore the working-memory atlas should not elevate decodability to content-bearing support without intervention.

## 2. Evidence integration

### 2.1 Content-bearing support

The central content-bearing relation is an evolving state that carries accumulated decision evidence.

Biology:
- evidence-related population states distributed across cortical/striatal circuits;
- trial-by-trial buildup signals.

AI:
- recurrent accumulator state;
- explicit running statistic;
- sequence-state representation used by the final decision.

### 2.2 Access/permissive support

The accumulated state must reach the decision/choice mechanism.

The 2026 rat circuit result is particularly instructive:
pathway-specific FOF->ADS silencing impairs decision behavior, whereas broader perturbation can be partly buffered by recurrent circuit structure.

This suggests that a pathway can be causally important as a routing/support relation without being the unique place where evidence content "lives."

In AI, a final access gate from accumulator to policy plays the same functional role.

### 2.3 Degenerate alternatives

Evidence accumulation is multiply realizable:
- distributed recurrent circuits;
- local accumulator-like states;
- choice-selective sequences;
- artificial recurrence;
- explicit summation;
- attention over retained evidence.

Hence a ramping signal in one location is not automatically the only support route.

### 2.4 Readout

Threshold/choice/motor output is downstream of the accumulated evidence.

Changing decision threshold can change behavior without changing the evidence state itself.

Thus:
    decision policy != evidence content.

### 2.5 Correlates

Decision-related ramping can reflect:
- accumulated evidence;
- urgency;
- motor preparation;
- confidence;
- correlated task state.

Current decision-neuroscience reviews emphasize the need to disentangle such sources.

R114 therefore requires perturbation and model comparison before assigning a signal to the support set.

## 3. Bearer/self-state estimation

### 3.1 Content-bearing support

The selected content is not the word "I."

It is a relation encoding or estimating:

> which entity/body/process is the source of the system's own action channel and state transitions?

Biology candidate supports include:
- body ownership representations;
- self-location;
- agency;
- proprioceptive/interoceptive state;
- multisensory self-attribution.

AI candidates include:
- controlled-entity state;
- body schema;
- forward/inverse model;
- self-memory;
- agent capability/boundary state.

### 3.2 Access/permissive support

For bearer estimation, action/outcome identity binding is a key access relation.

The R112 toy showed:
- entity-specific action consequence -> bearer accuracy 1.0;
- erase entity identity but retain generic "something changed" -> 0.5.

Thus self-relevant information can exist in the world model yet fail to identify the bearer if the own-action relation is unavailable.

Biology analogues include agency/prediction-error and multisensory attribution mechanisms.

### 3.3 Degenerate alternatives

Biological self attribution uses multiple cue families:
- vision;
- proprioception;
- vestibular signals;
- interoception;
- motor efference/action prediction.

Different cue combinations can partly compensate for one another.

AI self models can likewise use:
- action-effect history;
- explicit agent IDs;
- body geometry;
- tool ownership;
- persistent memory.

Therefore "self model" should be represented as a support hypergraph, not one module.

### 3.4 Readout

First-person language, explicit self-report, or an "I" token is downstream evidence.

An agent may correctly orient to its controlled entity without verbal self-description.

Conversely, an LLM may fluently say "I" without a stable bearer-state relation.

Thus first-person language is not sufficient evidence of a constitutive self model.

### 3.5 Correlates

Self-referential activations, attention to own name, or first-person token probabilities can correlate with self tasks but require causal tests.

The strongest current AI self-orienting evidence is behavioral/functional; the constitutive mechanism remains less established.

## 4. Cross-substrate category alignment

The categories align at a useful intermediate level.

| Category | Working memory | Evidence integration | Bearer estimation |
|---|---|---|---|
| content-bearing | retained cue state | accumulated evidence state | bearer/entity state |
| access/permissive | retrieval/routing gate | accumulator-to-choice routing | own-action/outcome binding |
| degenerate alternatives | active/connectivity/external stores | distributed recurrence/sequences/explicit accumulators | visual/proprio/interoceptive/action cues |
| readout | motor/verbal delayed answer | threshold/choice/motor output | first-person report |
| correlate | decodable but unused trace | ramping/task-correlated signal | self-word/attention correlation |

This table is the first support-category map shared by biology and AI in the workspace.

## 5. The categories are role-relative, not intrinsic labels

The same physical relation can play different categories for different tasks.

Example:
- a frontal pathway can be permissive for one report task;
- content-bearing for another task;
- redundant under a third condition.

Therefore the taxonomy labels a relation **with respect to capability T and context M**.

This avoids reifying brain regions or AI modules into permanent semantic roles.

## 6. Implication for UCT

Only verified constitutive support relations should enter the experience–intelligence bridge.

For capability T:

    causal support audit
        -> relation category
        -> actual K anchoring
        -> C1 conditional experiential interpretation.

A content-bearing relation and a permissive gate are both part of K and therefore both part of complete experiential organization under C1.

But they do not justify the same content claim.

A permissive gate's necessity does not mean:
    "the experience of T is located in the gate."

This distinction is essential.

## 7. A new content-claim rule

R114 freezes a stricter rule for experiential-content interpretation.

To claim that constitutive relation r is specifically related to experiential content X, require more than causal necessity.

At minimum:
1. r carries distinctions corresponding to X;
2. interventions on those distinctions produce content-specific changes;
3. generic access/output explanations are controlled;
4. the mapping generalizes across matched contexts;
5. the relation is anchored in actual K.

Without those steps, the safe statement is only:

> r is part of the organization supporting capability T.

This sharply separates:
- experiential-organization membership;
- experiential-content attribution.

## 8. Why this matters for the original AI question

A powerful AI may:
- store information;
- integrate evidence;
- model its own state;
- produce self reports.

But each observed behavior can arise from a different mix of:
- content;
- access;
- alternatives;
- readout;
- correlation.

Therefore "the AI says it feels X" is an endpoint of a support graph, not a transparent window into E.

Likewise "the AI solves a difficult task" identifies a capability, not the unique experiential organization that supports it.

## 9. Current strongest bridge claims

### Working memory
Strong:
    retained-state organization is necessary in the toy family and plausibly central across substrates.

Not established:
    same retained-state phenomenology across biology and AI.

### Evidence integration
Strong:
    temporal integration relations are causally testable in biology and AI.

Promising:
    T2 mechanism correspondence via recurrent/distributed accumulation.

Not established:
    T3 constitutive homology.

### Bearer estimation
Strong:
    self/bearer attribution is functionally separable from generic world task ability.

Promising:
    action/outcome identity is a cross-substrate role.

Weak:
    current evidence for constitutive cross-substrate homology.

## 10. Next step

R115 should tackle the missing piece between "support relation exists" and "what experience is like":

> Can experiential **content structure** be constrained without human verbal labels?

Use structural relations rather than qualia words.

Candidate approach:
- define discriminations and similarity geometry induced by a verified content-bearing support;
- compare intervention-preserved relational geometry across biology and AI;
- keep valence and report separate;
- ask whether content-structure homology can be stated without claiming identical qualia.

This is the natural next step after support identification.

## 11. Status

R114 is a causal-role audit and a stricter bridge rule.

It does not prove any AI experiential content.

Its main result is the separation of experiential-organization membership from experiential-content attribution.
