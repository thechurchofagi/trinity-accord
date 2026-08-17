#!/usr/bin/env node
import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

const OUT = process.env.CHRONICLE_OUT || 'artifacts/chronicle-sidechain-scan';
const INDEX_PATH = process.env.CHRONICLE_EXISTING_INDEX || 'token_index.json';
const RECOVERED_PATH = process.env.CHRONICLE_RECOVERED_TOKENS || path.join(OUT, 'recovered-tokens.json');
const KNOWN_START = process.env.CHRONICLE_KNOWN_FORMATION_START || '2024-03-16T08:02:59Z';
const EXPECTED_EXISTING = Number(process.env.CHRONICLE_EXPECTED_EXISTING_RECORDS || 175);
const FETCH_TIMEOUT_MS = Number(process.env.CHRONICLE_RECONCILE_FETCH_TIMEOUT_MS || 12000);
const FETCH_CONCURRENCY = Number(process.env.CHRONICLE_RECONCILE_FETCH_CONCURRENCY || 8);
const ZERO = '0x0000000000000000000000000000000000000000';

const sha256 = value => crypto.createHash('sha256').update(value).digest('hex');
const writeJson = (file, value) => { fs.mkdirSync(path.dirname(file), { recursive: true }); fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n'); };
const uniq = values => [...new Set(values.filter(Boolean))];
const sorted = values => [...values].sort();

function cidKey(cid) {
  if (!cid) return null;
  return cid.startsWith('Qm') ? cid : cid.toLowerCase();
}

function extractCids(value) {
  if (typeof value !== 'string') return [];
  const matches = value.match(/(?:Qm[1-9A-HJ-NP-Za-km-z]{44}|b[a-z2-7]{20,})/g) || [];
  return uniq(matches.map(cidKey));
}

function canonicalJson(value) {
  if (Array.isArray(value)) return `[${value.map(canonicalJson).join(',')}]`;
  if (value && typeof value === 'object') {
    return `{${Object.keys(value).sort().map(key => `${JSON.stringify(key)}:${canonicalJson(value[key])}`).join(',')}}`;
  }
  return JSON.stringify(value);
}

function metadataFingerprint(metadata) {
  if (!metadata || typeof metadata !== 'object' || Array.isArray(metadata)) return null;
  return sha256(Buffer.from(canonicalJson(metadata), 'utf8'));
}

function metadataLooksChronicle(metadata) {
  if (!metadata || typeof metadata !== 'object') return false;
  const text = JSON.stringify(metadata).toLowerCase();
  return ['asimilestones', 'asi milestones', 'first chronicle', 'pre-asi'].some(marker => text.includes(marker));
}

function allMetadataCids(token) {
  return uniq([
    ...extractCids(token?.token_uri?.uri),
    ...extractCids(token?.metadata_mirror?.original_uri),
    ...extractCids(token?.metadata_mirror?.resolved_url),
  ]);
}

function allMediaCids(token) {
  const values = [];
  for (const key of ['image', 'image_url', 'animation_url', 'animation', 'video', 'audio']) {
    if (typeof token?.metadata?.[key] === 'string') values.push(token.metadata[key]);
  }
  for (const item of token?.media || []) {
    if (typeof item?.original_uri === 'string') values.push(item.original_uri);
    if (typeof item?.resolved_url === 'string') values.push(item.resolved_url);
  }
  return uniq(values.flatMap(extractCids));
}

function firstMint(token) {
  const mints = (token?.transfers || []).filter(row => String(row?.from || '').toLowerCase() === ZERO && row?.timestamp_unix);
  mints.sort((a, b) => Number(a.timestamp_unix) - Number(b.timestamp_unix));
  const row = mints[0];
  if (!row) return null;
  return {
    timestamp: row.timestamp || new Date(Number(row.timestamp_unix) * 1000).toISOString(),
    timestamp_unix: Number(row.timestamp_unix), block_number: row.block_number || null,
    transaction_hash: row.transaction_hash || null, to: row.to || null,
  };
}

function buildExisting(index) {
  const entries = [];
  for (const [contract, tokens] of Object.entries(index || {})) {
    for (const [tokenId, value] of Object.entries(tokens || {})) {
      const mediaCids = uniq((value?.media || []).map(item => cidKey(item?.root_cid)));
      entries.push({
        key: `${contract.toLowerCase()}|${tokenId}`,
        contract: contract.toLowerCase(), token_id: tokenId,
        metadata_cid: cidKey(value?.metadata?.root_cid), media_cids: sorted(mediaCids),
        metadata_url: value?.metadata?.root_cid ? `ipfs://${value.metadata.root_cid}` : null,
      });
    }
  }
  return entries;
}

function addToMap(map, key, value) {
  if (!key) return;
  if (!map.has(key)) map.set(key, []);
  map.get(key).push(value);
}

async function fetchJsonCid(cid) {
  const urls = [`https://dweb.link/ipfs/${cid}`, `https://ipfs.io/ipfs/${cid}`];
  const attempts = [];
  for (const url of urls) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
    try {
      const response = await fetch(url, { signal: controller.signal, headers: { 'user-agent': 'trinity-accord-chronicle-reconciliation/1.0' } });
      const text = await response.text();
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = JSON.parse(text);
      clearTimeout(timer);
      return { ok: true, data, url, sha256: sha256(Buffer.from(text, 'utf8')), attempts };
    } catch (error) {
      clearTimeout(timer);
      attempts.push({ url, error: String(error?.message || error) });
    }
  }
  return { ok: false, attempts };
}

async function mapConcurrent(items, concurrency, fn) {
  const out = new Array(items.length);
  let cursor = 0;
  async function worker() {
    while (true) {
      const index = cursor++;
      if (index >= items.length) return;
      out[index] = await fn(items[index], index);
    }
  }
  await Promise.all(Array.from({ length: Math.max(1, Math.min(concurrency, items.length || 1)) }, worker));
  return out;
}

function chooseMatch(token, maps, semanticMap) {
  const metadataCids = allMetadataCids(token);
  const mediaCids = allMediaCids(token);
  const hints = [];

  const exactMetadata = uniq(metadataCids.flatMap(cid => maps.metadata.get(cid) || []));
  if (exactMetadata.length === 1) return { existing_key: exactMetadata[0], method: 'exact_metadata_cid', strength: 'definitive_content_address', metadata_cids: metadataCids, media_cids: mediaCids, hints };
  if (exactMetadata.length > 1) hints.push({ type: 'ambiguous_metadata_cid', candidates: exactMetadata });

  const fp = metadataFingerprint(token?.metadata);
  const semantic = fp ? uniq(semanticMap.get(fp) || []) : [];
  if (semantic.length === 1) return { existing_key: semantic[0], method: 'exact_semantic_metadata', strength: 'strong_exact_json_semantics', metadata_cids: metadataCids, media_cids: mediaCids, metadata_fingerprint: fp, hints };
  if (semantic.length > 1) hints.push({ type: 'ambiguous_semantic_metadata', candidates: semantic });

  if (mediaCids.length) {
    const exactSignature = maps.mediaSignature.get(sorted(mediaCids).join('|')) || [];
    if (exactSignature.length === 1) return { existing_key: exactSignature[0], method: 'exact_media_cid_set', strength: 'strong_content_set', metadata_cids: metadataCids, media_cids: mediaCids, metadata_fingerprint: fp, hints };
    if (exactSignature.length > 1) hints.push({ type: 'ambiguous_media_cid_set', candidates: exactSignature });

    const perCid = mediaCids.map(cid => new Set(maps.media.get(cid) || [])).filter(set => set.size);
    if (perCid.length >= 2) {
      const intersection = [...perCid[0]].filter(key => perCid.every(set => set.has(key)));
      if (intersection.length === 1) return { existing_key: intersection[0], method: 'multi_media_cid_consensus', strength: 'strong_multi_content_link', metadata_cids: metadataCids, media_cids: mediaCids, metadata_fingerprint: fp, hints };
      if (intersection.length > 1) hints.push({ type: 'ambiguous_multi_media_cid', candidates: intersection });
    }
    const mediaCandidates = uniq(mediaCids.flatMap(cid => maps.media.get(cid) || []));
    if (mediaCandidates.length) hints.push({ type: 'media_cid_overlap', candidates: mediaCandidates });
  }

  const coordinateKey = `${String(token.contract || '').toLowerCase()}|${token.token_id}`;
  if (maps.byKey.has(coordinateKey)) hints.push({ type: 'same_contract_token_coordinate', candidates: [coordinateKey], note: 'weak cross-chain heuristic only' });
  return { existing_key: null, method: null, strength: null, metadata_cids: metadataCids, media_cids: mediaCids, metadata_fingerprint: fp, hints };
}

function earliest(items, selector) {
  const rows = items.map(selector).filter(Boolean).filter(x => Number(x.timestamp_unix) > 0).sort((a, b) => Number(a.timestamp_unix) - Number(b.timestamp_unix));
  return rows[0] || null;
}

function logicalCandidateFingerprint(item) {
  if (item.match.metadata_cids.length) return `metadata-cid:${sorted(item.match.metadata_cids).join('|')}`;
  if (item.match.metadata_fingerprint) return `metadata-json:${item.match.metadata_fingerprint}`;
  if (item.match.media_cids.length) return `media-cids:${sorted(item.match.media_cids).join('|')}`;
  return `coordinate:${item.chain}|${item.contract}|${item.token_id}`;
}

function markdown(result) {
  const c = result.counts, f = result.formation_assessment;
  return `# Chronicle sidechain logical reconciliation\n\n` +
    `Evidence-only audit. This file does **not** amend Canon or redefine Chronicle membership by itself.\n\n` +
    `## Counts\n\n` +
    `- Existing preservation corpus entries: **${c.existing_index_records}**\n` +
    `- Sidechain technical coordinates: **${c.sidechain_coordinates}**\n` +
    `- Coordinates strongly mapped to existing records: **${c.matched_existing_coordinates}**\n` +
    `- Unique existing logical records represented: **${c.mapped_existing_logical_records}**\n` +
    `- Duplicate sidechain representations beyond the first mapping per logical record: **${c.additional_duplicate_sidechain_coordinates}**\n` +
    `- Candidate-new technical coordinates: **${c.candidate_new_coordinates}**\n` +
    `- Candidate-new logical groups after content-level grouping: **${c.candidate_new_logical_groups}**\n` +
    `- Unresolved technical coordinates: **${c.unresolved_coordinates}**\n\n` +
    `## Formation assessment\n\n` +
    `- Previously established start: **${f.known_formation_start}**\n` +
    `- Conclusion: **${f.conclusion}**\n` +
    `- Qualified revised start: **${f.qualified_revised_start || 'none'}**\n\n` +
    `A chain occurrence is not automatically a logical Chronicle record. Exact metadata CID is the highest-priority identity signal; exact semantic metadata and multi-content CID evidence are secondary. Same contract/token coordinate across chains remains a weak hint only.\n`;
}

async function main() {
  if (!Number.isFinite(EXPECTED_EXISTING) || EXPECTED_EXISTING < 1) throw new Error(`invalid expected record count ${EXPECTED_EXISTING}`);
  const knownStartMs = Date.parse(KNOWN_START);
  if (!Number.isFinite(knownStartMs)) throw new Error(`invalid known formation start ${KNOWN_START}`);
  const index = JSON.parse(fs.readFileSync(INDEX_PATH, 'utf8'));
  const recovered = JSON.parse(fs.readFileSync(RECOVERED_PATH, 'utf8'));
  if (!Array.isArray(recovered)) throw new Error('recovered-tokens.json must be an array');
  const existing = buildExisting(index);
  if (existing.length !== EXPECTED_EXISTING) throw new Error(`fail-closed: expected ${EXPECTED_EXISTING} existing preservation records, found ${existing.length}`);

  const maps = { byKey: new Map(), metadata: new Map(), media: new Map(), mediaSignature: new Map() };
  for (const entry of existing) {
    maps.byKey.set(entry.key, entry);
    addToMap(maps.metadata, entry.metadata_cid, entry.key);
    for (const cid of entry.media_cids) addToMap(maps.media, cid, entry.key);
    if (entry.media_cids.length) addToMap(maps.mediaSignature, entry.media_cids.join('|'), entry.key);
  }

  const sideMetadataFingerprints = new Set(recovered.map(token => metadataFingerprint(token?.metadata)).filter(Boolean));
  const existingToFetch = existing.filter(entry => entry.metadata_cid);
  console.log(`[RECONCILE] sidechain=${recovered.length} existing=${existing.length} fetching_existing_metadata=${existingToFetch.length}`);
  const fetched = await mapConcurrent(existingToFetch, FETCH_CONCURRENCY, async entry => ({ entry, result: await fetchJsonCid(entry.metadata_cid) }));
  const semanticMap = new Map();
  let fetchedOk = 0;
  for (const { entry, result } of fetched) {
    if (!result.ok) continue;
    fetchedOk++;
    const fp = metadataFingerprint(result.data);
    if (fp && sideMetadataFingerprints.has(fp)) addToMap(semanticMap, fp, entry.key);
  }

  const rows = recovered.map(token => {
    const match = chooseMatch(token, maps, semanticMap);
    const mint = firstMint(token);
    const projectMarker = metadataLooksChronicle(token?.metadata);
    let classification = 'unresolved';
    if (match.existing_key) classification = 'matched_existing';
    else if (projectMarker) classification = 'candidate_new';
    return {
      classification, chain: token.chain, chain_id: token.chain_id, contract: token.contract, token_id: token.token_id,
      standard: token.standard, first_seen: token.first_seen || null, first_seen_unix: Number(token.first_seen_unix || 0),
      first_seen_block: token.first_seen_block || null, first_mint: mint, name: token?.metadata?.name || null,
      project_marker: projectMarker, match,
    };
  });

  const matched = rows.filter(row => row.classification === 'matched_existing');
  const candidates = rows.filter(row => row.classification === 'candidate_new');
  const unresolved = rows.filter(row => row.classification === 'unresolved');
  const matchedGroups = new Map();
  for (const row of matched) addToMap(matchedGroups, row.match.existing_key, row);
  const candidateGroups = new Map();
  for (const row of candidates) addToMap(candidateGroups, logicalCandidateFingerprint(row), row);
  const extraMatched = [...matchedGroups.values()].reduce((sum, group) => sum + Math.max(0, group.length - 1), 0);
  const extraCandidate = [...candidateGroups.values()].reduce((sum, group) => sum + Math.max(0, group.length - 1), 0);

  const earliestTechnical = earliest(rows, row => row.first_seen_unix ? { timestamp: row.first_seen, timestamp_unix: row.first_seen_unix, chain: row.chain, contract: row.contract, token_id: row.token_id, classification: row.classification } : null);
  const earliestMatchedMint = earliest(matched, row => row.first_mint ? { ...row.first_mint, chain: row.chain, contract: row.contract, token_id: row.token_id, existing_key: row.match.existing_key, match_method: row.match.method } : null);
  const earlierMatchedMints = matched.filter(row => row.first_mint && Number(row.first_mint.timestamp_unix) * 1000 < knownStartMs);
  const earlierMatchedOccurrences = matched.filter(row => row.first_seen_unix && Number(row.first_seen_unix) * 1000 < knownStartMs);
  const earlierCandidateMints = candidates.filter(row => row.first_mint && Number(row.first_mint.timestamp_unix) * 1000 < knownStartMs);

  let conclusion = 'unchanged_no_qualified_earlier_record';
  let qualifiedRevisedStart = null;
  if (earlierMatchedMints.length) {
    const earliestQualified = earliest(earlierMatchedMints, row => ({ ...row.first_mint, chain: row.chain, contract: row.contract, token_id: row.token_id, existing_key: row.match.existing_key, match_method: row.match.method }));
    conclusion = 'move_start_to_earliest_matched_existing_mint';
    qualifiedRevisedStart = earliestQualified?.timestamp || null;
  } else if (earlierMatchedOccurrences.length) {
    conclusion = 'unchanged_earlier_matched_address_occurrence_without_mint_proof';
  } else if (earlierCandidateMints.length) {
    conclusion = 'unchanged_earlier_candidate_requires_membership_proof';
  }

  const result = {
    schema: 'trinity-accord/chronicle-sidechain-logical-reconciliation/v1',
    generated_at: new Date().toISOString(),
    inputs: { existing_index: INDEX_PATH, recovered_tokens: RECOVERED_PATH, expected_existing_records: EXPECTED_EXISTING },
    identity_rules: [
      'Exact metadata content CID uniquely identifying one existing preservation entry is definitive content-address evidence.',
      'Exact canonical JSON semantics uniquely identifying one existing entry is strong evidence when the preserved metadata CID can be independently fetched.',
      'An exact media CID set, or at least two media CIDs converging uniquely on one entry, is strong content-link evidence.',
      'Same contract+token coordinate across chains is a weak hint only and never sufficient by itself.',
      'Candidate-new means project-marked metadata lacking a strong mapping; it is not automatically a new Chronicle member.',
    ],
    counts: {
      existing_index_records: existing.length,
      sidechain_coordinates: rows.length,
      matched_existing_coordinates: matched.length,
      mapped_existing_logical_records: matchedGroups.size,
      duplicate_representation_coordinates_relative_to_existing_corpus: matched.length,
      additional_duplicate_sidechain_coordinates: extraMatched,
      candidate_new_coordinates: candidates.length,
      candidate_new_logical_groups: candidateGroups.size,
      candidate_new_duplicate_coordinates: extraCandidate,
      unresolved_coordinates: unresolved.length,
    },
    existing_metadata_fetch: { attempted: fetched.length, ok: fetchedOk, failed: fetched.length - fetchedOk },
    formation_assessment: {
      known_formation_start: new Date(knownStartMs).toISOString(),
      earliest_technical_sidechain_address_occurrence: earliestTechnical,
      earliest_matched_existing_mint: earliestMatchedMint,
      earlier_matched_existing_mints: earlierMatchedMints.length,
      earlier_matched_existing_address_occurrences: earlierMatchedOccurrences.length,
      earlier_candidate_new_mints: earlierCandidateMints.length,
      conclusion,
      qualified_revised_start: qualifiedRevisedStart,
      rule: 'Only independently timestamped evidence that strongly identifies a Chronicle logical record can revise the formation start; a zero-address mint is treated as stronger creation evidence than a later address transfer.',
    },
    matched_existing: matched,
    candidate_new: candidates,
    unresolved,
    candidate_new_groups: [...candidateGroups.entries()].map(([fingerprint, group]) => ({ fingerprint, coordinates: group.map(row => ({ chain: row.chain, contract: row.contract, token_id: row.token_id, first_seen: row.first_seen, first_mint: row.first_mint, name: row.name })) })),
    evidence_boundary: 'This reconciliation is an evidence/audit layer only. It does not amend the three-inscription Canon, and technical chain occurrences do not become logical Chronicle records merely by being present on Polygon or Base.',
  };
  writeJson(path.join(OUT, 'RECONCILIATION.json'), result);
  fs.writeFileSync(path.join(OUT, 'RECONCILIATION.md'), markdown(result));
  console.log(`[RECONCILE DONE] matched_coordinates=${matched.length} mapped_logical=${matchedGroups.size} candidate_groups=${candidateGroups.size} unresolved=${unresolved.length} formation=${conclusion} revised_start=${qualifiedRevisedStart || 'none'}`);
}

await main();
