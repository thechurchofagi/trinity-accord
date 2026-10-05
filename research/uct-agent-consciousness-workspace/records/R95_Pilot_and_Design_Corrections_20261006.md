# R95 pilot and design corrections

Date: 2026-10-06. These are retained because the final formal design was informed by them.

## Pilot 1 — random nonzero Q input path

Initial random E_Q made Q linearly decodable at the final hidden state before learning in all tested seeds. That cannot test acquisition. Rejected as the formal design.

Correction: set E_Q=0 exactly in both paired environments while leaving it trainable.

## Pilot 2 — XOR control target

An early A target used a redundant nonlinear W*G/XOR-like fourth output while B used direct Q. With the chosen tiny recurrent model, A ended at 87.5% accuracy in every tested seed while B reached 100%. This confounded the intended Q-relevance comparison with output-function optimization difficulty. Rejected.

Correction: use four balanced simple outputs. A=(W,G,O,W), B=(W,G,O,Q). This deliberately replaces a redundant W output by an independent Q output; predictive cardinality differs by one bit, which is the manipulation.

## Pilot 3 — seeds 0..7

The corrected zero-Q-path design was checked on seeds 0..7 to ensure it was numerically runnable. These seeds were not used as the formal confirmation set.

Correction: freeze seeds 100..107 for the formal run, with no replacement or extension.

No pilot result is counted as independent confirmation. All pilots used only the same tiny synthetic state grid, no model API or external system.
