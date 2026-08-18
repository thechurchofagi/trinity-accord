import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';
import { sanitizeEndpoint, sanitizeTraceText } from './chronicle-sidechain-car-trace.mjs';

function nowIso() { return new Date().toISOString(); }

export function updateCarProgressFromLine(state, line) {
  let m = line.match(/\[EVIDENCE START\]\s+(\d+)\/(\d+)\s+worker=(\d+)\s+([^\s]+)\s+([^\s]+)\s+#(.+)$/);
  if (m) {
    state.records_expected = Number(m[2]);
    state.workers ||= {};
    state.workers[m[3]] = {
      record_index: Number(m[1]),
      chain: m[4],
      contract: m[5],
      token_id: m[6],
      started_at: nowIso(),
    };
    state.last_event = 'evidence_start';
    state.last_event_at = nowIso();
    return true;
  }

  m = line.match(/\[EVIDENCE PROGRESS\]\s+(\d+)\/(\d+)\s+origin=([^\s]+)\s+car=([^\s]+)/);
  if (m) {
    state.records_completed = Number(m[1]);
    state.records_expected = Number(m[2]);
    state.last_origin = m[3];
    state.last_metadata_car_status = m[4];
    state.last_event = 'evidence_progress';
    state.last_event_at = nowIso();
    return true;
  }

  m = line.match(/\[CAR FAILED\]\s+cid=([^\s]+)/);
  if (m) {
    state.car_failed_events = (state.car_failed_events || 0) + 1;
    state.failed_cids ||= [];
    if (!state.failed_cids.includes(m[1]) && state.failed_cids.length < 40) state.failed_cids.push(m[1]);
    state.last_cid = m[1];
    state.last_event = 'car_failed';
    state.last_event_detail = sanitizeTraceText(line);
    state.last_event_at = nowIso();
    return true;
  }

  const counters = [
    ['[CAR WHOLE-DAG VERIFIED]', 'whole_dag_verified'],
    ['[CAR BLOCKWISE COMPLETE]', 'blockwise_completed'],
    ['[CAR HISTORICAL CHUNK VERIFIED]', 'historical_chunk_verified'],
    ['[CAR KUBO BLOCK VERIFIED]', 'kubo_blocks_verified'],
    ['[CAR LASSIE START]', 'lassie_starts'],
    ['[CAR LASSIE ROOT REUSE]', 'lassie_root_reuse'],
    ['[CAR RAW BLOCK VERIFIED]', 'raw_blocks_verified'],
    ['[CAR CACHE REJECTED]', 'cache_rejected_events'],
  ];
  for (const [needle, key] of counters) {
    if (line.includes(needle)) {
      state[key] = (state[key] || 0) + 1;
      const cid = line.match(/\bcid=([^\s]+)/)?.[1];
      if (cid) state.last_cid = cid;
      state.last_event = needle.slice(1, -1).toLowerCase().replaceAll(' ', '_');
      state.last_event_detail = sanitizeTraceText(line);
      state.last_event_at = nowIso();
      return true;
    }
  }
  return false;
}

export function updateCarProgressFromEvent(state, event) {
  if (!event || typeof event !== 'object') return false;
  const name = String(event.event || 'car_event');
  const row = {
    timestamp: nowIso(),
    event: name,
    status: event.status || null,
    root_cid: event.root_cid || null,
    endpoint: event.endpoint ? sanitizeEndpoint(event.endpoint) : null,
    http_status: event.http_status ?? null,
    elapsed_ms: event.elapsed_ms ?? null,
    error: event.error ? sanitizeTraceText(event.error) : null,
  };
  state.last_recovery_event = row;
  state.last_event = name;
  state.last_event_at = row.timestamp;
  if (row.root_cid) state.last_cid = row.root_cid;
  state.recovery_event_counts ||= {};
  state.recovery_event_counts[name] = (state.recovery_event_counts[name] || 0) + 1;
  state.recent_recovery_events ||= [];
  state.recent_recovery_events.push(row);
  if (state.recent_recovery_events.length > 20) state.recent_recovery_events.splice(0, state.recent_recovery_events.length - 20);
  if (row.status === 'failure') {
    state.recent_recovery_failures ||= [];
    state.recent_recovery_failures.push(row);
    if (state.recent_recovery_failures.length > 20) state.recent_recovery_failures.splice(0, state.recent_recovery_failures.length - 20);
  }
  return true;
}

function checkoutAuthorization() {
  try {
    const raw = execFileSync('git', ['config', '--local', '--get', 'http.https://github.com/.extraheader'], { encoding: 'utf8' }).trim();
    const colon = raw.indexOf(':');
    if (colon < 0 || raw.slice(0, colon).trim().toLowerCase() !== 'authorization') return null;
    return raw.slice(colon + 1).trim();
  } catch {
    return null;
  }
}

export function createCarProgress({ out, audit, intervalMs = 30000 }) {
  const state = {
    schema: 'trinity-accord/chronicle-sidechain-car-live-progress/v3',
    phase: 'car_l1',
    status: 'running',
    run_id: process.env.GITHUB_RUN_ID || null,
    run_attempt: process.env.GITHUB_RUN_ATTEMPT || null,
    source_sha: process.env.GITHUB_SHA || null,
    evidence_concurrency: Number(process.env.CHRONICLE_EVIDENCE_CONCURRENCY || 0) || null,
    car_block_concurrency: Number(process.env.CHRONICLE_CAR_BLOCK_CONCURRENCY || 0) || null,
    whole_dag_endpoint_limit: Number(process.env.CHRONICLE_CAR_WHOLE_DAG_ENDPOINT_LIMIT || 0) || null,
    cache_audit: audit,
    records_completed: 0,
    records_expected: 217,
    workers: {},
    failed_cids: [],
    recovery_event_counts: {},
    recent_recovery_events: [],
    recent_recovery_failures: [],
    started_at: nowIso(),
    published_at: null,
  };
  const file = path.join(out, 'runtime', 'CAR-PROGRESS.json');
  const repo = process.env.GITHUB_REPOSITORY;
  const issue = process.env.CHRONICLE_PROGRESS_ISSUE || '1020';
  const authorization = checkoutAuthorization();

  const write = () => {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    const tmp = `${file}.tmp`;
    fs.writeFileSync(tmp, JSON.stringify(state, null, 2) + '\n');
    fs.renameSync(tmp, file);
  };

  const publish = async () => {
    state.published_at = nowIso();
    write();
    if (!repo || !authorization || !state.run_id) return false;
    const runUrl = `https://github.com/${repo}/actions/runs/${state.run_id}`;
    const body = [
      '# Sidechain evidence live progress', '',
      '> Operational telemetry only. This does not amend Canon or evidence contents.', '',
      `- Repository: \`${repo}\``,
      `- Run: \`${state.run_id}\` — ${runUrl}`,
      `- Source SHA: \`${state.source_sha || 'unknown'}\``,
      '- Phase: `car_l1`',
      `- Status: \`${state.status}\``,
      `- Published heartbeat: \`${state.published_at}\``, '',
      '```json', JSON.stringify(state, null, 2), '```',
    ].join('\n');
    try {
      const response = await fetch(`https://api.github.com/repos/${repo}/issues/${issue}`, {
        method: 'PATCH',
        headers: {
          authorization,
          accept: 'application/vnd.github+json',
          'content-type': 'application/json',
          'user-agent': 'trinity-accord-sidechain-car-progress/3.0',
          'x-github-api-version': '2022-11-28',
        },
        body: JSON.stringify({ body }),
      });
      return response.ok;
    } catch {
      return false;
    }
  };

  const observe = line => {
    if (updateCarProgressFromLine(state, line)) write();
  };
  const observeEvent = event => {
    if (updateCarProgressFromEvent(state, event)) write();
  };
  const timer = setInterval(() => { publish().catch(() => {}); }, intervalMs);
  timer.unref();
  return {
    state,
    observe,
    observeEvent,
    publish,
    async finish(status) {
      state.status = status;
      state.finished_at = nowIso();
      clearInterval(timer);
      await publish();
    },
  };
}
