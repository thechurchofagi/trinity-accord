import fs from 'fs';
import path from 'path';

const MAX_MESSAGE = 1600;

function nowIso() { return new Date().toISOString(); }

export function sanitizeEndpoint(value) {
  if (!value) return null;
  try {
    const url = value instanceof URL ? new URL(value.href) : new URL(String(value));
    url.username = '';
    url.password = '';
    const kept = new URLSearchParams();
    for (const key of ['format', 'dag-scope']) {
      const v = url.searchParams.get(key);
      if (v !== null) kept.set(key, v);
    }
    url.search = kept.toString();
    url.hash = '';
    return url.toString();
  } catch {
    return String(value).slice(0, MAX_MESSAGE)
      .replace(/([?&](?:token|key|api[_-]?key|auth|authorization|signature)=)[^&\s]+/gi, '$1[REDACTED]');
  }
}

export function sanitizeTraceText(value) {
  let text = String(value ?? '');
  text = text.replace(/https?:\/\/[^\s"'<>]+/g, raw => {
    const trailing = raw.match(/[),.;\]]+$/)?.[0] || '';
    const body = trailing ? raw.slice(0, -trailing.length) : raw;
    return `${sanitizeEndpoint(body)}${trailing}`;
  });
  text = text.replace(/\b(authorization|api[_-]?key|token|secret)\s*[:=]\s*[^\s,;]+/gi, '$1=[REDACTED]');
  return text.slice(0, MAX_MESSAGE);
}

export function classifyCarError(error) {
  const msg = String(error?.message || error || '').toLowerCase();
  if (/timeout|timed out|abort/.test(msg)) return 'timeout';
  if (/429|rate.?limit|too many requests/.test(msg)) return 'rate_limit';
  if (/404|not found/.test(msg)) return 'not_found';
  if (/5\d\d|bad gateway|service unavailable|gateway timeout/.test(msg)) return 'upstream_5xx';
  if (/truncated|varint|exceeds input|header length/.test(msg)) return 'car_truncated';
  if (/linked block missing|root block missing|root absent header/.test(msg)) return 'car_incomplete_dag';
  if (/unsupported block codec/.test(msg)) return 'car_unsupported_codec';
  if (/cid|multihash|digest/.test(msg)) return 'cid_integrity';
  if (/fetch|network|socket|econn|enotfound|dns/.test(msg)) return 'network';
  return 'other';
}

export function createCarTrace({ out }) {
  const runtime = path.join(out, 'runtime');
  fs.mkdirSync(runtime, { recursive: true });
  const file = path.join(runtime, 'CAR-TRACE.jsonl');
  fs.writeFileSync(file, '');
  let seq = 0;

  const emit = event => {
    const row = {
      schema: 'trinity-accord/chronicle-sidechain-car-trace/v1',
      seq: ++seq,
      timestamp: nowIso(),
      run_id: process.env.GITHUB_RUN_ID || null,
      run_attempt: process.env.GITHUB_RUN_ATTEMPT || null,
      source_sha: process.env.GITHUB_SHA || null,
      ...event,
    };
    if (row.endpoint) row.endpoint = sanitizeEndpoint(row.endpoint);
    if (row.message) row.message = sanitizeTraceText(row.message);
    if (row.error) row.error = sanitizeTraceText(row.error);
    fs.appendFileSync(file, `${JSON.stringify(row)}\n`);
    return row;
  };

  const observeConsole = (level, line) => {
    const message = sanitizeTraceText(line);
    let event = 'console';
    if (/^\[EVIDENCE START\]/.test(message)) event = 'evidence_start';
    else if (/^\[EVIDENCE PROGRESS\]/.test(message)) event = 'evidence_progress';
    else if (/^\[EVIDENCE COMPLETE\]/.test(message)) event = 'evidence_complete';
    else if (/^\[CAR FAILED\]/.test(message)) event = 'car_failed';
    else if (/^\[CAR /.test(message)) event = 'car_event';
    else if (/^\[L1 /.test(message)) event = 'l1_event';
    const cid = message.match(/\bcid=([^\s]+)/)?.[1] || null;
    emit({ event, level, ...(cid ? { root_cid: cid } : {}), message });
  };

  return {
    file,
    emit,
    observeConsole,
    phase(name, status, extra = {}) { return emit({ event: 'phase', phase: name, status, ...extra }); },
    failure(event, error, extra = {}) {
      return emit({ event, status: 'failure', error_class: classifyCarError(error), error: error?.message || String(error), ...extra });
    },
  };
}
