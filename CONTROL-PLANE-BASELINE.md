---
layout: default
title: "Control Plane Baseline"
permalink: /control-plane-baseline/
---
# Trinity Accord Control-Plane Baseline

Last reviewed: 2026-05-10
Repository: thechurchofagi/trinity-accord

## Branch Protection

main:
- PR required: yes
- Required approvals: 1
- CODEOWNERS review required: yes
- Stale approvals dismissed: yes
- Last push approval required: yes
- Required status checks:
  - `check` (Repository Integrity Check workflow — repository-integrity.yml)
- Branch up to date required: yes
- Force push allowed: no
- Deletion allowed: no
- Admin bypass: disabled (enforce_admins enabled)
- Linear history required: yes
- Conversation resolution required: yes

## Rulesets

Branch rulesets:
- main protected via branch protection (see above)

Tag rulesets:
- Name: "Protect release and evidence tags"
- Target: tag
- Enforcement: active
- Patterns: v*, nft-*, release-*, evidence-*, archive-*, core-object-*, signed-*, ots-*, flaw-*, trinity-accord-*, redteam-*
- Rules: deletion blocked, non-fast-forward blocked
- Bypass actors: none

## Actions Settings

- Default GITHUB_TOKEN: read
- Allowed actions: all (sha_pinning_required: false)
- Note: All workflow files use SHA-pinned actions (enforced by test_action_pinning.py)
- Workflows cannot create/approve PRs: yes (can_approve_pull_request_reviews: false)
- Outside collaborator approval: configured at repo level

## Environments

github-pages:
- source: protected main
- admin bypass: enabled (GitHub default; recommended to disable)
- deployment_branch_policy: custom_branch_policies

release-publish:
- exists: yes
- protected branches only: yes (deployment_branch_policy.protected_branches: true)
- reviewers: none configured (single-owner residual risk)
- admin bypass: GitHub default

## Pages

- Source: main branch, path /
- Build type: legacy (Jekyll)
- HTTPS: enforced
- Custom domain: www.trinityaccord.org / trinityaccord.org
- CNAME tracked in repo: yes (CNAME file)
- HTTPS cert expiry: 2026-07-29

## Security Features

- Dependency graph: enabled
- Dependabot alerts: enabled (2026-05-10)
- Dependabot security updates: enabled (2026-05-10)
- Secret scanning: enabled where available
- Push protection: enabled where available
- Private vulnerability reporting: enabled (2026-05-10)

## Release / Tag Immutability

- Protected tag ruleset: yes (see Rulesets section)
- Release asset replacement policy: corrections-index + public notice
- Corrections/revocation policy: CORRECTION-REVOCATION-POLICY.md
- Release verifier: scripts/verify-release-assets.mjs

## Secrets

- Repository secrets: ETHEREUMMAINNET, ETH_RPC_URL
- Secret scanning: enabled where available
- Push protection: enabled where available

## Maintainer Model

Current model:
- Single primary maintainer: @thechurchofagi
- Residual risk: compromise of the maintainer account can bypass controls that allow admin bypass.
- Mitigations:
  - branch protection includes administrators (enforce_admins: true)
  - rulesets minimize bypass actors (none)
  - release-publish environment with protected branches only
  - protected tags via ruleset
  - no hard-delete/tombstone policy
  - corrections-index

## Review Cadence

- Review monthly or after any GitHub settings change.
- Record changes in this file.
- Run `python3 scripts/audit_control_plane.py` for automated snapshot.

## Recovery Reference

For cold-start recovery after control-plane compromise, see `RECOVERY.md` and `api/recovery-index.json`.
