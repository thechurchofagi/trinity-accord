# UCT Paper B v0.57 — Quantitative Shared-Law Model
## One Gate Parameter Linking DIT-like Interaction, RPT-like Recurrence, and GNWT-like Global Access

**Date:** 2026-09-28  
**Status:** CROSS-THEORY TOY-MODEL RESULT / NO THEORY-SPECIFIC REFITTING

## 1. Fixed model

One scalar gate parameter \(g\in[0,1]\) is transformed into:

\[
q(g)=\sigma[10(g-0.5)].
\]

The same \(q(g)\) is used in all three theory-linked observables.

### DIT-like local interaction

\[
d(a,b;g)=\sigma[-2+1.2a+1.2b+3q(g)ab].
\]

\[
\Delta_{AB}(g)=d(1,1)-d(1,0)-d(0,1)+d(0,0).
\]

### RPT-like recurrent core

The two-node loop has one fixed edge \(r=2\) and one gated return edge \(3q(g)\).

\[
\rho(g)=\sqrt{6q(g)}.
\]

The exact \(\rho=1\) threshold is:

\[
g_\rho = 0.339056.
\]

### GNWT-like workspace dynamics

The same gated return edge enters the fixed-point system:

\[
x_1=\sigma(5[-0.5+s+2x_2]),
\]

\[
x_2=\sigma(5[-0.5+3q(g)x_1]).
\]

At baseline:

\[
s=0.3.
\]

Five fixed consumer channels are driven by \(m=(x_1+x_2)/2\):

\[
K_j=\sigma(b_j+7m),
\]

\[
G=\frac{1}{5}\sum_jK_j.
\]

High access is operationally:

\[
G\ge0.8.
\]

No GNWT-specific parameter is fitted after the DIT/RPT model is fixed.

## 2. Main result

As \(g\) increases:

1. \(\Delta_{AB}(g)\) rises smoothly;
2. recurrent gain crosses \(\rho=1\) at \(g\approx 0.339\);
3. global access enters the high-access regime at \(g\approx 0.403\).

The same parameter therefore drives three different organization observables without theory-specific refitting.

## 3. Negative control: same local gate, no return path

The local DIT-like interaction is unchanged, but the gated edge is prevented from returning into the recurrent core.

Then:

\[
\rho(g)=0
\]

for the control topology, and:

\[
G_{\max}=0.039714.
\]

Thus local gating alone does not force recurrent criticality or global broadcast.

## 4. Held-out drive sweep

All model parameters remain fixed while only the content drive \(s\) is changed:

|   content_drive_s |   RPT_rho1_gate_analytic |   GNWT_G0.8_ignition_gate |   max_global_access_G | ignition_observed   |
|------------------:|-------------------------:|--------------------------:|----------------------:|:--------------------|
|           -0.4000 |                   0.3391 |                  nan      |                0.0119 | False               |
|           -0.3000 |                   0.3391 |                    0.5750 |                0.8791 | True                |
|           -0.2000 |                   0.3391 |                    0.4725 |                0.8794 | True                |
|           -0.1000 |                   0.3391 |                    0.4100 |                0.8797 | True                |
|            0.0000 |                   0.3391 |                    0.4025 |                0.8798 | True                |
|            0.1000 |                   0.3391 |                    0.4025 |                0.8799 | True                |
|            0.2000 |                   0.3391 |                    0.4025 |                0.8799 | True                |
|            0.3000 |                   0.3391 |                    0.4025 |                0.8800 | True                |
|            0.4000 |                   0.3391 |                    0.4025 |                0.8800 | True                |

The recurrent structural threshold remains fixed because it depends on the loop architecture.

GNWT-like high access depends additionally on content drive.

At \(s=-0.4\), no high-access state appears over the full gate sweep. At weaker negative drive, ignition appears later. For nonnegative drive it appears near the same high-access gate region.

Therefore:

\[
\boxed{
\text{recurrent gain above threshold is not sufficient for global access without adequate drive.}
}
\]

## 5. Why this is stronger than verbal complementarity

The model supplies:

- one shared dynamical system;
- one shared gate parameter;
- three theory-linked observables;
- one no-return negative control;
- one held-out drive sweep;
- no separate theory-specific re-fitting.

This is genuine shared quantitative-law reuse at the toy-model level.

## 6. Limits

It does not establish biological validity of DIT, empirical truth of RPT or GNWT, human-data fit, or full-theory compression.

Correct status:

\[
\boxed{
\text{cross-theory quantitative proof of concept at model/R3 level.}
}
\]