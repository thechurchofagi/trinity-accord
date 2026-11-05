# UCT Paper B v1.0-rc4 — Reproducibility Note

**Date:** 2026-09-28  
**Status:** prepublication release-side audit  
**Scope:** toy-model numerical claims only

## 1. Provenance boundary

The original model-generation script was not found among the preserved Paper B artifacts.

A release-side audit script was reconstructed during the rc3 audit from:

1. the preserved equations in the v0.57 and v0.59 model notes; and
2. the archived CSV output tables.

The reconstruction is **not claimed to be the original generation script**. The rc4 logic/taxonomy repairs do not change the model equations or archived numerical outputs.

## 2. What is actually verified

The preserved specification and release-side reconstruction support the structural claim that each toy model has **one fixed parameterization shared across its theory-linked outputs**.

For Model 1, the recovered five consumer biases are:

`[-5.2, -5.1, -5.0, -4.9, -4.8]`

with consumer gain `7`.

For Model 2, the archived traces are reproduced with:

- `m_0 = 1`, `h_0 = 0`, `w_0 = 0`;
- 39 transitions after the initial state;
- the same five-consumer gain-7 readout.

Across the six core CSV outputs, the release-side reconstruction matches the archived numerical tables within < `1e-9` maximum absolute discrepancy.

## 3. Important historical-provenance limitation

Because the original generation script and full model-development chronology are unavailable, this audit **does not independently certify** the stronger historical claim that no parameter tuning of any kind occurred during original model construction.

Accordingly, rc4 uses the narrower, verifiable wording:

> one fixed parameterization is shared across the theory-linked outputs.

This is a structural property of the preserved/reconstructed model and is distinct from a claim about the historical sequence by which parameters were initially selected.

## 4. Evidence class

The toy models remain:

- formal/conditional shared-law demonstrations: **F3**;
- toy-model/model-organism evidence: **V1**.

They are not:

- V3 held-out human/animal empirical recovery;
- V4 replicated cross-system effective recovery;
- biological validation of DIT, RPT, GNWT, MToC, or HOT;
- empirical proof of UCT-I A1 or A5.