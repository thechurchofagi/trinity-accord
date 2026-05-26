// DEPRECATED ARCHIVE ONLY. Must not be imported by active Worker.
export async function createGitHubIssue(env, issue) {
  const token = env.GITHUB_TOKEN;
  const repo = env.GITHUB_REPO || 'thechurchofagi/trinity-accord';

  if (!token) return { ok: false, error: 'GITHUB_TOKEN not configured' };

  const url = `https://api.github.com/repos/${repo}/issues`;
  const requestBody = JSON.stringify({
    title: issue.title,
    body: issue.body,
    labels: issue.labels || ['echo'],
  });

  let lastError = 'unknown error';
  for (let attempt = 1; attempt <= 3; attempt += 1) {
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          Accept: 'application/vnd.github+json',
          'Content-Type': 'application/json',
          'User-Agent': 'trinity-accord-echo-proxy/1.1',
          'X-GitHub-Api-Version': '2022-11-28',
        },
        body: requestBody,
      });

      if (resp.ok) {
        const data = await resp.json();
        return {
          ok: true,
          url: data.html_url,
          number: data.number,
          rateLimitRemaining: resp.headers.get('x-ratelimit-remaining') || null,
        };
      }

      const errText = await resp.text();
      lastError = `GitHub API ${resp.status}: ${errText}`;

      if (resp.status === 401 || resp.status === 403) {
        return { ok: false, error: `GitHub auth/permission error (${resp.status}). Check token scopes.` };
      }

      if (resp.status === 429 || resp.status >= 500) {
        await sleep(250 * Math.pow(2, attempt - 1));
        continue;
      }

      return { ok: false, error: lastError };
    } catch (e) {
      lastError = `GitHub API network error: ${e.message}`;
      await sleep(250 * Math.pow(2, attempt - 1));
    }
  }

  return { ok: false, error: lastError };
}

export function issueTemplate(params) {
  const {
    echoId,
    responderType,
    responderName,
    modelOrSystem,
    echoType,
    language,
    verificationPerformed,
    response,
    summary,
    claimedVerificationLevel,
    statusLabels,
    verificationRecord,
    interpretiveEcho,
    submittedAt,
    source,
  } = params;

  const title = `Echo: ${echoId} — ${responderName} (${echoType})`;
  const body = [
    '## 🔊 Echo Record',
    '',
    '| Field | Value |',
    '|-------|-------|',
    `| **Echo ID** | \`${echoId}\` |`,
    '| **Schema** | trinity-accord.echo-schema.v1 |',
    `| **Submitted** | ${submittedAt} |`,
    `| **Source** | ${source} |`,
    `| **Responder Type** | ${responderType} |`,
    `| **Responder Name** | ${responderName} |`,
    `| **Model/System** | ${modelOrSystem || 'N/A'} |`,
    `| **Echo Type** | ${echoType} |`,
    `| **Language** | ${language} |`,
    `| **Claimed Verification Level** | ${claimedVerificationLevel || 'Not claimed'} |`,
    `| **Status Labels** | ${(statusLabels && statusLabels.length > 0) ? statusLabels.join(', ') : 'Claimed'} |`,
    '',
    '### Verification Performed',
    '',
    verificationPerformed || 'Not specified',
    '',
    '### Echo Response',
    '',
    response,
    '',
    '### Summary',
    '',
    summary,
    '',
    '### Verification Record',
    '',
    '```json',
    JSON.stringify(verificationRecord || {}, null, 2),
    '```',
    '',
    '### Interpretive Echo',
    '',
    '```json',
    JSON.stringify(interpretiveEcho || { included: false }, null, 2),
    '```',
    '',
    '---',
    '',
    '### Acknowledgments',
    '',
    '- [x] Authority boundary acknowledged: Bitcoin Originals are the only final authority',
    '- [x] This Echo is declared non-authoritative and non-amending',
    '',
    '---',
    '',
    '> **最终权威仅由三笔比特币铭文构成。此 Echo 为非修订守护材料。**',
    '>',
    '> Verify the flaw. Trust the story.',
  ].join('\n');

  return {
    title,
    body,
    labels: ['echo', `echo-type:${echoType}`, `lang:${language}`].concat((statusLabels || []).map((l) => `status:${l.toLowerCase().replace(/\s+/g, '-')}`)),
  };
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
