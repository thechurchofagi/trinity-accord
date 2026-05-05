#!/usr/bin/env node
/**
 * verify-signed-manifest-coverage.mjs
 *
 * This is the new V3+ signed-manifest hard gate.
 *
 * It verifies:
 *   1. Existing BTC BIP340 signature coverage script passes.
 *   2. Legacy ETH witness for the BTC BIP340 signature package passes.
 *   3. digest-manifest.json/csv are declared in authority.jcs.json and match.
 *   4. Target files/hashes are present in the signed authority/digest coverage chain.
 *
 * Output:
 *   SIGNED-MANIFEST-COVERAGE-AUDIT.json
 *
 * Usage:
 *   node scripts/verify-signed-manifest-coverage.mjs
 *   node scripts/verify-signed-manifest-coverage.mjs --target-manifest audit/v3plus-targets.json
 */

import fs from "fs";
import path from "path";
import crypto from "crypto";
import { execFileSync } from "child_process";

const ROOT = process.cwd();
const AUTHORITY_PATH = path.join(ROOT, "archive/authority-manifest/authority.jcs.json");
const DIGEST_JSON_PATH = path.join(ROOT, "archive/evidence/digest-manifest.json");
const DIGEST_CSV_PATH = path.join(ROOT, "archive/evidence/digest-manifest.csv");
const OUT_PATH = path.join(ROOT, "SIGNED-MANIFEST-COVERAGE-AUDIT.json");

function argValue(name) {
  const idx = process.argv.indexOf(name);
  return idx >= 0 ? process.argv[idx + 1] : null;
}

const TARGET_MANIFEST = argValue("--target-manifest");

function sha256hex(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

function readJson(p) {
  return JSON.parse(fs.readFileSync(p, "utf8"));
}

function isHexHash(s) {
  return typeof s === "string" && /^[a-f0-9]{64}$|^[a-f0-9]{128}$/i.test(s.trim());
}

function normalizeHash(s) {
  return String(s || "").trim().toLowerCase().replace(/^0x/, "");
}

function addIndex(index, hash, source) {
  const h = normalizeHash(hash);
  if (!isHexHash(h)) return;
  if (!index[h]) index[h] = [];
  index[h].push(source);
}

function parseCsv(text) {
  const rows = [];
  let row = [], cell = "", inQuotes = false;
  for (let i = 0; i < text.length; i++) {
    const ch = text[i];
    const next = text[i + 1];

    if (inQuotes) {
      if (ch === '"' && next === '"') {
        cell += '"';
        i++;
      } else if (ch === '"') {
        inQuotes = false;
      } else {
        cell += ch;
      }
      continue;
    }

    if (ch === '"') {
      inQuotes = true;
    } else if (ch === ",") {
      row.push(cell);
      cell = "";
    } else if (ch === "\n") {
      row.push(cell);
      rows.push(row);
      row = [];
      cell = "";
    } else if (ch === "\r") {
      // ignore
    } else {
      cell += ch;
    }
  }
  if (cell.length || row.length) {
    row.push(cell);
    rows.push(row);
  }
  if (!rows.length) return [];
  const headers = rows[0].map(h => String(h).trim());
  return rows.slice(1).filter(r => r.length > 1).map(r => {
    const obj = {};
    headers.forEach((h, i) => obj[h] = r[i]);
    return obj;
  });
}

function addRecordHashes(index, record, sourcePrefix) {
  const hashKeys = [
    "sha256",
    "sha3_256",
    "blake2b_256",
    "shake256_256",
    "sha512_256",
    "blake3_256",
    "ar_sha256",
    "input_sha256",
    "expected_sha256"
  ];
  for (const k of hashKeys) {
    if (record && record[k]) addIndex(index, record[k], {...sourcePrefix, field: k});
  }
}

function normalizeDigestItems(raw) {
  if (Array.isArray(raw)) return raw;
  if (Array.isArray(raw.items)) return raw.items;
  if (Array.isArray(raw.files)) return raw.files;
  if (raw.manifest && Array.isArray(raw.manifest)) return raw.manifest;
  return [];
}

function loadTargets() {
  if (!TARGET_MANIFEST) {
    return {path: null, targets: []};
  }
  const obj = readJson(path.resolve(TARGET_MANIFEST));
  const targets = Array.isArray(obj) ? obj : (obj.targets || []);
  return {path: TARGET_MANIFEST, targets};
}

function computeTargetSha(target) {
  if (target.sha256) return normalizeHash(target.sha256);
  if (!target.path) return "";
  const p = path.resolve(ROOT, target.path);
  if (!fs.existsSync(p)) {
    if (target.required !== false) throw new Error(`target missing: ${target.path}`);
    return "";
  }
  return sha256hex(fs.readFileSync(p));
}

function runExistingScript(scriptPath) {
  execFileSync("node", [scriptPath], {
    cwd: ROOT,
    stdio: "inherit",
    env: process.env
  });
}

function mustPassAudit(filePath, fieldName) {
  const audit = readJson(path.join(ROOT, filePath));
  if (audit[fieldName] !== true) throw new Error(`${filePath} ${fieldName} is not true`);
  return audit;
}

async function main() {
  const audit = {
    schema: "trinityaccord.signed-manifest-coverage-audit.v1",
    generated_at: new Date().toISOString(),
    signed_manifest_coverage_pass: false,
    btc_bip340_signature_verified: false,
    legacy_eth_witness_verified: false,
    authority_path: "archive/authority-manifest/authority.jcs.json",
    digest_manifest_json_declared: false,
    digest_manifest_csv_declared: false,
    digest_manifest_json_hash_match: false,
    digest_manifest_csv_hash_match: false,
    coverage_hashes_total: 0,
    target_manifest: TARGET_MANIFEST || null,
    targets_total: 0,
    targets_covered: 0,
    targets_failed: 0,
    nft_or_flaw_targets_total: 0,
    nft_or_flaw_targets_failed: 0,
    target_results: [],
    coverage_index_sample: {},
    errors: []
  };

  try {
    if (!fs.existsSync(AUTHORITY_PATH)) throw new Error("authority.jcs.json missing");
    if (!fs.existsSync(DIGEST_JSON_PATH)) throw new Error("digest-manifest.json missing");
    if (!fs.existsSync(DIGEST_CSV_PATH)) throw new Error("digest-manifest.csv missing");

    runExistingScript("scripts/verify-btc-signature-coverage.mjs");
    const btcAudit = mustPassAudit("BTC-SIGNATURE-COVERAGE-AUDIT.json", "btc_signature_coverage_pass");
    audit.btc_bip340_signature_verified = true;

    runExistingScript("scripts/verify-legacy-eth-witness.mjs");
    mustPassAudit("LEGACY-ETH-WITNESS-AUDIT.json", "legacy_eth_witness_pass");
    audit.legacy_eth_witness_verified = true;

    const authorityRaw = fs.readFileSync(AUTHORITY_PATH);
    const authority = JSON.parse(authorityRaw.toString("utf8"));
    const docs = authority?.arweave?.documents || [];
    const jsonDoc = docs.find(d => String(d.label || "").toLowerCase() === "digest-manifest.json");
    const csvDoc = docs.find(d => String(d.label || "").toLowerCase() === "digest-manifest.csv");

    audit.digest_manifest_json_declared = Boolean(jsonDoc?.ar_sha256);
    audit.digest_manifest_csv_declared = Boolean(csvDoc?.ar_sha256);

    const digestJsonRaw = fs.readFileSync(DIGEST_JSON_PATH);
    const digestCsvRaw = fs.readFileSync(DIGEST_CSV_PATH);
    audit.digest_manifest_json_hash_match = jsonDoc && normalizeHash(jsonDoc.ar_sha256) === sha256hex(digestJsonRaw);
    audit.digest_manifest_csv_hash_match = csvDoc && normalizeHash(csvDoc.ar_sha256) === sha256hex(digestCsvRaw);

    if (!audit.digest_manifest_json_hash_match) throw new Error("digest-manifest.json not matched to authority.jcs.json");
    if (!audit.digest_manifest_csv_hash_match) throw new Error("digest-manifest.csv not matched to authority.jcs.json");

    const index = {};

    for (const doc of docs) {
      addRecordHashes(index, doc, {
        source: "authority.jcs.json",
        class: "authority_arweave_document",
        label: doc.label || "",
        txid: doc.txid || ""
      });
    }

    const digestJson = JSON.parse(digestJsonRaw.toString("utf8"));
    for (const [i, item] of normalizeDigestItems(digestJson).entries()) {
      addRecordHashes(index, item, {
        source: "digest-manifest.json",
        class: "digest_manifest_json",
        index: i,
        path: item.path || item.file || item.filename || item.name || ""
      });
    }

    const csvRows = parseCsv(digestCsvRaw.toString("utf8"));
    for (const [i, row] of csvRows.entries()) {
      addRecordHashes(index, row, {
        source: "digest-manifest.csv",
        class: "digest_manifest_csv",
        index: i,
        path: row.path || row.file || row.filename || row.name || ""
      });
    }

    audit.coverage_hashes_total = Object.keys(index).length;
    audit.coverage_index_sample = Object.fromEntries(Object.entries(index).slice(0, 20));

    const targetObj = loadTargets();
    audit.target_manifest = targetObj.path;
    audit.targets_total = targetObj.targets.length;

    for (const target of targetObj.targets) {
      const category = String(target.category || "general").toLowerCase();
      const isNftOrFlaw = ["nft", "chronicle", "flaw", "covenant", "physical_anchor", "core_object_alpha"].some(x => category.includes(x));
      if (isNftOrFlaw) audit.nft_or_flaw_targets_total++;

      const result = {
        id: target.id || target.path || target.sha256 || "target",
        path: target.path || null,
        category,
        required: target.required !== false,
        sha256: null,
        covered_by_signed_manifest_chain: false,
        coverage_sources: [],
        pass: false,
        error: null
      };

      try {
        result.sha256 = computeTargetSha(target);
        if (!result.sha256) {
          if (result.required) throw new Error("target has no sha256 and no readable path");
          result.pass = true;
        } else {
          result.coverage_sources = index[result.sha256] || [];
          result.covered_by_signed_manifest_chain = result.coverage_sources.length > 0;
          result.pass = result.covered_by_signed_manifest_chain || (!result.required && !isNftOrFlaw);
        }

        if (isNftOrFlaw && !result.covered_by_signed_manifest_chain) {
          result.pass = false;
          throw new Error("NFT / Flaw target hash is not in signed manifest coverage chain");
        }
      } catch (e) {
        result.error = String(e.message || e);
      }

      if (result.pass) audit.targets_covered++;
      else {
        audit.targets_failed++;
        if (isNftOrFlaw) audit.nft_or_flaw_targets_failed++;
      }
      audit.target_results.push(result);
    }

    audit.signed_manifest_coverage_pass =
      audit.btc_bip340_signature_verified &&
      audit.legacy_eth_witness_verified &&
      audit.digest_manifest_json_hash_match &&
      audit.digest_manifest_csv_hash_match &&
      audit.targets_failed === 0;
  } catch (e) {
    audit.errors.push(String(e.message || e));
  }

  fs.writeFileSync(OUT_PATH, JSON.stringify(audit, null, 2));
  console.log(`wrote ${OUT_PATH}`);

  if (!audit.signed_manifest_coverage_pass) {
    console.error("SIGNED MANIFEST COVERAGE FAIL");
    console.error(JSON.stringify(audit.errors, null, 2));
    process.exit(1);
  }

  console.log("SIGNED MANIFEST COVERAGE PASS");
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
