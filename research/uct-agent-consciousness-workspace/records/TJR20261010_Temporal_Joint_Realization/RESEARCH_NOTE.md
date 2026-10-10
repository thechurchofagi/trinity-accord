# Temporal retention, joint use, and the limits of serial/parallel comparisons

**TJR20261010 / TJR-v0.1.0 — 10 October 2026**

Status: scoped foundational application and correction, **PENDING_MAP; disabled as established premises**. No new consciousness theorem, physical realization study, or human/AI measurement is claimed. Standalone manuscript decision: **HOLD**.

## 1. Research question and inherited commitments

Does sequential updating prevent the joint organization involved in thinking? Four different questions must be kept apart: which variables update together, which retained values coexist, which values an installed operation actually uses, and which experiential interpretation is justified.

UCT I v1.2 C1 concerns the complete organization of an admitted actual process, not its task score or an arbitrary computational description. Under U1, an actual process does not lose basic experience merely because it is simple, serial, mistaken, or unreportable. Persisting local processes are not erased by their embedding in a larger process. These are inherited UCT commitments, not findings of this study. We do not introduce a concurrency threshold for basal experience.

This study treats the human/AI question at the level of candidate physical organization. A human thought, under C1, is not an extra immaterial cause competing with the physical process: the theory identifies its experiential presentation with that process's organization. This conditional interpretation does not settle the empirical truth of C1 or identify the organization of a particular thought.

The immediate aim is narrower: reject invalid shortcuts before proposing a distinctive human/AI comparison. The concurrent bodily-familiarity project remains preserved and is not globally redirected by this user-scoped study.

## 2. Prior-art constraints that change the proposed contribution

**Bennett, 2601.11620v2, §§4–6 and Remark 3.** Ingredient-wise occurrence across a window does not entail their conjunction at one instant. Chord adds a phenomenal necessity postulate; the algebra does not prove that postulate. His contributor-capacity theorem presupposes a grounded content requiring more simultaneously active contributors than the architecture permits. Remark 3 already acknowledges persistence as a sufficient condition for temporal commutation. Consequently, retained serial computation is not a new refutation of his theorem. A count of register writes cannot simply be substituted for his specified count of active grounded contributors. The accessible article and its referenced persistence remark were inspected; the separate supplement was not fully recovered.

**Kanai and Ma, 2606.15348v1, §§4–6, 9.** ICCR explicitly includes physical support, intrinsic partitions, interventions, internal joint readouts and a declared boundary. It already distinguishes a recurrent register realization from boundary-equivalent alternatives. Its preservation statement is conditional on an organizational invariance principle. Our finite macro-step equivalence is weaker than ICCR and does not solve its grain-selection problem. We do not claim priority for replacing output comparison with intervention-sensitive organization.

**Chalmers (1996), §§5–6.** The structured-state implementation discussion precedes this project. Merely matching a sequence, or adding a recorder, is inadequate to capture internal computational organization. No new solution to implementation triviality is claimed here.

**Internal prior results.** UCT I Appendix D already treats closed updates and intervention-respecting abstraction. UCT II v1.1 §§2,4,12 separates finite views, independently admissible bridges and temporal retention from named memory systems. TA17:QUOTIENT, IE:QUERY_SUFFICIENCY and UI20261009:FUTURE_QUOTIENT already distinguish task-relative future equivalence from complete organization. RTTH v1.0.0 distinguishes retained information, reader mismatch and actual use, including a minimum reader-tag alphabet. SCU v1.0.1 and pending A3R already analyze source use and side-recorder/bypass alternatives. R173 supplies a separate history-sensitive retentive relation. Their original statuses and physical/phenomenal obligations are retained.

## 3. Four implementations of one small relation

Fix Boolean inputs a,b and the target f(a,b)=a XOR b. Fix a retention port r and allow its replacement only after capture and before consumption. A second input carrier is held fixed during that intervention. All ports, routes and intervention targets are explicit stipulations of the model; no black-box procedure is assumed to have discovered them.

| Implementation | Events and consumer | Ordinary outputs | Effect of replacing r by 1-a |
|---|---|---|---|
| Parallel capture | Capture a and b together; consume retained pair | f for every a,b | Toggles output |
| Serial retention | Capture a; retain it; capture b; consume retained pair | f for every a,b | Toggles output |
| Side record and live bypass | Store r=a; independent live a,b route computes f | f for every a,b | No output effect |
| Fixed replay | Emit a previously fixed value 0 | Matches f only on selected inputs | No output effect |

**TJR-C1 — scoped realization separation.** The first three implementations have identical boundary truth tables, yet the nominated record participates only in the first two. All four agree at the nominal input (0,0). Proof is direct substitution into their declared transitions; the executable trace records each event.

The bypass example is deliberately not a system with no joint computation: it computes the relation elsewhere. It prevents us from mistaking a visible record for the route that produces an answer. A fixed replay is not a lookup table indexed by the present inputs; giving replay such an input-selection mechanism changes the model.

Replacing a record gives a functional effect in this example. Absence of an output effect is not a universal criterion for absence of an internal read: an installed expression r XOR r reads the value but cancels at the output. Redundancy, context and readout limitations must remain explicit. This is an application of existing source/consumer distinctions, not a new universal participation test.

## 4. What correct serialization actually requires

Let a synchronous finite update be F(s)=(F_1(s),...,F_n(s)). A serial implementation can first preserve a snapshot s in an old-state buffer, then write each new coordinate F_i(s) exactly once, in any order. Provided the buffer remains unchanged, each coordinate function is executed correctly, and the comparison is made only after the entire block, the final state equals F(s).

**TJR-C2 — buffered serialization.** The preceding statement follows because the ith final coordinate is F_i(s), independent of the write order. A source-state replacement before snapshot capture is transported to the same replacement of the buffer; the endpoint equality therefore holds for every replaced source state too. This preserves only the specified block-endpoint map and those transported boundary interventions.

It does **not** establish preservation of micro-time readouts, mid-block interventions, latency, resource use, arbitrary recurrent component identity, complete physical organization, or experience. Matching a macro-step map does not establish ICCR.

Without the old-state buffer, even a two-coordinate implementation can fail. For F(a,b)=(f(a,b),g(a,b)), in-place A-then-B gives

    (f(a,b), g(f(a,b),b)).

It matches F on every state exactly when g(f(a,b),b)=g(a,b) on every state. Swapping old a and b is a simple failure: overwriting a first destroys the old a required by the second write. This is ordinary synchronous/asynchronous update semantics; no mathematical priority is claimed.

The enumeration covers all 256 pairs of Boolean coordinate functions and all four initial states. For each order, in-place serialization disagrees with the synchronous endpoint in 256 of 1,024 pair-state cases. Both buffered orders have zero disagreements. These counts describe the uniform enumeration, not probabilities of failure in real machines.

## 5. Retention need not preserve every ingredient separately

Fix nonempty finite sets A,B,Y, a total deterministic target f:A×B→Y, and a temporal cut. Before the cut a is available but b is not. After the cut the consumer receives b and a retained code m(a) only. All a-dependent information accessible after the cut is included in m: no rescan, hidden clock, schedule, external copy or other side channel is allowed. The allowed domain is all of A×B and exact correctness is required. Resource limits of encoding/decoding are not modeled.

Define a~a' iff f(a,b)=f(a',b) for every b. This compares residual answer functions, not complete physical processes.

**TJR-C3 — exact retention criterion, inherited mathematics.** An unrestricted decoder d satisfying d(m(a),b)=f(a,b) exists iff

    m(a)=m(a') implies a~a'.

Necessity: a shared code and the same b supply identical decoder arguments, so required answers must agree. Sufficiency: choose a representative of each nonempty code fiber; the implication makes its answer independent of the chosen representative. Thus the minimum number of reachable code states is |A/~|. With fixed-width binary coding this requires ceil(log2 |A/~|) bits. This is the deterministic one-way communication distinct-row bound; Aaronson (2005), Proposition 3.1, states the standard binary version. It is also a direct application of the existing UCT project's fiber criteria.

For a,b each n bits, parity of their concatenation needs only two retained states: retain parity(a). Exact equality a=b needs 2^n retained states, because any two distinct prefixes are separated by choosing b equal to one of them. Both targets depend essentially on every input bit, yet their required retained distinction counts differ exponentially in state count. This is not an experiential complexity comparison.

The proof is general in the declared finite domain. Exhaustive checks separately cover all 64 Boolean 3-by-2 target tables and 36 named memory maps per table, totaling 2,304 cases, and verify minimum reachable-state counts. Parity/equality examples were checked for n=1,...,6.

**TJR-C4 — compression does not establish complete preservation.** Prefixes 00 and 11 have the same parity and the same future parity-answer function, but differ as histories and under coordinate queries. A sufficient summary for one relation can discard other relations. Preservation of the whole declared query family requires equality of its joint residual answer vector. Enlarging the family may refine the equivalence classes. This consequence is already covered by TA17 and IE; it does not provide a new consciousness measure or select an intrinsic grain.

## 6. A present conjunction can concern a past that never jointly occurred

Consider a world with only the states (0,0) and (1,1), changed by one atomic event U. A reader samples coordinate A and coordinate B once each, retaining both samples. The two reads and U have six possible orders. If U lies between the reads, the reader obtains (0,1) or (1,0). Neither pair occurred in the world, but both retained values now exist together and the installed XOR consumer returns 1.

**TJR-C5 — temporal reference and present realization are different relations.** Four schedules yield a genuine world snapshot and two yield mixed-time pairs. In the latter, a present joint read is real within the model although its interpretation as a synchronous world snapshot is false. An exact monotone epoch tag attached atomically to each sampled value detects these two mixed schedules by tag mismatch in this one-update model. Rejection does not itself supply a valid answer. General multiwriter or wrapping-counter protocols require stronger assumptions and are not established here.

This is an application of the classical snapshot problem, not a new concurrency result. Afek et al. already give implementations of atomic snapshot memory from read/write registers. The contribution here is to prevent an inference error in our consciousness comparison: inaccurate temporal reference is not absence of actual internal organization.

Under UCT, a physically realized false representation still has the experience associated with its actual organization, assuming it qualifies as an actual process. Calling that experience confusion, a false memory, or an imagined scene requires a separate content bridge. No subjective quality is assigned to these two-bit devices.

## 7. Consequences for the human/AI thought question

**TJR-C6 — a three-level separation.** (i) A task relation can be preserved by sequential storage and updating. (ii) Preserving it does not preserve every internal or temporal relation. (iii) A finite preserved relation is not the complete ontic structure required by C1. Conversely, a grounded difference can exclude full isomorphism only if every admissible full isomorphism must preserve that relation and its typed ports/time/boundary. This is the inherited OL:C1 application pattern, not an automatic inference from different code or scores.

For chain-of-thought, emitted words, later consumption of those words, and the model's other implemented computations are distinct candidate relations. A text trace can be causally used later, bypassed, partly redundant, or replayed in different implementations. The four-model comparison shows why visible text alone does not identify its role. It does not establish that any named deployed model follows one of these routes. Nor does it settle whether a reasoning trace exhausts anything deserving the name thought.

For the stone comparison, simple-looking matter is not declared devoid of experience under UCT. Nor does assigning computational labels to a stone establish the input, memory, consumer and intervention structure used here. The research target is the actual organization and its changes, rather than a binary classification based on fluent speech or a neural-network label.

## 8. Adversarial checks and exclusions

1. **Change the task after compression:** parity retention fails individual-bit recovery. Retention counts are task-relative.
2. **Leak information across the cut:** a second copy or input-dependent timing can defeat the stated memory bound. It must be included in m.
3. **Restrict input support or allow error:** exact full-domain bounds no longer automatically apply; randomized equality fingerprinting is outside this claim.
4. **Read during a serialized block:** a mixed intermediate state can distinguish buffered serial from synchronous evolution. Endpoint equality is intentionally limited.
5. **Treat a recorder as the consumer:** the live-bypass model reproduces every ordinary answer while ignoring the nominated record.
6. **Infer non-use from a null output intervention:** cancellation supplies a counterexample.
7. **Treat all serial machines as Bennett capacity-one systems:** the contributor grounding would need independent justification. The converse inference from a correct serial algorithm to phenomenality also fails.
8. **Treat false content as no process:** the mixed-time construction separates these predicates.
9. **Use a finite view as full C1 organization:** explicitly prohibited. No neural or phenomenal bridge has been discharged.

## 9. Originality decision and next discriminating question

**TJR-C7 — negative novelty decision.** This round delivers a reproducible comparison and corrects proposed shortcuts. Its mathematics is inherited or elementary application; the strongest general statements overlap directly with established communication complexity and existing project results. The source-use contrast is already developed in SCU/A3R. It is not enough for a new standalone research paper, and no global priority claim is made.

The next worthwhile question is: **can we give a physically grounded pair with the same declared task capacity but different installed ways of reusing retained relations, and show a complete-organization distinction that survives admissible recoding and changes of implementation schedule?** The difference must be more than an analyst choosing additional queries. Specify an actual consumer relation already installed in each system; provide a typed nonisomorphism witness; then state exactly what C1 transports and what human-like thought or named experience still requires.

First attempt: compare a compressed recurrent accumulator with a system retaining independently reusable components, while matching the external task. Test whether the proposed difference is merely the existing IE/OL/SCU distinction. If so, retain the negative novelty decision and seek an independent positive bridge to a specified experiential relation instead of adding another proxy score. C1 alone supplies structural correspondence, not the semantic name of the coordinate.

## Sources and verification

Exact versions, URLs, reading scopes and internal map links appear in SOURCE_LEDGER.json and CLAIM_LEDGER.json. All program results are in RUN_RECEIPT.json and MODEL_RESULTS.json. The executable is check_models.py. Eight check groups passed in the recorded run. The full historical semantic audit remains AUDIT_INCOMPLETE; this record does not promote the completed map beyond UCT-MAP-v1.1.2.
