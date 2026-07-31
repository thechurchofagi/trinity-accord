#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import Arweave from "arweave";

const WINSTON_PER_AR = 1_000_000_000_000n;
const DEFAULT_RESERVE_AR = "0.25";

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
  if (!Number.isInteger(value) || value < 0 || value > 4) {
    throw new Error(`Unsafe ${name}: ${process.env[name]}`);
  }
  return value;
}

function paidToday(kind) {
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
  const today = new Date().toISOString().slice(0, 10);
  return ledger.entries.filter((entry) =>
    entry &&
    entry.status === "paid" &&
    entry.kind === kind &&
    typeof entry.paid_at === "string" &&
    entry.paid_at.slice(0, 10) === today
  ).length;
}

const allowCanaryTags = envTrue("ARWEAVE_CANARY_RECORD") || Boolean(process.env.E2E_RUN_ID);
const originalInit = Arweave.init.bind(Arweave);

Arweave.init = function guardedInit(config) {
  const instance = originalInit(config);
  const originalCreateTransaction = instance.createTransaction.bind(instance);
  instance.createTransaction = async (...args) => {
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
      const limit = dailyLimit(kind);
      const count = paidToday(kind);
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
      const reserve = decimalArToWinston(
        process.env.ARWEAVE_MINIMUM_REMAINING_AR || DEFAULT_RESERVE_AR
      );
      if (balance - reward < reserve) {
        throw new Error(
          `Arweave reserve balance gate blocked ${kind}: balance=${balance} reward=${reward} reserve=${reserve}`
        );
      }
      console.log(
        `[ARWEAVE RUNTIME SPEND GUARD] kind=${kind} paid_today=${count}/${limit} ` +
        `remaining_after_reward=${balance - reward} reserve=${reserve}`
      );
    }
    return originalPost(transaction);
  };

  return instance;
};
