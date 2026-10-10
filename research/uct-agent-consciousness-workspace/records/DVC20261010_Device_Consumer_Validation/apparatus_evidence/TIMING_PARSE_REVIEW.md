# Time columns, device identity and actual-event evidence

**Status:** archival semantics unresolved. The evidence below neither measures physical stimulus onset nor establishes a human neural consumer.

## 1. Raw rows and alternatives

`results/TIMING_PARSE_WITNESSES.json` retains ten exact source-row examples with file and line hashes, headers, complete tokens and conditional reconstructions. Examples include active, passive, control, a NaN duration, an out-of-range command and a blank line.

For example, `Active/Start/AD21_Aec.csv`, line 3, starts:

```text
2,1,5,1,937,2,959,1,937,0,000,1,937,1,022
```

Its header has nine fields. A strict comma parser returns fifteen. The first three fields remain unambiguous. Silently assigning only the first nine tokens to the nine headers loses six values and is not an admissible complete record.

The declared six time fields can instead be reconstructed as six pairs of an integer part and exactly three fractional digits, with `NaN` accepted as a single missing value. This gives `(1.937, 2.959, 1.937, 0.000, 1.937, 1.022)`. It is a stated reconstruction hypothesis, with every row checked, not a modification of the archive.

There are at least three unit readings to preserve. Decimal-comma seconds and grouped-integer milliseconds give the same physical durations after conversion. Decimal-comma milliseconds follows the literal `(ms)` header differently. The exporter format and original clock definitions are unavailable, so parsing alone does not select the intended units. More decisively, none of these parses establishes what event a variable assignment recorded.

## 2. Exhaustive conditional arithmetic

All 8,985 nonempty records with time fields have more CSV tokens than headers; all fit the explicit pair/NaN reconstruction. Across the entire archive, 242 duration values are NaN. The remaining finite `End−Start−Duration` discrepancies are bounded by 0.001000000000002 in reconstructed numeric units, compatible with separately rounded timestamps. This arithmetic supports the reconstruction but does not validate its physical timing meaning.

| Final 18-person cell | Nonempty records | `Stimulation−StartMovement`, reconstructed numeric values | Median finite duration |
| --- | ---: | --- | ---: |
| Active/Start | 1,620 | 0.000 for all | 0.580 |
| Active/End | 1,620 | 0.000 for all | 0.679 |
| Passive/Start | 1,610 | 0.500 for 1,609; 0.000 for one command-zero record | 1.088 |
| Passive/End | 1,615 | 0.500 for all | 1.105 |
| Control/Start | 1,620 | No time columns | unavailable |
| Control/End | 1,620 | All time fields zero | 0.000 |

`Latency` equals `StartMovement` in every reconstructed row. In the passive rows, `StimulationAfterMovement` matches the reconstructed offset shown above. These facts are exact properties of the downloaded file. A column whose name mentions “after movement” cannot thereby become an observed second vibration onset.

The paper's Methods and Figure 1 specify a 200-ms movement-onset delay for the probe in both movement conditions, and a comparison after arrival. Its apparatus paragraph and procedure also describe matched kinematics. The archived labels and arithmetic do not certify these conditions. They could reflect scheduled variables, different zero points, delayed asynchronous calls, placeholders, or export differences. Without the original assignment sites and an independent physical readout, this audit does not choose among those explanations or infer an actual 0-ms versus 500-ms tactile manipulation.

Similarly, conditional duration medians do not establish unequal physical trajectories: the clocks and start/stop definitions may differ. They do prevent us from treating “matched kinematics” as independently verified by this release. Continuous position and force records would be needed.

## 3. Four distinct event layers

| Layer | Required evidence | What is available |
| --- | --- | --- |
| Intended schedule | Versioned code specifying desired trigger times | Article's protocol description |
| Software event | Assignment site, clock/reset definition and raw log | Named time fields, with unresolved semantics |
| Physical onset | Calibrated vibration/force/displacement threshold and common clock | Not present in the inspected release |
| Consumer intake | Named consumer, source-token and actual capture/read instrumentation | Not present |

No deterministic function of the present log columns can conjure the missing event layers. A software replay that matches them would also not complete the hardware validation.

## 4. Eye-tracker ambiguity

The paper says “Tobii 5 eye tracker (250 Hz)”. [Tobii's official Eye Tracker 5 specification](https://help.tobii.com/hc/en-us/articles/360012483818-Specifications-for-Eye-Tracker-5), updated 29 January 2024, distinguishes 133-Hz image sampling and 33-Hz gaze output. The article does not provide a full device model, serial number, SDK or sampling stream. We therefore record **unresolved model/rate provenance**, rather than declare that the installed device must have been the vendor model on that page or that the experiment necessarily used an incorrect rate.

The released trial files contain no eye-position stream with which to validate fixation windows, update intervals or drift. A new device contract needs the actual identifier, delivered sample timestamps and fixation algorithm. The quoted publication rate alone is insufficient.

## 5. Precise repair needed

An adequate clarification would supply the controller/export source, locale and format string, definitions for each logged field, clock units and origins, timing diagrams, hardware configuration and an independent recording of actual vibrotactile onset. For the research's stronger source-use claim, one must additionally instrument the selected branch and consumer read. The current conclusion remains **evidence insufficient for actual-consumer admission**, while the observable behavioral contrasts retain their bounded support.
