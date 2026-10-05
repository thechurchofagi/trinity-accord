# Workspace migration log

## 2026-10-05 — GitHub becomes the primary research archive

User authorization: after repeated Library saving failures, create a GitHub directory for research files and record that future research should be stored on GitHub.

Resolved destination: existing repository `thechurchofagi/trinity-accord`, dedicated branch `uct-agent-consciousness-workspace`, directory `research/uct-agent-consciousness-workspace/`. The connected account has push access. The repository is public; the ordinary discussion explicitly noted this. `research/AGENTS.md` was read; English manuscript and published-edition preservation requirements remain in force. No DOI, release, timestamp or archive publication is part of this operation.

Preserve the available R71–R76 artifacts and manuscript v0.1/v0.2/v0.3 bytes, with a SHA-256 migration manifest. Preserve the exact R76 recovery ZIP as an additional recovery artifact. Its nested history includes earlier recovery packages; the current flat records are the convenient continuation entry points. Do not treat an old ZIP's embedded handoff as newer than the current top-level handoff.

The locally edited old master is explicitly marked uncommitted/historical. The new `MASTER_INDEX.md` and `HANDOFF.md` establish current continuity without falsely claiming that the failed Library uploads succeeded. Earlier-round complete migration is not claimed.

Future workflow: fetch branch; read handoff and index; perform substantive work; save manuscript/code/results/failures/source scope; update index and handoff; commit; verify remote branch and file identities; then report. Concurrent updates must be reconciled without force-pushing. A failed commit is logged and reported as a failure rather than a successful save.

This storage migration does not count as R77 or as a scientific result. The latest completed scientific work remains R76. The existing recurring research task should read this GitHub entry point first; its research scope and schedule remain unchanged.

### Completion evidence

Initial migration commit: `39beffa5ee14248bb0b94f71dface1074b919c40`. The remote research branch was created successfully. All 62 committed file blob identities matched the local staged bytes; the original-artifact SHA-256 manifest is retained separately. See `MIGRATION_VERIFICATION.json` for the checked commit and tree.

The existing recurring UCT research task was updated successfully to read the latest GitHub handoff/index first and commit future outputs here. Its schedule, enabled state, and scientific constraints were preserved. No additional task was created. Historical Library failure receipts remain unchanged; current GitHub persistence resolves the available recent-artifact recovery gap.

## 2026-10-05 — No CI for routine research storage

The user clarified that saving academic research in this separate directory should not require CI. The research branch had zero Actions runs at inspection. Targeted workflow inspection showed Repository Integrity pushes limited to main and Research Index checks triggered by pull requests. No new CI was installed for the workspace.

Decision: direct storage-only branch commits carry `[skip ci]`; no storage PR, workflow dispatch, site build, deployment, or repetitive validation. Add the rule to the handoff, README, and workspace instructions, and to the existing research task. Existing repository workflow files and main remain unchanged. Confirm only the remote save; scientific validation remains independent. GitHub documents that the marker skips push/pull_request workflows, not all event types: https://docs.github.com/en/actions/how-tos/manage-workflow-runs/skip-workflow-runs .
