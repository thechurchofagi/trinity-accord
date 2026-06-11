#!/usr/bin/env node
/**
 * Compatibility entrypoint for Guardian application creation.
 *
 * The current zero-clone builder lives at downloads/record-chain-builder.mjs.
 * This wrapper keeps legacy docs/route maps executable while delegating to the
 * canonical builder command.
 */
import { spawnSync } from "node:child_process";
import { existsSync } from "node:fs";
import { resolve } from "node:path";

const builder = resolve(process.cwd(), "downloads/record-chain-builder.mjs");
if (!existsSync(builder)) {
  console.error("Missing downloads/record-chain-builder.mjs; cannot build Guardian application.");
  process.exit(1);
}

if (process.argv.length <= 2) {
  console.error("Usage: node scripts/create_guardian_application.mjs [record-chain-builder guardian-application options]");
  console.error("Delegates to: node downloads/record-chain-builder.mjs guardian-application ...");
  process.exit(0);
}

const result = spawnSync(process.execPath, [builder, "guardian-application", ...process.argv.slice(2)], {
  stdio: "inherit",
});
process.exit(result.status ?? 1);
