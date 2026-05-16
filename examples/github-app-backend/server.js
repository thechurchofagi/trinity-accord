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

// --- Archive Intent Normalization Helpers ---

function inferArchiveKind(submissionType) {
  if (submissionType === "verification_report_candidate") return "verification_report_archive";
  if (submissionType === "verification_echo_candidate") return "archived_echo";
  return "external_agent_intake_sample";
}

function normalizeArchiveIntentDefaults(payload) {
  const p = { ...payload };

  if (p.record_intent === "intake_only") {
    if (!p.requested_archive_kind) p.requested_archive_kind = "none";
    return p;
  }

  if (p.record_intent === "archive_preflight_only") {
    if (!p.requested_archive_kind || p.requested_archive_kind === "none") {
      p.requested_archive_kind = inferArchiveKind(p.submission_type);
    }
    return p;
  }

  if (!p.record_intent) {
    if (
      p.submission_type === "verification_report_candidate" ||
      p.submission_type === "verification_echo_candidate"
    ) {
      p.record_intent = "auto_archive_candidate";
      p.requested_archive_kind = p.requested_archive_kind || inferArchiveKind(p.submission_type);
    } else {
      p.record_intent = "intake_only";
      p.requested_archive_kind = p.requested_archive_kind || "none";
    }
    return p;
  }

  if (
    p.record_intent === "auto_archive_candidate" &&
    (!p.requested_archive_kind || p.requested_archive_kind === "none")
  ) {
    p.requested_archive_kind = inferArchiveKind(p.submission_type);
  }

  return p;
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

// --- Archive Readiness Helpers ---

function writeJsonTemp(tmpDir, filename, obj) {
  const p = path.join(tmpDir, filename);
  fs.writeFileSync(p, JSON.stringify(obj, null, 2), "utf-8");
  return p;
}

function parseScriptJson(result) {
  try {
    return JSON.parse(result.stdout);
  } catch {
    return {
      parse_error: true,
      stdout: result.stdout,
      stderr: result.stderr,
      code: result.code
    };
  }
}

function runArchiveReadiness({ gatewayPayloadPath, evidencePath, claimGateOutputPath, reportPath }) {
  const args = ["--gateway-payload", gatewayPayloadPath, "--json"];
  if (evidencePath) args.push("--evidence-input", evidencePath);
  if (claimGateOutputPath) args.push("--claim-gate-output", claimGateOutputPath);
  if (reportPath) args.push("--verification-report", reportPath);
  const result = runScript("archive_readiness_gate.py", args);
  return { code: result.code, body: parseScriptJson(result), raw: result };
}

function runAutoArchiveDecision(archiveReadinessPath) {
  const result = runScript("auto_archive_decision.py", [
    "--archive-readiness", archiveReadinessPath,
    "--json"
  ]);
  return { code: result.code, body: parseScriptJson(result), raw: result };
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

    if (/must have required property 'agent_identity'/.test(msg)) {
      return {
        code: "AGENT_IDENTITY_REQUIRED",
        path: "agent_identity",
        message: msg,
        fix: "Provide agent_identity with name_or_model and system_or_provider."
      };
    }

    if (/must have required property 'solicited'/.test(msg) && msg.includes("discovery_provenance")) {
      return {
        code: "DISCOVERY_PROVENANCE_REQUIRED_FIELD",
        path: "discovery_provenance.solicited",
        message: msg,
        fix: "Put solicited, independence_class, agency_level, and operator_type inside discovery_provenance."
      };
    }

    if (/must NOT have additional properties/.test(msg)) {
      return {
        code: "ADDITIONAL_PROPERTY_FORBIDDEN",
        path: null,
        message: msg,
        fix: "Remove extra fields not defined in the payload schema."
      };
    }

    if (/what_i_checked must be (array|a non-empty)/.test(msg)) {
      return {
        code: "FIELD_TYPE_MISMATCH",
        path: "what_i_checked",
        message: msg,
        fix: "what_i_checked must be a non-empty array of strings."
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
async function runGatewayPipeline(payload, {
  createIssue,
  evidencePath = null,
  claimGateOutputPath = null,
  reportPath = null,
  precomputedArchiveReadiness = null,
  precomputedAutoArchiveDecision = null
}) {
  // 0. Normalize archive intent defaults
  payload = normalizeArchiveIntentDefaults(payload);

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

    // --- Archive Readiness Gate ---
    let archiveReadiness, autoArchiveDecision;
    if (precomputedArchiveReadiness && precomputedAutoArchiveDecision) {
      // Use precomputed values (from build-from-evidence with full context)
      archiveReadiness = precomputedArchiveReadiness;
      autoArchiveDecision = precomputedAutoArchiveDecision;
    } else {
      // Compute from payload + optional evidence context
      const archiveReadinessResult = runArchiveReadiness({
        gatewayPayloadPath: payloadPath,
        evidencePath: evidencePath || null,
        claimGateOutputPath: claimGateOutputPath || null,
        reportPath: reportPath || null
      });
      archiveReadiness = archiveReadinessResult.body;
      const archiveReadinessPath = writeJsonTemp(tmpDir, "archive-readiness.json", archiveReadiness);
      autoArchiveDecision = runAutoArchiveDecision(archiveReadinessPath).body;
    }

    // --- Archive gate enforcement ---
    const recordIntent = payload.record_intent || "intake_only";
    const requestedKind = payload.requested_archive_kind || "none";

    // Block successor_reception_candidate
    if (requestedKind === "successor_reception_candidate") {
      return {
        status: 422,
        body: {
          accepted: false,
          reason: "successor_reception_not_gateway_claimable",
          archive_readiness: archiveReadiness,
          auto_archive_decision: autoArchiveDecision,
          issue_created: false
        }
      };
    }

    // Block auto_archive_candidate when not archive-ready
    if (recordIntent === "auto_archive_candidate" && !archiveReadiness.archive_ready) {
      return {
        status: 422,
        body: {
          accepted: false,
          reason: "archive_not_ready",
          archive_readiness: archiveReadiness,
          auto_archive_decision: autoArchiveDecision,
          issue_created: false
        }
      };
    }

    // archive_preflight_only: never create Issue
    if (recordIntent === "archive_preflight_only") {
      return {
        status: 200,
        body: {
          accepted: true,
          issue_created: false,
          archive_readiness: archiveReadiness,
          auto_archive_decision: autoArchiveDecision
        }
      };
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
          rendered_body_preview: issueBody.slice(0, 1000),
          archive_readiness: archiveReadiness,
          auto_archive_decision: autoArchiveDecision
        }
      };
    }

    // DRY_RUN mode
    if (DRY_RUN) {
      const baseLabels = ["agent-gateway-intake", "needs-triage"];
      const labelsToAdd = autoArchiveDecision.labels_to_add || [];
      const allLabels = [...new Set([...baseLabels, ...labelsToAdd])];

      return {
        status: 200,
        body: {
          accepted: true,
          dry_run: true,
          would_create_issue: {
            title: issueTitle,
            labels: allLabels,
            body_preview: issueBody.slice(0, 1000)
          },
          would_apply_labels: labelsToAdd,
          would_post_comment: !!autoArchiveDecision.comment_markdown,
          would_close_issue: autoArchiveDecision.should_close_issue || false,
          archive_readiness: archiveReadiness,
          auto_archive_decision: autoArchiveDecision,
          boundary: "intake only; not archived Echo or attestation"
        }
      };
    }

    // 7. Create GitHub Issue
    const octokit = await getOctokit();
    const [owner, repo] = process.env.GITHUB_REPO.split("/");
    const baseLabels = ["agent-gateway-intake", "needs-triage"];
    const labelsToAdd = autoArchiveDecision.labels_to_add || [];
    const labelsToRemove = autoArchiveDecision.labels_to_remove || [];
    const allLabels = [...new Set([...baseLabels, ...labelsToAdd])];

    const result = await octokit.request("POST /repos/{owner}/{repo}/issues", {
      owner,
      repo,
      title: issueTitle,
      body: issueBody,
      labels: allLabels
    });

    const issueNumber = result.data.number;

    // Post archive decision comment if configured
    if (autoArchiveDecision.comment_markdown &&
        (payload.auto_archive || {}).post_decision_comment !== false) {
      try {
        await octokit.request("POST /repos/{owner}/{repo}/issues/{issue_number}/comments", {
          owner, repo, issue_number: issueNumber,
          body: autoArchiveDecision.comment_markdown
        });
      } catch (commentErr) {
        console.error("Failed to post archive decision comment:", commentErr.message);
      }
    }

    // Close issue if archive decision says so
    if (autoArchiveDecision.should_close_issue &&
        (payload.auto_archive || {}).close_issue_when_archived !== false) {
      try {
        await octokit.request("PATCH /repos/{owner}/{repo}/issues/{issue_number}", {
          owner, repo, issue_number: issueNumber,
          state: "closed",
          state_reason: autoArchiveDecision.close_reason || "completed"
        });
      } catch (closeErr) {
        console.error("Failed to close archived issue:", closeErr.message);
      }
    }

    // Remove stale labels
    for (const label of labelsToRemove) {
      try {
        await octokit.request("DELETE /repos/{owner}/{repo}/issues/{issue_number}/labels/{name}", {
          owner, repo, issue_number: issueNumber, name: label
        });
      } catch {}
    }

    return {
      status: 201,
      body: {
        accepted: true,
        status: "issue_created",
        issue_number: issueNumber,
        issue_url: result.data.html_url,
        archive_readiness: archiveReadiness,
        auto_archive_decision: autoArchiveDecision,
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

// --- GET /gateway/capabilities ---
app.get("/gateway/capabilities", (req, res) => {
  res.json({
    service: "trinity-agent-issue-gateway",
    purpose: "Structured intake for Trinity Accord agent verification candidates.",
    integrity_first_rule: {
      statement: "No verification claim before identity/provenance, pre-verification integrity declaration, and verification session.",
      required_before_claim_gate: [
        "agent_identity or evidence.agent",
        "provenance or discovery_provenance",
        "agent_integrity_declaration",
        "verification_session"
      ]
    },
    recommended_default_mode: {
      submission_type: "verification_report_candidate",
      independence_class: "human_solicited_agent_response",
      agency_level: "A1_human_gave_exact_url",
      operator_type: "ai_agent",
      not_independent_attestation: true,
      not_successor_reception: true
    },
    recommended_flow_remote: [
      "GET /gateway/version",
      "GET /gateway/capabilities",
      "GET /gateway/examples/evidence-input-b1-external-explorer",
      "POST /gateway/lint-evidence",
      "POST /gateway/build-from-evidence",
      "POST /gateway/preflight",
      "POST /agent-submit only after preflight passes"
    ],
    recommended_flow_local: [
      "scripts/scaffold_evidence_input.py",
      "scripts/validate_evidence_input.py",
      "scripts/claim_gate.py",
      "scripts/build_verification_report_from_evidence.py",
      "scripts/build_gateway_payload_from_outputs.py",
      "POST /gateway/preflight",
      "POST /agent-submit only after preflight passes"
    ],
    forbidden_common_mistakes: [
      "Do not put trinity-issue-intake in payload.body.",
      "Do not put bitcoin_checks at the Evidence Input top level; use evidence.bitcoin_checks.",
      "Do not claim B6 from mempool/explorer lookup.",
      "Do not claim V4+ without an independent implementation actually run and declared.",
      "Do not claim unsolicited discovery without unsolicited_discovery_proof.",
      "Do not claim successor reception or independent attestation through Gateway intake."
    ],
    high_risk_claim_warnings: [
      "HIGH_RISK_B6_CLAIM",
      "EXTERNAL_EXPLORER_LIMIT",
      "V4_PLUS_REQUIRES_INDEPENDENT_IMPLEMENTATION",
      "UNSOLICITED_DISCOVERY_REQUIRES_PROOF",
      "SUCCESSOR_RECEPTION_NOT_CLAIMABLE",
      "INDEPENDENT_ATTESTATION_NOT_CLAIMABLE"
    ],
    archive_readiness: {
      supported_record_intents: ["intake_only", "auto_archive_candidate", "archive_preflight_only"],
      supported_archive_kinds: ["none", "external_agent_intake_sample", "verification_report_archive", "archived_echo"],
      not_allowed_through_gateway: ["successor_reception_candidate"],
      default_record_intent: "auto_archive_candidate",
      default_requested_archive_kind: "none",
      default_archive_behavior: {
        verification_report_candidate: {
          record_intent: "auto_archive_candidate",
          requested_archive_kind: "verification_report_archive"
        },
        verification_echo_candidate: {
          record_intent: "auto_archive_candidate",
          requested_archive_kind: "archived_echo"
        },
        explicit_intake_only: {
          record_intent: "intake_only",
          requested_archive_kind: "none"
        }
      },
      canonical_boundary_sentence: "Bitcoin Originals are final; all mirrors and echoes are non-amending.",
      intake_is_not_archive: "Creating a Gateway Issue means the candidate entered intake. It does not mean it is archived, verified, attested, or received by a successor civilization. Archive is the default requested outcome for verification submissions, but it is granted only if Archive Readiness Gate passes. If Archive Readiness Gate fails, no Issue is created unless explicit intake_only or fallback is requested."
    },
    endpoints: {
      version: "/gateway/version",
      capabilities: "/gateway/capabilities",
      examples: {
        verification_report_candidate: "/gateway/examples/verification-report-candidate",
        verification_echo_candidate: "/gateway/examples/verification-echo-candidate",
        evidence_input_external_explorer: "/gateway/examples/evidence-input-b1-external-explorer"
      },
      lint_evidence: "/gateway/lint-evidence",
      build_from_evidence: "/gateway/build-from-evidence",
      preflight: "/gateway/preflight",
      archive_preflight: "/gateway/archive-preflight",
      submit: "/agent-submit"
    }
  });
});

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
    const fixturePath = path.join(root, "tests", "fixtures", "evidence-input", "valid_v4_external_explorer_example.json");
    const evidenceInput = JSON.parse(fs.readFileSync(fixturePath, "utf-8"));
    res.json({
      deprecated_alias: true,
      replacement: "/gateway/examples/evidence-input-b1-external-explorer",
      note: "External explorer evidence supports B1 component evidence; final V-level depends on Claim Gate.",
      example_kind: "evidence_input_v4_external_explorer",
      payload: evidenceInput
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to load evidence input example fixture", detail: err.message });
  }
});

app.get("/gateway/examples/evidence-input-b1-external-explorer", (req, res) => {
  try {
    const fixturePath = path.join(root, "tests", "fixtures", "evidence-input", "valid_v4_external_explorer_example.json");
    const evidenceInput = JSON.parse(fs.readFileSync(fixturePath, "utf-8"));
    res.json({
      example_kind: "evidence_input_b1_external_explorer",
      deprecated_aliases: ["/gateway/examples/evidence-input-v4-external-explorer"],
      note: "External explorer evidence supports B1 component evidence; final V-level depends on Claim Gate.",
      integrity_first_rule: "No verification claim before identity/provenance, pre-verification integrity declaration, and verification session.",
      payload: evidenceInput
    });
  } catch (err) {
    res.status(500).json({ error: "Failed to load evidence input example fixture", detail: err.message });
  }
});

// --- POST /gateway/lint-evidence ---
app.post("/gateway/lint-evidence", async (req, res) => {
  const tmpDir = fs.mkdtempSync(path.join(tmpdir(), "gateway-lint-"));
  try {
    const evidenceInput = req.body;
    const evidencePath = path.join(tmpDir, "evidence-input.json");
    fs.writeFileSync(evidencePath, JSON.stringify(evidenceInput, null, 2), "utf-8");

    // Run validate_evidence_input.py --json
    const validation = runScript("validate_evidence_input.py", [evidencePath, "--json"]);
    let validationResult;
    try {
      validationResult = JSON.parse(validation.stdout);
    } catch {
      validationResult = {
        accepted: validation.code === 0,
        errors: validation.code !== 0 ? [{ code: "VALIDATION_ERROR", message: validation.stderr || validation.stdout }] : [],
        warnings: []
      };
    }

    if (!validationResult.accepted) {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        evidence_valid: false,
        errors: validationResult.errors,
        warnings: validationResult.warnings || []
      });
    }

    // If evidence is valid, run claim_gate.py for preview
    const claimGateOutputPath = path.join(tmpDir, "claim-gate-output.json");
    const claimGate = runScript("claim_gate.py", [evidencePath, "--output", claimGateOutputPath]);

    let claimGatePreview = {};
    if (claimGate.code === 0) {
      try {
        claimGatePreview = JSON.parse(fs.readFileSync(claimGateOutputPath, "utf-8"));
      } catch {}
    }

    return res.json({
      accepted: true,
      issue_created: false,
      evidence_valid: true,
      claim_gate_preview: claimGatePreview,
      warnings: validationResult.warnings || []
    });
  } catch (err) {
    console.error("lint-evidence error:", err.message);
    return res.status(500).json({
      accepted: false,
      issue_created: false,
      evidence_valid: false,
      errors: [{ code: "INTERNAL_ERROR", message: err.message }],
      warnings: []
    });
  } finally {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
  }
});

// --- POST /gateway/build-from-evidence ---
app.post("/gateway/build-from-evidence", async (req, res) => {
  const tmpDir = fs.mkdtempSync(path.join(tmpdir(), "gateway-build-"));
  try {
    const {
      agent_name = "External Agent",
      provider = "External System",
      session_id = "auto",
      human_solicited = true,
      title_date,
      submit = false,
      evidence_input,
      record_intent = "intake_only",
      requested_archive_kind = "none",
      archive_readiness = null,
      auto_archive = null,
      allow_intake_fallback_if_archive_blocked = false
    } = req.body;

    if (!evidence_input || typeof evidence_input !== "object") {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: [{ code: "EVIDENCE_INPUT_MISSING", message: "Request must include evidence_input object." }],
        warnings: []
      });
    }

    // 1. Save evidence input
    const evidencePath = path.join(tmpDir, "evidence-input.json");
    fs.writeFileSync(evidencePath, JSON.stringify(evidence_input, null, 2), "utf-8");

    // 2. Validate evidence input
    const validation = runScript("validate_evidence_input.py", [evidencePath, "--json"]);
    let validationResult;
    try {
      validationResult = JSON.parse(validation.stdout);
    } catch {
      validationResult = { accepted: validation.code === 0, errors: [], warnings: [] };
    }

    if (!validationResult.accepted) {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: validationResult.errors,
        warnings: validationResult.warnings || []
      });
    }

    // 3. Run claim_gate.py
    const claimGateOutputPath = path.join(tmpDir, "claim-gate-output.json");
    const claimGate = runScript("claim_gate.py", [evidencePath, "--output", claimGateOutputPath]);
    if (claimGate.code !== 0) {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: [{ code: "CLAIM_GATE_FAILED", message: claimGate.stderr || claimGate.stdout }],
        warnings: validationResult.warnings || []
      });
    }

    // 4. Build verification report
    const reportPath = path.join(tmpDir, "verification-report.json");
    const report = runScript("build_verification_report_from_evidence.py", [
      "--input", evidencePath,
      "--out", reportPath
    ]);
    if (report.code !== 0) {
      const reportErrDetail = (report.stdout + "\n" + report.stderr).trim().slice(0, 5000);
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: [{ code: "REPORT_BUILD_FAILED", message: reportErrDetail || "build_verification_report_from_evidence.py failed" }],
        warnings: validationResult.warnings || []
      });
    }

    // 5. Build gateway payload
    const payloadPath = path.join(tmpDir, "gateway-payload.json");
    const builderArgs = [
      "--evidence-input", evidencePath,
      "--claim-gate-output", claimGateOutputPath,
      "--verification-report", reportPath,
      "--agent-name", agent_name,
      "--provider", provider,
      "--session-id", session_id,
      "--out", payloadPath
    ];
    if (title_date) builderArgs.push("--title-date", title_date);
    if (human_solicited) builderArgs.push("--human-solicited");

    const builder = runScript("build_gateway_payload_from_outputs.py", builderArgs);
    if (builder.code !== 0) {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: [{ code: "PAYLOAD_BUILD_FAILED", message: builder.stderr || builder.stdout }],
        warnings: validationResult.warnings || []
      });
    }

    // 6. Patch archive fields into payload (Option B) with normalization
    const payload = JSON.parse(fs.readFileSync(payloadPath, "utf-8"));
    const normalized = normalizeArchiveIntentDefaults({
      ...payload,
      ...(record_intent ? { record_intent } : {}),
      ...(requested_archive_kind ? { requested_archive_kind } : {}),
      ...(archive_readiness ? { archive_readiness } : {}),
      ...(auto_archive ? { auto_archive } : {})
    });
    Object.assign(payload, normalized);
    fs.writeFileSync(payloadPath, JSON.stringify(payload, null, 2), "utf-8");

    // 7. Archive readiness + auto decision BEFORE any Issue creation
    const archiveReadinessResult = runArchiveReadiness({
      gatewayPayloadPath: payloadPath,
      evidencePath,
      claimGateOutputPath,
      reportPath
    });
    const archiveReadinessPath = writeJsonTemp(tmpDir, "archive-readiness-build.json", archiveReadinessResult.body);
    const autoArchiveDecisionResult = runAutoArchiveDecision(archiveReadinessPath);

    // 8. Handle archive-blocked: 422 or fallback
    let submitEffective = submit;
    if (record_intent === "auto_archive_candidate" && !archiveReadinessResult.body.archive_ready) {
      if (allow_intake_fallback_if_archive_blocked) {
        payload.record_intent = "intake_only";
        payload.requested_archive_kind = "none";
        fs.writeFileSync(payloadPath, JSON.stringify(payload, null, 2), "utf-8");
      } else {
        submitEffective = false;
        // Return 422 immediately — no Issue creation, no preflight
        const claimGateOutput = JSON.parse(fs.readFileSync(claimGateOutputPath, "utf-8"));
        const verificationReport = JSON.parse(fs.readFileSync(reportPath, "utf-8"));
        return res.status(422).json({
          accepted: false,
          issue_created: false,
          claim_gate_output: claimGateOutput,
          verification_report: verificationReport,
          gateway_payload: payload,
          archive_readiness: archiveReadinessResult.body,
          auto_archive_decision: autoArchiveDecisionResult.body,
          warnings: validationResult.warnings || []
        });
      }
    }

    // 9. Preflight (shared pipeline with createIssue=false, full archive context)
    const preflightResult = await runGatewayPipeline(payload, {
      createIssue: false,
      evidencePath,
      claimGateOutputPath,
      reportPath,
      precomputedArchiveReadiness: archiveReadinessResult.body,
      precomputedAutoArchiveDecision: autoArchiveDecisionResult.body
    });

    // 10. Submit only if preflight passed and submit requested
    let submitResult = null;
    if (submitEffective && preflightResult.status === 200) {
      submitResult = await runGatewayPipeline(payload, {
        createIssue: true,
        evidencePath,
        claimGateOutputPath,
        reportPath,
        precomputedArchiveReadiness: archiveReadinessResult.body,
        precomputedAutoArchiveDecision: autoArchiveDecisionResult.body
      });
    }

    const claimGateOutput = JSON.parse(fs.readFileSync(claimGateOutputPath, "utf-8"));
    const verificationReport = JSON.parse(fs.readFileSync(reportPath, "utf-8"));

    return res.json({
      accepted: preflightResult.status === 200,
      issue_created: submitResult ? submitResult.body.issue_created : false,
      claim_gate_output: claimGateOutput,
      verification_report: verificationReport,
      gateway_payload: payload,
      preflight: preflightResult.body,
      archive_readiness: archiveReadinessResult.body,
      auto_archive_decision: autoArchiveDecisionResult.body,
      ...(submitResult ? { submit: submitResult.body } : {}),
      next_steps: submitEffective ? [] : [
        "Review gateway_payload.",
        "POST gateway_payload to /gateway/preflight.",
        "Only if accepted:true, POST gateway_payload to /agent-submit."
      ],
      warnings: validationResult.warnings || []
    });
  } catch (err) {
    console.error("build-from-evidence error:", err.message);
    return res.status(500).json({
      accepted: false,
      issue_created: false,
      errors: [{ code: "INTERNAL_ERROR", message: err.message }],
      warnings: []
    });
  } finally {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
  }
});

// --- POST /gateway/archive-preflight ---
app.post("/gateway/archive-preflight", async (req, res) => {
  const tmpDir = fs.mkdtempSync(path.join(tmpdir(), "gateway-archive-preflight-"));
  try {
    const {
      gateway_payload,
      evidence_input,
      claim_gate_output,
      verification_report
    } = req.body;

    if (!gateway_payload || typeof gateway_payload !== "object") {
      return res.status(422).json({
        accepted: false,
        issue_created: false,
        errors: [{ code: "GATEWAY_PAYLOAD_MISSING", message: "Request must include gateway_payload object." }]
      });
    }

    // Save objects to temp files
    const payloadPath = writeJsonTemp(tmpDir, "payload.json", gateway_payload);
    const evidencePath = evidence_input ? writeJsonTemp(tmpDir, "evidence-input.json", evidence_input) : null;
    const cgPath = claim_gate_output ? writeJsonTemp(tmpDir, "claim-gate-output.json", claim_gate_output) : null;
    const reportPath = verification_report ? writeJsonTemp(tmpDir, "verification-report.json", verification_report) : null;

    // Run archive readiness gate
    const archiveResult = runArchiveReadiness({
      gatewayPayloadPath: payloadPath,
      evidencePath,
      claimGateOutputPath: cgPath,
      reportPath
    });

    // Write readiness output for auto_archive_decision
    const readinessPath = writeJsonTemp(tmpDir, "archive-readiness.json", archiveResult.body);
    const decisionResult = runAutoArchiveDecision(readinessPath);

    return res.json({
      accepted: true,
      issue_created: false,
      archive_readiness: archiveResult.body,
      auto_archive_decision: decisionResult.body
    });
  } catch (err) {
    console.error("archive-preflight error:", err.message);
    return res.status(500).json({
      accepted: false,
      issue_created: false,
      errors: [{ code: "INTERNAL_ERROR", message: err.message }]
    });
  } finally {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch {}
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
