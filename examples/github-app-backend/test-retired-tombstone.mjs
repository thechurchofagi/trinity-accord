import { spawnSync } from "node:child_process";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const result = spawnSync(process.execPath, ["server.js", "--self-test"], {
  cwd: here,
  env: { ...process.env, DRY_RUN: "true" },
  encoding: "utf8",
});

const output = `${result.stdout || ""}\n${result.stderr || ""}`;

if (result.status !== 1) {
  console.error(output);
  throw new Error(
    `Expected the retired legacy Gateway self-test to fail closed with exit 1, got ${result.status}`,
  );
}

if (!output.includes("WRONG_PATH_FOR_V0_V5")) {
  console.error(output);
  throw new Error("Expected WRONG_PATH_FOR_V0_V5 fail-closed marker");
}

console.log(
  "SELF TEST PASS: retired legacy Gateway rejects the obsolete V0-V5 submission path",
);
