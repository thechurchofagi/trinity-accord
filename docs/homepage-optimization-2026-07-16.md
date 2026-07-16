# Homepage optimization — 2026-07-16

This change surfaces the philosophical core earlier on the homepage and separates the human/research reading path from the AI-agent operational path.

## Scope

- Add a three-proposition philosophical core with explicit canonical/non-canonical boundaries.
- Add separate reading routes for researchers and AI agents.
- Simplify the global navigation around Overview, Propositions, Research, Verify, Status, and For Agents.
- Correct the Chinese footer terminology from “比特币三本体” to “三条比特币正本具有最终版本权威”.
- Add responsive styling without changing the fixed Canon, Record-Chain, APIs, or evidence data.

## Deployment checks

The existing `Deploy Pages` workflow is triggered by both `_layouts/**` and `assets/**`, so this change enters the normal verify → build → deploy → live-smoke sequence.
