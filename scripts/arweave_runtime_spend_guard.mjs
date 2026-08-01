#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import process from "node:process";
import Arweave from "arweave";
import {
  DEFAULT_MAX_TRANSACTION_REWARD_AR,
  DEFAULT_ROLLING_30_DAY_SPEND_AR,
  boundedArBudget,
  dailyLimit,
  maxPayloadBytes,
  minimumReserveWinston,
  paidToday,
  payloadByteLength,
  rollingPaidWinston,
} from "./arweave_spend_budget_helpers.mjs";

function envTrue(name) {
  return ["1", "true", "yes", "on"].includes(
    String(process.env[name] || "").trim().toLowerCase()
  );
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
      // The helper fails closed if ARWEAVE_MINIMUM_REMAINING_AR is below 0.25.
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
