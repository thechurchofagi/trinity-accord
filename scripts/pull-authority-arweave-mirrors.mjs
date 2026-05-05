#!/usr/bin/env node
/**
 * pull-authority-arweave-mirrors.mjs
 *
 * Downloads every authority.jcs.json arweave.documents[] object into GitHub tree.
 * This turns the old-homepage / guardian Arweave materials into local mirrors.
 *
 * Output:
 *   archive/arweave-authority-mirror/<slug>__<txid>.bin
 *   ARWEAVE-GITHUB-MIRROR-COVERAGE.json
 *   ARWEAVE-GITHUB-MIRROR-COVERAGE.md
 *
 * Usage:
 *   node scripts/pull-authority-arweave-mirrors.mjs
 *   node scripts/pull-authority-arweave-mirrors.mjs --verify-only
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
      source_url_used: null,
      exists_local: fs.existsSync(localPath),
      actual_sha256: null,
      actual_size: null,
      sha256_match: false,
      size_match: false,
      downloaded: false,
      pass: false,
      error: null
    };

    try {
      if (!row.exists_local && VERIFY_ONLY) {
        throw new Error("mirror missing and --verify-only set");
      }

      if (!row.exists_local) {
        const dl = await downloadArweave(txid, doc.gateway);
        fs.writeFileSync(localPath, dl.buf);
        row.source_url_used = dl.url;
        row.downloaded = true;
        row.exists_local = true;
      }

      const buf = fs.readFileSync(localPath);
      row.actual_sha256 = sha256hex(buf);
      row.actual_size = buf.length;
      row.sha256_match = expectedSha ? row.actual_sha256 === expectedSha : false;
      row.size_match = Number.isFinite(expectedSize) ? row.actual_size === expectedSize : false;
      row.pass = row.exists_local && row.sha256_match && row.size_match;

      if (!row.pass) {
        throw new Error(`mirror mismatch sha=${row.sha256_match} size=${row.size_match}`);
      }
    } catch (e) {
      row.error = String(e.message || e);
    }

    rows.push(row);
    console.log(`${row.pass ? "PASS" : "FAIL"} ${label} ${relPath}`);
  }

  const audit = {
    schema: "trinityaccord.arweave-github-mirror-coverage.v1",
    generated_at: new Date().toISOString(),
    authority_path: "archive/authority-manifest/authority.jcs.json",
    documents_total: rows.length,
    documents_pass: rows.filter(r => r.pass).length,
    documents_fail: rows.filter(r => !r.pass).length,
    pass: rows.length > 0 && rows.every(r => r.pass),
    rows
  };

  const md = [
    "# Arweave → GitHub Mirror Coverage",
    "",
    `Generated: ${audit.generated_at}`,
    "",
    "| Label | TXID | GitHub mirror | SHA-256 | Size | Status |",
    "|---|---|---|---|---:|---|",
    ...rows.map(r =>
      `| ${String(r.label).replace(/\|/g, "\\|")} | \`${r.txid}\` | \`${r.local_path}\` | ${r.sha256_match ? "PASS" : "FAIL"} | ${r.actual_size ?? ""} | ${r.pass ? "PASS" : "FAIL"}${r.error ? `: ${String(r.error).replace(/\|/g, "\\|")}` : ""} |`
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
