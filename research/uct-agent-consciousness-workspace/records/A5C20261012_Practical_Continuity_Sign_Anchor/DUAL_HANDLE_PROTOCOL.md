# Dual-handle cross-orbit protocol

Status: physically implementable protocol, not executed and not a phenomenal calibration.

## Apparatus and mappings

Use two independently sampled two-axis handles, left route `r0=(Lx,Ly)` and right route `r1=(Rx,Ry)`, controlling two named one-dimensional cursor targets `t0,t1`. Log raw handles, displayed cursors, perturbation injection and response timing from one clock.

- **Joint orbit:** `y0=(Lx+Rx)/sqrt(2)` and `y1=(Ly+Ry)/sqrt(2)`. Both routes participate in both targets: `Pi_J={(r0,t0),(r1,t0),(r0,t1),(r1,t1)}`.
- **Distributed orbit:** `y0=Lx` and `y1=Ry`, with unused axes disabled and monitored. `Pi_D={(r0,t0),(r1,t1)}`.

The `1/sqrt(2)` gain equalizes squared mapping gain per target. The target traces, display, trial timing, reward rule, neutral task instruction, conceptual-self wording and report interface are identical. The two relations lie in different route-label-swap orbits; the contrast is not a relabeling.

## Perturbation and organizational endpoints

On preregistered trials inject a brief zero-mean displacement or gain pulse into one target-relevant route coordinate after movement onset. The pulse schedule is drawn after the start state is bound and is not announced. Measure:

1. route-specific corrective change in the unperturbed handle coordinate;
2. cursor-error recovery and latency;
3. within-route correction by the perturbed route;
4. targetwise cross-route compensation `C_t` under the A5B definition;
5. raw-port lineage and whether the displayed cursor actually consumed each sampled route.

Use an adaptive pretest, not post-outcome selection, to keep perturbation magnitude inside a range in which both mappings retain high target success. Report the full error distribution; do not condition the main comparison on success. A replay arm can reproduce the displayed cursor while disconnecting live handles, serving as an actuality refuter rather than an experimental condition for phenomenal inference.

## Required organizational checks

- Calibrate and freeze the two mapping matrices before outcome collection.
- Verify actual port consumption by logged mapping code, time-aligned raw input and route-specific perturbation effects; code declaration alone is insufficient.
- Predeclare alternate input paths, assistance, cursor smoothing and experimenter overrides.
- Include route cut and same-port rescue trials to detect a hidden external compensator.
- Treat movement, endpoint success, effort, adaptation and cross-route correction as organizational/behavioral observations, not as `H_pc` truth.

## Phenomenal endpoint firewall

The same phenomenally worded `E_pc` prompt may be presented after a fixed subset of trials, with randomized response-key coding. That fixes report machinery and gives prospective coding failures. It does not establish positive reliability. Nonverbal resumption latency and corrective force are additional fallible channels, not privileged anchors. Accordingly, this protocol can test a cross-orbit `Pi/W/C` contrast but cannot by itself activate the phenomenal bridge.

## Feasibility basis and limits

Published human motor-control experiments have already implemented shared-cursor mappings in which both hands contribute to one displayed cursor, independent-cursor conditions, rapid cursor/target perturbations and hand-specific correction measurements. Those precedents establish apparatus-level feasibility, not the exact A5C two-target mapping, actual installation here, or any UCT phenomenal interpretation.

