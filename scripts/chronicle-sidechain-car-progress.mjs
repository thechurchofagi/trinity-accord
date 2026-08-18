import fs from 'fs';
import path from 'path';
import { execFileSync } from 'child_process';

function nowIso() { return new Date().toISOString(); }

export function updateCarProgressFromLine(state, line) {
  let m = line.match(/\[EVIDENCE PROGRESS\]\s+(\d+)\/(\d+)\s+origin=([^\s]+)\s+car=([^\s]+)/);
  if (m) {
    state.records_completed = Number(m[1]);
    state.records_expected = Number(m[2]);
    state.last_origin = m[3];
    state.last_metadata_car_status = m[4];
    state.last_event_at = nowIso();
    return true;
  }
  const counters = [
    ['[CAR WHOLE-DAG VERIFIED]', 'whole_dag_verified'],
    ['[CAR BLOCKWISE COMPLETE]', 'blockwise_completed'],
    ['[CAR HISTORICAL CHUNK VERIFIED]', 'historical_chunk_verified'],
    ['[CAR KUBO BLOCK VERIFIED]', 'kubo_blocks_verified'],
    ['[CAR LASSIE ROOT REUSE]', 'lassie_root_reuse'],
    ['[CAR RAW BLOCK VERIFIED]', 'raw_blocks_verified'],
    ['[CAR CACHE REJECTED]', 'cache_rejected_events'],
    ['[CAR FAILED]', 'car_failed_events'],
  ];
  for (const [needle, key] of counters) {
    if (line.includes(needle)) {
      state[key] = (state[key] || 0) + 1;
      state.last_event = needle.slice(1, -1).toLowerCase().replaceAll(' ', '_');
      state.last_event_at = nowIso();
      return true;
    }
  }
  return false;
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
    schema: 'trinity-accord/chronicle-sidechain-car-live-progress/v1',
    phase: 'car_l1',
    status: 'running',
    run_id: process.env.GITHUB_RUN_ID || null,
    run_attempt: process.env.GITHUB_RUN_ATTEMPT || null,
    source_sha: process.env.GITHUB_SHA || null,
    evidence_concurrency: Number(process.env.CHRONICLE_EVIDENCE_CONCURRENCY || 0) || null,
    car_block_concurrency: Number(process.env.CHRONICLE_CAR_BLOCK_CONCURRENCY || 0) || null,
    cache_audit: audit,
    records_completed: 0,
    records_expected: 217,
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
          'user-agent': 'trinity-accord-sidechain-car-progress/1.0',
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
  const timer = setInterval(() => { publish().catch(() => {}); }, intervalMs);
  timer.unref();
  return {
    state,
    observe,
    publish,
    async finish(status) {
      state.status = status;
      state.finished_at = nowIso();
      clearInterval(timer);
      await publish();
    },
  };
}
