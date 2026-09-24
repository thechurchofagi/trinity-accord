#!/usr/bin/env node
// Scheduling only: the uploader's runtime spend and readback guards still apply.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {PAPER_CAP_WINSTON, publicationKeys, paperPaidWinston, ledgerPublicationKeys} from './research_paper_budget.mjs';

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
const keys = publicationKeys(read(path.join(batch, 'targets.json')));
const totals = paperPaidWinston(keys, ledger, ledgerPublicationKeys);
const main = process.env.GITHUB_REF_NAME === 'main';
const remaining = Object.values(totals).every(n => n < PAPER_CAP_WINSTON);
const allowed = main && (resume || remaining);
const state = allowed ? 'ELIGIBLE_OR_READBACK_RESUME' : main ? 'DEFERRED_PAPER_BUDGET' : 'DEFERRED_MAIN_BRANCH';
const scheduling = {
  state, budget_policy: 'per-publication-strictly-less-than-0.1-AR', daily_limit_applies: false,
  prior_winston_by_publication: Object.fromEntries(Object.entries(totals).map(([k,v])=>[k,String(v)])),
  recorded_transaction_resume: resume,
  next_action: allowed ? 'Continue to live quote, cumulative paper budget, reserve and rolling-spend guards or resume readback' : 'Resolve paper budget or main-branch eligibility',
};
// Stable scheduling receipts avoid hourly no-op commits while waiting.
fs.writeFileSync(path.join(batch, 'scheduling-status.json'), JSON.stringify(scheduling, null, 2) + '\n');
fs.appendFileSync(process.env.GITHUB_OUTPUT, `allowed=${allowed}\n`);
console.log(state);
if (process.env.GITHUB_STEP_SUMMARY) {
  fs.appendFileSync(process.env.GITHUB_STEP_SUMMARY, `\n${batch}: ${state}. Preservation is complete only at ARWEAVE_READBACK_PASS.\n`);
}
