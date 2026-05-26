// DEPRECATED: This Cloudflare Worker example has been archived.
// Production recommendation is GitHub App backend; see examples/github-app-backend.
// Archived: 2026-05-14
// Do not use for new deployments.

function jsonResponse(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "Content-Type": "application/json" }
  });
}

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return jsonResponse({ ok: false, error: "method_not_allowed" }, 405);
    }

    let payload;
    try {
      payload = await request.json();
    } catch {
      return jsonResponse({ ok: false, error: "invalid_json" }, 400);
    }

    if (payload.schema !== "trinityaccord.agent-issue-gateway-payload.v1") {
      return jsonResponse({ ok: false, error: "invalid_schema" }, 400);
    }

    // Validate required fields (server-side schema validation)
    const requiredFields = ["submission_type", "agent_identity", "title", "body", "boundary_acknowledgement"];
    const missing = requiredFields.filter((f) => !payload[f]);
    if (missing.length > 0) {
      return jsonResponse({ ok: false, error: "missing_required_fields", fields: missing }, 400);
    }
    if (typeof payload.title === "string" && payload.title.length < 5) {
      return jsonResponse({ ok: false, error: "title_too_short" }, 400);
    }
    if (typeof payload.body === "string" && payload.body.length < 20) {
      return jsonResponse({ ok: false, error: "body_too_short" }, 400);
    }

    // Secret detection: reject payloads containing leaked tokens/keys.
    const bodyText = JSON.stringify(payload);
    const secretPatterns = [
      /ghp_[A-Za-z0-9_]+/i,
      /github_pat_[A-Za-z0-9_]+/i,
      /x-access-token[:/@]/i,
      /BEGIN (RSA |OPENSSH |)PRIVATE KEY/i,
      /(?:OPENAI|ANTHROPIC)[_]API[_]KEY/i,
      /sk-[A-Za-z0-9]{20,}/
    ];
    if (secretPatterns.some((p) => p.test(bodyText))) {
      return jsonResponse({ ok: false, error: "secret_pattern_detected" }, 400);
    }

    const b = payload.boundary_acknowledgement || {};
    if (
      b.not_authority !== true ||
      b.not_amendment !== true ||
      b.not_attestation !== true ||
      b.not_verification_unless_claim_gate_report_attached !== true ||
      b.bitcoin_originals_prevail !== true
    ) {
      return jsonResponse({ ok: false, error: "boundary_acknowledgement_required" }, 400);
    }

    const title = `[Agent Gateway] ${String(payload.title || "").slice(0, 180)}`;
    const body = [
      "This issue was submitted through the Agent Issue Gateway.",
      "",
      "Boundary:",
      "- Not authority",
      "- Not amendment",
      "- Not attestation",
      "- Not archived Echo",
      "- Not verification",
      "- Does not raise verification level",
      "- Does not bypass Claim Gate or Validator",
      "",
      "Submission type:",
      String(payload.submission_type),
      "",
      "Payload:",
      "```json",
      JSON.stringify(payload, null, 2),
      "```"
    ].join("\n");

    try {
      const res = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}/issues`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${env.GITHUB_TOKEN}`,
          "Accept": "application/vnd.github+json",
          "User-Agent": "trinityaccord-agent-gateway"
        },
        body: JSON.stringify({
          title,
          body,
          labels: ["agent-gateway-intake", "needs-triage"]
        })
      });

      if (!res.ok) {
        const errText = await res.text();
        return jsonResponse({ ok: false, error: "github_api_error", status: res.status }, 502);
      }

      const issue = await res.json();

      return jsonResponse({
        ok: true,
        issue_url: issue.html_url,
        issue_number: issue.number,
        boundary: "intake only; not archived Echo or attestation"
      });
    } catch (err) {
      return jsonResponse({ ok: false, error: "internal_error" }, 500);
    }
  }
};
