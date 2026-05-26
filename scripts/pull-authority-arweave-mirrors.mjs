#!/usr/bin/env node
/**
 * GitHub-first authority mirror coverage.
 *
 * Checks authority.jcs.json arweave.documents[] against:
 *   1. existing repo-tree files from archive/hash-manifest.json
 *   2. GitHub Release assets from RELEASE-LARGE-DATA-MANIFEST.json
 *   3. optional direct Arweave cross-source retrieval
 *
 * For V3/V4/V4+, repo-tree or Release asset bytes are sufficient if signed hash matches.
 */

import fs from "fs";
import path from "path";
import crypto from "crypto";

const ROOT = process.cwd();
const REPO = process.env.REPO || "thechurchofagi/trinity-accord";
const AUTHORITY_PATH = path.join(ROOT, "archive/authority-manifest/authority.jcs.json");
const HASH_MANIFEST_PATH = path.join(ROOT, "archive/hash-manifest.json");
const RELEASE_MANIFEST_PATH = path.join(ROOT, "RELEASE-LARGE-DATA-MANIFEST.json");
const MIRROR_DIR = path.join(ROOT, "archive/arweave-authority-mirror");
const OUT_JSON = path.join(ROOT, "ARWEAVE-GITHUB-MIRROR-COVERAGE.json");
const OUT_MD = path.join(ROOT, "ARWEAVE-GITHUB-MIRROR-COVERAGE.md");

const CROSS_SOURCE = process.argv.includes("--cross-source");
const REQUIRE_CROSS_SOURCE = process.argv.includes("--require-cross-source");
const VERIFY_ONLY = process.argv.includes("--verify-only");

function sha256hex(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

function normalizeHash(s) {
  return String(s || "").trim().toLowerCase();
}

function slugify(s) {
  return String(s || "object").normalize("NFKD").replace(/[^\w.-]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 80) || "object";
}

function readJsonIfExists(p) {
  return fs.existsSync(p) ? JSON.parse(fs.readFileSync(p, "utf8")) : null;
}

function ghHeaders(extra = {}) {
  const h = {"Accept": "application/vnd.github+json", "User-Agent": "trinity-accord-verifier", ...extra};
  if (process.env.GITHUB_TOKEN) h.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  return h;
}

async function fetchBuffer(url, headers = {}) {
  const res = await fetch(url, {headers});
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return Buffer.from(await res.arrayBuffer());
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
  const res = await fetch(asset.url, {headers: ghHeaders({"Accept": "application/octet-stream"})});
  if (!res.ok) throw new Error(`asset download ${assetName} failed: HTTP ${res.status}`);
  const buf = Buffer.from(await res.arrayBuffer());
  const p = path.resolve(ROOT, cachePath || path.join(".cache/release-assets", assetName));
  fs.mkdirSync(path.dirname(p), {recursive: true});
  fs.writeFileSync(p, buf);
  return {buf, rel_path: path.relative(ROOT, p).replace(/\\/g, "/")};
}

async function downloadArweave(txid, gateway) {
  const bases = [];
  if (gateway) bases.push(gateway.replace(/\/+$/, ""));
  bases.push("https://arweave.net", "https://ar-io.net", "https://permagate.io");

  let lastErr = null;
  for (const base of [...new Set(bases)]) {
    const url = `${base}/${txid}`;
    try {
      const buf = await fetchBuffer(url);
      if (buf.length > 0) return {url, buf};
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error(`unable to fetch Arweave ${txid}`);
}

function buildLocalCandidates(hashManifest, doc) {
  const files = hashManifest?.files || [];
  const expected = normalizeHash(doc.ar_sha256);
  const txid = doc.txid;
  return files
    .filter(f => normalizeHash(f.sha256) === expected || normalizeHash(f.expected_sha256) === expected || f.arweave_tx === txid)
    .map(f => f.path);
}

function buildReleaseCandidate(releaseManifest, doc) {
  const assets = releaseManifest?.assets || [];
  const expected = normalizeHash(doc.ar_sha256);
  const txid = doc.txid;
  return assets.find(a => normalizeHash(a.sha256) === expected || a.arweave_tx === txid) || null;
}

function verifyBytes(buf, expectedSha, expectedSize) {
  const actualSha = sha256hex(buf);
  const actualSize = buf.length;
  return {
    actual_sha256: actualSha,
    actual_size: actualSize,
    sha256_match: actualSha === expectedSha,
    size_match: Number.isFinite(expectedSize) ? actualSize === expectedSize : true,
    pass: actualSha === expectedSha && (!Number.isFinite(expectedSize) || actualSize === expectedSize)
  };
}

async function main() {
  if (!fs.existsSync(AUTHORITY_PATH)) throw new Error(`missing ${AUTHORITY_PATH}`);
  fs.mkdirSync(MIRROR_DIR, {recursive: true});

  const authority = JSON.parse(fs.readFileSync(AUTHORITY_PATH, "utf8"));
  const hashManifest = readJsonIfExists(HASH_MANIFEST_PATH);
  const releaseManifest = readJsonIfExists(RELEASE_MANIFEST_PATH);
  const docs = authority?.arweave?.documents || [];
  const rows = [];

  for (const doc of docs) {
    const expectedSha = normalizeHash(doc.ar_sha256);
    const expectedSize = Number(doc.size);
    const row = {
      label: doc.label || doc.txid,
      txid: doc.txid,
      expected_sha256: expectedSha,
      expected_size: expectedSize,
      github_scope_pass: false,
      github_source_kind: null,
      github_source_path: null,
      actual_sha256: null,
      actual_size: null,
      cross_source_checked: false,
      cross_source_consistency_pass: null,
      status: "UNKNOWN",
      warning: null,
      error: null
    };

    try {
      // 1. Existing repo-tree paths from hash-manifest.json
      for (const rel of buildLocalCandidates(hashManifest, doc)) {
        const p = path.join(ROOT, rel);
        if (!fs.existsSync(p)) continue;
        const v = verifyBytes(fs.readFileSync(p), expectedSha, expectedSize);
        if (v.pass) {
          Object.assign(row, v);
          row.github_scope_pass = true;
          row.github_source_kind = "repo_tree";
          row.github_source_path = rel;
          break;
        }
      }

      // 2. Release-backed asset
      if (!row.github_scope_pass) {
        const asset = buildReleaseCandidate(releaseManifest, doc);
        if (asset) {
          try {
            const dl = await downloadReleaseAsset(releaseManifest.release_tag, asset.asset_name, path.join(".cache/release-assets", asset.asset_name));
            const v = verifyBytes(dl.buf, expectedSha, expectedSize);
            if (!v.pass) throw new Error("release asset hash/size mismatch");
            Object.assign(row, v);
            row.github_scope_pass = true;
            row.github_source_kind = "github_release_asset";
            row.github_source_path = dl.rel_path;
          } catch (e) {
            row.warning = `release asset failed: ${String(e.message || e)}`;
          }
        }
      }

      // 3. Legacy/generated mirror directory, if present
      if (!row.github_scope_pass) {
        const fileName = `${slugify(doc.label)}__${doc.txid}.bin`;
        const p = path.join(MIRROR_DIR, fileName);
        if (fs.existsSync(p)) {
          const v = verifyBytes(fs.readFileSync(p), expectedSha, expectedSize);
          if (v.pass) {
            Object.assign(row, v);
            row.github_scope_pass = true;
            row.github_source_kind = "arweave-authority-mirror-dir";
            row.github_source_path = path.relative(ROOT, p).replace(/\\/g, "/");
          }
        }
      }

      // 4. Optional Arweave cross-source
      if (CROSS_SOURCE || REQUIRE_CROSS_SOURCE) {
        row.cross_source_checked = true;
        try {
          const dl = await downloadArweave(doc.txid, doc.gateway);
          const v = verifyBytes(dl.buf, expectedSha, expectedSize);
          row.cross_source_consistency_pass = row.github_scope_pass && v.pass && v.actual_sha256 === row.actual_sha256;
          if (!row.cross_source_consistency_pass) row.warning = "cross-source mismatch or GitHub scope missing";
        } catch (e) {
          row.cross_source_consistency_pass = false;
          row.warning = `Arweave cross-source unavailable: ${String(e.message || e)}`;
        }
      }

      if (row.github_scope_pass) {
        if (REQUIRE_CROSS_SOURCE && !row.cross_source_consistency_pass) row.status = "GITHUB_PASS_CROSS_SOURCE_FAIL";
        else row.status = row.cross_source_consistency_pass === true ? "GITHUB_PASS_CROSS_SOURCE_PASS" : "GITHUB_PASS";
      } else if (!VERIFY_ONLY) {
        // 5. Last resort: fetch Arweave to populate mirror dir
        try {
          const dl = await downloadArweave(doc.txid, doc.gateway);
          const v = verifyBytes(dl.buf, expectedSha, expectedSize);
          if (v.pass) {
            const fileName = `${slugify(doc.label)}__${doc.txid}.bin`;
            const p = path.join(MIRROR_DIR, fileName);
            fs.writeFileSync(p, dl.buf);
            Object.assign(row, v);
            row.github_scope_pass = true;
            row.github_source_kind = "downloaded_arweave_to_mirror_dir";
            row.github_source_path = path.relative(ROOT, p).replace(/\\/g, "/");
            row.status = "GITHUB_PASS_AFTER_ARWEAVE_DOWNLOAD";
          } else {
            row.status = "GITHUB_FAIL";
            row.error = "downloaded Arweave bytes did not match expected";
          }
        } catch (e) {
          row.status = "GITHUB_FAIL";
          row.error = row.warning || `no GitHub mirror and Arweave unavailable: ${String(e.message || e)}`;
        }
      } else {
        row.status = "GITHUB_FAIL";
        row.error = "no GitHub mirror found";
      }
    } catch (e) {
      row.status = "ERROR";
      row.error = String(e.message || e);
    }

    rows.push(row);
    console.log(`${row.github_scope_pass ? "GITHUB_PASS" : "GITHUB_FAIL"} ${row.label} via ${row.github_source_kind || "none"}`);
  }

  const githubPass = rows.length > 0 && rows.every(r => r.github_scope_pass);
  const crossPass = rows.length > 0 && rows.every(r => r.cross_source_consistency_pass === true);

  const audit = {
    schema: "trinityaccord.arweave-github-mirror-coverage.v3",
    generated_at: new Date().toISOString(),
    github_first: true,
    release_aware: true,
    cross_source_requested: CROSS_SOURCE || REQUIRE_CROSS_SOURCE,
    require_cross_source: REQUIRE_CROSS_SOURCE,
    documents_total: rows.length,
    github_scope_pass_total: rows.filter(r => r.github_scope_pass).length,
    github_scope_fail_total: rows.filter(r => !r.github_scope_pass).length,
    pass: githubPass && (!REQUIRE_CROSS_SOURCE || crossPass),
    pass_github_scope_v3_v4_v4plus: githubPass,
    pass_cross_source_v5_candidate: crossPass,
    rows
  };

  const md = [
    "# Arweave → GitHub / Release Mirror Coverage",
    "",
    `Generated: ${audit.generated_at}`,
    "",
    `GitHub-scope V3/V4/V4+ pass: **${audit.pass_github_scope_v3_v4_v4plus ? "PASS" : "FAIL"}**`,
    `Cross-source V5 candidate pass: **${audit.pass_cross_source_v5_candidate ? "PASS" : "FAIL / not checked"}**`,
    "",
    "| Label | TXID | Source | SHA | Status |",
    "|---|---|---|---|---|",
    ...rows.map(r =>
      `| ${String(r.label).replace(/\|/g, "\\|")} | \`${r.txid}\` | ${r.github_source_kind || ""}: \`${r.github_source_path || ""}\` | ${r.actual_sha256 === r.expected_sha256 ? "PASS" : "FAIL"} | ${r.status}${r.warning ? ` — ${String(r.warning).replace(/\|/g, "\\|")}` : ""}${r.error ? ` — ${String(r.error).replace(/\|/g, "\\|")}` : ""} |`
    ),
    "",
    "Boundary: mirrors and releases are non-amending. Bitcoin Originals prevail."
  ].join("\n");

  fs.writeFileSync("ARWEAVE-GITHUB-MIRROR-COVERAGE.json", JSON.stringify(audit, null, 2));
  fs.writeFileSync("ARWEAVE-GITHUB-MIRROR-COVERAGE.md", md);

  if (!audit.pass) process.exit(1);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
