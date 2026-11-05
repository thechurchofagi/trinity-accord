# UCT Paper B v0.59 — Second Quantitative Shared-Law Model
## Memory Retention → Higher-Order Tracking → Global Access

**Date:** 2026-09-28  
**Status:** SECOND INDEPENDENT CROSS-THEORY TOY-MODEL RESULT  
**Theories linked:** MToC → HOT → GNWT  
**No theory-specific refitting across outputs**

---

## 1. Why this model is independent of v0.57

v0.57 linked:

\[
DIT\rightarrow RPT\rightarrow GNWT.
\]

v0.59 uses a different state space and a different shared parameter:

\[
MToC\rightarrow HOT\rightarrow GNWT.
\]

The shared control parameter is the memory-retention factor:

\[
\lambda\in[0,1].
\]

---

## 2. Fixed model

A single content pulse initializes:

\[
m_0=1.
\]

### MToC-like retained content

\[
m_{t+1}=\lambda m_t.
\]

Thus:

\[
R_5(\lambda)=m_5=\lambda^5.
\]

### HOT-like higher-order state

\[
h_{t+1}
=
0.6h_t
+
0.4\,\sigma[12(m_t-0.35)].
\]

This is a primitive higher-order tracking model, not full semantic HOT.

### GNWT-like recurrent workspace

\[
w_{t+1}
=
0.7w_t
+
0.3\,\sigma[10(h_t+1.2w_t-0.8)].
\]

Five fixed consumer channels read \(w_t\), producing global availability:

\[
G_t=\frac15\sum_j K_j.
\]

High access is operationally:

\[
\max_tG_t\ge0.8.
\]

All parameters other than \(\lambda\) remain fixed.

---

## 3. Main result

MToC-like retention grows continuously with \(\lambda\).

A primitive higher-order activation criterion:

\[
\max_t h_t\ge0.5
\]

is first reached at approximately:

\[
\boxed{\lambda_{HOT}\approx 0.403}.
\]

The GNWT-like high-access criterion is first reached at approximately:

\[
\boxed{\lambda_{GNWT}\approx 0.722}.
\]

Thus the same retention parameter yields distinct transitions:

\[
\boxed{
\text{retention}
\rightarrow
\text{higher-order activation}
\rightarrow
\text{global access}.
}
\]

The three quantities are not identical.

---

## 4. Negative controls

### Cut memory → higher-order state

Memory retention remains unchanged, but the \(m\to h\) edge is removed.

Result:

- MToC-like retention remains;
- higher-order activation collapses to baseline;
- GNWT-like high access never appears.

### Cut higher-order state → workspace

Memory and higher-order tracking remain unchanged, but the \(h\to w\) edge is removed.

Result:

- MToC-like retention remains;
- HOT-like activation remains;
- GNWT-like high access disappears.

Control summary:

| Condition         |   max_MToC_retention_t5 |   max_HOT_peak_h |   max_GNWT_peak_G | GNWT_high_access_any   |
|:------------------|------------------------:|-----------------:|------------------:|:-----------------------|
| full model        |                  0.9510 |           0.9978 |            0.8800 | True                   |
| cut memory→HOT    |                  0.9510 |           0.0148 |            0.0068 | False                  |
| cut HOT→workspace |                  0.9510 |           0.9978 |            0.0068 | False                  |

Therefore:

\[
\boxed{
\text{retention alone}
\not\Rightarrow
\text{higher-order organization}
\not\Rightarrow
\text{global availability}.
}
\]

The causal links matter.

---

## 5. Theory-fidelity interpretation

### MToC

The model represents only a retention/temporal-assembly primitive.

It does not reconstruct the stronger MToC claim that the explicit-memory system is responsible for all conscious experiences.

### HOT

The model represents a primitive higher-order state causally tracking retained lower-order content.

It does not solve representational aboutness.

Therefore:

\[
R5_{primitive}\neq R5_{HOT}.
\]

### GNWT

The model represents a recurrent global-access transition into multiple consumer channels.

It does not recover GNWT-specific neural localization or timing claims.

---

## 6. Why this matters

v0.57 and v0.59 now provide two independent shared-law examples:

\[
DIT\rightarrow RPT\rightarrow GNWT
\]

and:

\[
MToC\rightarrow HOT\rightarrow GNWT.
\]

Both contain:

- one fixed model;
- theory-linked observables;
- no separate fitting for each output;
- negative controls;
- separable intermediate stages.

This is stronger evidence for nontrivial formal unification than a translation catalog alone.

---

## 7. Limits

Neither model is an empirical neural fit.

Neither establishes R4 recovery, full-theory compression, biological truth of the target theories, or truth of UCT A1/A5.

Correct status:

\[
\boxed{
\text{second independent cross-theory quantitative proof of concept.}
}
\]