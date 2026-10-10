# CTD TA26: fixed-publication preservation continuation

This is an operational waiting checkpoint, not a completed OTS/Arweave receipt. The published science is frozen. Read the latest remote branches and this case's later records before acting.

## Actual state observed on 2026-10-10

- DOI `10.5281/zenodo.23279189` is public. Its nine exact assets and independent DOI resolution have passed readback. Scientific storage commit `fda7a0ae491c4bf3a7c9bc80ccab38acb3984299` and initial operational checkpoint `891433b6e91f564feeccc9f3c55cf117f2c2a3fe` were independently fetched and byte-verified.
- Release branch `research/ctd-noise-identifiability-v100-20261010` was still at `df37353d5153e981caae4017cae1fc12677e085d` in the fresh check. Batch `research/paper-timestamps/2026-10-10-paper26-v100/status.json` has top-level `WAITING`; its one PDF has `PENDING_BITCOIN`. Its Bitcoin heights array is empty and four calendar attestations remain pending.
- The initial proof is 770 bytes, SHA256 `a407ef8f904c9bb67d49d3017d8acecebfe8a7e2c082a31dfe3a35f57cc762c7`. The public PDF remains 269961 bytes, SHA256 `479b4f2403ad7416f99f7676533fd4a8b9efed1bb289c7fcd52f64a09bf81c94`.
- The second bounded read-only calendar watch ended at 10:53:58 UTC after ten queries. Alice reported Bitcoin transaction `ea9ac90f9c9a850808a0d2c8d9c3d2200634491668cc2d999547439b21f2dbbe`; Bob later reported `a64e09e857d0b488ebb3aaa06d38e737ff02d0fd063cd19416e3367a7fd8ca3d`. Both said they were waiting for six confirmations. These statements are calendar-reported context, not embedded Bitcoin attestations.
- Independent read-only transaction-status requests to Blockstream and mempool at 10:50:38 UTC agreed that the Alice transaction was confirmed at height 970752, hash `00000000000000000002060f5d031a8e26e1f4504f8a50be0fd44e2cf7511214`. This transaction lookup does not cryptographically connect the PDF to that block. An earlier tip-height lookup returned HTTP 404 for the block-height resource; that failure is retained, not rewritten as success.
- Latest observed main workflow run `38044262845`, attempt 1, completed a successful waiting iteration. There were no later matching runs in the fresh inventory. The batch directory had no paid intent, AR receipt, or AR bundle. No Arweave payment or upload had occurred for this batch at that observation.
- The separate conditional task “TA26 存证收尾” was actually created and enabled. Its receipt and exact prompt are stored beside this file. It continues the already-authorized fixed-version operation and disables itself after verified completion. Normal waiting is not grounds for repeated user notifications or changing unrelated research tasks.

## Durable recovery inputs

Paths below are relative to this case directory, `research/uct-agent-consciousness-workspace/records/CTD20261010_Noise_Identifiability_v10/`.

1. `release/` contains the exact nine public assets. `publication-record.json`, `DOI_RESOLUTION.json`, and `operations/verification/` contain publication, remote-readback and review evidence. Preserve these bytes and the original 201-member scientific archive.
2. `operations/initial_ots/` preserves the first real batch and its exact Git readback. The latest actual release branch, rather than this initial copy, supplies a future completed batch.
3. `operations/second_calendar_watch/` preserves all second-watch copies/logs, the unannotated terminal receipt, and the final annotated receipt. `operations/chain_context/` preserves the distinct root transaction/header observations, including the failure.
4. `operations/verification/tools/verify_public_preservation.py` is statically reviewed but has NOT been run against an AR transaction. Its review is `operations/verification/VERIFY_PUBLIC_PRESERVATION_REVIEW.md`. It requires a real final batch and exact public PDF before one anonymous HTTPS GET.
5. `operations/verification/tools/build_completion_bundle.py` is the separately reviewed completed-chain packager. It has NOT been run with completed inputs. `operations/prepared/COMPLETION_REPORT_DRAFT_ZH.md` retains three explicit completion placeholders; do not deliver it as a completed preservation report.
6. `operations/CONTINUATION_TASK_PROMPT.txt` specifies the already-authorized action and stop conditions. `operations/CONTINUATION_AUTOMATION_CREATED.json` records actual creation. `operations/CONTINUATION_SOURCE_IDENTITIES.json` binds the copied files to their source bytes.

## Completing the existing pipeline

Read current batch and workflow state before any rerun. Keep the main-only event guard, DOI gate, independent header checks, fixed target identity, strict cumulative edition budget, reserve/rolling limits, durable paid-intent checkpoint and duplicate-post recovery logic. With a known transaction recover its readback; with an uncertain prior payment recover the retained artifact/receipt before any paid retry. Do not lower confirmation or acceptance criteria to accelerate the wait.

After actual `ARWEAVE_READBACK_PASS`, fetch the final batch at its exact committed SHA, retain the original files, and execute the independent reader with a NEW receipt path:

```sh
python3 operations/verification/tools/verify_public_preservation.py --preservation /absolute/final-batch --public-pdf release/noise-identifiability-bodily-judgments-v1.0.0.pdf --out /absolute/ROOT_ARWEAVE_READBACK.json
```

Require the downloaded payload bytes and every embedded member to match, including the published PDF and verified proof. The script inherits Bitcoin verification from the exact workflow receipt; it does not claim a new local full-node verification. Record real transaction/reward/readback facts, never placeholders.

Create `FINAL_CHAIN_RECEIPT.json` with state `DOI_OTS_ARWEAVE_PUBLIC_READBACK_COMPLETE`, the DOI, exactly nine `public_assets` entries (`name`, `bytes`, `sha256`), and the successful independent `root_arweave_readback`. Stage the nine exact assets under `public/`, relevant operation receipts under `verification/`, and clear verification instructions. Fill the Chinese report with real completion facts. Pass these and the real final batch to `build_completion_bundle.py`. The final delivery ZIP is a separate artifact; the AR payload covers the PDF and its OTS evidence, not all nine DOI assets.

Save the complete deliverable using the Library skill and update the same master handoff identity `libfile_4175a81748fc819187fa8f5771f056fa` with the latest expected version, retaining all old content. Commit case-specific completion evidence with `[skip ci]` and expected-SHA safeguards; independently verify remote bytes. Keep concurrent research priorities, graph status, historical failures and early waiting receipts intact. Only then report the full completed chain and stop this one conditional task.
