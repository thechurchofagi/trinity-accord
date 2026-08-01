#!/usr/bin/env node

// Pure, dependency-free budget helpers. Keeping these separate from the
// runtime Arweave monkeypatch lets every Python-only CI lane execute the exact
// production calculations without installing the Arweave npm package.
import process from "node:process";

const WINSTON_PER_AR = 1_000_000_000_000n;
const DEFAULT_RESERVE_AR = "0.25";
const DEFAULT_MAX_TRANSACTION_REWARD_AR = "0.05";
const DEFAULT_ROLLING_30_DAY_SPEND_AR = "0.50";
const DEFAULT_MAX_PAYLOAD_BYTES = 8 * 1024 * 1024;
const ROLLING_WINDOW_MILLISECONDS = 30 * 24 * 60 * 60 * 1000;

function decimalArToWinston(value) {
  const text = String(value).trim();
  if (!/^\d+(?:\.\d{1,12})?$/.test(text)) {
    throw new Error(`Invalid AR budget value: ${text}`);
  }
  const [whole, fraction = ""] = text.split(".");
  return BigInt(whole) * WINSTON_PER_AR + BigInt(fraction.padEnd(12, "0"));
}

function boundedArBudget(name, fallback) {
  const configured = decimalArToWinston(process.env[name] || fallback);
  const hardMaximum = decimalArToWinston(fallback);
  if (configured < 1n || configured > hardMaximum) {
    throw new Error(`Unsafe ${name}: must be > 0 and <= ${fallback} AR`);
  }
  return configured;
}

function maxPayloadBytes() {
  const raw = process.env.ARWEAVE_MAX_PAYLOAD_BYTES || String(DEFAULT_MAX_PAYLOAD_BYTES);
  const value = Number(raw);
  if (!Number.isInteger(value) || value < 1 || value > DEFAULT_MAX_PAYLOAD_BYTES) {
    throw new Error(
      `Unsafe ARWEAVE_MAX_PAYLOAD_BYTES: must be an integer between 1 and ${DEFAULT_MAX_PAYLOAD_BYTES}`
    );
  }
  return value;
}

function payloadByteLength(value) {
  if (value == null) return 0;
  if (typeof value === "string") return Buffer.byteLength(value);
  if (Buffer.isBuffer(value)) return value.length;
  if (ArrayBuffer.isView(value)) return value.byteLength;
  if (value instanceof ArrayBuffer) return value.byteLength;
  throw new Error("Unsupported Arweave transaction payload type");
}

function dailyLimit(kind) {
  const name = kind === "record_chain_arweave_archive"
    ? "ARWEAVE_DAILY_RECORD_CHAIN_UPLOAD_LIMIT"
    : "ARWEAVE_DAILY_NATIVE_OTS_UPLOAD_LIMIT";
  const value = Number(process.env[name] || "1");
  if (!Number.isInteger(value) || value < 0 || value > 1) {
    throw new Error(`Unsafe ${name}: ${process.env[name]}`);
  }
  return value;
}

function minimumReserveWinston() {
  const configured = decimalArToWinston(
    process.env.ARWEAVE_MINIMUM_REMAINING_AR || DEFAULT_RESERVE_AR
  );
  const hardMinimum = decimalArToWinston(DEFAULT_RESERVE_AR);
  if (configured < hardMinimum) {
    throw new Error(
      `Unsafe ARWEAVE_MINIMUM_REMAINING_AR: must be >= ${DEFAULT_RESERVE_AR} AR`
    );
  }
  return configured;
}

function paidToday(kind, ledger, now = new Date()) {
  const today = now.toISOString().slice(0, 10);
  return ledger.entries.filter((entry) =>
    entry &&
    entry.status === "paid" &&
    entry.kind === kind &&
    typeof entry.paid_at === "string" &&
    entry.paid_at.slice(0, 10) === today
  ).length;
}

function rollingPaidWinston(ledger, now = new Date()) {
  const cutoff = now.getTime() - ROLLING_WINDOW_MILLISECONDS;
  let total = 0n;
  for (const entry of ledger.entries) {
    if (!entry || entry.status !== "paid" || typeof entry.paid_at !== "string") continue;
    const paidAt = Date.parse(entry.paid_at);
    if (!Number.isFinite(paidAt) || paidAt < cutoff || paidAt > now.getTime()) continue;
    const winston = String(entry.winston ?? "");
    if (!/^\d+$/.test(winston)) {
      throw new Error(
        `Cannot verify rolling Arweave spend: paid ledger entry ${entry.tx_id || "unknown"} has no valid winston cost`
      );
    }
    total += BigInt(winston);
  }
  return total;
}

export {
  DEFAULT_MAX_PAYLOAD_BYTES,
  DEFAULT_MAX_TRANSACTION_REWARD_AR,
  DEFAULT_RESERVE_AR,
  DEFAULT_ROLLING_30_DAY_SPEND_AR,
  ROLLING_WINDOW_MILLISECONDS,
  boundedArBudget,
  dailyLimit,
  decimalArToWinston,
  maxPayloadBytes,
  minimumReserveWinston,
  paidToday,
  payloadByteLength,
  rollingPaidWinston,
};
