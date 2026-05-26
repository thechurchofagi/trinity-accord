import assert from "node:assert";
import fs from "node:fs";

const src = fs.readFileSync("examples/github-app-backend/server.js", "utf8");

assert(src.includes("WORKFLOW_MANUAL"));
assert(src.includes("WORKFLOW_MANUAL_MACHINE"));
assert(src.includes("ARTIFACT_CUSTODY"));
assert(src.includes("workflowIdForPayload"));
assert(src.includes("workflowDocumentForId"));
assert(src.includes("saveForDebuggingList"));
assert(src.includes("payload = null"));
assert(src.includes("workflow_id"));
assert(src.includes("next_document"));
assert(src.includes("workflow_manual"));
assert(src.includes("workflow_manual_machine"));
assert(src.includes("artifact_custody"));
assert(src.includes("save_for_debugging"));
assert(src.includes("https://www.trinityaccord.org/gateway-workflows/"));
assert(src.includes("https://www.trinityaccord.org/api/gateway-workflows.v1.json"));
assert(src.includes("https://www.trinityaccord.org/api/gateway-artifact-custody.v1.json"));
assert(!src.includes("rebuild with scripts/build_agent_declared_archive_payload.py and POST the raw JSON to /gateway/preflight"));

console.log("PASS: test-gateway-error-workflow-context");
