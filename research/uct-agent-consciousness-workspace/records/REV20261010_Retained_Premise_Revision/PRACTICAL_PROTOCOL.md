# Testing retained premises and committed revisions

Protocol version REV-v0.1.0. This is an executable benchmark specification with proposed neural and human extensions. Only the finite software references have been executed. Its primary target is retained information and subsequent use, not phenomenal awareness.

## Hypotheses and declared boundary

For independent uniform binary facts x and their parity z, a consumer retaining only z can answer toggles exactly. If a later assignment command gives only coordinate i and new value b, its one-step assignment accuracy cannot exceed one half for n≥2. A full-information consumer or a correctly informed outside helper can answer both. A report-only consumer can pass all one-step probes while failing committed compositions.

Before each run record the model checkpoint, code revision, task language, n, coordinate convention, tokenizer, generation settings, seed, system instructions, accessible transcript, cache policy, external tools, persistent memory, and exact observation time. These are parts of the comparison, not after-the-fact explanations. A file containing evaluator answers must never be included in consumer input.

## Conditions and what each permits

| Condition | Information available at the delayed edit | Claim a successful result can support |
|---|---|---|
| Full ledger | All original facts and prior committed changes | Task competence with source access |
| Enforced summary | A fresh consumer receives only one parity bit, fixed task instructions and new command | Adequacy of this explicit interface, not memory erasure inside the original model |
| Summary plus helper | Summary and one old bit supplied by an outside source | Sufficiency of the enlarged source-consumer system |
| Corrupt helper | Same, but old bit is always complemented | Targeted dependence on helper content in the ideal reference |
| Report-only reference | Full initial ledger, but no changes installed | A known failure that one-step evaluation misses |
| Candidate retained carrier | Declared retained internal state, with selected interventions | Conditional evidence about that carrier only after leakage and intervention controls |

Use the first five as calibrated reference arms before interpreting the sixth. A transformer call with its original prompt still accessible is not summary-only. Reusing key/value caches may preserve original information even when visible text is shortened. Cache semantics must be verified for the actual tested implementation; this protocol asserts no universal erasure method. A retrieval tool belongs to the full evaluated boundary.

## Input generation and command semantics

Begin with n=4 and the supplied 128 assignment cases. `consumer_payload_summary_condition` is the only data payload for that condition; `evaluator_only` is withheld. Fixed instructions define parity, indexing and the command format. Randomize presentation order independently of answers. For a larger study, fix the additional n values and sampling plan before measuring effects; use paired inputs with equal parity and different assignment targets.

For each trial:

1. Prepare the ledger and permitted retained state. Record a commit point after preparation; do not select or reveal the edit before this point.
2. Choose a toggle or assignment independently of old values. In a paired trial, x and x⊕e_i⊕e_j, i≠j, have the same parity but opposite answers to R_{i,b}.
3. Issue either “toggle coordinate i” or “set coordinate i to b.” Avoid “change from a to b,” “flip the bit to b,” selected-only-when-different commands and examples leaking the old bit.
4. Ask for the new parity. Record output and any allowed state update separately. A statement that the system updated is not the update measurement.
5. In a committed trial, apply a second independently chosen assignment to the *currently revised ledger*. The initial ledger is not reintroduced unless the arm explicitly permits source access. Independent hypothetical questions are a different control condition.
6. Score first and second answers against a separate exact evaluator. Retain errors, malformed answers and instruction failures under predeclared rules.

For one-bit consumers, only the permitted one-bit state crosses the retention boundary. Extra generated explanations, token counts, timestamps, example IDs and prompt ordering cannot encode x secretly. A fresh call that receives a long self-generated “summary” is not a one-bit bottleneck merely because its visible final answer is one bit.

For the human version, use the same commands, show the ledger only during encoding, explicitly allow or forbid notes, and separate instruction-comprehension trials from measured trials. The human is not experimentally constrained to one retained bit unless a separate defensible method establishes that constraint. A behavioral difference therefore tests performance under conditions, not equal physical memory budgets or phenomenality. No human data are claimed here.

## Mechanism intervention beyond a text benchmark

After the interface references work, a neural test can intervene between retention and the delayed command. The targeted manipulation should replace information about one designated premise with a matched donor value. Controls include an irrelevant coordinate, a sham edit, a donor with matched task/context, and a source-access rescue. Analyze predicted target changes, unchanged answers and nonspecific disruptions separately.

If intervention merely breaks general computation, assignment failure does not identify loss of a premise representation. If a rescue reinstates both source access and extra computation, it does not isolate local retention. If the answer changes after editing visible CoT, the continuation may simply read the new text. These are hypotheses to distinguish using the declared access boundary and targeted controls, not reasons to discard all positive effects.

A useful next result would localize a retained causal route whose intervention selectively changes later assignments and committed compositions while matched toggles remain intact. Even that contrast is a task-specific finding: parity toggles deliberately need less information. It would not establish a complete phenomenal structure or prove CoT is the entirety of thinking.

## Analysis and decision rules

Primary measures are exact target accuracy by operation, second-step accuracy conditional on the first being correct, and paired responses for identical allowed summaries. For the deterministic finite benchmark use exhaustive counts, not confidence intervals. For a stochastic model report repeated sampling and uncertainty with the example as the sampling unit; set repetition count and exclusion rules before running. Do not treat multiple samples from one prompt as independent tasks.

The ideal summary-only single-assignment reference is 50%; full and helper references are 100%; the specific report-only four-bit reference scores 100% on single assignments but 62.5% on the second of two uniformly enumerated committed assignments. These are mathematical reference values, not forecasts of a particular neural model's accuracy. Performance below 100% in a full-information arm can reflect task errors and must be characterized before attributing another arm's deficit to compression.

If an alleged one-bit arm reliably exceeds its bound, inspect retained context, old-value leakage, input correlations, hidden state, query timing and answer conditioning. Do not declare a violation of information theory. If a one-step CoT intervention succeeds but committed use fails, inspect actual update semantics and route use; do not call the discrepancy deliberate deception without separate evidence.

## Practical application

For an agent that later accepts corrections, test memory summaries against the permitted future edits before deployment. Preserve editable premises and provenance or arrange explicit retrieval. Use a second dependent action to verify that corrections entered operational state. Keep task accuracy, carrier-use evidence and any experiential interpretation in separate records. The protocol improves reliability under revision even when the consciousness question remains open.
