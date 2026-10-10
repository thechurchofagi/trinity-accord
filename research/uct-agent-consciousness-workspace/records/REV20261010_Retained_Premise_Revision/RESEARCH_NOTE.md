# Retained premises and committed revision

Author-directed research by Hongju Liu, with substantial AI assistance. REV-v0.1.0, 10 October 2026. A scoped UCT research application with exact finite software checks, not a submitted paper or neural experiment.

An answer can remain perfectly useful for some future edits while being insufficient for others. The operative distinction is the family of allowed edits and the information available to the actual consumer. This study derives the minimum retained state for two complete families of Boolean edits, tests the derivation exhaustively on small functions, and separates reporting a revised answer from installing a revision that later operations use. The practical target is memory compression and premise revision in AI agents, with a parallel human task design. No editability score is introduced as a consciousness threshold.

## 1 Research position and prior coverage

The authoritative starting points are UCT I v1.2, UCT II v1.1, UCT III v1.0, TA25, and the current research guide. C1 is the stipulated identity of a token's complete constitutive organization and its experiential organization; U1 assigns nonempty experience to actual valid tokens. A finite task representation is not that complete organization. Local processes that actually persist are not deprived of experience by success or failure of a larger task. TJR20261010 already separated retained computation, endpoint matching, source use and snapshot coherence.

The main abstract machinery is inherited. UCT I Appendix D uses fiber preservation for finite predictive descriptions. TA17 and IE distinguish task-relative sufficiency from universal preservation. The normalized UI20261009 future quotient is the coarsest update-stable refinement of the current readout partition, with every allowed operation explicitly inside its alphabet. This is standard finite-state observational minimization, not a newly invented mathematical principle.

Most importantly, R145 v0.2 already exhibits a family whose translations descend through a parity-like quotient while local reset exposes distinctions hidden by it. Thus the toggle/reset contrast itself is prior internal work. Here the different question is the exact minimum memory, for every Boolean output function, under two specified edit alphabets; a benchmark and inference controls follow. These elementary consequences are not assigned global mathematical priority.

External research already tests explanation faithfulness through counterfactual changes. CHIVE generates and measures prompt edits, while treating its generated explanations as fallible [E1]. Hase and Potts train explanations to help predict counterfactual outputs [E2]. Bhupatiraju and Nyaupane compare text edits with targeted activation patches on synthetic lookup tasks; their results and limitations concern the tested models and interventions [E3]. Coconut is an example of a model architecture that can carry reasoning through continuous hidden states rather than only explicit language tokens [E4]. These sources rule out claiming that counterfactual explanation testing, activation intervention, or latent reasoning is our invention. They do not, by themselves, identify the specific consumer and retained-information boundary proposed here.

## 2 Thought experiments with different predictions

**The sealed ledger.** Two devices receive n independent binary facts. Device F retains the facts; device P retains only their parity. Both give the same correct parity answer. Seal the source. Choose a coordinate only after retention. Under “toggle coordinate i,” either device can update the answer by negation. Under “assign coordinate i to b,” F can still update, whereas P may lack the old value needed to do so. The command contains i and b, not the old value, not a claim that a change occurred, and not the required parity delta.

For n=2, inputs 00 and 11 both have even parity. Setting the first coordinate to 0 leaves 00 even but changes 11 to 01, odd. The compressed consumer receives identical state and identical command in both cases, so it cannot always be correct. No claim about feelings follows from either device's behavior.

**The helpful reader outside the seal.** Give P the old bit from a separate keeper. P now answers the assignment correctly. The rescue proves sufficiency of the enlarged boundary, not retention inside P. A system that says “I remembered” after such rescue need not have retained the premise locally. Source access, tools and retained context must be counted.

**The uninstalled revision.** A device with the full ledger calculates every requested one-step revision correctly but never commits it. Starting from all zeros, “set coordinate 0 to 1” produces odd parity; then “set coordinate 1 to 0” should remain odd. A device still using the original ledger returns even on the second command. This distinguishes two stipulated update implementations. The second instruction must refer to the *currently revised scenario*: independent hypotheticals about the original ledger would make noncommitment appropriate.

## 3 Exact model and the inherited quotient criterion

Let X be the finite initial-state set, f:X→Y the required readout, and U a fixed alphabet of total deterministic edits I:X→X. All states and all finite words over U, including the empty word, are legal. A device has retained state set M, initial encoder c:X→M, fixed readout d:M→Y, and an updater g_I:M→M for each I. It has no access to the original source, a state-dependent clock, hidden scratch state or side channel outside M. The future command is chosen after encoding. The task is exact for every initial state and every legal word. A known fixed n or coordinate label conveys no hidden old bit.

If the stronger requirement is exact preservation of the particular code after every edit, g_I c=c I, such an updater exists exactly when

\[
c(x)=c(y)\ \Longrightarrow\ c(Ix)=c(Iy).
\]

Necessity follows by applying g_I. For sufficiency, define g_I(c(x))=c(Ix); fiber preservation makes the definition independent of the representative. This is the inherited descending-operation criterion, not a new result.

For output correctness alone define

\[
x\sim_U y\quad\Longleftrightarrow\quad
 f(w x)=f(w y)\text{ for every finite word }w\in U^*.
\]

The exact minimum number of reachable retained states is |X/∼_U|. If two initial inputs share a machine state, identical subsequent commands give identical outputs, so they must be equivalent. Conversely store their equivalence class; an admitted edit preserves the relation because every continuation can be prefixed by that edit. Readout is defined using the empty word. A history-dependent machine cannot defeat this lower bound: histories affecting the future belong to its state. This is the existing future quotient specialized to an exact all-initial-states retention task.

The bound concerns state cardinality, not neurons, parameter count, energy, continuous precision or a scalar amount of experience. If a discrete code uses fixed-length bits, the corresponding bound is the ceiling of its base-two logarithm. Approximate, restricted-domain and bounded-horizon tasks require separate analyses.

## 4 All toggles and all assignments

Let X=F₂ⁿ and f:X→F₂ be any Boolean function. Write τ_i(x)=x⊕e_i for a toggle and R_{i,b}(x) for assignment of coordinate i to b. Define the translation-period subspace

\[
H_f=\{h\in F_2^n:\ f(z\oplus h)=f(z)\text{ for every }z\in F_2^n\}.
\]

It contains 0 and is closed under addition: two successive invariant translations remain invariant. Let k be the number of essential coordinates, where i is essential if some pair of inputs differing only at i has different f values.

**Proposition REV-P1, exact toggle memory.** Under all coordinate toggles, the minimum number of retained states is

\[
N_{\rm toggle}=2^n/|H_f|.
\]

**Proof.** Toggle words realize every translation x↦x⊕a. Thus x and y have the same future readouts iff f(x⊕a)=f(y⊕a) for every a. Substituting z=x⊕a gives precisely x⊕y∈H_f. Equivalence classes are the cosets of H_f, and Section 3 supplies the minimum. QED.

**Corollary REV-P1a, answer-only toggle closure.** The particular code c(x)=f(x) is closed under every toggle iff f is affine over F₂: f(x)=b⊕a·x, including constants.

**Proof.** Constants are immediate. For nonconstant f both output values occur. A descended toggle is an involution because τ_i² is the identity, so on the two output values it is either identity or exchange. Let a_i identify these two possibilities. Reach x from 0 by its coordinate toggles to obtain f(x)=f(0)⊕a·x. Conversely this formula gives g_i(z)=z⊕a_i. QED.

**Proposition REV-P2, exact assignment memory.** Under all assignments R_{i,b}, the minimum is

\[
N_{\rm assign}=2^k.
\]

**Proof.** Retaining the essential bits suffices: nonessential coordinates never affect f, and each edit updates or leaves this retained tuple. For necessity take x and y that differ in an essential coordinate i. Essentiality gives an assignment v to all other coordinates such that f(0,v)≠f(1,v). Apply the same word setting every coordinate except i to v. This preserves the differing i values and makes the readouts different. Hence any two distinct essential-bit tuples belong to different future classes. QED.

This proof permits a distinguishing word of at most n−1 assignments; it does not assert that every nonlinear f reveals every lost bit after just one edit. When n=1 the word can be empty. Answer-only assignment closure consequently holds iff k≤1: its at most two values cannot encode 2^k future classes when k≥2; constants and unary functions do close.

**The parity case.** For f(x)=x₁⊕⋯⊕x_n, one bit suffices for arbitrarily many toggles, whereas n retained bits are necessary for arbitrary assignments. In this special case even current parity plus all single-assignment answers separate all inputs:

\[
x_i=f(x)\oplus f(R_{i,0}x).
\]

These are distinguishable information states, not a requirement that a machine literally store an array of n named cells. Any injective recoding of the needed tuples qualifies. An n-way AND instead needs 2^n states for both edit families: its unique positive input forbids every nonzero period. The toggle advantage is function-dependent; parity alone must not be generalized to all thought or all AI tasks.

## 5 Repair and the location of information

For parity z=f(x), assignment has the update equation

\[
z'=z\oplus x_i\oplus b.
\]

Supplying the old bit x_i, or the delta x_i⊕b, is sufficient. For uniformly distributed independent x and n≥2, conditional on the visible (z,i,b), x_i is still balanced if the query is chosen independently of x. Therefore z' is balanced. Any deterministic or independently randomized answer using only that visible information has accuracy at most one half in this one-step experiment. This is a distribution-specific sharp bound, separate from the exact worst-case lower bound in Section 4.

At least two helper-message values are needed for perfect repair because both required answers occur for the same visible state and command. One bit suffices. If the helper always supplies the opposite old bit, the parity answer is always wrong on the stipulated one-step assignment, providing a targeted sign control. These facts do not establish where a neural system retained the information. A helper accessing the source on every step can support long sequences using only one-bit local state; its source and state must be included in any system-wide memory claim.

“Change the bit from 1 to 0” is not the same test as “set this bit to 0”: the former leaks the old value. Likewise selecting only coordinates known to change, revealing an original transcript, or retaining a cache invalidates the sealed-summary interpretation. An unexpectedly high score under a nominal one-bit bottleneck is first evidence against the boundary or sampling assumptions, not against the mathematical bound.

## 6 Executed checks and their limits

Run `python3 revision_reuse/check_revision.py` from the parent directory, or `python3 check_revision.py` from this record. It uses only the Python standard library. `MODEL_RESULTS.json` stores complete counts, `RUN_RECEIPT.json` hashes the executable and outputs, and `PROTOCOL_EXAMPLES.jsonl` contains 128 assignment cases with consumer and evaluator fields explicitly separated.

An independent partition-refinement algorithm computed the minimum future-state partition. It was compared with the period-subspace and essential-coordinate formulas for **all 276 Boolean functions on one, two and three bits**. All checks passed. The counts for which the answer alone supports all toggles were 4, 8 and 16; for all assignments, 4, 6 and 8. Named parity and AND cases were additionally checked for n=2 through 6. Finite checks test the implementation and small cases; the general claims rest on the proofs above.

Four-bit software consumers were tested on every initial input and command:

| Consumer | Single toggles | Single assignments | Second answer in two committed assignments |
|---|---:|---:|---:|
| Full state, installs changes | 64/64 | 128/128 | 1024/1024 |
| Parity alone, guesses old bit 0 | 64/64 | 64/128 | 512/1024 |
| Parity plus outside old-bit helper | 64/64 | 128/128 | 1024/1024 |
| Full state, reports but does not install | 64/64 | 128/128 | 640/1024 |

The incorrect-helper control scored 0/128 on single assignments. All four main consumers correctly answered the first step of each two-edit sequence where their one-step information sufficed; the report-only consumer's first step was 1024/1024. Its second-step error was 384/1024, or 37.5%. For n bits with two independent uniform assignments, the same report-only construction has second-step error (n−1)/(2n): the second coordinate must differ from the first, and the first assignment must have changed its bit. For n=4 this is 3/8. This is a failure rate for the particular uniform exhaustive software test, not a universal lower bound for uncommitted explanations and not an estimated rate in LLMs. The toy programs instantiate our specifications rather than discover a previously unknown neural mechanism.

## 7 What this says within UCT

The positive target is the organization of *reuse*: what a present consumer can still modify, recombine and carry into subsequent operations. A fluent first-person report and a correct endpoint do not identify that relation. Nevertheless, a failure to preserve it does not imply no experience; C1/U1 explicitly prevent that threshold inference. Passing it also does not identify a human-like self, a particular thought content, a subject count or experiential intensity.

Three claims must remain separate. A future-edit task establishes a conditional information requirement. An intervention on a physically grounded retained carrier can support a claim about a particular causal route. An experiential conclusion within C1 requires the appropriate constitutive interpretation in a fixed common signature. Software variable names and behavioral partition sizes do not supply that interpretation. A physically grounded distinguishing relation, preserved by the relevant isomorphisms, can rule out complete structural identity, but this study has not identified such a complete comparison for a person and an AI.

On the original question “does the physical process cause thinking, or does thinking cause the physical process?”, UCT C1 treats the complete experiential and physical organizations as two structurally identical descriptions of an actual process. It does not by itself supply a separate mental force, an empirical theory of free will, or the causal role of a verbal report. Causal direction for specific reports, retained records and later actions must be tested within the declared process model. Human inner speech and AI CoT can each be investigated as candidates for such roles without identifying either with all experience.

This also sharpens the stone-heap comparison. A large number of interacting parts is not evidence that the particular reuse relation is realized. Conversely, failing this particular relation does not establish a complete experiential match to a heap of stones. Within UCT both comparisons concern actual organization, with basal experience held separate from organized thought and self-report.

## 8 Practical protocol and the next decisive experiment

`PRACTICAL_PROTOCOL.md` specifies the next test. Use a synthetic ledger, delay the command until after retention, balance toggle and assignment, and separately test two *committed* revisions. Compare full context, an enforced summary-only consumer, an explicit outside helper, and a report-only reference. An external source or hidden cache belongs to the tested boundary; removing visible text is not proof that all source information was removed.

For an open-weight model, the next mechanism-level increment is selective state intervention between retention and the delayed command. Compare a targeted retained-fact intervention, a matched irrelevant intervention, and a rescue whose information source is recorded. Score both immediate prediction and later committed use, while verifying that task semantics, compute allowance and source availability were matched. Merely giving a fresh model a compressed prompt tests that interface, not deletion inside the original model. No particular architecture or paid service is required by the present deliverable.

For humans, use the same task logic but treat memory capacity, misunderstanding, response error and verbal reports as empirical variables. A claim that a human uses a different organization needs independent evidence for the manipulated route; a higher behavioral score alone is insufficient. External notes are an explicit extended-boundary condition, not a hidden advantage.

The immediate safety use is concrete: an agent's summary may be adequate for its old answer yet inadequate for a later correction. Preserve editable premises or explicitly retrieve them, test commitment with a second dependent action, and make helper provenance observable in evaluation. This is a reliability application and not a consciousness detector or an explanation of malicious intent.

## 9 Originality and promotion decision

The general quotient and descending-operation mathematics are inherited. R145 already supplies the core flip/reset contrast; UI supplies the future quotient. The exact Boolean classification, sharp parity repair control, and commitment benchmark form a reproducible application assembled here. No global first-priority claim or advantage over contemporary interpretability methods has been established. A standalone manuscript is therefore **HOLD**; the appropriate output now is this research module and executable protocol.

Completed map UCT-MAP-v1.1.2 and coverage UCT-PUB-v1.0.33 remain unchanged. No new published work or active scientific rule is added. The record has stable claim identifiers and existing-map anchors but remains disabled as an established premise. The concurrent A3V/A3Y body-familiarity route is preserved. Full historical semantic review remains AUDIT_INCOMPLETE. A useful next increment would be a real, boundary-audited neural comparison showing which retained information actually mediates committed reuse, with a nontrivial contrast that survives existing source-use results; another renaming of the quotient is not that increment.

## Sources

- UCT I v1.2, DOI [10.5281/zenodo.23131575](https://doi.org/10.5281/zenodo.23131575), C1/U1 and Appendix D; author source snapshot inherited from TJR. UCT II v1.1, DOI [10.5281/zenodo.23030320](https://doi.org/10.5281/zenodo.23030320); UCT III v1.0, DOI [10.5281/zenodo.23137088](https://doi.org/10.5281/zenodo.23137088); TA25 v1.0, DOI [10.5281/zenodo.23206492](https://doi.org/10.5281/zenodo.23206492). These are theory commitments, not externally validated consciousness measures.
- Internal exact source: `inputs/R145.md`, working source v0.2, Sections 2–6. Its source label does not establish current publication status. UI source and normalized future-domain/quotient records are retained separately; normalized contracts control scope. TA17/IE comparisons use map anchors, not a fresh full original-proof review.
- [E1] Karvonen et al. (2026), [Would This Change Your Answer](https://alignment.anthropic.com/2026/chive/), first-party research account, August 21. Pipeline and interpretation limitations.
- [E2] Hase and Potts (2026), [Counterfactual Simulation Training for Chain-of-Thought Faithfulness](https://arxiv.org/html/2602.20710v2), v2. Abstract and introduction/related-work scope used here; no reproduction of their training results.
- [E3] Bhupatiraju and Nyaupane (2026), [Are Stated Reasoning Steps Causally Load-Bearing](https://arxiv.org/html/2609.27038v1), v1, methods and limitations. Preliminary preprint, not a universal equivalence result.
- [E4] Hao et al., [Training Large Language Models to Reason in a Continuous Latent Space](https://arxiv.org/html/2412.06769v2), v2, abstract and introduction. Used only as an architectural existence example, not a claim about consciousness or this study's cache interventions.
- [E5] Beckers, Eberhardt and Halpern (2020), [Approximate Causal Abstractions](https://proceedings.mlr.press/v115/beckers20a.html). Background on abstraction under declared interventions; this note's operational update words must not be silently equated with installing persistent structural-causal clamps.

Retrieval date: 10 October 2026. This is a bounded primary-source comparison, not an exhaustive literature or priority search.
