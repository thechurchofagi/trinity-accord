#!/usr/bin/env bash
set -euo pipefail

node - <<'NODE'
const fs = require("fs");
const path = require("path");
const crypto = require("crypto");

const ROOT = process.cwd();
const REPO = process.env.REPO || "thechurchofagi/trinity-accord";
const HASH_MANIFEST = path.join(ROOT, "archive/hash-manifest.json");
const RELEASE_MANIFEST = path.join(ROOT, "RELEASE-LARGE-DATA-MANIFEST.json");

function sha256hex(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

function readJsonIfExists(p) {
  return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : null;
}

function ghHeaders(extra = {}) {
  const h = {"Accept": "application/vnd.github+json", "User-Agent": "trinity-accord-archive-verifier", ...extra};
  if (process.env.GITHUB_TOKEN) h.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  return h;
}

async function fetchReleaseAsset(tag, assetName) {
  const relRes = await fetch(`https://api.github.com/repos/${REPO}/releases/tags/${tag}`, {headers: ghHeaders()});
  if (!relRes.ok) throw new Error(`release ${tag} HTTP ${relRes.status}`);
  const rel = await relRes.json();
  const asset = (rel.assets || []).find(a => a.name === assetName);
  if (!asset) throw new Error(`asset ${assetName} not found`);
  const dataRes = await fetch(asset.url, {headers: ghHeaders({"Accept": "application/octet-stream"})});
  if (!dataRes.ok) throw new Error(`asset ${assetName} download HTTP ${dataRes.status}`);
  return Buffer.from(await dataRes.arrayBuffer());
}

function releaseAssetFor(releaseManifest, entry) {
  if (!releaseManifest) return null;
  const assets = releaseManifest.assets || [];
  return assets.find(a => a.logical_path === entry.path || String(a.sha256).toLowerCase() === String(entry.sha256).toLowerCase()) || null;
}

async function main() {
  if (!fs.existsSync(HASH_MANIFEST)) throw new Error("archive/hash-manifest.json missing");
  const manifest = JSON.parse(fs.readFileSync(HASH_MANIFEST, "utf8"));
  const releaseManifest = readJsonIfExists(RELEASE_MANIFEST);

  let pass = 0, fail = 0, missing = 0, releasePass = 0;
  const failures = [];

  for (const entry of manifest.files || []) {
    if (!entry.path || !entry.sha256) continue;
    const expected = String(entry.sha256).toLowerCase();
    const p = path.join(ROOT, entry.path);

    try {
      let buf = null;
      let source = null;

      if (fs.existsSync(p)) {
        buf = fs.readFileSync(p);
        source = "repo_tree";
      } else {
        const asset = releaseAssetFor(releaseManifest, entry);
        if (asset) {
          buf = await fetchReleaseAsset(releaseManifest.release_tag, asset.asset_name);
          source = `release:${releaseManifest.release_tag}/${asset.asset_name}`;
        }
      }

      if (!buf) {
        missing++;
        failures.push({path: entry.path, error: "missing in repo tree and no release asset"});
        console.log(`❌ MISSING ${entry.path}`);
        continue;
      }

      const actual = sha256hex(buf);
      if (actual !== expected) {
        fail++;
        failures.push({path: entry.path, source, expected, actual});
        console.log(`❌ FAIL    ${entry.path} (${source})`);
      } else {
        pass++;
        if (source.startsWith("release:")) releasePass++;
        console.log(`✅ PASS    ${entry.path} (${source})`);
      }
    } catch (e) {
      fail++;
      failures.push({path: entry.path, error: String(e.message || e)});
      console.log(`❌ ERROR   ${entry.path}: ${String(e.message || e)}`);
    }
  }

  const report = {
    schema: "trinityaccord.github-archive-verification.v2",
    generated_at: new Date().toISOString(),
    release_aware: true,
    files_pass: pass,
    files_fail: fail,
    files_missing: missing,
    release_asset_pass: releasePass,
    status: fail === 0 && missing === 0 ? "PASS" : "FAIL",
    failures
  };

  fs.writeFileSync("GITHUB-ARCHIVE-VERIFY-AUDIT.json", JSON.stringify(report, null, 2));
  console.log("");
  console.log(`PASS=${pass} FAIL=${fail} MISSING=${missing} RELEASE_PASS=${releasePass}`);

  if (report.status !== "PASS") process.exit(1);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
NODE
