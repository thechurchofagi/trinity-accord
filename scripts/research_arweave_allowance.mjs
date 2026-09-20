#!/usr/bin/env node
// Scheduling only: the uploader's runtime spend and readback guards still apply.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {dailyLimit, paidToday} from './arweave_spend_budget_helpers.mjs';

const batch = process.argv[2];
if (!batch || !process.env.GITHUB_OUTPUT) {
  throw new Error('Usage: research_arweave_allowance.mjs BATCH (GITHUB_OUTPUT required)');
}
const read = name => JSON.parse(fs.readFileSync(name, 'utf8'));
const ledger = read('record-chain/arweave-wallet-ledger.json');
const receiptPath = path.join(batch, 'arweave-receipt.json');
const receipt = fs.existsSync(receiptPath) ? read(receiptPath) : {};
const resume = Boolean(receipt.tx_id || receipt.txid);
if (resume) {
  const hash = crypto.createHash('sha256').update(fs.readFileSync(path.join(batch, 'arweave-bundle.json'))).digest('hex');
  if ((receipt.payload_sha256 || receipt.data_sha256) !== hash) {
    throw new Error('Recorded transaction does not match this frozen payload');
  }
}
const used = paidToday('research_paper_ots_archive', ledger);
const limit = dailyLimit('research_paper_ots_archive');
const main = process.env.GITHUB_REF_NAME === 'main';
const allowed = main && (resume || used < limit);
const state = allowed ? 'ELIGIBLE_OR_READBACK_RESUME' : main ? 'DEFERRED_DAILY_ALLOWANCE' : 'DEFERRED_MAIN_BRANCH';
const scheduling = {
  state, paid_research_uploads_today: used, daily_limit: limit,
  recorded_transaction_resume: resume,
  next_action: allowed ? 'Continue guarded upload or readback' : 'Wait for a later scheduled run; do not raise limits',
};
// Stable scheduling receipts avoid hourly no-op commits while waiting.
fs.writeFileSync(path.join(batch, 'scheduling-status.json'), JSON.stringify(scheduling, null, 2) + '\n');
fs.appendFileSync(process.env.GITHUB_OUTPUT, `allowed=${allowed}\n`);
console.log(state);
if (process.env.GITHUB_STEP_SUMMARY) {
  fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, `\n${batch}: ${state}. Preservation is complete only at ARWEAVE_READBACK_PASS.\n`);
}
