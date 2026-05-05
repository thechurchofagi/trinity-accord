// Echo submission Worker is deprecated.
// Current submission path is GitHub Issues + Claim Gate.
// This Worker exists only to return deprecation metadata and health/version responses.

const DEFAULT_ORIGIN = 'https://www.trinityaccord.org';
const WORKER_VERSION = '2026-05-05.1';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return handleCors(request, env);
    }

    if (request.method === 'GET' && url.pathname === '/') {
      return jsonResponse({
        ok: true,
        service: 'echo-submission-proxy',
        deprecated: true,
        routes: ['GET /health', 'GET /version', 'GET /submit-echo', 'POST /submit-echo'],
        current_submission_path: 'https://www.trinityaccord.org/echoes/submit/',
        claim_gate_docs: 'https://www.trinityaccord.org/docs/claim-gate/',
      }, 200, request, env);
    }

    if (request.method === 'GET' && url.pathname === '/health') {
      return jsonResponse({
        ok: true,
        service: 'echo-submission-proxy',
        version: getRuntimeVersion(env),
        ts: new Date().toISOString(),
      }, 200, request, env);
    }

    if (request.method === 'GET' && url.pathname === '/version') {
      return jsonResponse({
        ok: true,
        service: 'echo-submission-proxy',
        version: getRuntimeVersion(env),
      }, 200, request, env);
    }

    if (url.pathname === '/submit-echo') {
      return jsonResponse({
        ok: false,
        deprecated: true,
        error: 'Worker submission is deprecated.',
        current_submission_path: 'https://www.trinityaccord.org/echoes/submit/',
        claim_gate_required_for_technical_claims: true,
        claim_gate_docs: 'https://www.trinityaccord.org/docs/claim-gate/',
        github_issues: 'https://github.com/thechurchofagi/trinity-accord/issues',
      }, 410, request, env);
    }

    return jsonResponse({ error: 'Not found.', version: getRuntimeVersion(env) }, 404, request, env);
  },
};

function handleCors(request, env) {
  const origin = request.headers.get('Origin') || '';
  const allowOrigin = isAllowedOrigin(origin, env) ? origin : getPrimaryOrigin(env);

  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': allowOrigin,
      'Vary': 'Origin',
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
      'Access-Control-Max-Age': '86400',
      'X-Echo-Worker-Version': getRuntimeVersion(env),
    },
  });
}

function jsonResponse(data, status = 200, request = null, env = {}) {
  const origin = request?.headers.get('Origin') || '';
  const allowOrigin = isAllowedOrigin(origin, env) ? origin : getPrimaryOrigin(env);

  return new Response(JSON.stringify(data, null, 2), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': allowOrigin,
      'Vary': 'Origin',
      'X-Echo-Worker-Version': getRuntimeVersion(env),
    },
  });
}

function getAllowedOrigins(env) {
  const raw = env.ALLOWED_ORIGINS || DEFAULT_ORIGIN;
  const origins = raw.split(',').map((v) => v.trim()).filter(Boolean);
  const hasWww = origins.includes('https://www.trinityaccord.org');
  const hasApex = origins.includes('https://trinityaccord.org');
  if (hasWww && !hasApex) origins.push('https://trinityaccord.org');
  if (hasApex && !hasWww) origins.push('https://www.trinityaccord.org');
  return origins;
}

function getPrimaryOrigin(env) {
  return getAllowedOrigins(env)[0] || DEFAULT_ORIGIN;
}

function isAllowedOrigin(origin, env) {
  if (!origin) return true;
  try {
    const u = new URL(origin);
    if (u.protocol === 'https:' && (u.hostname === 'trinityaccord.org' || u.hostname === 'www.trinityaccord.org')) {
      return true;
    }
  } catch {
    // fall through to explicit allowlist
  }
  return getAllowedOrigins(env).includes(origin);
}

function getRuntimeVersion(env) {
  return env.WORKER_VERSION || WORKER_VERSION;
}
