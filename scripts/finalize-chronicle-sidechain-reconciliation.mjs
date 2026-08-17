#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const OUT = process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan';
const FORMATION_IDENTITY_METHODS = new Set(['exact_metadata_cid', 'exact_semantic_metadata']);
const sha256 = buf => crypto.createHash('sha256').update(buf).digest('hex');
const writeJson = (file, value) => fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');
const sorted = values => [...values].sort();

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

function earliest(items, selector) {
  return items.map(selector).filter(Boolean).filter(row => Number(row.timestamp_unix) > 0)
    .sort((a, b) => Number(a.timestamp_unix) - Number(b.timestamp_unix))[0] || null;
}

function candidateFingerprint(row) {
  if (row?.match?.metadata_fingerprint) return `metadata-json:${row.match.metadata_fingerprint}`;
  if (row?.match?.metadata_cids?.length) return `metadata-cid:${sorted(row.match.metadata_cids).join('|')}`;
  if (row?.match?.media_cids?.length) return `media-cids:${sorted(row.match.media_cids).join('|')}`;
  return `coordinate:${row.chain}|${row.contract}|${row.token_id}`;
}

function addToMap(map, key, value) {
  if (!map.has(key)) map.set(key, []);
  map.get(key).push(value);
}

function renderMarkdown(result) {
  const c = result.counts;
  const f = result.formation_assessment;
  return `# Chronicle sidechain logical reconciliation\n\n` +
    `Evidence-only audit. This file does **not** amend Canon or redefine Chronicle membership by itself.\n\n` +
    `## Counts\n\n` +
    `- Existing preservation corpus entries: **${c.existing_index_records}**\n` +
    `- Sidechain technical coordinates: **${c.sidechain_coordinates}**\n` +
    `- Coordinates strongly mapped to existing records: **${c.matched_existing_coordinates}**\n` +
    `- Unique existing logical records represented: **${c.mapped_existing_logical_records}**\n` +
    `- Duplicate sidechain representations beyond the first mapping per logical record: **${c.additional_duplicate_sidechain_coordinates}**\n` +
    `- Candidate-new technical coordinates: **${c.candidate_new_coordinates}**\n` +
    `- Candidate-new logical groups after semantic/content grouping: **${c.candidate_new_logical_groups}**\n` +
    `- Unresolved technical coordinates: **${c.unresolved_coordinates}**\n\n` +
    `## Formation assessment\n\n` +
    `- Previously established start: **${f.known_formation_start}**\n` +
    `- Formation-qualified identity methods: **${f.qualifying_identity_methods.join(', ')}**\n` +
    `- Conclusion: **${f.conclusion}**\n` +
    `- Qualified revised start: **${f.qualified_revised_start || 'none'}**\n\n` +
    `Exact metadata identity plus independently timestamped mint evidence is required to move the formation start. Media-CID overlap can support duplicate mapping but cannot by itself revise chronology. Same contract/token coordinates across chains remain weak hints only.\n`;
}

const reconciliationPath = path.join(OUT, 'RECONCILIATION.json');
const reconciliation = requireJson(reconciliationPath);
const matched = Array.isArray(reconciliation.matched_existing) ? reconciliation.matched_existing : [];
const candidates = Array.isArray(reconciliation.candidate_new) ? reconciliation.candidate_new : [];

// Re-group candidate-new coordinates by exact semantic metadata before content-address fallback.
const candidateGroups = new Map();
for (const row of candidates) addToMap(candidateGroups, candidateFingerprint(row), row);
reconciliation.counts.candidate_new_logical_groups = candidateGroups.size;
reconciliation.counts.candidate_new_duplicate_coordinates = [...candidateGroups.values()]
  .reduce((sum, group) => sum + Math.max(0, group.length - 1), 0);
reconciliation.candidate_new_groups = [...candidateGroups.entries()].map(([fingerprint, group]) => ({
  fingerprint,
  coordinates: group.map(row => ({ chain: row.chain, contract: row.contract, token_id: row.token_id, first_seen: row.first_seen, first_mint: row.first_mint, name: row.name })),
}));

// Formation history is intentionally stricter than duplicate mapping: media-only matches cannot move the start.
const formation = reconciliation.formation_assessment || {};
const knownStartMs = Date.parse(formation.known_formation_start || '');
if (!Number.isFinite(knownStartMs)) throw new Error('fail-closed: invalid reconciliation known_formation_start');
const qualified = matched.filter(row => FORMATION_IDENTITY_METHODS.has(row?.match?.method));
const earlierQualifiedMints = qualified.filter(row => row.first_mint && Number(row.first_mint.timestamp_unix) * 1000 < knownStartMs);
const earlierQualifiedOccurrences = qualified.filter(row => row.first_seen_unix && Number(row.first_seen_unix) * 1000 < knownStartMs);
const earlierCandidateMints = candidates.filter(row => row.first_mint && Number(row.first_mint.timestamp_unix) * 1000 < knownStartMs);
const earliestQualifiedMint = earliest(qualified, row => row.first_mint ? {
  ...row.first_mint, chain: row.chain, contract: row.contract, token_id: row.token_id,
  existing_key: row.match.existing_key, match_method: row.match.method,
} : null);
let conclusion = 'unchanged_no_qualified_earlier_record';
let qualifiedRevisedStart = null;
if (earlierQualifiedMints.length) {
  const earliestEarlier = earliest(earlierQualifiedMints, row => ({
    ...row.first_mint, chain: row.chain, contract: row.contract, token_id: row.token_id,
    existing_key: row.match.existing_key, match_method: row.match.method,
  }));
  conclusion = 'move_start_to_earliest_metadata_identified_mint';
  qualifiedRevisedStart = earliestEarlier?.timestamp || null;
} else if (earlierQualifiedOccurrences.length) {
  conclusion = 'unchanged_earlier_metadata_identified_address_occurrence_without_mint_proof';
} else if (earlierCandidateMints.length) {
  conclusion = 'unchanged_earlier_candidate_requires_membership_proof';
}
reconciliation.formation_assessment = {
  ...formation,
  qualifying_identity_methods: [...FORMATION_IDENTITY_METHODS],
  earliest_qualified_identity_mint: earliestQualifiedMint,
  earlier_qualified_existing_mints: earlierQualifiedMints.length,
  earlier_qualified_existing_address_occurrences: earlierQualifiedOccurrences.length,
  earlier_candidate_new_mints: earlierCandidateMints.length,
  conclusion,
  qualified_revised_start: qualifiedRevisedStart,
  rule: 'Formation chronology can move only when metadata-level identity (exact content CID or exact JSON semantics) links the sidechain occurrence to a Chronicle record and an earlier zero-address mint independently timestamps creation. Media-only and coordinate-only evidence cannot move the start.',
};
writeJson(reconciliationPath, reconciliation);
fs.writeFileSync(path.join(OUT, 'RECONCILIATION.md'), renderMarkdown(reconciliation));

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
