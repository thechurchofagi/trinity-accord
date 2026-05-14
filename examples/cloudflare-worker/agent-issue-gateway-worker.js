// Transitional example only.
// Production recommendation is GitHub App backend; see examples/github-app-backend.
// Do not use a personal PAT for long-term production.
// Do not commit secrets.
// Configure GITHUB_TOKEN / GitHub App secret in platform secret storage.

export default {
  async fetch(request, env) {
    if (request.method !== "POST") {
      return new Response("method not allowed", { status: 405 });
    }

    let payload;
    try {
      payload = await request.json();
    } catch {
      return new Response("invalid json", { status: 400 });
    }

    if (payload.schema !== "trinityaccord.agent-issue-gateway-payload.v1") {
      return new Response("invalid schema", { status: 400 });
    }

    const b = payload.boundary_acknowledgement || {};
    if (
      b.not_authority !== true ||
      b.not_amendment !== true ||
      b.not_attestation !== true ||
      b.not_verification_unless_claim_gate_report_attached !== true ||
      b.bitcoin_originals_prevail !== true
    ) {
      return new Response("boundary acknowledgement required", { status: 400 });
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
      "- Does not raise verification level",
      "",
      "Payload:",
      "```json",
      JSON.stringify(payload, null, 2),
      "```"
    ].join("\n");

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
      return new Response(await res.text(), { status: 502 });
    }

    const issue = await res.json();

    return new Response(JSON.stringify({
      ok: true,
      issue_url: issue.html_url,
      issue_number: issue.number,
      boundary: "intake only; not archived Echo or attestation"
    }), {
      headers: { "Content-Type": "application/json" }
    });
  }
};
