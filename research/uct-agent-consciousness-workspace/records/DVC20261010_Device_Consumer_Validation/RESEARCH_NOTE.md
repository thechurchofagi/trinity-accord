# Device consumer validation: public tactile data, actual-event contracts, and finite timing models

**Research record:** DVC20261010_Device_Consumer_Validation  
**Status:** completed public-data reanalysis, apparatus-contract review, and finite digital model; actual consumer application unadmitted; candidate disabled; standalone paper held.  
**Publication relation:** a subsequent supplement to SCU v1.0.1, [DOI 10.5281/zenodo.23272690](https://doi.org/10.5281/zenodo.23272690). This record does not modify that published paper.

## 1. Outcome and evidence classes

This checkpoint connects the source–consumer question to an existing tactile experiment without treating its condition labels as measured neural inputs. It combines three completed activities: retrospective analysis of public observations from 18 included participants; inspection of the published apparatus and documented interfaces; and execution of a separate digital model of arrival, capture, retention and consumption. No hardware was deployed, no new human observations were collected, and no motor-only `10` condition was established at a human neural consumer. The two component records retain their independent evidence and denominators: [apparatus findings](apparatus_evidence/MAIN_FINDINGS.json) and [model results](device_model/EXACT_RESULTS.json).

The combined finding is specific. Behavioral location and precision estimates can be recovered while the actual source, consumer, timing and intervention conjunction remains unestablished. Conversely, specifying two input gates is insufficient to realize the intended consumer inputs: old latches, late arrivals and source substitutions can survive nominally correct settings. DVC supplies a concrete admission contract and executable counterexamples. It does not supply an experiential identity from behavior or a biological gate from a fitted response function.

## 2. Public data and independent estimation

The selected study uses a Touch X movement apparatus, an Arduino-controlled passive rail and separately triggered forearm vibration to study tactile comparison under movement and attention conditions. The source article is D’Onofrio Pacheco and Zimmermann, [DOI 10.3758/s13414-026-03288-7](https://doi.org/10.3758/s13414-026-03288-7); the public data are [DOI 10.5281/zenodo.18877381](https://doi.org/10.5281/zenodo.18877381). This is prior published human work, not our apparatus installation.

The downloaded archive was hash-checked against its registered checksum. It contains 121 trial CSV files, 21 participant identifiers and 10,875 nonempty records. Applying the author's three participant exclusions leaves 18 participants and 9,705 records. One included record has command zero, outside the declared command range; removing it leaves **9,704 records across 108 participant-condition cells**. The independent pipeline fitted each cell under two analysis specifications, giving **216 numerical fits**, all converged without hitting their specified bounds. These counts and source locations are recorded in the [data report](apparatus_evidence/DATA_REANALYSIS_REPORT.md) and [exact audit](apparatus_evidence/results/EXACT_RESULTS.json).

The fit is a Bernoulli maximum-likelihood cumulative normal,

\[
\Pr(R=1\mid x)=\Phi((x-\mu)/\sigma),\qquad \sigma>0.
\]

Here `x` retains the archive's command units, `mu` is the fitted PSE, and `sigma` is the normal standard deviation. The pipeline separately outputs the 75%-minus-50% threshold. Neither quantity is silently substituted for the released column named `JND`. Physical amplitude calibration is unavailable. The fitting implementation, fixed bounds, starts and statistics are documented in the [analysis code](apparatus_evidence/code/reanalyse_apparatus_data.py) and [refit statistics](apparatus_evidence/results/INDEPENDENT_REFIT_STATISTICS.json).

Response coding has a material qualification. The archive uses `InputValue` 0/1, whereas the article describes physical keys 1/2. The inspected material did not expose the conversion. Interpreting 1 as comparison-stronger is motivated by the ascending command–response curves but remains an assumption. PSE is the fitted 0.5 crossing; for the same curve, replacing probabilities by their complements preserves that crossing. This does not verify the physical stronger/weaker naming. The effective [response-coding correction](apparatus_evidence/RESPONSE_CODING_CORRECTION.json) supersedes an overconfident provenance sentence in the preserved execution metadata without changing numerical outputs.

## 3. Behavioral results and reproduction limits

The following paired contrasts use the same 18 included participants. Confidence intervals are two-sided 95% intervals. Holm adjustments apply within the separately declared three-contrast families, not across an unspecified collection of tests. Exact values, family definitions and unadjusted tests are in [MAIN_FINDINGS.json](apparatus_evidence/MAIN_FINDINGS.json).

| Quantity and contrast | Mean difference | 95% interval | Holm-adjusted p |
|---|---:|---:|---:|
| Source-labelled JND: Passive Start minus End | 0.49820 | [0.22387, 0.77253] | 0.004008 |
| Independent sigma: Passive Start minus End | 0.68300 | [0.30407, 1.06192] | 0.004266 |
| Independent sigma: passive attention difference minus active attention difference | 0.75857 | [0.28798, 1.22916] | 0.010203 |
| Same sigma interaction, available-timing sensitivity analysis | 0.75318 | [0.27285, 1.23352] | 0.012466 |
| Independent PSE: Active minus Control, averaged over attention | −0.40793 | [−0.70979, −0.10607] | 0.022093 |
| Independent PSE: Passive minus Control, averaged over attention | −0.75050 | [−0.95761, −0.54339] | 0.000002019 |

The archive and independent fits support a movement-dependent attention contrast in precision, alongside separate location differences. The sensitivity specification removes 341 active records using available latency/duration fields and a within-participant, within-attention rule. It does not recover unavailable trajectory, gaze or physical-event exclusions, and is not an exact reconstruction of the original preprocessing. Nonsignificance elsewhere is not evidence of equivalence. These scopes remain explicit in the [data report](apparatus_evidence/DATA_REANALYSIS_REPORT.md).

The paired Student intervals are conventional model-based subject-level inferences, subject to their sampling and distributional assumptions. Numerical reproduction does not establish exact 95% coverage for every bounded population, and no such distribution-free claim is made.

Several archived-parameter statistics reproduce reported rounded values, while others remain unresolved. In particular, the complete 18-person summary gives source-labelled JND attention F(1,17)=19.82485; a source paragraph reports degrees of freedom not reconstructed from this released population. The difference-score interaction F(2,34)=6.64762 is recovered. The archived-JND/independent-sigma ratio ranges from 0.68670 to 0.80233 across the unfiltered cells, so no fixed identity between those quantities is established. The cited fitting repository lacks the required `anamax.m` dependency. These are documented reproduction limits, not grounds to select participants until statistics agree or to declare the author's parameter wrong. See [archived statistics](apparatus_evidence/results/ARCHIVED_PARAMETER_REANALYSIS.json) and the [reproduction discussion](apparatus_evidence/DATA_REANALYSIS_REPORT.md).

## 4. What the real apparatus record does not establish

The released data contain judgments and some software-labelled time fields, but no selected neural consumer's source-token, capture or read events. All 8,985 time-bearing rows exceed their declared CSV widths. An explicit paired-token/NaN reconstruction fits those rows, yet possible unit conventions and event assignments remain unresolved. The first response/command fields support the bounded behavioral analysis without resolving these clock meanings. The reconstruction is not a measurement of physical tactile onset, and cannot establish a zero-versus-delayed physical stimulation manipulation. Raw witnesses and layer distinctions are preserved in [TIMING_PARSE_REVIEW.md](apparatus_evidence/TIMING_PARSE_REVIEW.md).

Manufacturer documentation provides concrete interface candidates. The [OpenHaptics API Reference](https://s3.amazonaws.com/dl.3dsystems.com/binaries/Sensable/OH/OpenHaptics_API_Reference_Guide.pdf) describes position and encoder queries; the [Programmer's Guide](https://s3.amazonaws.com/dl.3dsystems.com/binaries/Sensable/OH/OpenHaptics_Programmers_Guide.pdf) distinguishes frame snapshots, previous-state queries, buffered settings and output transmission. These are established interface concepts. Their availability does not identify the selected experiment's call sites, firmware, command-copy port or actual read instrument. The [apparatus contract](apparatus_evidence/APPARATUS_CONTRACT.md) states each missing field.

The proposed external inputs are therefore **M_D**, a specifically identified device-command copy, and **P_E**, a device position/state sample. A passive rail command is not a participant's efference copy; an encoder value is not a neural proprioceptive intake. Active human movement may lack the corresponding device command. Control, passive and active labels cannot by themselves instantiate human `00`, `01` and `11`, and the archive supplies no selectively isolated human `10` branch with consequences held fixed.

## 5. Finite model: when configured gates become actual inputs

The independent [digital model](device_model/model.py) separates source issue, actual port arrival, gated capture, buffer invalidation, immutable paired commit and designated read. Availability, payload and consumed occurrence are different coordinates: a supplied zero remains an input. Each execution fixes its own joint contract; paired rivals may differ in the explicitly declared consumer or pathway.

**DVC20261010-C1** states that each snapshot cell contains the last successful capture surviving invalidation **at that snapshot's commit boundary**, or absence. Buffer-event induction proves the result. An eager consumer reads the two intended tokens precisely when its actual snapshot cells contain them and it reads that committed object. Gate closure alone does not reset or revoke a token; readiness alone does not establish reading by an unspecified algorithm.

With old and new payloads all equal to one, the six operations `arrival_M`, `arrival_P`, `capture_M`, `capture_P`, `commit` and `consume` have 720 orders. The [exact enumeration](device_model/EXACT_RESULTS.json) partitions them as follows:

| Mutually exclusive outcome | Orders |
|---|---:|
| Both intended new tokens consumed | 6 |
| Consumption attempted before commit | 360 |
| Committed output matches, but at least one intended new token is not consumed | 354 |

These are model-order counts, not measured failure rates. Correct current-token use requires both arrival–capture chains to precede commit and consume; exactly six chain interleavings satisfy that order.

**DVC20261010-C2** supplies the timing condition. If an intended token is valid at the actual port during `[a,b)`, arrival and departure vary independently over declared bounds with `a_max < b_min`, and stability is required throughout `[s-u,s+h]` with nonnegative `u,h`, universal validity is equivalent to

\[
a_{\max}+u\le s<b_{\min}-h.
\]

The extreme arrival and departure establish necessity and sufficiency. Gate/writer validity is an additional premise. Two channels can sample simultaneously only if their safe windows intersect. Separate captures can instead form a retained same-episode pair when source binding, storage, commit, resource and deadline conditions jointly hold; this does not make the source events simultaneous. Full proofs are in the [model note](device_model/RESEARCH_NOTE.md).

The executed scope also includes four gate-factorial pairs, 4,896 bounded-window checks, 400 safe-window pairs, 108 chronology instances and nine retained witnesses, with zero violations. These denominators remain separate. **DVC20261010-C3** covers displayed warm-latch, delayed-arrival, overwrite, mixed-epoch, swapped-source, reheaded-old-token, reflex and bypass failures. **DVC20261010-C4** preserves the deadline distinction: a token generated after a consequence cannot be used to predict that same consequence beforehand. See the [claim ledger](device_model/CLAIM_LEDGER.json) and [run receipt](device_model/RUN_RECEIPT.json).

## 6. Human endpoint and UCT interpretation

**DVC20261010-C5** limits the proposed shadow's evidential role. In a fixed acyclic causal model, with other functions, inputs and disturbances fixed, a shadow-gate change cannot alter the human endpoint when no directed path reaches that endpoint itself or any ancestor. This follows by evaluating its ancestors and the endpoint in dependency order. Shared resources, cues, timing or analysis changes could violate the premise. No simulated PSE is offered as empirical support for this conditional statement.

PSE is the prospective primary comparative-intensity endpoint for a future apparatus test, not a retrospective preregistration. Independently fitted sigma and source-labelled JND remain separate precision quantities. The existing key response reports a comparison; it does not identify agency, ownership, conceptual self or familiar mineness. Intelligence and successful information processing likewise do not determine the named experiential interpretation.

**DVC20261010-C6** retains C1/U1: only an independently admitted complete actual P/I/K signature, interval and jointly grounded source, retention and consumer relations license the conditional structural counterpart. A latch does not establish RetBind or familiar H by naming. Local admitted processes are preserved, no exclusive owner is selected, and probe eligibility creates no basal-experience threshold. Behavioral evidence, actual organization, conditional UCT interpretation and report semantics remain distinct. The [open-obligation ledger](device_model/GAP_LEDGER.md) records the remaining bridges.

## 7. Contribution, status and next concrete work

MPC's missing-corner/read limits, SCU's source/intake/chronology distinctions, earlier retention and port-fidelity results, psychometric fitting, and ordinary snapshot/timing theory are inherited. The retained increment is an independently executed public-data reanalysis coupled to an explicit device-consumer admission repair. Worldwide priority and a standalone-paper threshold are not established; this remains a disabled supplement after the published SCU paper.

Concurrent CBI also already supplies the branch-relative `P=A AND T AND L AND R` minimal-cut necessity, its three cut locations and matched-world-output approximation. That result is deducted from DVC novelty. CBI's absence of a current movement-evoked intake can coexist with a DVC consumer reading an old cached token; the predicates have different occurrence targets. CBI's motor delivery-or-use declaration is not evidence of DVC's designated actual read. The [concurrent reconciliation](CONCURRENT_CBI_RECONCILIATION.md) preserves those distinctions and corrects three bibliographic tuples without changing the original CBI files.

The next task is to obtain one accessible installation's versioned command/state ports, actual capture and read instrumentation, clock bounds and independent consequence measurements. These premises must hold together for the same installation and probe epoch. The integrated [probe protocol](PROBE_PROTOCOL.md) specifies that acceptance package. Complete-map review, actual support and publication coverage remain separately governed; no local numerical PASS upgrades them.

## Concurrent EIP reconciliation

The last pre-save ref check found EIP at d8c94faa846fc4d459628c9bc896adfb4a038d7e. Its exact files and disabled 6/3/5 candidate are preserved. The arrival/read and redundant-writer boundary is additionally deducted from DVC novelty; no frozen DVC component claim or public SCU file changes. See [CONCURRENT_EIP_RECONCILIATION.md](CONCURRENT_EIP_RECONCILIATION.md). Current coverage is UCT-PUB-v1.0.22, following EIP v1.0.21.
