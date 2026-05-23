import assert from "node:assert";
import fs from "node:fs";

const src = fs.readFileSync("examples/github-app-backend/server.js", "utf8");

// Workflow constants
assert(src.includes("WORKFLOW_MANUAL"));
assert(src.includes("https://www.trinityaccord.org/gateway-workflows/"));
assert(src.includes("WORKFLOW_MANUAL_MACHINE"));
assert(src.includes("https://www.trinityaccord.org/api/gateway-workflows.v1.json"));
assert(src.includes("ARTIFACT_CUSTODY"));
assert(src.includes("https://www.trinityaccord.org/api/gateway-artifact-custody.v1.json"));

// Recovery context constants still present
assert(src.includes("RECOVERY_ENTRYPOINT"));
assert(src.includes("https://www.trinityaccord.org/agent-start/"));
assert(src.includes("MACHINE_RECOVERY_INDEX"));
assert(src.includes("https://www.trinityaccord.org/api/agent-start.v1.json"));
assert(src.includes("BUILDER_ROUTE_MAP"));
assert(src.includes("https://www.trinityaccord.org/api/gateway-builder-route-map.v1.json"));

// Workflow context in recovery context function
assert(src.includes("workflow_manual"));
assert(src.includes("workflow_manual_machine"));
assert(src.includes("artifact_custody"));

// Error responses include workflow context
assert(src.includes("recovery_entrypoint"));
assert(src.includes("machine_recovery_index"));
assert(src.includes("route_map"));

// Recovery rule present
assert(src.includes("Do not patch signed JSON"));

console.log("PASS: test-gateway-error-workflow-context");
