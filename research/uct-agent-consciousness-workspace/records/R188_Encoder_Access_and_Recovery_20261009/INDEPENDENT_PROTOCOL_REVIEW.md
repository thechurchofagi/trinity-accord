# R188 independent protocol and proof-application review

**Review date:** 2026-10-09. **Research:** R188-CER-20261009 / CER-RESULT-v0.1.0. **Guide read:** RESEARCH_MASTER_GUIDE v2.2. **Scope:** new R188 finite mathematics, executable protocol, reported receipts and mathematical statements in MAP_EXTENSION.json. The separate map reviewer owns full inherited-graph semantic review.

**Verdict:** the central weighted formula, six-state comparison and executed reference policies are consistent. No factor-of-two, source-context access or external-test-law defect was found in these core results. One clarification is required for the separate block-coding countercontrol: its side-information role is fixed across its two coordinates. It must not be described as a successful unrestricted iid two-use code. This scope clarification does not change or invalidate the core R188 result.

## 1. Evidence actually inspected

I read both Python source files in full, read the R188 module statements and inspected all receipt records programmatically. I checked receipt/source hashes, record/table totals, per-mode scores, all 126 recorded input/guess records, worker identities and event patterns. I did **not** rerun either experiment. This is code/proof/receipt review, not a second experimental replication or evidence about subjective experience.

Audited source SHA-256 values:

- `check_encoder_access.py`: `04c2049adccf6df7b5426ba40aff174f0cc99f01749071a4518400e1959c0354`
- `run_process_reference.py`: `49844d4134d68b2ee75c7b7c22d95ad424364dee57ddd64710d2214cd3c53b47`

Both match the hashes recorded in their execution receipts. The inspected receipt hashes were:

- `EXACT_RESULTS.json`: `8f063a43a05b69b18117488b8b73100acf42a82ef70c0b97f947c8c95c7f9c11`
- `PROCESS_RESULTS.json`: `165d0d152f035801e8c09c3fff5aa72d7be26aff07e679a74cfd131ae44611c4`

The inspected map snapshot hash was `8355d89c012041d2cc6b5f0ef790707294d1858b4a7120261e1b4c090dc9b104`; this identifies my read scope and is not a release checksum for later map edits.

## 2. Core formula and exact enumerations

The theoretical value

    S*=1-W+Cut_(K^L)(G,w),  w_e=min endpoint joint masses,

equals one minus the minimum total weight of equal-response-word endpoint pairs. This is exactly what `cut_optimum` computes. In the uniform case each endpoint/context pair has mass 1/(2|E|), so the formula is

    S*=1/2+MaxCut_(K^L)(G)/(2|E|).

There is no missing factor of two. For the prism, seven of nine edges can cross; S*=1/2+7/18=8/9. The complete-graph denominator `2*n*(n-1)` is also correct when its numerator is the sum of class sizes multiplied by class sizes minus one.

`direct_protocol_optimum` separately enumerates encoder reply tables and feedback selectors, then optimizes the decoder by direct posterior-cell maximization. Its observation key contains context, feedback and reply; feedback is a function of context and supplies no uncounted target information. This independently checks the graph reduction for the small three-state weighted cases. The larger interactive graph cases use the proven reduction and constructive attainment, and must not be called direct enumeration of every six-state interactive protocol.

The exact receipt contains 50 records: two external-law checks, eight optimum/attainment checks, two direct no-feedback enumerations, fifteen weighted full-protocol comparisons, twenty-one complete-graph checks, and two countercontrols. Summing the recorded enumeration fields gives the stated 38,013 candidate tables. These are finite corroborating computations, not proof by sample count. Independent-randomness optimality is proved analytically; the code does not enumerate all randomized protocols.

## 3. The compared external task is held fixed

Both graph implementations enumerate exactly the same external domain (T,J) in [6]×[3]. The graph-dependent neighbor router is the changed internal mechanism. The source receives T; the reader receives the resulting two-candidate edge. The code verifies T's marginal 1/6, context marginal 1/9 and both endpoint posteriors 1/2.

Consequently the claimed equal conditional entropy and equal isolated context-aware recovery are valid. The internal joint distributions P(T,X) differ, as explicitly acknowledged in the module. Do not replace that statement by “the two systems contain exactly the same information” or “their complete internal states are equal.” No changed external prior is hidden in the score comparison.

## 4. Process reference implements the declared policies

The 126 recorded cases consist of seven graph/mode combinations, each covering eighteen external stimuli. There are 252 distinct recorded worker PIDs, and source and reader PIDs differ in every trial. Source functions receive the target and fixed graph/code/mode configuration; reader functions receive the context and fixed configuration. Current reader context is not a source argument, and target is not a reader argument.

The prism blind code is (0,1,0,1,0,1), which cuts seven edges and gives 16/18 correct targets. The flexible prism code is the proper three-color assignment (0,1,2,1,2,0). The reader chooses a binary coordinate on which its two candidates differ, and the source returns that coordinate of its own code. It gives 18/18. The three-symbol control also gives 18/18.

The receipts preserve these event orders:

- Timely feedback: receiver sends selector; source receives selector; source replies; receiver fixes the scored guess.
- No feedback: source replies; receiver fixes the scored guess.
- Late feedback: source replies; receiver fixes its guess; only then does receiver send the selector and source receive it.

The late condition therefore has effective L=1 for the scored reply and correctly retains 16/18 on the prism. This is a test of logical protocol order. It does not measure a physical millisecond deadline, biological feedback delay or optimal real-time implementation speed.

The dedicated receipt channels report to the supervisor; the source's target-containing receipt is not forwarded to the reader. They are outside the scored actor-to-actor interface. The experiment is a transparent executed policy reference, not an independent proof of an upper bound over arbitrary OS processes.

## 5. Physical-isolation and UCT claims are appropriately limited

The workers share an operating-system environment, filesystem, machine and program installation. The current code does not use PID, file reads, scheduler information or timing to select its reply, but these facts do not establish physical causal closure for every possible program running in that environment. API arguments alone do not prove OS security or exhaust all physical influences.

Both the source comments and receipt explicitly deny OS-level isolation, complete physical organization, biological latency and phenomenal measurement. These limitations must remain in the manuscript and final communication. The successful reference policies certify the recorded finite construction under inspected code; they do not identify a unique source event or numerical subject.

The module's actual-process and UCT grounding premises remain OPEN. None of the reviewed calculations implies experience magnitude, an experience threshold, exclusive subject count, felt effort or erasure of continuing local experience. The user's C1/U1/P3 commitments and the distinction between actual admission, organization and finite observation are preserved.

## 6. Clarification required: what the block countercontrol proves

The separate matrix example uses two-bit vectors A,B, the invertible map

    M(b0,b1)=(b1,b0 xor b1),
    W=A xor M(B).

It tests three reader roles: observing **all of A**, **all of B**, or **all of A xor B**. The same role is used across both coordinates. Its 16 source assignments times three roles account for 48 decoded cases. Since M and I+M are invertible, the successful recovery assertions are sound.

It does **not** test independently changing the reader's role at each coordinate. A concrete failure witness for that broader protocol is:

    first source:  A=(0,0), B=(0,0), W=(0,0);
    second source: A=(0,1), B=(1,0), W=(0,0).

Both have mixed side information (A0,B1)=(0,0), so that mixed-role reader cannot distinguish them. The code therefore must not support a claim that ordinary iid two-use batching generally eliminates the single-use obstruction, nor that it repairs the six-state prism experiment.

**Required wording:** “a separate two-coordinate block with one common side-information role across the block is exactly decoded in 48 cases; this illustrates the importance of declaring the whole block protocol and does not cover arbitrary per-coordinate role changes.” The existing `DIFFERENT_PROTOCOL_NOT_REFUTATION` label is correct and should remain. No rerun is needed to establish the narrower already-executed statement; any source edit requires refreshing its recorded code hash by the normal execution workflow.

## 7. Final disposition

The main proof/application and the actual execution receipts support a scoped theoretical-methods candidate. They do not establish new foundational coding-theory priority or empirical UCT validity. Preserve the distinction between inherited Witsenhausen/Orlitsky machinery, the new project-level weighted application and matched construction, and unverified historical priority.

This review requests the block-scope clarification above and otherwise finds no blocking mathematical or protocol-application defect in the new core R188 result. Full-map release status is deliberately not decided here.
