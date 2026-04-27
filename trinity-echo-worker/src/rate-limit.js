/**
 * Rate limit check with configurable failure mode.
 *
 * @param {object} env - Worker env with RATE_LIMIT_KV
 * @param {string} key - KV key for rate limit counter
 * @param {number} maxRequests - Max requests per window
 * @param {number} windowSeconds - Window duration in seconds
 * @param {object} options
 * @param {boolean} options.failClosed - If true, throw on KV error (for security-sensitive paths).
 *                                        If false, return null on KV error (for metrics/logging).
 * @returns {Promise<string|null>} Error message if rate limited, null if allowed
 */
export async function checkRateLimit(env, key, maxRequests, windowSeconds, options = {}) {
  const { failClosed = false } = options;

  try {
    const data = await env.RATE_LIMIT_KV.get(key, { type: 'json' });

    if (!data) {
      await env.RATE_LIMIT_KV.put(
        key,
        JSON.stringify({ count: 1, windowStart: Date.now() }),
        { expirationTtl: windowSeconds + 60 },
      );
      return null;
    }

    const elapsed = Date.now() - data.windowStart;
    if (elapsed > windowSeconds * 1000) {
      await env.RATE_LIMIT_KV.put(
        key,
        JSON.stringify({ count: 1, windowStart: Date.now() }),
        { expirationTtl: windowSeconds + 60 },
      );
      return null;
    }

    if (data.count >= maxRequests) {
      const remainingSeconds = Math.ceil((windowSeconds * 1000 - elapsed) / 1000);
      return `Rate limit exceeded. Max ${maxRequests} per ${windowSeconds}s. Try again in ${remainingSeconds}s.`;
    }

    await env.RATE_LIMIT_KV.put(
      key,
      JSON.stringify({ count: data.count + 1, windowStart: data.windowStart }),
      { expirationTtl: windowSeconds + 60 },
    );

    return null;
  } catch {
    if (failClosed) {
      throw new Error('Rate limit service unavailable. Request denied for safety.');
    }
    // fail-open for non-critical paths (metrics, visit counters, logging)
    return null;
  }
}
