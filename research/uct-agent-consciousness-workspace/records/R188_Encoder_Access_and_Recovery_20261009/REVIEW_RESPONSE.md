# R188 response to protocol review and final-snapshot verification

**Research:** R188-CER-20261009 / CER-RESULT-v0.1.0. **Date:** 2026-10-09. **Review guide:** v2.2. **Document role:** append-only response closing the one scope clarification in `INDEPENDENT_PROTOCOL_REVIEW.md`. The earlier review remains unchanged as a record of the initial snapshot it actually inspected.

## 1. Initial and final evidence are distinct preserved snapshots

The original independent protocol review inspected an initial checker run containing **50 result records and 38,013 enumerated candidate tables**. It did not independently rerun that checker or the process reference. Its recorded source and receipt hashes match the preserved files under `initial_verification/`.

The authoring/execution workflow subsequently clarified the common-role block control, added the explicit mixed-role failure witness, and produced the final checker receipt containing **51 result records and the same 38,013 enumerated candidate tables**. This response reviews the final source, saved outputs and manuscript; it also does **not** independently rerun either experiment. Reading and checking a receipt is not represented as a second execution.

| Evidence snapshot | Source or receipt | SHA-256 |
|---|---|---|
| Initial checker | `initial_verification/check_encoder_access.py` | `04c2049adccf6df7b5426ba40aff174f0cc99f01749071a4518400e1959c0354` |
| Initial 50-record receipt | `initial_verification/EXACT_RESULTS.json` | `8f063a43a05b69b18117488b8b73100acf42a82ef70c0b97f947c8c95c7f9c11` |
| Final checker | `check_encoder_access.py` | `8245d18ce337d152f46ceb0d0c376abb4e51ca5d67b8bbf7998bfe88fbc265f8` |
| Final 51-record receipt | `EXACT_RESULTS.json` | `67414cb323922a99bfe949bb9e6e8ec256c04ed69942b8f5bc3834d180a53a59` |
| Unchanged process reference | `run_process_reference.py` | `49844d4134d68b2ee75c7b7c22d95ad424364dee57ddd64710d2214cd3c53b47` |
| Unchanged process receipt | `PROCESS_RESULTS.json` | `165d0d152f035801e8c09c3fff5aa72d7be26aff07e679a74cfd131ae44611c4` |
| Preserved original review | `INDEPENDENT_PROTOCOL_REVIEW.md` | `69711bc84e3da44ba3a89f9ebe0087b23978edd6d012da6caaefda4c6c166719` |

Both checker receipts record hashes matching their respective source snapshots. The first 49 result records are identical between the two saved runs. Record 50 retains the 48 successful common-role block cases and adds the explicit shared-role qualification. Record 51 records the new mixed-role failure witness. That witness is checked by direct assertions and does not add enumerated candidate tables, explaining the unchanged total of 38,013.

The process source and process receipt are unchanged. Their saved 126 finite trials, 252 worker processes, mode-specific results and limitations remain as previously reviewed. No additional process execution is claimed here.

## 2. Response to the requested common-role clarification

**Original review finding:** the two-coordinate matrix code recovers the source when the reader knows all of A, all of B, or all of A XOR B. Each reader's side-information role stays the same across both coordinates. The initial wording could be misread as a code for independently changing roles in two iid uses.

**Correction now present:** the final source and receipt explicitly set `common_side_information_role_across_coordinates` to true and describe the control as a common-role block. The manuscript §7.3 and `R188:ONE_SHOT` explicitly state that it is not an iid block-coding theorem with changing reader roles.

**Counterexample now present:** with M(b0,b1)=(b1,b0 XOR b1), the distinct source assignments

    (A,B)=((0,0),(0,0))
    (A,B)=((0,1),(1,0))

have the same transmitted word A XOR M(B)=(0,0) and the same mixed side information (A0,B1)=(0,0). Thus that mixed-role reader cannot identify the source with this code. The final code explicitly asserts these identities; the final receipt preserves the witness.

**Disposition:** the original scope clarification is resolved. The prior review's request remains historically correct for its initial snapshot; this response records its closure without rewriting that review. Neither the successful common-role block nor its mixed-role failure is a refutation of the main one-shot theorem, and neither is represented as a repair of the six-state prism protocol.

## 3. Final substantive mathematical checks

The final manuscript §§3–5, checker and relevant module statements use the same protocol: source access T, reader context e={a,b}, at most L feedback labels, then at most K forward labels, fixed target and scoring law, and no uncounted current-input information. K and L are cardinalities, not bit counts; no feedback is L=1.

### Weighted finite-error formula

The edge penalty is the **smaller joint endpoint mass**

    w_e=min{P(T=a,X=e),P(T=b,X=e)},

not the conditional error without its context probability. Equal response words incur precisely that penalty; unequal words can be separated by a reader-selected coordinate. With W=sum_e w_e, the formula

    S*=1-W+Cut_(K^L)(G,w)

is correct. The converse and constructive attainment refer to the same allowed encoder/reader class. Conditioning independent random tapes preserves the same input law and cannot improve the optimum. The assumption excludes input-correlated tapes and other uncounted access.

### Uniform and complete-graph formulas

Under uniform edges and fair endpoints, each joint endpoint mass is 1/(2|E|), yielding

    S*=1/2+MaxCut_(K^L)(G)/(2|E|).

There is no factor-of-two error. For a complete graph, with C=min(n,K^L), n=Cq+r, balancing response-word classes gives

    S*=1-[r(q+1)q+(C-r)q(q-1)]/[2n(n-1)].

The denominator and class counts are correct, including C=1 and C=n. Positive endpoint support makes zero error equivalent to chi(G)<=K^L. The K=1 case is handled separately; logarithms to base K are not applied there.

### Matched instance and repair

The common external input is uniform (T,J) in [6]×[3]. The graph-dependent context router is the changed mechanism. Both graphs are 3-regular on six targets and nine contexts, giving the stated equal marginals and two fair posterior candidates. Their complete internal P(T,X) laws differ, as acknowledged in the manuscript.

K3,3 admits a binary code cutting all nine edges. The prism's two disjoint triangles force at least two uncut edges, and the supplied binary code attains seven cut edges. Its exact optimum is therefore 8/9. The supplied proper three-color assignment can be represented by two-coordinate binary words; a timely coordinate selector gives exact recovery with K=2,L=2. A selector received only after the irrevocable scored reply cannot enter that reply, so its effective access remains L=1. These instance conditions and logical timing claims are correctly delimited.

### Relation to physical or experiential conclusions

The final manuscript retains the distinction between a proven admissible-protocol optimum, executed policies, physically justified access constraints and actual-process admission. No hardware isolation, biological latency, experience threshold, experience amount, named feeling or subject count is inferred from these examples. The actual grounding and UCT application premises remain separate. The theorem does not retract the inherited unrestricted-helper top-K upper bound; it restricts the class in which achievability is claimed.

**Final mathematical disposition:** no remaining substantive error was found in the checked R188 formulas, weighting, complete-graph expression, matched instance, constructive repair or their stated application conditions. This is a bounded review conclusion, not a claim of absolute error-freedom or externally established originality.

## 4. Final read scope and unchanged artifacts

The final manuscript snapshot read for this response has SHA-256 `a3a8578005bf24e38dc62b9b3a5ebba0364635e63266fc8b33ccf89e243f2046`. The final module snapshot inspected has SHA-256 `66c047490121ea27e668c89008936806ad15a92dbab15c8115e99dd421739be6`.

Only this new response document was written by this follow-up review. The frozen manuscript, checker, process reference, results, module and original independent review were not modified. Full-map release review and persistence are handled by the responsible parent/release workflow, not discharged by this response. No remote write, new experiment, DOI action or empirical UCT validation occurred in this review.
