# Exoskeleton Instrumentation Cannot by Itself Identify Proprioceptive Consumer Read

**Result version:** EIP-RESULT-v0.1.0  
**Status:** bounded exact countermodel plus prospective measurement contract; pending and disabled  
**Base:** completed UCT-MAP-v1.1.2, unchanged

## 1. Question and result

CBI left a concrete engineering question: can an exoskeleton preserve distal movement/contact while a selected proprioceptive branch is absent, and can instrumentation show where the branch is absent? The answer divides in two.

First, a robot can operationalize a declared *partial* match over endpoint kinematics, forces, contacts and timing. Human wrist-robot work demonstrates precise haptic tasks, while microneurography can record identified muscle-spindle afferents together with kinematics and EMG. These are genuine components of a test package. Second, neither matched output nor the joint observation of peripheral spikes, central arrival and aggregate downstream activity identifies actual read/use by a named consumer when a redundant writer remains uncontrolled. `model.py` gives an exact countermodel.

The constructive result is therefore a two-level contract: (i) transduction/delivery evidence and (ii) consumer-specific causal read evidence. The latter requires a selective discrepancy or block plus alternative-writer exclusion and a faithful, temporally bound readout. This is a methods result, not an actual human installation and not a phenomenal verdict.

## 2. Fixed ontology

For one episode fix bearer candidate `b`, movement/contact event `e`, selected peripheral carrier `s`, named central consumer `c`, delivery window `W_s`, consumer-read window `W_c`, distal envelope `D`, motor/muscle proxy envelope `M`, and evidence package `E`. Define:

- `S=1`: the selected carrier is delivered in `W_s`;
- `G=1`: consumer `c` actually gates/reads that carrier in `W_c`;
- `X=1`: an uncontrolled alternative writer supplies the same aggregate consumer update;
- `U=(S ∧ G) ∨ X`: the observed consumer update;
- `Y=U`: a deliberately favorable faithful distal/aggregate readout.

`S`, central arrival, `G`, `U`, `Y`, and evidence for them are distinct. A peripheral spike is not a central read; an evoked response is not yet route-specific causal use; successful output is not use.

## 3. Exact non-identification result

**EIP-C1 (consumer-read non-identification).** In the displayed mechanism, observing `S`, arrival=`S`, `U`, and `Y` does not identify `G` while `X` is uncontrolled.

*Proof.* For `S=1`, the worlds `(G=0,X=1)` and `(G=1,X=1)` both yield arrival `1`, update `1`, and output `1`. The complete enumeration finds ordinary evidence classes containing both gate values. This remains true despite an upstream single-carrier record and a downstream response.

**EIP-C2 (conditional exclusive-probe identification).** If `X=0` is independently secured, the Boolean interface is correct, `S=1`, the consumer readout faithfully reports `U`, and timing/selectivity premises hold, then `U=G` in that episode.

This is a conditional identification theorem, not evidence that those premises are physically satisfied. Off-target effects, another writer, common causes, latency mismatch or a mis-specified consumer defeat it.

## 4. Empirical feasibility boundary

The inspected primary work establishes important pieces rather than the whole contract. Dimitriou and Edin recorded human wrist-extensor spindle afferents with microneurography while simultaneously measuring wrist kinematics and EMG. Their results also show why simple geometric matching is insufficient: afferent discharge depends on velocity/acceleration and on extrafusal/fusimotor drive and load mechanics, not merely whole-muscle length. Cuppone and colleagues used a multi-degree wrist robot with measured haptic torques and vision blocked, showing that precise robotic sensorimotor envelopes and additional tactile feedback are feasible; it also shows that extra feedback can be incorporated and may be supplied contralaterally. Woldag and colleagues reported cortical neuromagnetic fields after voluntary and passive hand movement, supporting a central-arrival measurement family. None of these studies jointly fixes a single carrier, selective block/replay, a named consumer, exclusion of alternative writers and a causal consumer readout.

Accordingly, `SOURCE_SCOPE.md` records a source-bounded `not established`, not a universal impossibility or a claim that no future human protocol can qualify.

## 5. What an exoskeleton can and cannot freeze

It can hold a declared distal envelope `D` within tolerances by supplying torque. It can log applied forces and reduce some movement differences. It cannot make a true read-versus-no-read contrast while preserving the *complete* actual organization: the target consumer–carrier relation itself differs. That difference is logically unavoidable and is the experimental target, not a nuisance.

Other changes—effort, attention, EMG, fusimotor drive, cutaneous/visual input, prediction error, agency, ownership and report—are not entailed by the finite logic. They are plausible biological co-changes that must be measured, randomized, bounded or admitted as residual ambiguity. Calling all of them unavoidable would overstate the proof; calling them irrelevant would overstate the experiment.

## 6. Thought-experiment stress tests

The exoskeleton pair fixes output but changes lineage. The abacus/calculator pair fixes a result but varies the actual implementing organization. Human-implemented-agent and copy/switch/memory cases show that externally identical reports do not settle which installed route was consumed. The ancestor/formation family prevents the instrumentation package from becoming a new basal-experience gate. `THOUGHT_EXPERIMENT_MATRIX.md` states fixed and varied coordinates and the precise defeater each case supplies.

## 7. UCT interpretation and limits

If an actual bearer and complete signature are independently admitted, a carrier–consumer relation is independently constitutive for the target organization, and C1 is applied, then changing that actual relation has an experience-internal counterpart. EIP supplies none of the missing admission or phenomenal-direction premises. It does not identify familiar mineness `H`, agency, ownership, conceptual self, report, consciousness of any present system, or fear of death. It adds no introspection, language, recursive model, integration, prediction, control or instrumentation threshold to basal experience.

The result advances the body/action-related mineness programme narrowly: it tells a future experimenter what evidence would distinguish installed proprioceptive consumption from an output-matched behavioral proxy, and why arrival-only instrumentation cannot do so.

## 8. Direction check after result

PASS with bounded return. The work stayed on one body/action carrier–consumer relation and produced an exact underdetermination witness plus a falsifiable measurement contract. It did not turn generic robotics, neural decoding, scores, papers or map growth into the research objective. The next step, if pursued, is one named-consumer selective-discrepancy feasibility assessment, not broader instrumentation enumeration.
