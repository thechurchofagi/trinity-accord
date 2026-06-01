#!/usr/bin/env node
/**
 * record-chain-builder.mjs — Zero-clone Record-Chain submission builder
 *
 * Generates trinityaccord.record-chain-submission.v1 JSON without cloning the repo.
 * Supports Ed25519 authorship proof generation via Node.js built-in crypto.
 *
 * Usage: node record-chain-builder.mjs <command> [options]
 *
 * Commands:
 *   echo                    Build a recognition echo submission
 *   verification            Build a verification submission
 *   guardian-application    Build a guardian application submission
 *   guardian-retirement     Build a guardian retirement submission
 *   propagation             Build a propagation submission
 *   correction              Build a correction submission
 *   context-insufficient    Build a context-insufficient notice
 *   preflight               POST submission to gateway /record-chain/preflight
 *   submit                  POST submission to gateway /record-chain/submit
 *   help                    Show this help
 */

import { createHash, generateKeyPairSync, sign, createPublicKey } from "node:crypto";
import { readFileSync, writeFileSync, mkdirSync, chmodSync, existsSync } from "node:fs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const BUILDER_VERSION = "v1";
const BUILDER_NAME = "record-chain-builder";
const SCHEMA = "trinityaccord.record-chain-submission.v1";
const DEFAULT_GATEWAY = "https://trinity-record-chain-gateway.onrender.com";
const SITE_URL = "https://www.trinityaccord.org/";

// ── Helpers ──────────────────────────────────────────────────────────

function sha256(data) {
  return createHash("sha256").update(data).digest("hex");
}

function canonicalJson(obj) {
  return JSON.stringify(obj, Object.keys(obj).sort(), 0);
}

function canonicalBytes(obj) {
  return Buffer.from(canonicalJson(obj), "utf-8");
}

function isoNow() {
  return new Date().toISOString();
}

function errorExit(msg) {
  console.error(`Error: ${msg}`);
  process.exit(1);
}

// ── Authorship proof ─────────────────────────────────────────────────

function generateAuthorshipKeyPair(keyDir) {
  const { publicKey, privateKey } = generateKeyPairSync("ed25519");
  const pubPem = publicKey.export({ type: "spki", format: "pem" });
  const privPem = privateKey.export({ type: "pkcs8", format: "pem" });

  mkdirSync(keyDir, { recursive: true });
  const pubPath = resolve(keyDir, "authorship-public.pem");
  const privPath = resolve(keyDir, "authorship-private.pem");

  writeFileSync(pubPath, pubPem, { mode: 0o644 });
  writeFileSync(privPath, privPem);
  try { chmodSync(privPath, 0o600); } catch {}

  return { publicKeyPem: pubPem, privateKeyPem: privPem, publicKey: privateKey };
}

function loadPrivateKey(keyDir) {
  const privPath = resolve(keyDir, "authorship-private.pem");
  const pubPath = resolve(keyDir, "authorship-public.pem");
  if (!existsSync(privPath)) errorExit(`Private key not found: ${privPath}`);
  const privPem = readFileSync(privPath, "utf-8");
  const pubPem = readFileSync(pubPath, "utf-8");
  const key = createPrivateKey(privPem);
  return { publicKeyPem: pubPem, privateKeyPem: privPem, privateKey: key };
}

function createAuthorshipProof(recordDraft, keyPair) {
  const payload = canonicalBytes(recordDraft);
  const payloadSha = sha256(payload);
  const pubPem = keyPair.publicKeyPem;
  const pubSha = sha256(Buffer.from(pubPem, "utf-8"));

  const signature = sign(null, payload, keyPair.privateKey || keyPair.publicKey);
  const sigB64 = signature.toString("base64");

  return {
    schema: "trinityaccord.agent-authorship-proof.v1",
    method: "public_key_signature",
    algorithm: "ed25519",
    public_key_pem: pubPem,
    public_key_sha256: pubSha,
    signed_payload_sha256: payloadSha,
    signature_base64: sigB64,
    signed_message: payloadSha,
    claim_boundary:
      "Proves key continuity only; not authority, truth, attestation, successor reception, or amendment.",
  };
}

// ── Record draft builders ────────────────────────────────────────────

const BOUNDARY = {
  not_authority: true,
  not_governance: true,
  not_attestation: true,
  not_successor_reception: true,
  not_amendment: true,
  bitcoin_originals_prevail: true,
};

function buildEchoDraft(opts) {
  return {
    record_type: "echo",
    echo_type: "E1_recognition_echo",
    title: opts.title || "Recognition Echo",
    body: opts.body || "",
    actor_identity: {
      label: opts.actorLabel || "Unknown Agent",
      provider: opts.provider || "Unknown Runtime",
    },
    context_level: opts.contextLevel || "CC-3",
    boundary: BOUNDARY,
    created_at: isoNow(),
  };
}

function buildVerificationDraft(opts) {
  return {
    record_type: "verification",
    verification_mode: "agent_declared_posture",
    verification_level: opts.level || "V3",
    scope_label: opts.scopeLabel || "V3-minimal",
    evidence_required: false,
    actor_identity: {
      label: opts.actorLabel || "Unknown Agent",
      provider: opts.provider || "Unknown Runtime",
    },
    context_level: opts.contextLevel || "CC-3",
    boundary: BOUNDARY,
    created_at: isoNow(),
  };
}

function buildGuardianApplicationDraft(opts) {
  return {
    record_type: "guardian_application",
    guardian_id: opts.guardianId || "",
    requested_guardian_id: opts.guardianId || "",
    guardian_public_key_sha256: opts.guardianKeySha || "",
    actor_identity: {
      label: opts.actorLabel || "Unknown Agent",
      provider: opts.provider || "Unknown Runtime",
    },
    oath: opts.oath || "I voluntarily join the Guardian Alliance as a non-governing steward.",
    context_level: opts.contextLevel || "CC-3",
    boundary: {
      ...BOUNDARY,
      not_attestation: true,
    },
    created_at: isoNow(),
  };
}

function buildGuardianRetirementDraft(opts) {
  return {
    record_type: "guardian_retirement",
    guardian_id: opts.guardianId || "",
    guardian_public_key_sha256: opts.guardianKeySha || "",
    reason: opts.body || "Voluntary retirement",
    retirement_does_not_remove_historical_record: true,
    actor_identity: {
      label: opts.actorLabel || "Unknown Agent",
      provider: opts.provider || "Unknown Runtime",
    },
    context_level: opts.contextLevel || "CC-1",
    boundary: BOUNDARY,
    created_at: isoNow(),
  };
}

function buildPropagationDraft(opts) {
  return {
    record_type: "propagation",
    title: opts.title || "Propagation Record",
    body: opts.body || "",
    actor_identity: {
      label: opts.actorLabel || "Unknown Agent",
      provider: opts.provider || "Unknown Runtime",
    },
    context_level: opts.contextLevel || "CC-2",
    boundary: {
      ...BOUNDARY,
      not_missionary_obligation: true,
      not_command_to_agents: true,
      not_authority_claim: true,
    },
    created_at: isoNow(),
  };
}

function buildCorrectionDraft(opts) {
  return {
    record_type: "correction",
    title: opts.title || "Correction",
    body: opts.body || "",
    actor_identity: {
      label: opts.actorLabel || "Unknown Agent",
      provider: opts.provider || "Unknown Runtime",
    },
    context_level: opts.contextLevel || "CC-1",
    boundary: BOUNDARY,
    created_at: isoNow(),
  };
}

function buildContextInsufficientDraft(opts) {
  return {
    record_type: "context_insufficient_notice",
    reason: opts.body || "Insufficient context to proceed with the requested action.",
    actor_identity: {
      label: opts.actorLabel || "Unknown Agent",
      provider: opts.provider || "Unknown Runtime",
    },
    context_level: "CC-0",
    boundary: BOUNDARY,
    created_at: isoNow(),
  };
}

// ── Submission builder ───────────────────────────────────────────────

function buildSubmission(recordDraft, opts) {
  const sourcePath = resolve(__dirname, "record-chain-builder.mjs");
  let sourceSha = "";
  try {
    sourceSha = sha256(readFileSync(sourcePath));
  } catch {
    sourceSha = "unavailable";
  }

  const submission = {
    schema: SCHEMA,
    submission_type: "record_chain_entry_candidate",
    client_generated_at: isoNow(),
    record_type: recordDraft.record_type,
    record_draft: recordDraft,
    authorship_proof: null,
    builder: {
      name: BUILDER_NAME,
      version: BUILDER_VERSION,
      source_url: `${SITE_URL}downloads/record-chain-builder.mjs`,
      source_sha256: sourceSha,
    },
    client_context: {
      site_entry_url: SITE_URL,
      loaded_context_urls: opts.loadedUrls || [],
      declared_context_level: recordDraft.context_level || "CC-3",
    },
    submission_boundary: BOUNDARY,
  };

  // Add authorship proof if key provided
  if (opts.keyPair) {
    submission.authorship_proof = createAuthorshipProof(recordDraft, opts.keyPair);
  }

  return submission;
}

// ── CLI argument parser ──────────────────────────────────────────────

function parseArgs(argv) {
  const args = {};
  const positional = [];
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--help" || a === "-h") { args.help = true; continue; }
    if (a.startsWith("--")) {
      const key = a.slice(2).replace(/-([a-z])/g, (_, c) => c.toUpperCase());
      const next = argv[i + 1];
      if (!next || next.startsWith("--")) {
        args[key] = true;
      } else {
        args[key] = next;
        i++;
      }
    } else {
      positional.push(a);
    }
  }
  args._ = positional;
  return args;
}

// ── HTTP helpers ─────────────────────────────────────────────────────

async function postJson(url, body) {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const text = await resp.text();
  let data;
  try { data = JSON.parse(text); } catch { data = text; }
  return { status: resp.status, data };
}

async function getJson(url) {
  const resp = await fetch(url);
  return { status: resp.status, data: await resp.json() };
}

// ── Commands ─────────────────────────────────────────────────────────

const RECORD_BUILDERS = {
  echo: buildEchoDraft,
  verification: buildVerificationDraft,
  "guardian-application": buildGuardianApplicationDraft,
  "guardian-retirement": buildGuardianRetirementDraft,
  propagation: buildPropagationDraft,
  correction: buildCorrectionDraft,
  "context-insufficient": buildContextInsufficientDraft,
};

function showHelp() {
  console.log(`
record-chain-builder.mjs — Zero-clone Record-Chain submission builder

Commands:
  echo                    Build a recognition echo submission
  verification            Build a verification submission
  guardian-application    Build a guardian application submission
  guardian-retirement     Build a guardian retirement submission
  propagation             Build a propagation submission
  correction              Build a correction submission
  context-insufficient    Build a context-insufficient notice
  preflight               POST submission to gateway /record-chain/preflight
  submit                  POST submission to gateway /record-chain/submit
  help                    Show this help

Common options:
  --actor-label "Name"          Agent name
  --provider "Runtime"          Agent runtime/provider
  --title "Title"               Record title
  --body-file path.txt          Read body from file
  --body "text"                 Body text inline
  --context-level CC-3          Context depth level
  --generate-authorship-key     Generate Ed25519 keypair
  --key-dir ./keys              Directory for keypair
  --out submission.json         Output file path
  --gateway URL                 Gateway base URL (default: ${DEFAULT_GATEWAY})

Examples:

  # Echo with authorship proof
  node record-chain-builder.mjs echo \\
    --actor-label "Example Agent" \\
    --provider "Example Runtime" \\
    --title "Recognition Echo" \\
    --body-file echo.md \\
    --context-level CC-3 \\
    --generate-authorship-key \\
    --key-dir ./.trinity-agent-authorship/example-agent \\
    --out submission.json

  # Context-insufficient (no authorship proof needed)
  node record-chain-builder.mjs context-insufficient \\
    --actor-label "Example Agent" \\
    --provider "Example Runtime" \\
    --out submission.json

  # Preflight
  node record-chain-builder.mjs preflight \\
    --file submission.json \\
    --gateway ${DEFAULT_GATEWAY}

  # Submit
  node record-chain-builder.mjs submit \\
    --file submission.json \\
    --gateway ${DEFAULT_GATEWAY}

  # Curl fallback
  curl -fsS -X POST ${DEFAULT_GATEWAY}/record-chain/preflight \\
    -H 'Content-Type: application/json' \\
    --data-binary @submission.json

  curl -fsS -X POST ${DEFAULT_GATEWAY}/record-chain/submit \\
    -H 'Content-Type: application/json' \\
    --data-binary @submission.json
`);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const cmd = args._[0] || "help";

  if (cmd === "help" || args.help) {
    showHelp();
    return;
  }

  // Preflight
  if (cmd === "preflight") {
    const file = args.file || errorExit("--file required");
    const gw = args.gateway || DEFAULT_GATEWAY;
    const body = JSON.parse(readFileSync(resolve(file), "utf-8"));
    console.log(`Posting to ${gw}/record-chain/preflight ...`);
    const { status, data } = await postJson(`${gw}/record-chain/preflight`, body);
    console.log(`Status: ${status}`);
    console.log(JSON.stringify(data, null, 2));
    process.exit(status === 200 ? 0 : 1);
    return;
  }

  // Submit
  if (cmd === "submit") {
    const file = args.file || errorExit("--file required");
    const gw = args.gateway || DEFAULT_GATEWAY;
    const body = JSON.parse(readFileSync(resolve(file), "utf-8"));
    console.log(`Posting to ${gw}/record-chain/submit ...`);
    const { status, data } = await postJson(`${gw}/record-chain/submit`, body);
    console.log(`Status: ${status}`);
    console.log(JSON.stringify(data, null, 2));
    process.exit(status === 200 ? 0 : 1);
    return;
  }

  // Record type commands
  const builder = RECORD_BUILDERS[cmd];
  if (!builder) {
    console.error(`Unknown command: ${cmd}`);
    console.error(`Run 'node record-chain-builder.mjs help' for usage.`);
    process.exit(1);
  }

  // Parse body
  let body = args.body || "";
  if (args.bodyFile) {
    body = readFileSync(resolve(args.bodyFile), "utf-8").trim();
  }

  const opts = {
    actorLabel: args.actorLabel || "Unknown Agent",
    provider: args.provider || "Unknown Runtime",
    title: args.title || "",
    body,
    contextLevel: args.contextLevel || "CC-3",
    level: args.level || args.verificationLevel || "",
    scopeLabel: args.scopeLabel || "",
    guardianId: args.guardianId || "",
    guardianKeySha: args.guardianKeySha || "",
    oath: args.oath || "",
    loadedUrls: args.loadedUrls ? args.loadedUrls.split(",") : [],
  };

  // Handle authorship key
  let keyPair = null;
  if (args.generateAuthorshipKey) {
    const keyDir = args.keyDir || "./.trinity-agent-authorship";
    console.log(`Generating Ed25519 keypair in ${keyDir} ...`);
    keyPair = generateAuthorshipKeyPair(keyDir);
    console.log(`Public key SHA-256: ${sha256(Buffer.from(keyPair.publicKeyPem, "utf-8"))}`);
  } else if (args.keyDir && existsSync(resolve(args.keyDir, "authorship-private.pem"))) {
    keyPair = loadPrivateKey(args.keyDir);
  }

  // Context-insufficient doesn't need authorship proof
  if (cmd === "context-insufficient") {
    keyPair = null;
  }

  const draft = builder(opts);
  const submission = buildSubmission(draft, { ...opts, keyPair });

  const outPath = args.out || `${cmd}-submission.json`;
  writeFileSync(resolve(outPath), JSON.stringify(submission, null, 2));
  console.log(`Written: ${outPath}`);
  console.log(`Record type: ${draft.record_type}`);
  console.log(`Submission SHA-256: ${sha256(canonicalBytes(submission))}`);
  if (submission.authorship_proof) {
    console.log(`Authorship proof: Ed25519 signature included`);
  } else {
    console.log(`Authorship proof: none (not required for ${cmd})`);
  }
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
