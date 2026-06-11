#!/usr/bin/env node
/** Compatibility entrypoint for Guardian retirement bundle metadata. */
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";
const here = dirname(fileURLToPath(import.meta.url));
const target = resolve(here, "build_guardian_retirement_payload.mjs");
const result = spawnSync(process.execPath, [target, ...process.argv.slice(2)], { stdio: "inherit" });
process.exit(result.status ?? 1);
