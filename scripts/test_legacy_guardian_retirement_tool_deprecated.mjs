#!/usr/bin/env node
/**
 * Test: Legacy guardian retirement payload builder requires explicit legacy-only confirmation.
 */
import { spawnSync } from "node:child_process";

const result = spawnSync("node", ["scripts/build_guardian_retirement_payload.mjs"], {
  encoding: "utf8",
});

if (result.status === 0) {
  console.error("FAIL: legacy retirement builder should require explicit legacy-only confirmation");
  process.exit(1);
}

const output = (result.stderr || result.stdout || "").toLowerCase();
if (!output.includes("legacy")) {
  console.error("FAIL: expected legacy/deprecated message");
  process.exit(1);
}

console.log("PASS: legacy guardian retirement builder is gated");
