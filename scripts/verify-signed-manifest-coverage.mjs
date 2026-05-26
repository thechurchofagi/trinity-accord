#!/usr/bin/env node
/**
 * V3/V4/V4+ signed-manifest hard gate.
 *
 * Supports:
 *   - repo-tree local files
 *   - GitHub Release assets
 *   - hash-only coverage-only targets
 *
 * Sensitive required targets must verify actual bytes.
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
const REPO = process.env.REPO || "thechurchofagi/trinity-accord";

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

function normalizeHash(s) {
  return String(s || "").trim().toLowerCase().replace(/^0x/, "");
}

function isSha256(s) {
  return /^[a-f0-9]{64}$/i.test(String(s || "").trim());
}

function isHexHash(s) {
  return /^([a-f0-9]{64}|[a-f0-9]{128})$/i.test(String(s || "").trim());
}

function isSensitiveCategory(category) {
  const c = String(category || "").toLowerCase();
  return ["flaw", "covenant", "nft", "chronicle", "physical_anchor", "core_object_alpha"].some(x => c.includes(x));
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
    const ch = text[i], next = text[i + 1];

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

    if (ch === '"') inQuotes = true;
    else if (ch === ",") {
      row.push(cell);
      cell = "";
    } else if (ch === "\n") {
      row.push(cell);
      rows.push(row);
      row = [];
      cell = "";
    } else if (ch !== "\r") {
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
    "sha256", "sha3_256", "blake2b_256", "shake256_256",
    "sha512_256", "blake3_256", "ar_sha256",
    "input_sha256", "expected_sha256"
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
  if (!TARGET_MANIFEST) return {path: null, targets: []};
  const obj = readJson(path.resolve(TARGET_MANIFEST));
  return {path: TARGET_MANIFEST, targets: Array.isArray(obj) ? obj : (obj.targets || [])};
}

function ghHeaders(extra = {}) {
  const h = {"Accept": "application/vnd.github+json", "User-Agent": "trinity-accord-verifier", ...extra};
  if (process.env.GITHUB_TOKEN) h.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  return h;
}

async function getReleaseAsset(tag, assetName) {
  const res = await fetch(`https://api.github.com/repos/${REPO}/releases/tags/${tag}`, {headers: ghHeaders()});
  if (!res.ok) throw new Error(`release ${tag} not found: HTTP ${res.status}`);
  const release = await res.json();
  const asset = (release.assets || []).find(a => a.name === assetName);
  if (!asset) throw new Error(`asset ${assetName} not found in release ${tag}`);
  return asset;
}

async function downloadReleaseAsset(tag, assetName, cachePath) {
  const asset = await getReleaseAsset(tag, assetName);
  const targetPath = path.resolve(ROOT, cachePath || path.join(".cache/v3plus-release-assets", assetName));
  fs.mkdirSync(path.dirname(targetPath), {recursive: true});

  const res = await fetch(asset.url, {
    headers: ghHeaders({"Accept": "application/octet-stream"})
  });
  if (!res.ok) throw new Error(`asset download failed ${assetName}: HTTP ${res.status}`);

  const buf = Buffer.from(await res.arrayBuffer());
  fs.writeFileSync(targetPath, buf);
  return {
    bytes: buf,
    rel_path: path.relative(ROOT, targetPath).replace(/\\/g, "/"),
    asset_id: asset.id,
    asset_size: asset.size
  };
}

async function resolveTarget(target) {
  if (target.path) {
    const p = path.resolve(ROOT, target.path);
    if (!fs.existsSync(p)) {
      if (target.required !== false) throw new Error(`target path missing: ${target.path}`);
      return {byte_verified: false, source_kind: "missing_optional_path", sha256: normalizeHash(target.sha256 || "")};
    }
    const buf = fs.readFileSync(p);
    return {
      byte_verified: true,
      source_kind: "local_path",
      source_path: target.path,
      sha256: sha256hex(buf),
      size_bytes: buf.length
    };
  }

  if (target.release_tag && target.asset_name) {
    const dl = await downloadReleaseAsset(target.release_tag, target.asset_name, target.cache_path);
    return {
      byte_verified: true,
      source_kind: "github_release_asset",
      source_path: dl.rel_path,
      sha256: sha256hex(dl.bytes),
      size_bytes: dl.bytes.length,
      github_release_asset_id: dl.asset_id,
      github_release_asset_size: dl.asset_size
    };
  }

  if (target.sha256) {
    return {
      byte_verified: false,
      source_kind: "hash_only",
      sha256: normalizeHash(target.sha256),
      size_bytes: null
    };
  }

  return {byte_verified: false, source_kind: "no_source", sha256: ""};
}

function runExistingScript(scriptPath) {
  execFileSync("node", [scriptPath], {cwd: ROOT, stdio: "inherit", env: process.env});
}

function mustPassAudit(filePath, fieldName) {
  const audit = readJson(path.join(ROOT, filePath));
  if (audit[fieldName] !== true) throw new Error(`${filePath} ${fieldName} is not true`);
}

async function main() {
  const audit = {
    schema: "trinityaccord.signed-manifest-coverage-audit.v2",
    generated_at: new Date().toISOString(),
    signed_manifest_coverage_pass: false,
    btc_bip340_signature_verified: false,
    legacy_eth_witness_verified: false,
    digest_manifest_json_declared: false,
    digest_manifest_csv_declared: false,
    digest_manifest_json_hash_match: false,
    digest_manifest_csv_hash_match: false,
    coverage_hashes_total: 0,
    target_manifest: TARGET_MANIFEST || null,
    targets_total: 0,
    targets_covered: 0,
    targets_byte_verified: 0,
    targets_coverage_only: 0,
    targets_blocking_failed: 0,
    targets_optional_failed: 0,
    sensitive_required_byte_targets: 0,
    target_results: [],
    errors: []
  };

  try {
    for (const p of [AUTHORITY_PATH, DIGEST_JSON_PATH, DIGEST_CSV_PATH]) {
      if (!fs.existsSync(p)) throw new Error(`missing ${path.relative(ROOT, p)}`);
    }

    runExistingScript("scripts/verify-btc-signature-coverage.mjs");
    mustPassAudit("BTC-SIGNATURE-COVERAGE-AUDIT.json", "btc_signature_coverage_pass");
    audit.btc_bip340_signature_verified = true;

    runExistingScript("scripts/verify-legacy-eth-witness.mjs");
    mustPassAudit("LEGACY-ETH-WITNESS-AUDIT.json", "legacy_eth_witness_pass");
    audit.legacy_eth_witness_verified = true;

    const authority = readJson(AUTHORITY_PATH);
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
      addRecordHashes(index, doc, {source: "authority.jcs.json", class: "authority_arweave_document", label: doc.label || "", txid: doc.txid || ""});
    }

    const digestJson = JSON.parse(digestJsonRaw.toString("utf8"));
    normalizeDigestItems(digestJson).forEach((item, i) => {
      addRecordHashes(index, item, {source: "digest-manifest.json", class: "digest_manifest_json", index: i, path: item.path || item.file || item.filename || item.name || ""});
    });

    parseCsv(digestCsvRaw.toString("utf8")).forEach((row, i) => {
      addRecordHashes(index, row, {source: "digest-manifest.csv", class: "digest_manifest_csv", index: i, path: row.path || row.file || row.filename || row.name || ""});
    });

    audit.coverage_hashes_total = Object.keys(index).length;

    const targetObj = loadTargets();
    audit.target_manifest = targetObj.path;
    audit.targets_total = targetObj.targets.length;

    for (const target of targetObj.targets) {
      const category = String(target.category || "general").toLowerCase();
      const sensitive = isSensitiveCategory(category);
      const required = target.required !== false;
      const coverageOnly = target.coverage_only === true;

      const result = {
        id: target.id || target.path || target.asset_name || target.sha256 || "target",
        category,
        required,
        coverage_only: coverageOnly,
        sensitive,
        source_kind: null,
        source_path: target.path || null,
        release_tag: target.release_tag || null,
        asset_name: target.asset_name || null,
        sha256_expected: normalizeHash(target.sha256 || ""),
        sha256_observed: null,
        size_expected: Number.isFinite(Number(target.size_bytes)) ? Number(target.size_bytes) : null,
        size_observed: null,
        byte_verified: false,
        covered_by_signed_manifest_chain: false,
        coverage_sources: [],
        pass: false,
        blocking: false,
        error: null
      };

      try {
        if (coverageOnly && required) throw new Error("coverage_only target must not be required=true");

        const resolved = await resolveTarget(target);
        result.source_kind = resolved.source_kind;
        result.source_path = resolved.source_path || result.source_path;
        result.sha256_observed = resolved.sha256;
        result.size_observed = resolved.size_bytes ?? null;
        result.byte_verified = resolved.byte_verified === true;

        if (target.sha256 && result.byte_verified && normalizeHash(target.sha256) !== result.sha256_observed) {
          throw new Error(`target sha256 mismatch: expected ${normalizeHash(target.sha256)}, observed ${result.sha256_observed}`);
        }

        if (Number.isFinite(result.size_expected) && result.byte_verified && result.size_observed !== result.size_expected) {
          throw new Error(`target size mismatch: expected ${result.size_expected}, observed ${result.size_observed}`);
        }

        if (!isSha256(result.sha256_observed)) throw new Error("target has no valid SHA-256");

        result.coverage_sources = index[result.sha256_observed] || [];
        result.covered_by_signed_manifest_chain = result.coverage_sources.length > 0;
        if (!result.covered_by_signed_manifest_chain) {
          throw new Error("target SHA-256 is not in signed authority/digest coverage chain");
        }

        if (sensitive && required) {
          audit.sensitive_required_byte_targets++;
          if (!result.byte_verified) {
            throw new Error("sensitive required target must verify actual bytes; sha256-only is coverage preflight only");
          }
        }

        if (coverageOnly) {
          audit.targets_coverage_only++;
          result.pass = true;
        } else if (required) {
          result.pass = result.covered_by_signed_manifest_chain && result.byte_verified;
        } else {
          result.pass = result.covered_by_signed_manifest_chain;
        }
      } catch (e) {
        result.error = String(e.message || e);
      }

      if (result.pass) {
        audit.targets_covered++;
        if (result.byte_verified) audit.targets_byte_verified++;
      } else if (required || sensitive) {
        result.blocking = true;
        audit.targets_blocking_failed++;
      } else {
        audit.targets_optional_failed++;
      }

      audit.target_results.push(result);
    }

    audit.signed_manifest_coverage_pass =
      audit.btc_bip340_signature_verified &&
      audit.legacy_eth_witness_verified &&
      audit.digest_manifest_json_hash_match &&
      audit.digest_manifest_csv_hash_match &&
      audit.targets_blocking_failed === 0;
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
