# Review and execution changes

This is an unfrozen research checkpoint under result ID `ONLINE-AC-PROBE-20261009`. It is not a replacement for, or modification of, R188 or UCT-MAP-v1.1.2.

## Scoring-name correction

The first executed checker named its alternative objective `last_prefix_only`. Its implemented condition was the second round's **net increment** `state_end_2 XOR state_start_2 == e_0`. It did not compare the final plant state with the initial plant state or require repair of any first-round error.

Root independently read the checker and required the name to match that scoring rule. The objective is now `last_round_increment_only`, and the JSON contract explicitly says it is not terminal-memory or terminal-plant-state recovery. The all-prefix objective and all numerical results are unchanged.

The original draft bytes were overwritten before a separate byte archive was requested; they are **not preserved as files**, and have not been reconstructed. Their actual first-run hashes remain in the tool execution record:

- Initial code: `84008a948e9e503521f24152660a28dfd1a231fc43588a23f3228844c3fa7e8f`.
- Initial results: `768dd904325c09d1e84824601fbb4a58d2495bd259a1442876ab24d3f32ac226`.

The corrected run uses:

- Code: `bc829ade2c93197c86aed4646ae119628b8b4ebe25181f595dd6b7ee605bd304`.
- Results: `7054e1f31175f799c71e3bd6e21430017f90e557bb3659ef731faa4d4b8aa8a7`.

After the successful corrected execution, the same unchanged code was executed once more specifically to preserve its actual stdout, stderr, timestamps, exit status, and byte hashes. See `RUN_RECEIPT.json`, `RERUN_STDOUT.txt`, and `RERUN_STDERR.txt`. The two corrected executions produced identical result hashes. This is one local verifier, not two independently implemented proofs.

## Terminal feedback and physical probe effects

Both actions alter the same persistent plant by XOR. There is no reset between the probe and terminal action or between rounds. Main-branch readers receive the entire probe effect and entire terminal effect, and the known initial state plus those observations determine the actual plant state. The withheld-terminal-feedback branch is separately labelled; the main impossibility and `7/8` value do not depend on withholding that feedback.

The terminal command compensates for the probe's physical effect. On a successful round it must be `probe XOR inverse_wiring(e_0)` and its observed effect is `probe_effect XOR e_0`, already determined by the probe observation and the fixed net-goal contract. This is why complete terminal feedback cannot identify the hidden non-target transposition along the first successful ambiguous history.
