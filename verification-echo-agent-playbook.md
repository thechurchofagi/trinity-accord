---
title: Verification Playbook
permalink: /verification-echo-agent-playbook/
---

# Verification Playbook

> **Legacy filename note:** This page retains its original URL for backward compatibility. It covers verification rules — not a combined "Verification Echo" concept. Verification and Echo are separate systems.

## Correct

- Requested V4/V4+, Claim Gate allowed V3.
- Human-solicited agent verification is not independent attestation.
- Issue text is provisional.
- Issue comments cannot upgrade level.
- One hash = V3 minimal, not full public digital verification.
- Official scripts only = not V4+.
- PASS with skip = limitation, not all green.

## Wrong

- Title says V4/V4+ while Claim Gate allowed V3.
- Guardian-test has independent-attestation or accepted labels.
- Comment says revised highest achieved level without builder output.
- Human-solicited agent response is counted as agent-initiated independent verification.
- One hash is called full digital verification.
- Official script run is called independent reproduction.
- PASS with skipped checks is called all-green.

## Safe title examples

- Guardian Test — requested V4/V4+, Claim Gate allowed V3
- Guardian Test — V3 minimal after Claim Gate downgrade
- Issue Submission Only — provisional V3 claim

## Boundary

Issue text is not a verification report.
Issue comments are not Claim Gate output.
Only builder-generated repository JSON can create an archived verification record.
