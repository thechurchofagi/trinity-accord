#!/usr/bin/env node
import { readFileSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const data = JSON.parse(readFileSync(resolve(here, "../api/record-chain-agent-field-guidance.v1.json"), "utf-8"));

function usage() {
  console.log("Usage:");
  console.log("  node downloads/record-chain-agent-submit-guide.mjs list");
  console.log("  node downloads/record-chain-agent-submit-guide.mjs record-type correction");
  console.log("  node downloads/record-chain-agent-submit-guide.mjs field correction_content.target_record_sha256");
  console.log("");
  console.log("If a target id or target record_sha256 is unclear, stop with BUILDER_USAGE_UNCLEAR.");
}

function knownRecordTypes() {
  return Object.keys(data.record_types || {}).sort();
}

function knownFields() {
  return Object.keys(data.fields || {}).sort();
}

function showList() {
  console.log("Record types:");
  for (const key of knownRecordTypes()) {
    console.log("  " + key + " — " + data.record_types[key].purpose);
  }
  console.log("\nFields:");
  for (const key of knownFields()) console.log("  " + key);
}

function showRecordType(name) {
  const key = String(name || "").replace(/-/g, "_");
  const item = data.record_types?.[key];
  if (!item) {
    console.error("Unknown record type: " + name);
    console.error("Known record types: " + knownRecordTypes().join(", "));
    process.exitCode = 1;
    return;
  }
  console.log(key);
  console.log("Purpose: " + item.purpose);
  if (item.builder_command) console.log("Builder command: " + item.builder_command);
  if (Array.isArray(item.required_cli_options)) {
    console.log("\nRequired CLI options:");
    for (const opt of item.required_cli_options) console.log("  " + opt);
  }
  if (Array.isArray(item.before_build)) {
    console.log("\nBefore build:");
    for (const step of item.before_build) console.log("  - " + step);
  }
  if (item.example_cli_fragment) {
    console.log("\nExample CLI fragment:");
    console.log("  " + item.example_cli_fragment);
  }
}

function showField(name) {
  const item = data.fields?.[name];
  if (!item) {
    console.error("Unknown field: " + name);
    console.error("Run list to see known fields.");
    process.exitCode = 1;
    return;
  }
  console.log(name);
  console.log("Meaning: " + item.meaning);
  if (item.how_to_fill) console.log("How to fill: " + item.how_to_fill);
  if (item.source_of_truth) console.log("Source of truth: " + item.source_of_truth);
  if (Array.isArray(item.never_use)) console.log("Never use: " + item.never_use.join(", ") + ".");
  if (item.example) console.log("Example: " + JSON.stringify(item.example));
  if (item.unclear_action) console.log("If unclear: stop with " + item.unclear_action + ".");
}

const args = process.argv.slice(2);
const cmd = args[0];
const value = args[1];

if (!cmd || cmd === "help" || cmd === "--help" || cmd === "-h") usage();
else if (cmd === "list") showList();
else if (cmd === "record-type") showRecordType(value);
else if (cmd === "field") showField(value);
else {
  console.error("Unknown command: " + cmd);
  usage();
  process.exitCode = 1;
}
