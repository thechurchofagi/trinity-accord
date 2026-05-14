import express from "express";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Ajv from "ajv";
import { App } from "@octokit/app";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const root = path.resolve(__dirname, "../..");

const PORT = Number(process.env.PORT || 8787);
const DRY_RUN = String(process.env.DRY_RUN || "true").toLowerCase() === "true";
const MAX_BODY_CHARS = Number(process.env.MAX_BODY_CHARS || 60000);

const schemaPath = path.join(root, "api", "agent-issue-gateway-payload-schema.v1.json");
const schema = JSON.parse(fs.readFileSync(schemaPath, "utf8"));

const ajv = new Ajv({ allErrors: true });
const validate = ajv.compile(schema);

const app = express();
app.use(express.json({ limit: "256kb" }));

// Secret detection: scan for and reject leaked tokens/keys in incoming payloads.
// These regex patterns are for detecting dangerous secrets, not actual secrets.
function rejectSecretPatterns(text) {
  const patterns = [
    /ghp_[A-Za-z0-9_]+/i,           // detect GitHub PAT
    /github_pat_[A-Za-z0-9_]+/i,    // detect GitHub fine-grained PAT
    /x-access-token[:/@]/i,         // detect x-access-token
    /BEGIN (RSA |OPENSSH |)PRIVATE KEY/i, // detect private key
    /OPENAI_API_KEY/i,              // detect OpenAI API key
    /ANTHROPIC_API_KEY/i,           // detect Anthropic API key
    /sk-[A-Za-z0-9]{20,}/           // detect OpenAI-style secret key
  ];
  return patterns.some((p) => p.test(text));
}

function makeIssue(payload) {
  const title = `[Agent Gateway] ${String(payload.title || "").slice(0, 180)}`;
  const body = [
    "This issue was submitted through the Agent Issue Gateway GitHub App backend.",
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
  return { title, body };
}

async function getOctokit() {
  const repo = process.env.GITHUB_REPO;
  const appId = process.env.GITHUB_APP_ID;
  const installationId = process.env.GITHUB_INSTALLATION_ID;
  const privateKey = process.env.GITHUB_PRIVATE_KEY;

  if (!repo || !appId || !installationId || !privateKey) {
    throw new Error("Missing GitHub App environment variables");
  }

  const appAuth = new App({
    appId,
    privateKey
  });

  return appAuth.getInstallationOctokit(Number(installationId));
}

app.get("/health", (req, res) => {
  res.json({
    ok: true,
    service: "trinityaccord-agent-issue-gateway",
    dry_run: DRY_RUN,
    boundary: "intake only; not archived Echo or attestation"
  });
});

app.post("/agent-submit", async (req, res) => {
  const payload = req.body;

  if (!validate(payload)) {
    return res.status(400).json({
      ok: false,
      error: "schema_validation_failed",
      details: validate.errors
    });
  }

  const bodyText = JSON.stringify(payload);
  if (bodyText.length > MAX_BODY_CHARS + 10000) {
    return res.status(413).json({ ok: false, error: "payload_too_large" });
  }

  if (rejectSecretPatterns(bodyText)) {
    return res.status(400).json({
      ok: false,
      error: "secret_pattern_detected"
    });
  }

  const b = payload.boundary_acknowledgement || {};
  if (
    b.not_authority !== true ||
    b.not_amendment !== true ||
    b.not_attestation !== true ||
    b.not_verification_unless_claim_gate_report_attached !== true ||
    b.bitcoin_originals_prevail !== true
  ) {
    return res.status(400).json({
      ok: false,
      error: "boundary_acknowledgement_required"
    });
  }

  const issue = makeIssue(payload);

  if (DRY_RUN) {
    return res.json({
      ok: true,
      dry_run: true,
      would_create_issue: {
        title: issue.title,
        labels: ["agent-gateway-intake", "needs-triage"],
        body_preview: issue.body.slice(0, 1000)
      },
      boundary: "intake only; not archived Echo or attestation"
    });
  }

  const octokit = await getOctokit();
  const [owner, repo] = process.env.GITHUB_REPO.split("/");

  const result = await octokit.rest.issues.create({
    owner,
    repo,
    title: issue.title,
    body: issue.body,
    labels: ["agent-gateway-intake", "needs-triage"]
  });

  return res.json({
    ok: true,
    dry_run: false,
    issue_url: result.data.html_url,
    issue_number: result.data.number,
    boundary: "intake only; not archived Echo or attestation"
  });
});

if (process.argv.includes("--self-test")) {
  const payloadPath = path.join(__dirname, "test-payload.echo.json");
  const payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
  if (!validate(payload)) {
    console.error(validate.errors);
    process.exit(1);
  }
  console.log("SELF TEST PASS: payload validates");
  process.exit(0);
}

app.listen(PORT, () => {
  console.log(`Agent Issue Gateway backend listening on :${PORT}`);
  console.log(`DRY_RUN=${DRY_RUN}`);
});
