# R92 post-result diagnostic declaration

The frozen 32-run experiment has completed. Some two-state readout-only runs failed, despite initial/final local rank two. To avoid incorrectly treating finite-optimization failure as a representational impossibility, now compute the ordinary least-squares decoder from the TRAINING inputs and archived frozen hidden responses for all eight two-state readout-only runs, including successes. Evaluate this secondary decoder on the unchanged held-out grid and Jacobian contexts. Do not change or replace any frozen-run outcome, weight file, seed, stopping point or success count.

This is an explicitly post hoc diagnostic fit, not part of the preregistered Adam comparison and not additional evidence selected only from successful examples. Use it only to distinguish optimization/conditioning from limitations of an installed linear decoder on the fixed nonlinear representation. No test examples enter the fit. No further training is planned in this round.
