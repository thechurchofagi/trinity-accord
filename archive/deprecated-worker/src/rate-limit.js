// DEPRECATED ARCHIVE ONLY. Must not be imported by active Worker.
export async function checkRateLimit(env, key, maxRequests, windowSeconds) {
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
    // fail-open so transient KV errors do not block submission
    return null;
  }
}
