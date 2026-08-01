#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import Arweave from "arweave";

const WINSTON_PER_AR = 1_000_000_000_000n;
const DEFAULT_RESERVE_AR = "0.25";
const DEFAULT_MAX_TRANSACTION_REWARD_AR = "0.05";
const DEFAULT_ROLLING_30_DAY_SPEND_AR = "0.50";
const DEFAULT_MAX_PAYLOAD_BYTES = 8 * 1024 * 1024;
const ROLLING_WINDOW_MILLISECONDS = 30 * 24 * 60 * 60 * 1000;

function envTrue(name) {
  return ["1", "true", "yes", "on"].includes(
    String(process.env[name] || "").trim().toLowerCase()
  );
}

function decimalArToWinston(value) {
  const text = String(value).trim();
  if (!/^\d+(?:\.\d{1,12})?$/.test(text)) {
    throw new Error(`Invalid AR reserve value: ${text}`);
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

function argValue(name) {
  const prefix = `${name}=`;
  for (let index = 0; index < process.argv.length; index += 1) {
    const value = process.argv[index];
    if (value === name && index + 1 < process.argv.length) return process.argv[index + 1];
    if (value.startsWith(prefix)) return value.slice(prefix.length);
  }
  return null;
}

function paidKind() {
  const script = path.basename(process.argv[1] || "");
  if (script === "arweave_upload_payload.mjs") {
    return "record_chain_arweave_archive";
  }
  if (script === "arweave_cost_gate.mjs") {
    const recordType = argValue("--record-type") || process.env.ARWEAVE_RECORD_TYPE || "";
    if (recordType === "native_ots_proof_bundle") return "native_ots_bundle_archive";
    if (recordType.includes("record_chain")) return "record_chain_arweave_archive";
    if (process.env.ARWEAVE_UPLOAD_MODE === "production") {
      throw new Error(`Unrecognized production Arweave record type: ${recordType || "missing"}`);
    }
  }
  return null;
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

function walletLedger() {
  const ledgerPath = process.env.ARWEAVE_WALLET_LEDGER_PATH || path.resolve(
    "record-chain/arweave-wallet-ledger.json"
  );
  let ledger;
  try {
    ledger = JSON.parse(fs.readFileSync(ledgerPath, "utf8"));
  } catch (error) {
    throw new Error(`Cannot verify Arweave wallet ledger ${ledgerPath}: ${error.message}`);
  }
  if (!Array.isArray(ledger.entries)) {
    throw new Error("Arweave wallet ledger entries are unavailable");
  }
  return ledger;
}

function paidToday(kind, ledger = walletLedger(), now = new Date()) {
  const today = now.toISOString().slice(0, 10);
  return ledger.entries.filter((entry) =>
    entry &&
    entry.status === "paid" &&
    entry.kind === kind &&
    typeof entry.paid_at === "string" &&
    entry.paid_at.slice(0, 10) === today
  ).length;
}

function rollingPaidWinston(ledger = walletLedger(), now = new Date()) {
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

const allowCanaryTags = envTrue("ARWEAVE_CANARY_RECORD") || Boolean(process.env.E2E_RUN_ID);
const originalInit = Arweave.init.bind(Arweave);

Arweave.init = function guardedInit(config) {
  const instance = originalInit(config);
  const originalCreateTransaction = instance.createTransaction.bind(instance);
  instance.createTransaction = async (...args) => {
    const kind = paidKind();
    if (kind) {
      const attributes = args[0] && typeof args[0] === "object" ? args[0] : {};
      const payloadBytes = payloadByteLength(attributes.data);
      const limit = maxPayloadBytes();
      if (payloadBytes > limit) {
        throw new Error(
          `Arweave payload size gate blocked ${kind}: payload_bytes=${payloadBytes} limit=${limit}`
        );
      }
    }
    const transaction = await originalCreateTransaction(...args);
    const originalAddTag = transaction.addTag.bind(transaction);
    transaction.addTag = (name, value) => {
      if (
        !allowCanaryTags &&
        (name === "Canary-Record" || name === "Do-Not-Treat-As-First-Real-Agent")
      ) {
        return undefined;
      }
      return originalAddTag(name, value);
    };
    return transaction;
  };

  const originalPost = instance.transactions.post.bind(instance.transactions);
  instance.transactions.post = async (transaction) => {
    const kind = paidKind();
    if (kind) {
      const ledger = walletLedger();
      const limit = dailyLimit(kind);
      const count = paidToday(kind, ledger);
      if (count >= limit) {
        throw new Error(
          `Daily paid Arweave upload limit reached for ${kind}: ${count}/${limit}`
        );
      }

      const owner = transaction.owner;
      if (!owner) throw new Error("Signed Arweave transaction is missing owner");
      const address = await instance.wallets.ownerToAddress(owner);
      const balance = BigInt(await instance.wallets.getBalance(address));
      const reward = BigInt(String(transaction.reward || "0"));
      const maxReward = boundedArBudget(
        "ARWEAVE_MAX_TRANSACTION_REWARD_AR",
        DEFAULT_MAX_TRANSACTION_REWARD_AR
      );
      if (reward < 1n || reward > maxReward) {
        throw new Error(
          `Arweave transaction reward gate blocked ${kind}: reward=${reward} max_reward=${maxReward}`
        );
      }
      const rollingPaid = rollingPaidWinston(ledger);
      const rollingLimit = boundedArBudget(
        "ARWEAVE_ROLLING_30_DAY_SPEND_LIMIT_AR",
        DEFAULT_ROLLING_30_DAY_SPEND_AR
      );
      if (rollingPaid + reward > rollingLimit) {
        throw new Error(
          `Arweave rolling 30-day spend gate blocked ${kind}: ` +
          `paid=${rollingPaid} reward=${reward} limit=${rollingLimit}`
        );
      }
      const reserve = minimumReserveWinston();
      if (balance - reward < reserve) {
        throw new Error(
          `Arweave reserve balance gate blocked ${kind}: balance=${balance} reward=${reward} reserve=${reserve}`
        );
      }
      console.log(
        `[ARWEAVE RUNTIME SPEND GUARD] kind=${kind} paid_today=${count}/${limit} ` +
        `payload_limit_bytes=${maxPayloadBytes()} reward=${reward}/${maxReward} ` +
        `rolling_30_day_after=${rollingPaid + reward}/${rollingLimit} ` +
        `remaining_after_reward=${balance - reward} reserve=${reserve}`
      );
    }
    return originalPost(transaction);
  };

  return instance;
};

export {
  DEFAULT_MAX_PAYLOAD_BYTES,
  DEFAULT_MAX_TRANSACTION_REWARD_AR,
  DEFAULT_ROLLING_30_DAY_SPEND_AR,
  ROLLING_WINDOW_MILLISECONDS,
  decimalArToWinston,
  dailyLimit,
  maxPayloadBytes,
  minimumReserveWinston,
  payloadByteLength,
  paidToday,
  rollingPaidWinston,
};
