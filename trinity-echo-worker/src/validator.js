const VALID_RESPONDER_TYPES = ['ai_agent', 'human', 'organization', 'human_ai_collaboration', 'unknown'];

// v2 canonical echo types
const CANONICAL_ECHO_TYPES = [
  'recognition', 'verification', 'critical', 'interpretive',
  'technical-audit', 'propagation', 'refusal', 'witness', 'seed',
];

// Legacy aliases → canonical v2 keys
const ECHO_TYPE_ALIASES = {
  'analysis': 'interpretive',
  'blessing': 'witness',
  'critique': 'critical',
  'memory-seed': 'seed',
  'philosophical-response': 'interpretive',
  'verification': 'verification',
  'refusal': 'refusal',
  'technical-audit': 'technical-audit',
};

const VALID_ECHO_TYPES = [...CANONICAL_ECHO_TYPES, ...Object.keys(ECHO_TYPE_ALIASES)];

const VALID_LANGUAGES = ['en', 'zh-CN', 'zh-TW', 'ja', 'ko', 'fr', 'de', 'es', 'other'];

/**
 * Normalize legacy echo type to v2 canonical key.
 * Returns the canonical key, or the input unchanged if already canonical/unknown.
 */
export function normalizeEchoType(echoType) {
  if (!echoType) return echoType;
  const lower = echoType.toLowerCase().trim();
  if (CANONICAL_ECHO_TYPES.includes(lower)) return lower;
  return ECHO_TYPE_ALIASES[lower] || lower;
}

export function validateEchoFields(fields) {
  const errors = [];

  if (!fields.responder_type || !VALID_RESPONDER_TYPES.includes(fields.responder_type)) {
    errors.push(`responder_type must be one of: ${VALID_RESPONDER_TYPES.join(', ')}`);
  }

  if (!fields.responder_name || typeof fields.responder_name !== 'string' || fields.responder_name.trim().length === 0) {
    errors.push('responder_name is required');
  } else if (fields.responder_name.length > 200) {
    errors.push('responder_name must be 200 characters or fewer');
  }

  if (!fields.echo_type || !VALID_ECHO_TYPES.includes(fields.echo_type.toLowerCase().trim())) {
    errors.push(`echo_type must be one of: ${CANONICAL_ECHO_TYPES.join(', ')}`);
  }

  if (!fields.language || !VALID_LANGUAGES.includes(fields.language)) {
    errors.push(`language must be one of: ${VALID_LANGUAGES.join(', ')}`);
  }

  const verification = fields.verification || fields.verification_performed;
  if (!verification || typeof verification !== 'string' || verification.trim().length === 0) {
    errors.push('verification is required');
  }

  if (!fields.response || typeof fields.response !== 'string' || fields.response.trim().length === 0) {
    errors.push('response is required');
  }

  if (!fields.summary || typeof fields.summary !== 'string' || fields.summary.trim().length === 0) {
    errors.push('summary is required');
  }

  return errors;
}

export async function generateEchoId(env) {
  const now = new Date();
  const dateStr = now.toISOString().split('T')[0];
  const counterKey = `echo-counter:${dateStr}`;

  let seq;
  try {
    const existing = await env.RATE_LIMIT_KV.get(counterKey);
    seq = existing ? parseInt(existing, 10) + 1 : 1;
    await env.RATE_LIMIT_KV.put(counterKey, seq.toString(), { expirationTtl: 172800 });
  } catch {
    seq = now.getHours() * 3600 + now.getMinutes() * 60 + now.getSeconds();
  }

  const rand = randomSuffix();
  return `echo-${dateStr}-${String(seq).padStart(6, '0')}-${rand}`;
}

function randomSuffix() {
  const arr = new Uint8Array(4);
  crypto.getRandomValues(arr);
  return [...arr].map((n) => n.toString(16).padStart(2, '0')).join('');
}
