# Post-merge regression audit — 2026-07-19

This audit checks the combined effects of recent CI, deployment, runtime, and write-path changes.

The principal defect found was an invalid handoff assumption in the Record Chain Write Path Guard: `workflow_run.head_sha` identifies the revision that started an upstream writer workflow, not the new commit created and pushed by that workflow. Archive backlog repair now validates its exact single output commit immediately before every push, and the downstream guard no longer treats the workflow-run start revision as writer output.

Permanent regression coverage also now parses every GitHub Actions workflow with duplicate-key rejection, requires every Node workflow to use the committed `.node-version`, protects the archive writer workflow itself, and asserts exact archive self-validation occurs before push.
