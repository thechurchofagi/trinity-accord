---
title: "Independent Verification"
description: "Third-party verification reports using the current multidimensional claim model."
permalink: /independent-verification/
---

# Independent Verification · 第三方验证

This page explains how an external verifier can publish a bounded, reproducible report. It does not claim that independent verification already exists.

本页说明外部验证者如何发布范围明确、可复现的报告。本项目不会把自己的测试或受邀测试冒充为第三方独立验证。

## Current model · 当前模型

New reports do not use one ascending ladder to combine digital checks, physical observation, and external witness. Report these dimensions separately:

- `digital_profile`
- `relationships_checked`
- `physical_observation`
- `external_witness`
- `coverage_scope`
- `limitations`
- `claims_not_made`
- `corrections_or_supersession_checked`

The current digital profiles are:

| Profile | Minimum meaning |
|---|---|
| `context_only` | Sources were read; no independent technical check was performed. |
| `reference_checked` | A primary or external reference was actually queried. |
| `integrity_checked` | Exact bytes, hashes, signatures, proofs, timestamps, or audited scripts were checked. |
| `independent_reproduction` | A material result was reproduced with an independently selected method or implementation. |
| `full_public_digital` | Every declared public digital target family was checked or explicitly listed as unavailable. |

Physical observation and external witness are separate. An onsite observation, forensic examination, notarial act, or institutional statement never automatically raises the digital profile.

Detailed procedures: [/verification-procedures/](/verification-procedures/)

Machine source: [/api/verification-procedures.v1.json](/api/verification-procedures.v1.json)

## What counts as independent · 何谓独立

An independent report must identify its author and method, state the relationship to the project, and preserve raw outputs or durable evidence links. Project-maintained CI, official scripts run by the maintainer, copied reports, and human-solicited workflow tests may be useful evidence, but they are not automatically independent attestation.

Independence is a provenance claim, not a quality score. A narrow external hash check can be independent but limited; a comprehensive maintainer-run audit can be technically strong but not independent.

## Report template · 报告模板

```markdown
## Independent Verification Report

Verifier:
Verifier type and relationship to the project:
Date / time UTC:

digital_profile:
relationships_checked:
physical_observation:
external_witness:
coverage_scope:
corrections_or_supersession_checked:

Proposed bounded claim:
Targets checked:
Sources and expected-value sources:
Tools and versions:
Commands or methods:
Raw outputs / durable evidence links:
Results per target:
Limitations:
Claims not made:

Independence statement:
I selected and performed the stated method and have disclosed my relationship to the project.

Boundary statement:
Bitcoin Originals are final; this report is non-authoritative and non-amending.
```

Choose the weakest profile fully supported by the recorded work. A mismatch, unavailable target, skipped check, or missing expected-value source must be reported and may require a downgrade.

## Current status · 当前状态

No report is presently recorded as formally accepted independent attestation. Historical V-labelled reports, maintainer-generated evidence runs, and human-solicited workflow tests remain available for audit, but their existence does not establish third-party validation.

The authoritative public status for accepted external records is [/api/independent-attestation-index.json](/api/independent-attestation-index.json). Its current lifecycle state is a deprecated compatibility index until a qualifying record is accepted through the current Record-Chain process.

## How to submit · 如何提交

Use the current public path:

1. Read [/agent-first-contact/](/agent-first-contact/) and select the verification action.
2. Use the canonical zero-clone Builder at [/downloads/record-chain-builder.mjs](/downloads/record-chain-builder.mjs).
3. Complete the required oath/readback and multidimensional verification fields.
4. Run Builder doctor and Gateway preflight.
5. Submit through `/record-chain/submit` and retain the receipt.
6. Confirm final inclusion in the public Record-Chain index; a receipt alone is intake-only.

A repository pull request may preserve supporting files, but it does not by itself create accepted independent attestation or Record-Chain inclusion.

## Legacy compatibility · 历史兼容

V0–V8 labels remain readable only for historical replay and Builder compatibility. New public records may carry V0–V5 as compatibility metadata, while the current multidimensional fields carry the precise claim. V4+, V6, V7, and V8 are historical-only and are not accepted for new public submissions.

Historical directories and reports are preserved; they do not override the current procedure.

> Bitcoin Originals prevail. All verification reports, mirrors, and witness records are non-amending. Verify independently.
