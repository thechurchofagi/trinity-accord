#!/usr/bin/env node
/**
 * Build a release manifest for large data files listed in archive/hash-manifest.json.
 *
 * Default threshold: 10 MB.
 *
 * Output:
 *   RELEASE-LARGE-DATA-MANIFEST.json
 *   RELEASE-LARGE-DATA-MANIFEST.md
 */

import fs from "fs";
import path from "path";
import crypto from "crypto";

const ROOT = process.cwd();

function argValue(name, def = null) {
  const idx = process.argv.indexOf(name);
  return idx >= 0 && idx + 1 < process.argv.length ? process.argv[idx + 1] : def;
}

const RELEASE_TAG = argValue("--release-tag", "signed-large-data-mirror-v1");
const MIN_SIZE_MB = Number(argValue("--min-size-mb", "10"));
const MIN_SIZE_BYTES = MIN_SIZE_MB * 1024 * 1024;
const HASH_MANIFEST = path.join(ROOT, "archive/hash-manifest.json");
const OUT_JSON = path.join(ROOT, "RELEASE-LARGE-DATA-MANIFEST.json");
const OUT_MD = path.join(ROOT, "RELEASE-LARGE-DATA-MANIFEST.md");

function sha256hex(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

function assetNameFor(p, used) {
  const base = path.basename(p);
  if (!used.has(base)) {
    used.add(base);
    return base;
  }
  const alt = p.replace(/[\/\\]+/g, "__");
  used.add(alt);
  return alt;
}

function inferCategory(p) {
  const s = String(p).toLowerCase();
  if (s.includes("covenant") || s.includes("flaw")) return "flaw";
  if (s.includes("nft") || s.includes("chronicle")) return "chronicle";
  return "general";
}

function main() {
  if (!fs.existsSync(HASH_MANIFEST)) throw new Error(`Missing ${HASH_MANIFEST}`);
  const manifest = JSON.parse(fs.readFileSync(HASH_MANIFEST, "utf8"));
  const files = manifest.files || [];
  const used = new Set();
  const assets = [];

  for (const f of files) {
    const size = Number(f.size_bytes || 0);
    if (size < MIN_SIZE_BYTES) continue;
    if (!f.path || !f.sha256) continue;

    const full = path.join(ROOT, f.path);
    const entry = {
      logical_path: f.path,
      asset_name: assetNameFor(f.path, used),
      sha256: String(f.sha256).toLowerCase(),
      size_bytes: size,
      arweave_tx: f.arweave_tx || null,
      category: inferCategory(f.path),
      source_path_exists: fs.existsSync(full),
      non_amending: true
    };

    if (entry.source_path_exists) {
      const buf = fs.readFileSync(full);
      const actualSha = sha256hex(buf);
      if (actualSha !== entry.sha256) {
        throw new Error(`SHA mismatch for ${f.path}: manifest=${entry.sha256} actual=${actualSha}`);
      }
      if (buf.length !== size) {
        throw new Error(`Size mismatch for ${f.path}: manifest=${size} actual=${buf.length}`);
      }
    }

    assets.push(entry);
  }

  const out = {
    schema: "trinityaccord.release-large-data-manifest.v1",
    generated_at: new Date().toISOString(),
    release_tag: RELEASE_TAG,
    min_size_mb: MIN_SIZE_MB,
    boundary: "non-amending; Bitcoin Originals prevail",
    note: "Release assets are mirrors. Identity is determined by signed-covered hashes, not by release authority.",
    assets_total: assets.length,
    assets
  };

  const md = [
    "# Trinity Accord Signed Large Data Release Manifest",
    "",
    `Generated: ${out.generated_at}`,
    `Release tag: \`${RELEASE_TAG}\``,
    "",
    "Release assets are non-amending mirrors. The authoritative identity of each asset is its signed-covered hash.",
    "",
    "| Asset | Logical path | SHA-256 | Size | Arweave TX | Category |",
    "|---|---|---|---:|---|---|",
    ...assets.map(a =>
      `| \`${a.asset_name}\` | \`${a.logical_path}\` | \`${a.sha256}\` | ${a.size_bytes} | ${a.arweave_tx ? "`" + a.arweave_tx + "`" : ""} | ${a.category} |`
    )
  ].join("\n");

  fs.writeFileSync(OUT_JSON, JSON.stringify(out, null, 2));
  fs.writeFileSync(OUT_MD, md);
  console.log(`Wrote ${OUT_JSON}`);
  console.log(`Wrote ${OUT_MD}`);

  if (assets.length === 0) {
    console.error("No large assets found. Check --min-size-mb.");
    process.exit(1);
  }

  for (const a of assets) {
    if (!a.source_path_exists) {
      console.error(`Missing source file before release upload: ${a.logical_path}`);
      process.exit(1);
    }
  }
}

main();
