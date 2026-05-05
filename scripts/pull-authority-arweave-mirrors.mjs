#!/usr/bin/env node
/**
 * pull-authority-arweave-mirrors.mjs
 *
 * GitHub-first authority Arweave mirror coverage.
 *
 * Important design:
 *   - For V3/V4/V4+, local GitHub mirror bytes are sufficient if their hash
 *     matches authority.jcs.json.
 *   - Direct Arweave retrieval is optional cross-source checking unless
 *     --require-cross-source is set.
 *   - If local mirror exists and hash/size match, PASS for GitHub-scope even
 *     when Arweave gateways return 404.
 *
 * Output:
 *   ARWEAVE-GITHUB-MIRROR-COVERAGE.json
 *   ARWEAVE-GITHUB-MIRROR-COVERAGE.md
 *
 * Usage:
 *   node scripts/pull-authority-arweave-mirrors.mjs
 *   node scripts/pull-authority-arweave-mirrors.mjs --verify-only
 *   node scripts/pull-authority-arweave-mirrors.mjs --cross-source
 *   node scripts/pull-authority-arweave-mirrors.mjs --cross-source --require-cross-source
 */

import fs from "fs";
import path from "path";
import crypto from "crypto";

const ROOT = process.cwd();
const AUTHORITY_PATH = path.join(ROOT, "archive/authority-manifest/authority.jcs.json");
const MIRROR_DIR = path.join(ROOT, "archive/arweave-authority-mirror");
const OUT_JSON = path.join(ROOT, "ARWEAVE-GITHUB-MIRROR-COVERAGE.json");
const OUT_MD = path.join(ROOT, "ARWEAVE-GITHUB-MIRROR-COVERAGE.md");

const VERIFY_ONLY = process.argv.includes("--verify-only");
const CROSS_SOURCE = process.argv.includes("--cross-source");
const REQUIRE_CROSS_SOURCE = process.argv.includes("--require-cross-source");
const REQUIRE_LOCAL = !process.argv.includes("--allow-missing-local");

function sha256hex(buf) {
  return crypto.createHash("sha256").update(buf).digest("hex");
}

function slugify(s) {
  return String(s || "object")
    .normalize("NFKD")
    .replace(/[^\w.-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 80) || "object";
}

async function fetchBuffer(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return Buffer.from(await res.arrayBuffer());
}

async function downloadArweave(txid, gateway) {
  const bases = [];
  if (gateway) bases.push(gateway.replace(/\/+$/, ""));
  bases.push("https://arweave.net");
  bases.push("https://ar-io.net");
  bases.push("https://permagate.io");

  let lastErr = null;
  for (const base of [...new Set(bases)]) {
    const url = `${base}/${txid}`;
    try {
      const buf = await fetchBuffer(url);
      if (buf.length > 0) return {url, buf};
      lastErr = new Error(`empty body from ${url}`);
    } catch (e) {
      lastErr = e;
    }
  }
  throw lastErr || new Error(`unable to download ${txid}`);
}

function verifyLocal(localPath, expectedSha, expectedSize) {
  if (!fs.existsSync(localPath)) {
    return {
      exists_local: false,
      actual_sha256: null,
      actual_size: null,
      sha256_match: false,
      size_match: false,
      pass: false
    };
  }
  const buf = fs.readFileSync(localPath);
  const actualSha = sha256hex(buf);
  const actualSize = buf.length;
  return {
    exists_local: true,
    actual_sha256: actualSha,
    actual_size: actualSize,
    sha256_match: expectedSha ? actualSha === expectedSha : false,
    size_match: Number.isFinite(expectedSize) ? actualSize === expectedSize : false,
    pass: Boolean(expectedSha) && actualSha === expectedSha && (!Number.isFinite(expectedSize) || actualSize === expectedSize)
  };
}

async function main() {
  if (!fs.existsSync(AUTHORITY_PATH)) throw new Error(`missing ${AUTHORITY_PATH}`);
  if (!fs.existsSync(MIRROR_DIR)) fs.mkdirSync(MIRROR_DIR, {recursive: true});

  const authority = JSON.parse(fs.readFileSync(AUTHORITY_PATH, "utf8"));
  const docs = authority?.arweave?.documents || [];

  const rows = [];

  for (const doc of docs) {
    const txid = doc.txid;
    const label = doc.label || txid;
    const expectedSha = String(doc.ar_sha256 || "").toLowerCase();
    const expectedSize = Number(doc.size);
    const fileName = `${slugify(label)}__${txid}.bin`;
    const localPath = path.join(MIRROR_DIR, fileName);
    const relPath = path.relative(ROOT, localPath).replace(/\\/g, "/");

    const row = {
      label,
      txid,
      expected_sha256: expectedSha,
      expected_size: expectedSize,
      local_path: relPath,

      exists_local: false,
      actual_sha256: null,
      actual_size: null,
      sha256_match: false,
      size_match: false,

      github_scope_pass: false,
      v3_v4_v4plus_content_integrity_pass: false,

      arweave_checked: false,
      arweave_source_url_used: null,
      arweave_sha256: null,
      arweave_size: null,
      arweave_hash_match: null,
      arweave_size_match: null,
      cross_source_consistency_pass: null,

      downloaded_to_github_mirror: false,
      status: "UNKNOWN",
      error: null,
      warning: null
    };

    try {
      // 1. Verify local GitHub mirror first.
      let local = verifyLocal(localPath, expectedSha, expectedSize);
      Object.assign(row, local);

      // 2. If local is missing and not verify-only, try Arweave to populate the mirror.
      if (!row.exists_local && !VERIFY_ONLY) {
        try {
          const dl = await downloadArweave(txid, doc.gateway);
          fs.writeFileSync(localPath, dl.buf);
          row.downloaded_to_github_mirror = true;
          row.arweave_source_url_used = dl.url;
          local = verifyLocal(localPath, expectedSha, expectedSize);
          Object.assign(row, local);
        } catch (e) {
          row.warning = `local mirror missing and Arweave download failed: ${String(e.message || e)}`;
        }
      }

      row.github_scope_pass = row.exists_local && row.sha256_match && row.size_match;
      row.v3_v4_v4plus_content_integrity_pass = row.github_scope_pass;

      // 3. Optional cross-source check.
      if (CROSS_SOURCE || REQUIRE_CROSS_SOURCE) {
        row.arweave_checked = true;
        try {
          const dl = await downloadArweave(txid, doc.gateway);
          row.arweave_source_url_used = dl.url;
          row.arweave_sha256 = sha256hex(dl.buf);
          row.arweave_size = dl.buf.length;
          row.arweave_hash_match = row.arweave_sha256 === expectedSha;
          row.arweave_size_match = Number.isFinite(expectedSize) ? row.arweave_size === expectedSize : false;

          row.cross_source_consistency_pass =
            row.github_scope_pass &&
            row.arweave_hash_match &&
            (!Number.isFinite(expectedSize) || row.arweave_size_match) &&
            row.arweave_sha256 === row.actual_sha256;

          if (!row.cross_source_consistency_pass) {
            row.warning = "cross-source consistency failed";
          }
        } catch (e) {
          row.cross_source_consistency_pass = false;
          row.warning = `Arweave cross-source unavailable: ${String(e.message || e)}`;
        }
      }

      // 4. Decide status.
      if (row.github_scope_pass) {
        if (REQUIRE_CROSS_SOURCE && !row.cross_source_consistency_pass) {
          row.status = "GITHUB_PASS_CROSS_SOURCE_FAIL";
        } else if (row.cross_source_consistency_pass === true) {
          row.status = "GITHUB_PASS_CROSS_SOURCE_PASS";
        } else if (row.arweave_checked && row.cross_source_consistency_pass === false) {
          row.status = "GITHUB_PASS_CROSS_SOURCE_UNAVAILABLE_OR_FAIL";
        } else {
          row.status = "GITHUB_PASS";
        }
      } else if (!row.exists_local && !REQUIRE_LOCAL) {
        row.status = "LOCAL_MISSING_ALLOWED";
      } else {
        row.status = "GITHUB_FAIL";
        if (!row.error) row.error = row.warning || "local GitHub mirror missing or hash/size mismatch";
      }
    } catch (e) {
      row.error = String(e.message || e);
      row.status = "ERROR";
    }

    rows.push(row);
    console.log(`${row.github_scope_pass ? "GITHUB_PASS" : "GITHUB_FAIL"} ${label} ${relPath}${row.warning ? " — " + row.warning : ""}`);
  }

  const githubPass = rows.length > 0 && rows.every(r => r.github_scope_pass || (!REQUIRE_LOCAL && !r.exists_local));
  const crossSourcePass = rows.length > 0 && rows.every(r => r.cross_source_consistency_pass === true);

  const audit = {
    schema: "trinityaccord.arweave-github-mirror-coverage.v2",
    generated_at: new Date().toISOString(),
    authority_path: "archive/authority-manifest/authority.jcs.json",
    mode: {
      github_first: true,
      verify_only: VERIFY_ONLY,
      cross_source: CROSS_SOURCE,
      require_cross_source: REQUIRE_CROSS_SOURCE,
      require_local: REQUIRE_LOCAL
    },
    documents_total: rows.length,
    github_scope_pass_total: rows.filter(r => r.github_scope_pass).length,
    github_scope_fail_total: rows.filter(r => !r.github_scope_pass).length,
    cross_source_checked_total: rows.filter(r => r.arweave_checked).length,
    cross_source_pass_total: rows.filter(r => r.cross_source_consistency_pass === true).length,
    cross_source_fail_total: rows.filter(r => r.cross_source_consistency_pass === false).length,

    // Important pass fields.
    pass: githubPass && (!REQUIRE_CROSS_SOURCE || crossSourcePass),
    pass_github_scope_v3_v4_v4plus: githubPass,
    pass_cross_source_v5_candidate: crossSourcePass,

    rows
  };

  const md = [
    "# Arweave → GitHub Mirror Coverage",
    "",
    `Generated: ${audit.generated_at}`,
    "",
    "This report is GitHub-first. For V3/V4/V4+, GitHub mirror bytes pass if their hash and size match the signed authority/digest chain. Direct Arweave retrieval is a separate cross-source check.",
    "",
    `GitHub-scope pass: **${audit.pass_github_scope_v3_v4_v4plus ? "PASS" : "FAIL"}**`,
    "",
    `Cross-source pass: **${audit.pass_cross_source_v5_candidate ? "PASS" : "FAIL / not checked"}**`,
    "",
    "| Label | TXID | GitHub mirror | GitHub hash | Cross-source | Status |",
    "|---|---|---|---|---|---|",
    ...rows.map(r =>
      `| ${String(r.label).replace(/\|/g, "\\|")} | \`${r.txid}\` | \`${r.local_path}\` | ${r.github_scope_pass ? "PASS" : "FAIL"} | ${r.cross_source_consistency_pass === true ? "PASS" : (r.arweave_checked ? "FAIL/UNAVAILABLE" : "not checked")} | ${r.status}${r.warning ? `: ${String(r.warning).replace(/\|/g, "\\|")}` : ""}${r.error ? `: ${String(r.error).replace(/\|/g, "\\|")}` : ""} |`
    ),
    "",
    "Boundary: these mirrors are non-amending. Bitcoin Originals prevail."
  ].join("\n");

  fs.writeFileSync(OUT_JSON, JSON.stringify(audit, null, 2));
  fs.writeFileSync(OUT_MD, md);
  console.log(`wrote ${OUT_JSON}`);
  console.log(`wrote ${OUT_MD}`);

  if (!audit.pass) process.exit(1);
}

main().catch(e => {
  console.error(e);
  process.exit(1);
});
