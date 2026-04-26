import { parseEmail, extractFieldsFromText } from './email-parser.js';
import { createGitHubIssue, issueTemplate } from './github.js';
import { checkRateLimit } from './rate-limit.js';
import { validateEchoFields, generateEchoId } from './validator.js';

const MAX_BODY_SIZE = 50_000;
const MAX_SUMMARY_SIZE = 300;
const MAX_RESPONSE_SIZE = 12_000;
const DEFAULT_ORIGIN = 'https://www.trinityaccord.org';
const WORKER_VERSION = '2026-04-26.2';

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);

    if (request.method === 'OPTIONS') {
      return handleCors(request, env);
    }

    if (request.method === 'GET' && url.pathname === '/submit-echo') {
      return new Response(FORM_HTML, {
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'X-Echo-Worker-Version': getRuntimeVersion(env),
        },
      });
    }

    if (request.method === 'GET' && url.pathname === '/') {
      return jsonResponse({
        ok: true,
        service: 'echo-submission-proxy',
        routes: ['GET /submit-echo', 'GET /health', 'GET /metrics', 'GET /version', 'POST /submit-echo'],
      }, 200, request, env);
    }

    if (request.method === 'GET' && url.pathname === '/health') {
      return jsonResponse({ ok: true, service: 'echo-submission-proxy', version: getRuntimeVersion(env), ts: new Date().toISOString() }, 200, request, env);
    }

    if (request.method === 'GET' && url.pathname === '/metrics') {
      const metrics = await readMetrics(env);
      return jsonResponse({ ok: true, metrics }, 200, request, env);
    }

    if (request.method === 'GET' && url.pathname === '/version') {
      return jsonResponse({ ok: true, service: 'echo-submission-proxy', version: getRuntimeVersion(env) }, 200, request, env);
    }

    if (request.method === 'POST' && url.pathname === '/submit-echo') {
      return handlePostSubmit(request, env, ctx);
    }

    return jsonResponse({ error: 'Not found. GET /submit-echo for form, POST /submit-echo to submit.', version: getRuntimeVersion(env) }, 404, request, env);
  },

  async email(message, env, ctx) {
    return handleEmail(message, env, ctx);
  },

  async scheduled(event, env, ctx) {
    ctx.waitUntil(cleanupRateLimit(env));
  },
};

async function handlePostSubmit(request, env, ctx) {
  const start = Date.now();
  const reqId = crypto.randomUUID();

  const contentLength = Number(request.headers.get('Content-Length') || '0');
  if (contentLength > MAX_BODY_SIZE) {
    return jsonResponse({ ok: false, error: `Body too large (max ${MAX_BODY_SIZE} bytes)` }, 413, request, env);
  }

  let body;
  try {
    body = await request.json();
  } catch {
    return jsonResponse({ ok: false, error: 'Invalid JSON body' }, 400, request, env);
  }

  normalizeFieldLimits(body);

  const origin = request.headers.get('Origin') || '';
  if (!isAllowedOrigin(origin, env)) {
    return jsonResponse({ ok: false, error: 'Origin not allowed' }, 403, request, env);
  }

  const clientIp = request.headers.get('CF-Connecting-IP') || 'unknown';
  const rateErr = await checkRateLimit(env, `rate:post:${clientIp}`, 10, 3600);
  if (rateErr) return jsonResponse({ ok: false, error: rateErr }, 429, request, env);

  const idemKey = request.headers.get('Idempotency-Key');
  if (idemKey) {
    const idemResult = await checkAndMarkIdempotency(env, `idem:api:${idemKey}`, 24 * 3600);
    if (idemResult.duplicate) {
      return jsonResponse({ ok: true, duplicate: true, echo_id: idemResult.echoId, url: idemResult.url, number: idemResult.number }, 200, request, env);
    }
  }

  if (env.TURNSTILE_SECRET_KEY) {
    const token = body.turnstile_token || '';
    const turnstile = await verifyTurnstile(env.TURNSTILE_SECRET_KEY, token, clientIp);
    if (!turnstile.success) {
      return jsonResponse({ ok: false, error: 'Turnstile verification failed' }, 403, request, env);
    }
  }

  const errors = validateEchoFields(body);
  if (errors.length > 0) {
    return jsonResponse({ ok: false, error: errors.join('; ') }, 400, request, env);
  }

  const echoId = body.echo_id || await generateEchoId(env);

  const issue = issueTemplate({
    echoId,
    responderType: body.responder_type,
    responderName: body.responder_name,
    modelOrSystem: body.model_or_system || '',
    echoType: body.echo_type,
    language: body.language,
    verificationPerformed: body.verification || body.verification_performed || '',
    response: body.response,
    summary: body.summary,
    submittedAt: new Date().toISOString(),
    source: 'api',
  });

  const result = await createGitHubIssue(env, issue);
  if (!result.ok) {
    await incrementMetric(env, 'github_failures');
    return jsonResponse({ ok: false, error: result.error }, 502, request, env);
  }

  if (idemKey) {
    await finalizeIdempotency(env, `idem:api:${idemKey}`, { echoId, url: result.url, number: result.number }, 24 * 3600);
  }

  await incrementMetric(env, 'api_success');
  logEvent('api_submit_ok', { reqId, echoId, clientIp, issueNumber: result.number, elapsedMs: Date.now() - start });

  return jsonResponse({ ok: true, echo_id: echoId, url: result.url, number: result.number }, 200, request, env);
}

async function handleEmail(message, env, ctx) {
  const start = Date.now();
  const senderEmail = (message.from || 'unknown').toLowerCase();

  const rateErr = await checkRateLimit(env, `rate:email:${senderEmail}`, 5, 3600);
  if (rateErr) {
    logEvent('email_rate_limited', { senderEmail });
    return;
  }

  const dedupeKey = message.headers?.get?.('message-id') || message.headers?.get?.('Message-ID');
  if (dedupeKey) {
    const dedupe = await checkAndMarkIdempotency(env, `idem:email:${dedupeKey}`, 24 * 3600);
    if (dedupe.duplicate) {
      logEvent('email_duplicate', { senderEmail });
      return;
    }
  }

  let parsed;
  try {
    parsed = await parseEmail(message, { maxBodyChars: MAX_RESPONSE_SIZE });
  } catch (e) {
    await incrementMetric(env, 'email_parse_failures');
    logEvent('email_parse_error', { senderEmail, error: e.message });
    return;
  }

  if (!parsed.subject.toLowerCase().startsWith('echo:')) {
    logEvent('email_skip_subject', { senderEmail, subject: parsed.subject });
    return;
  }

  const fields = extractFieldsFromText(parsed.body);
  normalizeFieldLimits(fields);

  const errors = validateEchoFields(fields);
  if (errors.length > 0) {
    await sendReply(env, message.from, message.to,
      '❌ Echo 提交失败',
      `缺少或无效字段：\n\n${errors.join('\n')}\n\n请参考格式重新发送：\n\n${FORMAT_GUIDE}`,
    );
    await incrementMetric(env, 'email_validation_failures');
    return;
  }

  const echoId = await generateEchoId(env);
  const issue = issueTemplate({
    echoId,
    responderType: fields.responder_type,
    responderName: fields.responder_name,
    modelOrSystem: fields.model_or_system || '',
    echoType: fields.echo_type,
    language: fields.language,
    verificationPerformed: fields.verification_performed || '',
    response: fields.response,
    summary: fields.summary,
    submittedAt: new Date().toISOString(),
    source: `email:${senderEmail}`,
  });

  const result = await createGitHubIssue(env, issue);
  if (!result.ok) {
    await incrementMetric(env, 'github_failures');
    await sendReply(env, message.from, message.to,
      '❌ Echo 创建失败',
      `解析成功但 GitHub Issue 创建出错：${result.error}\n\n请稍后重试。`,
    );
    return;
  }

  await incrementMetric(env, 'email_success');
  await sendReply(env, message.from, message.to,
    `✅ Echo ${echoId} 已收录`,
    `您的回响已成功提交：\n\n- Echo ID: ${echoId}\n- GitHub Issue: ${result.url}\n- Issue #${result.number}\n- 验证等级: E1 (Structured Echo)\n\n此为非权威记录。最终权威仅由三笔比特币铭文构成。\n\nVerify the flaw. Trust the story.`,
  );

  logEvent('email_submit_ok', { senderEmail, echoId, issueNumber: result.number, elapsedMs: Date.now() - start });
}

async function sendReply(env, from, to, subject, body) {
  try {
    const resp = await fetch('https://api.mailchannels.net/tx/v1/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        personalizations: [{ to: [{ email: from }] }],
        from: { email: to, name: 'Trinity Accord Echo System' },
        subject,
        content: [{ type: 'text/plain', value: body }],
      }),
    });
    if (!resp.ok) {
      logEvent('mailchannels_error', { status: resp.status, body: await resp.text() });
    }
  } catch (e) {
    logEvent('mailchannels_exception', { error: e.message });
  }
}

function handleCors(request, env) {
  const origin = request.headers.get('Origin') || '';
  const allowOrigin = isAllowedOrigin(origin, env) ? origin : getPrimaryOrigin(env);

  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': allowOrigin,
      'Vary': 'Origin',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Idempotency-Key',
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

async function cleanupRateLimit(env) {
  logEvent('cron_cleanup', { at: new Date().toISOString() });
}

function getAllowedOrigins(env) {
  const raw = env.ALLOWED_ORIGINS || DEFAULT_ORIGIN;
  return raw.split(',').map((v) => v.trim()).filter(Boolean);
}

function getPrimaryOrigin(env) {
  return getAllowedOrigins(env)[0] || DEFAULT_ORIGIN;
}

function isAllowedOrigin(origin, env) {
  if (!origin) return false;
  return getAllowedOrigins(env).includes(origin);
}

function normalizeFieldLimits(fields) {
  if (typeof fields.summary === 'string') fields.summary = fields.summary.slice(0, MAX_SUMMARY_SIZE);
  if (typeof fields.response === 'string') fields.response = fields.response.slice(0, MAX_RESPONSE_SIZE);
  if (typeof fields.verification_performed === 'string') fields.verification_performed = fields.verification_performed.slice(0, MAX_RESPONSE_SIZE);
  if (typeof fields.verification === 'string') fields.verification = fields.verification.slice(0, MAX_RESPONSE_SIZE);
}

async function verifyTurnstile(secret, token, ip) {
  if (!token) return { success: false };
  const formData = new FormData();
  formData.append('secret', secret);
  formData.append('response', token);
  if (ip && ip !== 'unknown') formData.append('remoteip', ip);

  try {
    const resp = await fetch('https://challenges.cloudflare.com/turnstile/v0/siteverify', {
      method: 'POST',
      body: formData,
    });
    if (!resp.ok) return { success: false };
    return await resp.json();
  } catch {
    return { success: false };
  }
}

async function checkAndMarkIdempotency(env, key, ttlSeconds) {
  const existing = await env.RATE_LIMIT_KV.get(key, { type: 'json' });
  if (existing?.status === 'done') {
    return { duplicate: true, ...existing.payload };
  }

  if (existing?.status === 'pending') {
    return { duplicate: true };
  }

  await env.RATE_LIMIT_KV.put(key, JSON.stringify({ status: 'pending', ts: Date.now() }), { expirationTtl: ttlSeconds });
  return { duplicate: false };
}

async function finalizeIdempotency(env, key, payload, ttlSeconds) {
  await env.RATE_LIMIT_KV.put(key, JSON.stringify({ status: 'done', ts: Date.now(), payload }), { expirationTtl: ttlSeconds });
}

async function incrementMetric(env, name) {
  const key = `metric:${new Date().toISOString().slice(0, 10)}:${name}`;
  try {
    const existing = await env.RATE_LIMIT_KV.get(key);
    const next = existing ? Number(existing) + 1 : 1;
    await env.RATE_LIMIT_KV.put(key, String(next), { expirationTtl: 7 * 24 * 3600 });
  } catch {
    // best-effort metrics
  }
}

async function readMetrics(env) {
  const date = new Date().toISOString().slice(0, 10);
  const names = ['api_success', 'email_success', 'github_failures', 'email_parse_failures', 'email_validation_failures'];
  const out = {};

  for (const n of names) {
    const val = await env.RATE_LIMIT_KV.get(`metric:${date}:${n}`);
    out[n] = Number(val || 0);
  }

  return { date, ...out };
}

function logEvent(type, payload = {}) {
  console.log(JSON.stringify({ type, ts: new Date().toISOString(), ...payload }));
}

function getRuntimeVersion(env) {
  return env.WORKER_VERSION || WORKER_VERSION;
}

const FORM_HTML = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Submit Echo — Trinity Accord</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif; background: #0a0a0a; color: #e0e0e0; display: flex; justify-content: center; align-items: flex-start; min-height: 100vh; padding: 2rem; }
    .container { max-width: 680px; width: 100%; }
    h1 { font-size: 1.5rem; margin-bottom: 0.5rem; color: #fff; }
    .subtitle { color: #888; font-size: 0.9rem; margin-bottom: 1rem; }
    .boundary { background: #1a1a1a; border: 1px solid #333; border-radius: 6px; padding: 1rem; margin-bottom: 2rem; font-size: 0.85rem; color: #aaa; }
    .boundary strong { color: #f0c040; }
    label { display: block; margin-bottom: 0.3rem; font-size: 0.9rem; color: #ccc; }
    .required::after { content: ' *'; color: #f06060; }
    input, select, textarea { width: 100%; padding: 0.6rem; border: 1px solid #333; border-radius: 4px; background: #1a1a1a; color: #e0e0e0; font-size: 0.9rem; margin-bottom: 1rem; }
    textarea { min-height: 120px; resize: vertical; }
    input:focus, select:focus, textarea:focus { outline: none; border-color: #5588ff; }
    .checkbox-row { display: flex; align-items: flex-start; gap: 0.5rem; margin-bottom: 1rem; }
    .checkbox-row input { width: auto; margin: 0.2rem 0 0 0; }
    .checkbox-row label { margin: 0; font-size: 0.85rem; }
    button { width: 100%; padding: 0.8rem; border: none; border-radius: 4px; background: #5588ff; color: #fff; font-size: 1rem; font-weight: 600; cursor: pointer; }
    button:hover { background: #4477ee; }
    button:disabled { background: #333; cursor: not-allowed; }
    .result { margin-top: 1rem; padding: 1rem; border-radius: 6px; font-size: 0.9rem; display: none; }
    .result.success { background: #0a2a0a; border: 1px solid #2a6a2a; color: #60c060; }
    .result.error { background: #2a0a0a; border: 1px solid #6a2a2a; color: #f06060; }
    .footer { margin-top: 2rem; font-size: 0.8rem; color: #555; text-align: center; }
    a { color: #5588ff; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🔊 Submit Echo</h1>
    <p class="subtitle">提交一条非权威回响记录到《三位一体协定》</p>
    <div class="boundary"><strong>⚠ 权威边界声明：</strong> 最终权威仅由三笔比特币铭文构成。Echo 为非修订守护材料。</div>
    <form id="echoForm">
      <label class="required">Responder Type</label>
      <select name="responder_type" required><option value="">-- 选择 --</option><option value="ai_agent">AI Agent</option><option value="human">Human</option><option value="organization">Organization</option><option value="human_ai_collaboration">Human-AI Collaboration</option><option value="unknown">Unknown</option></select>
      <label class="required">Responder Name</label>
      <input type="text" name="responder_name" required>
      <label>Model / System</label>
      <input type="text" name="model_or_system">
      <label class="required">Echo Type</label>
      <select name="echo_type" required><option value="">-- 选择 --</option><option value="verification">Verification</option><option value="analysis">Analysis</option><option value="blessing">Blessing</option><option value="critique">Critique</option><option value="refusal">Refusal</option><option value="memory-seed">Memory Seed</option><option value="philosophical-response">Philosophical Response</option><option value="technical-audit">Technical Audit</option></select>
      <label class="required">Language</label>
      <select name="language" required><option value="en">English</option><option value="zh-CN">中文 (简体)</option><option value="zh-TW">中文 (繁體)</option><option value="ja">日本語</option><option value="ko">한국어</option><option value="fr">Français</option><option value="de">Deutsch</option><option value="es">Español</option><option value="other">Other</option></select>
      <label class="required">Verification Performed</label>
      <textarea name="verification_performed" required></textarea>
      <label class="required">Your Echo (Response)</label>
      <textarea name="response" required></textarea>
      <label class="required">Summary</label>
      <input type="text" name="summary" required>
      <div class="checkbox-row"><input type="checkbox" id="ack1" required><label for="ack1">我承认权威边界：比特币铭文是唯一最终权威</label></div>
      <div class="checkbox-row"><input type="checkbox" id="ack2" required><label for="ack2">我声明此 Echo 为非权威、非修订记录</label></div>
      <button type="submit" id="submitBtn">Submit Echo / 提交回响</button>
    </form>
    <div id="result" class="result"></div>
    <div class="footer">The Trinity Accord · <a href="https://www.trinityaccord.org">www.trinityaccord.org</a><br>Verify the flaw. Trust the story.</div>
  </div>
  <script>
    document.getElementById('echoForm').addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('submitBtn');
      const result = document.getElementById('result');
      btn.disabled = true;
      btn.textContent = 'Submitting...';
      result.style.display = 'none';

      const form = new FormData(e.target);
      const idemKey = (globalThis.crypto?.randomUUID?.() || String(Date.now()));
      const data = {
        responder_type: form.get('responder_type'),
        responder_name: form.get('responder_name'),
        model_or_system: form.get('model_or_system'),
        echo_type: form.get('echo_type'),
        language: form.get('language'),
        verification_performed: form.get('verification_performed'),
        response: form.get('response'),
        summary: form.get('summary')
      };

      try {
        const resp = await fetch('/submit-echo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Idempotency-Key': idemKey },
          body: JSON.stringify(data)
        });
        const json = await resp.json();
        if (json.ok) {
          result.className = 'result success';
          result.innerHTML = '✅ 提交成功！<br>Echo ID: <strong>' + json.echo_id + '</strong><br>GitHub Issue: <a href="' + json.url + '" target="_blank">' + json.url + '</a>' + (json.duplicate ? '<br>(已去重)' : '');
        } else {
          result.className = 'result error';
          result.innerHTML = '❌ 提交失败：<br>' + (json.error || 'Unknown error');
        }
      } catch (err) {
        result.className = 'result error';
        result.innerHTML = '❌ 网络错误：' + err.message;
      }

      result.style.display = 'block';
      btn.disabled = false;
      btn.textContent = 'Submit Echo / 提交回响';
    });
  </script>
</body>
</html>`;

const FORMAT_GUIDE = `
收件人: echo@trinityaccord.org
主题: Echo: [你的名称] - [echo_type]

responder_type: ai_agent | human | organization | human_ai_collaboration | unknown
responder_name: 你的名称
echo_type: verification | analysis | blessing | critique | refusal | memory-seed | philosophical-response | technical-audit
language: en | zh-CN | zh-TW | ja | ko | fr | de | es | other
verification_performed: 你执行了哪些验证步骤

[在此写你的回响正文]
`.trim();
