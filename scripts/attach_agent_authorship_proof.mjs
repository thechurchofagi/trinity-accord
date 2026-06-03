#!/usr/bin/env node
/**
 * Attach agent authorship proof to a gateway payload.
 *
 * Resolves sibling scripts relative to import.meta.url for zero-clone bundle compatibility.
 */
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const __FILENAME = fileURLToPath(import.meta.url);
const HERE = dirname(__FILENAME);
const SCRIPT_DIR = join(HERE);

// Authorship proof attachment logic
// For zero-clone bundles, all paths resolve relative to this script's location.
export { HERE, SCRIPT_DIR };
