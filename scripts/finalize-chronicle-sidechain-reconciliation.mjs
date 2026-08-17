#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const OUT = process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan';
const sha256 = buf => crypto.createHash('sha256').update(buf).digest('hex');
const writeJson = (file, value) => fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');

function requireJson(file) {
  if (!fs.existsSync(file)) throw new Error(`fail-closed: missing ${file}`);
  return JSON.parse(fs.readFileSync(file, 'utf8'));
}

function buildManifest() {
  const manifest = [];
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      const file = path.join(dir, entry.name);
      const relative = path.relative(OUT, file).replaceAll('\\', '/');
      if (entry.isDirectory()) {
        if (relative === 'runtime') continue;
        walk(file);
      } else if (entry.name !== 'MANIFEST.sha256' && entry.name !== 'MANIFEST.sha256.json') {
        const buf = fs.readFileSync(file);
        manifest.push({ path: relative, bytes: buf.length, sha256: sha256(buf) });
      }
    }
  }
  walk(OUT);
  manifest.sort((a, b) => a.path.localeCompare(b.path));
  return manifest;
}

const reconciliation = requireJson(path.join(OUT, 'RECONCILIATION.json'));
const summaryPath = path.join(OUT, 'SUMMARY.json');
const summary = requireJson(summaryPath);
summary.logical_reconciliation = {
  schema: reconciliation.schema,
  counts: reconciliation.counts,
  existing_metadata_fetch: reconciliation.existing_metadata_fetch,
  formation_assessment: reconciliation.formation_assessment,
  artifacts: ['RECONCILIATION.json', 'RECONCILIATION.md'],
};
writeJson(summaryPath, summary);

const manifest = buildManifest();
writeJson(path.join(OUT, 'MANIFEST.sha256.json'), manifest);
fs.writeFileSync(path.join(OUT, 'MANIFEST.sha256'), manifest.map(item => `${item.sha256}  ${item.path}`).join('\n') + '\n');
console.log(`[RECONCILIATION FINALIZED] manifest_entries=${manifest.length} matched=${reconciliation.counts?.matched_existing_coordinates ?? 'unknown'} candidate_groups=${reconciliation.counts?.candidate_new_logical_groups ?? 'unknown'} unresolved=${reconciliation.counts?.unresolved_coordinates ?? 'unknown'} formation=${reconciliation.formation_assessment?.conclusion ?? 'unknown'}`);
