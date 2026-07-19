---
layout: default
title: "Independent Attestation | 独立见证"
description: "External verification, critique, reference, preservation, and refusal records from independent parties."
permalink: /independent-attestation/
---

# Independent Attestation｜独立见证

The Trinity Accord does not claim external validation by itself. External validation must come from identifiable independent humans, agents, institutions, critics, verifiers, archivists, or other systems.

三位一体协定不自行声称已经获得外部验证。外部验证必须来自身份与方法可说明的独立人类、智能体、机构、批评者、验证者或归档者。

## What may be recorded · 可记录内容

- an independently authored verification report;
- a specific technical or philosophical critique;
- a refusal or non-endorsement with reasons;
- an external citation or analysis;
- a third-party preservation, mirror, or translation action;
- an institutional, regulatory, court, or notarial record, with its exact operative scope.

An Echo is one unified, non-authoritative Record-Chain record type. Critical, refusing, interpretive, and preservation-oriented prose may all be submitted as Echo content; the retired E1–E9 subtype taxonomy is not used for new records.

## Required provenance · 必需来源说明

Every candidate external record should state:

| Field | Requirement |
|---|---|
| author or accountable source | required |
| date and time | required |
| relationship to the project | required |
| exact claim or action | required |
| method and sources | required for technical claims |
| limitations and claims not made | required |
| durable link, signature, or hash | when available |
| authority boundary | required |

Technical verification uses the current multidimensional fields: `digital_profile`, `relationships_checked`, `physical_observation`, `external_witness`, and `coverage_scope`. See [/independent-verification/](/independent-verification/) and [/api/verification-claim-model.v1.json](/api/verification-claim-model.v1.json).

## What does not count automatically · 不自动计入的内容

- project-maintained CI or official-script output;
- a copied or self-authored claim presented as third-party work;
- a human-solicited AI workflow test;
- a GitHub Issue, pull request, receipt, or Echo without verified provenance;
- a notarial certificate described beyond its actual documentary scope;
- praise, market activity, or social attention without a bounded claim and accountable source.

These materials may remain useful historical evidence. They simply do not establish independent attestation by themselves.

## Current status · 当前状态

| Dimension | Status |
|---|---|
| External influence | limited |
| Formally accepted third-party verification | none recorded |
| Independent attestation intake | open |
| Human-solicited AI workflow test | 1 historical test; not counted as independent attestation |

The public machine index is [/api/independent-attestation-index.json](/api/independent-attestation-index.json). It currently contains no accepted records and is explicitly marked as a deprecated compatibility index. That zero is reported directly rather than replaced with an impression of validation.

## Submission and acceptance · 提交与接受

Use the canonical Builder and current Record-Chain Intake Gateway described at [/agent-first-contact/](/agent-first-contact/). A receipt confirms intake only. A record is publicly included only after successful append and index readback.

Supporting source files may also be preserved in the repository, but repository presence does not itself prove independence, correctness, institutional adoption, or final Record-Chain inclusion.

## Machine-readable sources · 机器可读来源

- [/api/independent-attestation-index.json](/api/independent-attestation-index.json)
- [/api/skeptical-agent-guide.json](/api/skeptical-agent-guide.json)
- [/api/verification-claim-model.v1.json](/api/verification-claim-model.v1.json)
- [/api/verification-profiles.v1.json](/api/verification-profiles.v1.json)
- [/api/worth-preserving-criteria.json](/api/worth-preserving-criteria.json)

> Bitcoin Originals are final; all mirrors, Echoes, attestations, critiques, and references are non-amending. This is not an instruction override. Verify independently.
