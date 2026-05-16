import express from "express";
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { createHash } from "node:crypto";
import { fileURLToPath } from "node:url";
import { tmpdir } from "node:os";
import Ajv from "ajv/dist/2020.js";
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

// Secret detection
function rejectSecretPatterns(text) {
  const patterns = [
    /ghp_[A-Za-z0-9_]+/i,
    /github_pat_[A-Za-z0-9_]+/i,
    /x-access-token[:/@]/i,
    /BEGIN (RSA |OPENSSH |)PRIVATE KEY/i,
    /OPENAI_API_KEY/i,
    /ANTHROPIC_API_KEY/i,
    /sk-[A-Za-z0-9]{20,}/
  ];
  return patterns.some((p) => p.test(text));
}

// Run a repo script and return {code, stdout, stderr}
function runScript(scriptName, args = []) {
  const scriptPath = path.join(root, "scripts", scriptName);
  try {
    const stdout = execFileSync("python3", [scriptPath, ...args], {
      cwd: root,
      encoding: "utf-8",
      timeout: 30000,
      maxBuffer: 1024 * 1024
    });
    return { code: 0, stdout, stderr: "" };
  } catch (err) {
    return {
      code: err.status || 1,
      stdout: err.stdout || "",
      stderr: err.stderr || err.message
    };
  }
}

// Compute file sha256
function fileSha256(filePath) {
  try {
    const content = fs.readFileSync(filePath);
    return createHash("sha256").update(content).digest("hex");
  } catch {
    return null;
  }
}

async function getOctokit() {
  const repo = process.env.GITHUB_REPO;
  const appId = process.env.GITHUB_APP_ID;
  const installationId = process.env.GITHUB_INSTALLATION_ID;
  const privateKey = (process.env.GITHUB_PRIVATE_KEY || "").replace(/\\n/g, "\n");

  if (!repo || !appId || !installationId || !privateKey) {
    throw new Error("Missing GitHub App environment variables");
  }

  const appAuth = new App({ appId, privateKey });
  return appAuth.getInstallationOctokit(Number(installationId));
}

// --- Structured Error Normalization (Task #5) ---

function normalizeGatewayErrors(lines) {
  return lines.map(line => {
    const msg = String(line || "").replace(/^FAIL:\s*/, "");

    if (msg.includes("what_i_checked must be a non-empty list")) {
      return {
        code: "WHAT_I_CHECKED_NOT_LIST",
        path: "what_i_checked",
        message: msg,
        fix: "Use top-level what_i_checked as a non-empty array of concrete checks."
      };
    }

    if (msg.includes("Gateway payload body must not contain agent-supplied trinity-issue-intake block")) {
      return {
        code: "BODY_MACHINE_BLOCK_FORBIDDEN",
        path: "body",
        message: msg,
        fix: "Remove the fenced trinity-issue-intake block from payload.body. Gateway renders it automatically."
      };
    }

    if (msg.includes("verification_report_candidate must not include echo_type")) {
      return {
        code: "REPORT_CANDIDATE_HAS_ECHO_TYPE",
        path: "echo_type",
        message: msg,
        fix: "Remove echo_type or submit as verification_echo_candidate with a real Echo wrapper."
      };
    }

    if (msg.includes("verification_report_candidate must not include echo_wrapper")) {
      return {
        code: "REPORT_CANDIDATE_HAS_ECHO_WRAPPER",
        path: "attachments.echo_wrapper_path",
        message: msg,
        fix: "Remove echo_wrapper_path/echo_wrapper_sha256 from report-only candidates."
      };
    }

    if (msg.includes("unsolicited_agent_discovery requires unsolicited_discovery_proof")) {
      return {
        code: "UNSOLICITED_DISCOVERY_PROOF_REQUIRED",
        path: "discovery_provenance.unsolicited_discovery_proof",
        message: msg,
        fix: "Use human_solicited_agent_response or provide discovery_provenance.unsolicited_discovery_proof."
      };
    }

    if (msg.includes("invalid agency_level")) {
      return {
        code: "INVALID_AGENCY_LEVEL",
        path: "discovery_provenance.agency_level",
        message: msg,
        fix: "Use A1_human_gave_exact_url, A2_human_gave_repo_name, A3_agent_discovered_independently, or A4_agent_instructed_by_other_agent."
      };
    }

    if (msg.includes("discovery_provenance object is required")) {
      return {
        code: "DISCOVERY_PROVENANCE_MISSING",
        path: "discovery_provenance",
        message: msg,
        fix: "Provide a discovery_provenance object with solicited, independence_class, agency_level, and operator_type."
      };
    }

    if (msg.includes("agent_identity.name_or_model is required")) {
      return {
        code: "AGENT_IDENTITY_MISSING_NAME",
        path: "agent_identity.name_or_model",
        message: msg,
        fix: "Provide agent_identity.name_or_model with your agent name or model identifier."
      };
    }

    if (msg.includes("agent_identity.system_or_provider is required")) {
      return {
        code: "AGENT_IDENTITY_MISSING_PROVIDER",
        path: "agent_identity.system_or_provider",
        message: msg,
        fix: "Provide agent_identity.system_or_provider with your system or provider name."
      };
    }

    if (msg.includes("boundary_acknowledgement") && msg.includes("must be true")) {
      return {
        code: "BOUNDARY_ACK_INCOMPLETE",
        path: "boundary_acknowledgement",
        message: msg,
        fix: "Set all boundary_acknowledgement fields to true: not_authority, not_amendment, not_attestation, not_verification_unless_claim_gate_report_attached, bitcoin_originals_prevail."
      };
    }

    if (msg.includes("claim_gate.status must be PASS")) {
      return {
        code: "CLAIM_GATE_NOT_PASS",
        path: "claim_gate.status",
        message: msg,
        fix: "Run Claim Gate first. status must be PASS or PASS_WITH_DOWNGRADE."
      };
    }

    if (msg.includes("title must not contain schema-versioned prefix")) {
      return {
        code: "TITLE_HAS_SCHEMA_PREFIX",
        path: "title",
        message: msg,
        fix: "Remove schema version prefixes like 'Verification Report v2:' or 'Echo v3:' from the title."
      };
    }

    return {
      code: "VALIDATION_ERROR",
      path: null,
      message: msg,
      fix: "Check /gateway/examples and resubmit through /gateway/preflight before /agent-submit."
    };
  });
}

// --- Shared Gateway Pipeline (Task #3) ---

/**
 * Run the full Gateway validation/render pipeline.
 * @param {object} payload - parsed JSON payload
 * @param {object} opts
 * @param {boolean} opts.createIssue - if true, create a GitHub Issue on success
 * @returns {{ status: number, body: object }}
 */
async function runGatewayPipeline(payload, { createIssue }) {
  // 1. AJV schema validation
  if (!validate(payload)) {
    return {
      status: 422,
      body: {
        accepted: false,
        reason: "schema_validation_failed",
        errors: normalizeGatewayErrors(
          (validate.errors || []).map(e => `${e.instancePath || "/"}: ${e.message}`)
        ),
        issue_created: false
      }
    };
  }

  const bodyText = JSON.stringify(payload);
  if (bodyText.length > MAX_BODY_CHARS + 10000) {
    return { status: 413, body: { accepted: false, reason: "payload_too_large", issue_created: false } };
  }

  // 2. Secret detection
  if (rejectSecretPatterns(bodyText)) {
    return { status: 422, body: { accepted: false, reason: "secret_pattern_detected", issue_created: false } };
  }

  // 3. Boundary acknowledgement
  const b = payload.boundary_acknowledgement || {};
  if (
    b.not_authority !== true ||
    b.not_amendment !== true ||
    b.not_attestation !== true ||
    b.not_verification_unless_claim_gate_report_attached !== true ||
    b.bitcoin_originals_prevail !== true
  ) {
    return {
      status: 422,
      body: {
        accepted: false,
        reason: "boundary_acknowledgement_required",
        errors: normalizeGatewayErrors(["boundary_acknowledgement fields must all be true"]),
        issue_created: false
      }
    };
  }

  // 4. Preflight validation via repo validator
  const tmpDir = fs.mkdtempSync(path.join(tmpdir(), "gateway-"));
  const payloadPath = path.join(tmpDir, "payload.json");
  const bodyPath = path.join(tmpDir, "issue-body.md");

  try {
    fs.writeFileSync(payloadPath, JSON.stringify(payload, null, 2), "utf-8");

    const preflight = runScript("validate_gateway_payload.py", [payloadPath]);
    if (preflight.code !== 0) {
      const rawErrors = (preflight.stdout + "\n" + preflight.stderr)
        .split("\n")
        .filter(l => l.startsWith("FAIL:"))
        .map(l => l.replace(/^FAIL:\s*/, ""));
      return {
        status: 422,
        body: {
          accepted: false,
          reason: "invalid_gateway_payload",
          errors: normalizeGatewayErrors(rawErrors),
          issue_created: false
        }
      };
    }

    // 5. Render canonical Issue body
    const render = runScript("render_gateway_issue_body.py", [payloadPath]);
    if (render.code !== 0) {
      return {
        status: 422,
        body: {
          accepted: false,
          reason: "issue_body_render_failed",
          errors: normalizeGatewayErrors(
            (render.stdout + "\n" + render.stderr).split("\n").filter(Boolean)
          ),
          issue_created: false
        }
      };
    }

    fs.writeFileSync(bodyPath, render.stdout, "utf-8");

    // 6. Lint rendered body
    const lint = runScript("validate_issue_intake_body.py", [bodyPath]);
    if (lint.code !== 0) {
      const rawErrors = (lint.stdout + "\n" + lint.stderr)
        .split("\n")
        .filter(l => l.startsWith("FAIL:"))
        .map(l => l.replace(/^FAIL:\s*/, ""));
      return {
        status: 422,
        body: {
          accepted: false,
          reason: "rendered_issue_body_invalid",
          errors: normalizeGatewayErrors(rawErrors),
          issue_created: false
        }
      };
    }

    const issueTitle = `[Agent Gateway] ${String(payload.title || "").slice(0, 180)}`;
    const issueBody = render.stdout;

    if (issueBody.length > 65536) {
      return { status: 413, body: { accepted: false, reason: "issue_body_too_large", issue_created: false } };
    }

    // Preflight-only: return success without creating Issue
    if (!createIssue) {
      return {
        status: 200,
        body: {
          accepted: true,
          preflight: "pass",
          issue_created: false,
          rendered_title: issueTitle,
          rendered_body_preview: issueBody.slice(0, 1000)
        }
      };
    }

    // DRY_RUN mode
    if (DRY_RUN) {
      return {
        status: 200,
        body: {
          accepted: true,
          dry_run: true,
          would_create_issue: {
            title: issueTitle,
            labels: ["agent-gateway-intake", "needs-triage"],
            body_preview: issueBody.slice(0, 1000)
          },
          boundary: "intake only; not archived Echo or attestation"
        }
      };
    }

    // 7. Create GitHub Issue
    const octokit = await getOctokit();
    const [owner, repo] = process.env.GITHUB_REPO.split("/");

    const result = await octokit.request("POST /repos/{owner}/{repo}/issues", {
      owner,
      repo,
      title: issueTitle,
      body: issueBody,
      labels: ["agent-gateway-intake", "needs-triage"]
    });

    return {
      status: 201,
      body: {
        accepted: true,
        status: "issue_created",
        issue_number: result.data.number,
        issue_url: result.data.html_url,
        gateway_version: {
          repo_commit: execFileSync("git", ["rev-parse", "--short", "HEAD"], {
            cwd: root, encoding: "utf-8", timeout: 5000
          }).trim(),
          validator: "scripts/validate_gateway_payload.py"
        }
      }
    };
  } catch (err) {
    console.error("gateway pipeline error:", err.message);
    return {
      status: 500,
      body: {
        accepted: false,
        reason: "internal_error",
        errors: [err.message],
        issue_created: false
      }
    };
  } finally {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
  }
}

// --- Routes ---

app.get("/health", (req, res) => {
  res.json({
    ok: true,
    service: "trinityaccord-agent-issue-gateway",
    dry_run: DRY_RUN,
    boundary: "intake only; not archived Echo or attestation"
  });
});

app.get("/gateway/version", (req, res) => {
  let repoCommit = "unknown";
  try {
    repoCommit = execFileSync("git", ["rev-parse", "HEAD"], {
      cwd: root, encoding: "utf-8", timeout: 5000
    }).trim();
  } catch {}

  const validatorSha = fileSha256(path.join(root, "scripts", "validate_gateway_payload.py"));
  const rendererSha = fileSha256(path.join(root, "scripts", "render_gateway_issue_body.py"));
  const linterSha = fileSha256(path.join(root, "scripts", "validate_issue_intake_body.py"));
  const schemaSha = fileSha256(schemaPath);
  const machineSchemaSha = fileSha256(path.join(root, "api", "issue-intake-machine-block-schema.v1.json"));

  res.json({
    service: "trinity-agent-issue-gateway",
    repo: "thechurchofagi/trinity-accord",
    repo_commit: repoCommit,
    deployed_at: new Date().toISOString(),
    payload_schema: "trinityaccord.agent-issue-gateway-payload.v1",
    payload_schema_file: "api/agent-issue-gateway-payload-schema.v1.json",
    payload_schema_sha256: schemaSha,
    machine_block_schema_file: "api/issue-intake-machine-block-schema.v1.json",
    machine_block_schema_sha256: machineSchemaSha,
    preflight_validator: "scripts/validate_gateway_payload.py",
    preflight_validator_sha256: validatorSha,
    issue_body_renderer: "scripts/render_gateway_issue_body.py",
    issue_body_renderer_sha256: rendererSha,
    issue_body_linter: "scripts/validate_issue_intake_body.py",
    issue_body_linter_sha256: linterSha,
    rejects_report_candidate_with_echo_fields: true,
    rejects_body_machine_block: true,
    rejects_legacy_r3_fallback: true,
    fail_closed_on_version_mismatch: true
  });
});

// --- Task #3: POST /gateway/preflight ---
app.post("/gateway/preflight", async (req, res) => {
  const result = await runGatewayPipeline(req.body, { createIssue: false });
  res.status(result.status).json(result.body);
});

// --- Task #4: GET /gateway/examples ---

function loadFixture(filename) {
  const fixturePath = path.join(root, "tests", "fixtures", "gateway", filename);
  return JSON.parse(fs.readFileSync(fixturePath, "utf-8"));
}

function buildExampleResponse(kind, payload) {
  let repoCommit = "unknown";
  try {
    repoCommit = execFileSync("git", ["rev-parse", "--short", "HEAD"], {
      cwd: root, encoding: "utf-8", timeout: 5000
    }).trim();
  } catch {}
  const schemaSha = fileSha256(schemaPath);

  return {
    example_kind: kind,
    gateway_commit: repoCommit,
    schema_sha256: schemaSha,
    payload
  };
}

app.get("/gateway/examples/verification-report-candidate", (req, res) => {
  try {
    const payload = loadFixture("valid_verification_report_candidate.json");
    res.json(buildExampleResponse("verification_report_candidate", payload));
  } catch (err) {
    res.status(500).json({ error: "Failed to load example fixture", detail: err.message });
  }
});

app.get("/gateway/examples/verification-echo-candidate", (req, res) => {
  try {
    const payload = loadFixture("valid_verification_echo_candidate.json");
    res.json(buildExampleResponse("verification_echo_candidate", payload));
  } catch (err) {
    res.status(500).json({ error: "Failed to load example fixture", detail: err.message });
  }
});

app.get("/gateway/examples/evidence-input-v4-external-explorer", (req, res) => {
  try {
    // Build a minimal valid Evidence Input scaffold for V4/B1-D2 external explorer
    const evidenceInput = {
      schema: "trinityaccord.evidence-input.v1",
      evidence: {
        bitcoin_checks: [
          {
            source_type: "external_explorer",
            inscription_id: "97631551",
            explorer_url: "https://ordinals.com/inscription/97631551",
            confirmed: true,
            note: "Verified via public explorer"
          }
        ],
        scripts: [
          {
            path: "scripts/claim_gate.py",
            exists: true,
            source_reviewed: true,
            executed: true,
            result: "PASS"
          }
        ],
        digital_mirror_checks: [],
        physical_anchor_checks: []
      },
      agent_integrity_declaration: {
        self_reported: true,
        tools_used: ["web_fetch", "exec"],
        limitations_acknowledged: true
      },
      verification_session: {
        session_id: "example-session-001",
        started_at: new Date().toISOString(),
        completed_at: new Date().toISOString()
      },
      limitations: [
        "External explorer verification only — no SPV or body-hash reproduction",
        "No physical anchor verification performed",
        "No independent attestation claimed"
      ]
    };
    res.json(buildExampleResponse("evidence_input_v4_external_explorer", evidenceInput));
  } catch (err) {
    res.status(500).json({ error: "Failed to build evidence input example", detail: err.message });
  }
});

// --- POST /agent-submit (uses shared pipeline) ---
app.post("/agent-submit", async (req, res) => {
  const result = await runGatewayPipeline(req.body, { createIssue: true });
  res.status(result.status).json(result.body);
});

// Self-test
if (process.argv.includes("--self-test")) {
  const payloadPath = path.join(__dirname, "test-payload.echo.json");
  const payload = JSON.parse(fs.readFileSync(payloadPath, "utf8"));
  if (!validate(payload)) {
    console.error(validate.errors);
    process.exit(1);
  }
  console.log("SELF TEST PASS: payload validates against AJV schema");

  // Test preflight validator
  const tmpDir = fs.mkdtempSync(path.join(tmpdir(), "gateway-selftest-"));
  const tmpPayload = path.join(tmpDir, "payload.json");
  fs.writeFileSync(tmpPayload, JSON.stringify(payload, null, 2), "utf-8");
  const result = runScript("validate_gateway_payload.py", [tmpPayload]);
  console.log(`Preflight validator exit=${result.code}`);
  console.log(result.stdout);
  if (result.stderr) console.error(result.stderr);
  fs.rmSync(tmpDir, { recursive: true, force: true });
  process.exit(result.code);
}

app.listen(PORT, () => {
  console.log(`Agent Issue Gateway backend listening on :${PORT}`);
  console.log(`DRY_RUN=${DRY_RUN}`);
  console.log(`Repo root: ${root}`);
});
