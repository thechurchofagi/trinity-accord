import assert from "node:assert";
import fs from "node:fs";

const src = fs.readFileSync("examples/github-app-backend/server.js", "utf8");

assert(src.includes("RECOVERY_ENTRYPOINT"));
assert(src.includes("https://www.trinityaccord.org/agent-start/"));
assert(src.includes("MACHINE_RECOVERY_INDEX"));
assert(src.includes("https://www.trinityaccord.org/api/agent-start.v1.json"));
assert(src.includes("BUILDER_ROUTE_MAP"));
assert(src.includes("https://www.trinityaccord.org/api/gateway-builder-route-map.v1.json"));
assert(src.includes("recovery_entrypoint"));
assert(src.includes("machine_recovery_index"));
assert(src.includes("route_map"));
assert(src.includes("Do not patch signed JSON"));

console.log("PASS: test-gateway-error-recovery-context");
