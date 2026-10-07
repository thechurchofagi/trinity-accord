# TA25 v1.0 publication and preservation handoff

7 October 2026. User-authorized order: DOI -> OTS -> Arweave.

## Released work

Experience, Intelligence, and Self Within Experience: Definitions, Conditional Theorems, and Thought Experiments for a Structural Account.
Author: Hongju Liu. Report TA-TR-2026-25, version 1.0.
DOI: https://doi.org/10.5281/zenodo.23206492
Record: https://zenodo.org/records/23206492
Publication branch: research/experience-intelligence-self-v1-20261007
Package: research/experience-intelligence-self/
Preservation batch: research/paper-timestamps/2026-10-07-paper25-v10/

The release derives from R151 v0.2 at research commit 09074a05337127f78b3a5c1b57edc9d29543df34. All ten scientific sections and references are byte-identical; only front matter, keywords, license and availability were updated. The formal map remains R149-v1.0. Self-related feeling and the conceptual I remain within experience; no owner or self-model is introduced as a basal gate.

## Review and exact identity

- General T1-T3 arguments reviewed within their explicitly stated scopes.
- R151 verifier rerun: 128 compatibility assignments, 2,368 rewiring state-command rows, nine pinned source hashes passed.
- All 14 final PDF pages visually reviewed. No observed clipping, overlapping content or missing symbols.
- Publication guard tests: 8 passed.
- PDF: experience-intelligence-self-v1.0.pdf
- PDF bytes: 112138
- PDF SHA-256: b4f456014213c5d4f34f41ed2bac8873fd9d90e38398d77daebdb787872b1c1a
- Exact remote publication manifest SHA-256: 590ece65f2c9875942b3c07aef3f7243322bf06da9c8adfc5fae0032ddbca52a
- First publication attempt was stopped before the remote publication call by a review-manifest mismatch caused by an extra local newline. The authorization hash was corrected against exact remote bytes. Paper and prepared assets were never rebuilt or changed.
- Successful DOI publication + initial OTS run: https://github.com/thechurchofagi/trinity-accord/actions/runs/37589701487
- First proof upgrade/preservation run: https://github.com/thechurchofagi/trinity-accord/actions/runs/37589880029

## State at handoff

DOI is published. Nine public assets passed anonymous SHA-256 readback. Separate doi-resolution.json records RESOLVER_PASS, HTTP 200 and the correct Zenodo record. The original publication receipt reports resolver pending because it predates that later resolution check; use both evidence files.

OTS is submitted, four pending calendar attestations. Bitcoin heights are empty; no Bitcoin-verification claim.
Current detached proof SHA-256: 945af06d9682f6a42dff3540685f15e5e679ec8d9e6030548ea2184e0af1c77e. This hash can change when upgraded; retain the original .submitted proof.
Arweave has not been uploaded and no transaction is claimed.

## Authorized continuation

Hourly task “TA25 存证闭环” was created successfully and enabled. Operational ID: 6ac5f9fd822481919611d94d3c477c8d. It is a continuation task for the already authorized preservation, not a new research schedule.

If not completed, inspect the current batch status, any paid-intent/receipt and workflow runs. Do not start a second concurrent run. Trigger the existing .github/workflows/research-paper-25-v10-ots-arweave.yml by incrementing iteration in research/experience-intelligence-self/PRESERVE-REQUEST.json with a normal fast-forward commit message containing [ta25-preserve]. This workflow lives on the publication branch and is push-triggered, not a default-branch cron. The hourly task supplies subsequent triggers.

The existing repository lifecycle script upgrades the OTS proof and verifies Bitcoin cryptography against agreeing Blockstream/mempool headers. This is not local full-node consensus verification. Arweave remains blocked until the exact PDF proof has BITCOIN_VERIFIED_REMOTE_HEADERS. Keep cumulative edition fees strictly below 0.1 AR, the 0.25 AR wallet reserve, rolling-spend ceilings, paid-intent checkpoints and duplicate-post protection. Reuse a paid transaction for readback; do not repay because a gateway is slow. Completion requires ARWEAVE_READBACK_PASS with an anonymously read-back matching payload hash. On completion notify the author, update this handoff with proof/height/transaction/cost evidence and disable the hourly task.

Do not create another DOI, mutate the published PDF or re-run publication to perform preservation. Do not describe the preprint as peer reviewed, C1 as independently validated, or the full research map as globally semantically verified.

## Current research purpose

Read RESEARCH_MASTER_GUIDE.md first on subsequent theory turns. The goal is original, reliable, reusable foundational work for future human and AI inquiry. Publication does not close the selected self-feeling interpretation problem and does not redirect the research toward a unique external owner.
