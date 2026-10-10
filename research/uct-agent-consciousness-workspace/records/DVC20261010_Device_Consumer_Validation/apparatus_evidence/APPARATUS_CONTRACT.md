# A device contract for testing a source–consumer relation

**Parent research:** DVC20261010_Device_Consumer_Validation  
**Scope:** a proposed external consumer installation based on a published apparatus family, with a completed public-data audit. No new device or human experiment was run.

## 1. Selected real apparatus and evidence boundary

The selected case is D’Onofrio Pacheco and Zimmermann's 2026 attention study, [DOI 10.3758/s13414-026-03288-7](https://doi.org/10.3758/s13414-026-03288-7). The version of record describes a Touch X stylus, voluntary 20-cm arm movement, and passive movement driven by an Arduino Leonardo stepper/rail system. An Arduino Nano triggers forearm vibration. The within-participant design varies movement condition and attention location. It measures comparative tactile judgments; the released package supplies those judgments and fitted PSE/JND values. The full source record, exact version and read scope are in `SOURCE_SCOPE.json`.

This is an actual published human apparatus. Its public record does not expose a selected human neural consumer's motor-command and proprioceptive intake events. The following contract therefore specifies an **additional external consumer**. The labels `M_D` and `P_E` intentionally refer to a device drive-command carrier and a device position carrier. Their physiological meanings must not be silently changed to human efference copy and proprioception.

## 2. Field-by-field installation requirements

Every row below is a requirement for one installation and one probe epoch. Filling different rows from different devices, participants, sessions or code versions does not establish the conjunction.

| Field | Contract for the proposed installation | Current evidence status |
| --- | --- | --- |
| Actual bearer and boundary | Name the human, plant, controller and external consumer separately. Select the process and interval to which a claim applies. | Archive has pseudonymous trial identifiers. No new complete process signature admitted. |
| Plant driver | Record the code/firmware version and the command actually committed to the rail driver. Keep requested, buffered, committed and physically executed commands distinct. | Apparatus described in the paper. Drive firmware and command-event stream absent from the release inspected here. |
| `M_D` carrier | Tap a named controller output after its commit event. Preserve controller ID, command sequence, epoch, payload and commit time. | Proposed port. A human motor command or EMG surrogate is not this carrier. |
| `P_E` carrier | Read a named position/encoder endpoint with device ID, calibration state, capture time, value and frame sequence. | Vendor documents suitable device APIs; use in this particular study and its exact driver version remain unverified. |
| Consumer | Run a fixed, versioned shadow consumer with declared input ports and an immutable consumed-snapshot record. | Proposed installation. Published key judgments do not identify such an internal event. |
| Plant separation | Consumer branch gates must leave the plant command route intact. Logging and probes must not feed back into the physical movement or tactile controller. | Must be demonstrated in the installed wiring and code. It is not established by the published condition names. |
| Intervention | Change only the selected incoming branch. Specify whether closing a gate blocks future captures, clears a latch, substitutes a value or disconnects a wire. | These are different operations. No four-cell branch-isolation experiment is present in the inspected archive. |
| Reset and freshness | Specify initial latch content, gate state and the last successful capture per branch. Require both consumed tokens to meet the selected probe-epoch condition. | Proposed requirement. Equal payloads and equal consumer read time cannot replace this lineage evidence. |
| Clock relation | Record each clock domain, conversion, resolution, drift bound and synchronization uncertainty. | Source time-column meanings remain unresolved; see `TIMING_PARSE_REVIEW.md`. |
| Physical consequence | Measure actual trajectory and tactile onset/amplitude using independent sensors on a common or calibrated time base. Predeclare permissible differences. | No physical stimulus-onset trace or continuous trajectory is included in the release. |
| Context | Hold or measure fixation, stabilization effort, muscle activation, body posture, tactile mounting and block/order effects. | Condition labels and some trial timing exist; the corresponding raw context streams are not available. |
| Endpoint | Fix the instrument and response coding before using it to test a source hypothesis. Preserve bias, precision, agency, ownership and verbal report as separate variables. | Tactile judgments available. Agency/ownership instruments absent in this case. |

## 3. Concrete interfaces without an anatomical substitution

The vendor's [OpenHaptics API Reference Guide](https://s3.amazonaws.com/dl.3dsystems.com/binaries/Sensable/OH/OpenHaptics_API_Reference_Guide.pdf), printed p. 56, documents raw encoders, Cartesian position in millimetres and velocity in millimetres per second. The velocity output is smoothed. These interfaces can define `P_E` for a new installation, subject to its actual supported device/driver. They do not measure spindle afferents, a biological state estimate or a downstream neural read.

The [OpenHaptics Programmer's Guide](https://s3.amazonaws.com/dl.3dsystems.com/binaries/Sensable/OH/OpenHaptics_Programmers_Guide.pdf), printed pp. 89–91, already describes synchronous state snapshots, frame-relative `CURRENT`/`LAST` values, delayed force flush, overwrite and asynchronous read inconsistency. A buffered value is therefore insufficient to identify a committed physical output. These are established engineering mechanisms, not a new DVC discovery. Both retrieved manuals identify OpenHaptics 3.4.0 and carry PDF creation metadata dated 17 June 2015. Their exact inspected pages and hashes are recorded.

An operational event record should contain `installation_id`, `device_id`, `consumer_id`, `code_hash`, `clock_id`, `probe_epoch`, `event_id`, `source_token_id`, `source_commit_time`, `capture_time`, `read_time`, `gate_operation`, `payload`, `frame_id`, `calibration_id` and `physical_measurement_id`. A consumed pair must retain both source identities. A single timestamp attached after the read cannot certify that both inputs were captured in the same epoch.

## 4. The four branch cells and the human limit

In the proposed shadow system, two branch gates can expose all four `M_D,P_E` states while the plant remains on its ordinary drive path. This makes the missing `10` cell an engineering target. Even there, MPC's functional response table and the actual read record remain different evidence objects. Constant output, a short-circuit implementation, cancellation or a held old token can prevent one from identifying the other.

No current source inspection establishes the corresponding four cells at a human neural consumer. Rest contains ongoing posture and sensory signals. Passive movement can include stabilization commands. Removing a peripheral afferent input can also change motor control and body state. Renaming these situations `00`, `01`, `10` and `11` does not satisfy the contract. The full human mapping stays **UNADMITTED**.

For each device probe, admit a source-use conclusion only if the carrier, actual event instrumentation, timing order, common epoch, branch selectivity and consequence constraints all hold for that same trial. If any fails, retain the observation and the failure reason. Do not turn missing evidence into a negative claim about experience or about all input use.

## 5. Independently specified experience-related endpoints

For a future registered use of this apparatus, select **comparative tactile intensity** as the primary named target. Operationalize it using a two-interval stronger/weaker judgment and a predeclared psychometric location parameter, PSE. Select fitted normal standard deviation `sigma` as a secondary discrimination parameter. Report the response model, lapse assumptions and stimulus units. The current archive reanalysis is exploratory and retrospective; it is not described as preregistered.

| Coordinate | Operational variable | Inference allowed here |
| --- | --- | --- |
| Comparative tactile intensity | PSE of a specified command–judgment psychometric function | A behavioral comparative-bias estimate under the response model. It is not a direct identity claim about experience. |
| Tactile discrimination | Fitted `sigma`; separately, `Phi^-1(.75) * sigma` for a 75%-minus-50% threshold | An estimate of discrimination precision in the same task. It cannot substitute for the location parameter. |
| Agency | A separately specified agency instrument would be required | Not measured in the selected dataset. Active/passive labels are not an agency score. |
| Ownership | A separately specified ownership instrument would be required | Not measured. Tactile attenuation alone does not identify ownership. |
| Conceptual self and report | Explicit linguistic/self-attribution instrument, with its own time and target | The recorded key response reports a comparison. It does not establish a conceptual “I”. |
| Familiar mineness `H_fam` | Independently grounded named-target bridge | No calibration or admission here. It is not formation history and not inferred from a narrow consumer relation. |

Under the inherited UCT C1 commitment, an independently established actual organizational relation has a token-relative counterpart within experiential organization. The measured task behavior does not identify that counterpart as any of the named coordinates above. U1 and basal experience acquire no new threshold. Prediction, discrimination and action control concern aspects of intelligence/organization; successful performance alone does not fix experience type, selfhood or report semantics.

## 6. Next concrete acceptance package

A future operator can make this contract reviewable by supplying the wiring/port diagram, versioned controller and consumer source, recorded device/firmware identities, sample and commit records, both probe-epoch tokens at each consumer read, independent movement/tactile measurements, clock calibration and the prospectively fixed endpoint analysis. The existing archive can help set realistic trial and psychometric handling, but cannot fill absent physical/neural events retroactively.

No hardware installation was executed in this component. The completed work here is the public-data reanalysis and source/contract review. DOI publication or map promotion is owned by the parent research workflow.
