# Record-Chain Intake

This directory stores server-side intake artifacts from the Record-Chain Intake Gateway on Render.

## Structure

- `submissions/YYYY/MM/<receipt_id>.submission.json` — full submission received from external agents
- `receipts/YYYY/MM/<receipt_id>.receipt.json` — server-generated receipts

## Boundary

- These files are created by the Render service, not by external agents.
- External agents must not write directly to this directory.
- The receipt is not a final chain record; it is an intake acknowledgment.
- Final chain records are appended by the internal `record-chain-append` workflow from `record-chain/pending/`.
