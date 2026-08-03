#!/usr/bin/env node
/**
 * Verified bootstrap and ambiguity-recovery wrapper for the canonical
 * Trinity Accord Record-Chain Builder.
 *
 * The original Builder remains byte-for-byte preserved in
 * record-chain-builder-core.mjs. This wrapper verifies that core before
 * execution and intercepts only ambiguous submit outcomes. Recovery is
 * read-only: it never issues a second POST.
 */

import { createHash } from "node:crypto";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const CORE_FILENAME = "record-chain-builder-core.mjs";
const CORE_SHA256 = "6b81d5e855d73db9e9b20dd756ac97ab72a55352589d06c16837779fdf3d0378";
const CORE_SIZE_BYTES = 195854;
const CORE_URLS = [
  "https://www.trinityaccord.org/downloads/record-chain-builder-core.mjs",
  "https://raw.githubusercontent.com/thechurchofagi/trinity-accord/main/downloads/record-chain-builder-core.mjs",
];

const nativeFetch = globalThis.fetch.bind(globalThis);
const wrapperFileUrl = import.meta.url;

function sha256Bytes(value) {
  return createHash("sha256").update(value).digest("hex");
}

function canonicalJson(value) {
  if (value === null || typeof value === "boolean" || typeof value === "string") {
    return JSON.stringify(value);
  }
  if (typeof value === "number") {
    if (!Number.isFinite(value)) throw new Error("Non-finite JSON number");
    return JSON.stringify(value);
  }
  if (Array.isArray(value)) {
    return `[${value.map((item) => canonicalJson(item)).join(",")}]`;
  }
  if (typeof value === "object") {
    return `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${canonicalJson(value[key])}`
    ).join(",")}}`;
  }
  throw new Error(`Unsupported JSON value type: ${typeof value}`);
}

function submissionSha256FromBody(body) {
  let text;
  if (typeof body === "string") {
    text = body;
  } else if (body instanceof Uint8Array) {
    text = new TextDecoder().decode(body);
  } else {
    return null;
  }
  const parsed = JSON.parse(text);
  return sha256Bytes(Buffer.from(canonicalJson(parsed), "utf8"));
}

function verifiedReceiptPayload(data, expectedSubmissionSha256) {
  if (!data || typeof data !== "object") return null;
  if (data.recovery_verified !== true || data.receipt_hash_verified !== true) return null;
  if (data.submission_sha256 !== expectedSubmissionSha256) return null;

  const receipt = data.receipt;
  if (!receipt || typeof receipt !== "object") return null;
  const receiptId = data.receipt_id;
  if (typeof receiptId !== "string" || !receiptId) return null;
  if (receipt.server_receipt_id !== receiptId) return null;
  if (receipt.submission_sha256 !== expectedSubmissionSha256) return null;
  if (typeof receipt.receipt_sha256 !== "string") return null;

  const receiptMaterial = { ...receipt };
  delete receiptMaterial.receipt_sha256;
  const computedReceiptSha256 = sha256Bytes(
    Buffer.from(canonicalJson(receiptMaterial), "utf8")
  );
  if (computedReceiptSha256 !== receipt.receipt_sha256) return null;

  return {
    accepted: true,
    submitted: true,
    duplicate: true,
    recovered_after_ambiguous_submit: true,
    recovery_was_read_only: true,
    receipt_id: receiptId,
    record_type: receipt.record_type || data.record_type || "",
    submission_sha256: expectedSubmissionSha256,
    append_status: data.final_status?.append_status || "recovered_existing_receipt",
    receipt,
    final_status: data.final_status || null,
    warnings: [
      "The original submit result was ambiguous. The Builder recovered a hash-verified durable receipt through a read-only endpoint and did not issue a second write request."
    ],
  };
}

function recoveryAttempts() {
  const parsed = Number.parseInt(
    process.env.TRINITY_SUBMIT_RECOVERY_ATTEMPTS || "12",
    10
  );
  return Number.isFinite(parsed) ? Math.min(Math.max(parsed, 1), 60) : 12;
}

function recoveryDelayMs() {
  const parsed = Number.parseInt(
    process.env.TRINITY_SUBMIT_RECOVERY_DELAY_MS || "750",
    10
  );
  return Number.isFinite(parsed) ? Math.min(Math.max(parsed, 0), 10_000) : 750;
}

async function sleep(ms) {
  if (ms > 0) await new Promise((resolve) => setTimeout(resolve, ms));
}

async function recoverSubmission(submitUrl, submissionSha256) {
  const recoveryUrl = new URL(submitUrl);
  recoveryUrl.pathname = `/record-chain/recovery/submission/${submissionSha256}`;
  recoveryUrl.search = "";
  recoveryUrl.hash = "";

  const attempts = recoveryAttempts();
  const delayMs = recoveryDelayMs();
  for (let attempt = 0; attempt < attempts; attempt += 1) {
    try {
      const response = await nativeFetch(recoveryUrl, {
        method: "GET",
        headers: {
          "Accept": "application/json",
          "Cache-Control": "no-cache",
        },
      });
      if (response.status === 200) {
        const data = await response.json();
        const recovered = verifiedReceiptPayload(data, submissionSha256);
        if (recovered) return recovered;
      } else if (response.status !== 404 && response.status < 500) {
        return null;
      }
    } catch {
      // A read-only recovery probe may race repository visibility or a
      // transient proxy fault. The bounded loop remains non-writing.
    }
    if (attempt + 1 < attempts) await sleep(delayMs);
  }
  return null;
}

function requestUrl(input) {
  if (typeof input === "string") return input;
  if (input instanceof URL) return input.href;
  if (input && typeof input.url === "string") return input.url;
  return "";
}

function requestMethod(input, init) {
  const method = init?.method || (input && typeof input.method === "string" ? input.method : "GET");
  return String(method).toUpperCase();
}

function isSubmitRequest(input, init) {
  if (requestMethod(input, init) !== "POST") return false;
  try {
    return new URL(requestUrl(input)).pathname === "/record-chain/submit";
  } catch {
    return false;
  }
}

globalThis.fetch = async function trinityAccordRecoveringFetch(input, init = {}) {
  if (!isSubmitRequest(input, init)) {
    return nativeFetch(input, init);
  }

  const submitUrl = requestUrl(input);
  let submissionSha256 = null;
  try {
    submissionSha256 = submissionSha256FromBody(init.body);
  } catch {
    // Preserve the canonical Builder's original response/error behavior when
    // the request body cannot be interpreted safely.
  }

  let originalResponse;
  try {
    originalResponse = await nativeFetch(input, init);
  } catch (error) {
    if (submissionSha256) {
      const recovered = await recoverSubmission(submitUrl, submissionSha256);
      if (recovered) {
        return new Response(JSON.stringify(recovered), {
          status: 200,
          headers: {
            "Content-Type": "application/json; charset=utf-8",
            "Cache-Control": "no-store",
            "X-Trinity-Submit-Recovered": "read-only",
          },
        });
      }
    }
    throw error;
  }

  if (
    submissionSha256
    && (originalResponse.status >= 500 || originalResponse.status === 429)
  ) {
    const recovered = await recoverSubmission(submitUrl, submissionSha256);
    if (recovered) {
      return new Response(JSON.stringify(recovered), {
        status: 200,
        headers: {
          "Content-Type": "application/json; charset=utf-8",
          "Cache-Control": "no-store",
          "X-Trinity-Submit-Recovered": "read-only",
        },
      });
    }
  }
  return originalResponse;
};

function verifyCoreBytes(bytes, sourceLabel) {
  if (bytes.length !== CORE_SIZE_BYTES) {
    throw new Error(
      `Canonical Builder core size mismatch from ${sourceLabel}: expected ${CORE_SIZE_BYTES}, got ${bytes.length}`
    );
  }
  const actual = sha256Bytes(bytes);
  if (actual !== CORE_SHA256) {
    throw new Error(
      `Canonical Builder core SHA-256 mismatch from ${sourceLabel}: expected ${CORE_SHA256}, got ${actual}`
    );
  }
}

async function readVerifiedLocalCore() {
  if (!wrapperFileUrl.startsWith("file:")) return null;
  const localUrl = new URL(`./${CORE_FILENAME}`, wrapperFileUrl);
  try {
    const bytes = await readFile(fileURLToPath(localUrl));
    verifyCoreBytes(bytes, localUrl.href);
    return localUrl.href;
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    throw error;
  }
}

async function readVerifiedCachedCore(cacheDir) {
  const corePath = join(cacheDir, CORE_FILENAME);
  try {
    const bytes = await readFile(corePath);
    verifyCoreBytes(bytes, corePath);
    return pathToFileURL(corePath).href;
  } catch (error) {
    if (error?.code === "ENOENT") return null;
    return null;
  }
}

async function downloadVerifiedCore() {
  let lastError = null;
  for (const url of CORE_URLS) {
    try {
      const response = await nativeFetch(url, {
        headers: { "Accept": "text/javascript, application/javascript" },
      });
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      const bytes = Buffer.from(await response.arrayBuffer());
      verifyCoreBytes(bytes, url);
      return bytes;
    } catch (error) {
      lastError = error;
    }
  }
  throw new Error(
    `Unable to retrieve the verified canonical Builder core: ${lastError?.message || lastError}`
  );
}

async function resolveCoreModule() {
  const local = await readVerifiedLocalCore();
  if (local) return local;

  const cacheDir = join(tmpdir(), "trinity-accord-builder", CORE_SHA256);
  await mkdir(cacheDir, { recursive: true });
  const cached = await readVerifiedCachedCore(cacheDir);
  if (cached) return cached;

  const coreBytes = await downloadVerifiedCore();
  const corePath = join(cacheDir, CORE_FILENAME);
  await writeFile(corePath, coreBytes);

  // The preserved core records the public wrapper's SHA-256 as its source
  // identity. Mirror the wrapper next to the cached core so that behavior is
  // identical to the repository-local two-file bundle.
  if (wrapperFileUrl.startsWith("file:")) {
    const wrapperBytes = await readFile(fileURLToPath(wrapperFileUrl));
    await writeFile(join(cacheDir, "record-chain-builder.mjs"), wrapperBytes);
  }

  verifyCoreBytes(await readFile(corePath), corePath);
  return pathToFileURL(corePath).href;
}

await import(await resolveCoreModule());
