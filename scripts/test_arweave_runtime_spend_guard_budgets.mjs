#!/usr/bin/env node
import assert from "node:assert/strict";

import {
  DEFAULT_MAX_PAYLOAD_BYTES,
  dailyLimit,
  decimalArToWinston,
  maxPayloadBytes,
  minimumReserveWinston,
  payloadByteLength,
  paidToday,
  rollingPaidWinston,
} from "./arweave_spend_budget_helpers.mjs";


assert.equal(decimalArToWinston("0.05"), 50_000_000_000n);
assert.equal(payloadByteLength(Buffer.alloc(128)), 128);
assert.equal(payloadByteLength("四"), 3);
assert.equal(maxPayloadBytes(), DEFAULT_MAX_PAYLOAD_BYTES);

const now = new Date("2026-08-01T12:00:00Z");
const ledger = {
  entries: [
    {
      tx_id: "within-window-record",
      kind: "record_chain_arweave_archive",
      status: "paid",
      paid_at: "2026-07-31T08:00:00Z",
      winston: "13000000000",
    },
    {
      tx_id: "within-window-ots",
      kind: "native_ots_bundle_archive",
      status: "paid",
      paid_at: "2026-07-15T08:00:00Z",
      winston: "3000000000",
    },
    {
      tx_id: "outside-window",
      kind: "record_chain_arweave_archive",
      status: "paid",
      paid_at: "2026-06-01T08:00:00Z",
      winston: "999999999999",
    },
  ],
};
assert.equal(rollingPaidWinston(ledger, now), 16_000_000_000n);
assert.equal(paidToday("record_chain_arweave_archive", ledger, now), 0);

const invalidLedger = {
  entries: [
    {
      tx_id: "missing-cost",
      kind: "record_chain_arweave_archive",
      status: "paid",
      paid_at: "2026-07-31T08:00:00Z",
      winston: null,
    },
  ],
};
assert.throws(
  () => rollingPaidWinston(invalidLedger, now),
  /no valid winston cost/
);

const oldPayloadLimit = process.env.ARWEAVE_MAX_PAYLOAD_BYTES;
const oldDailyLimit = process.env.ARWEAVE_DAILY_RECORD_CHAIN_UPLOAD_LIMIT;
const oldReserve = process.env.ARWEAVE_MINIMUM_REMAINING_AR;
try {
  process.env.ARWEAVE_MAX_PAYLOAD_BYTES = String(DEFAULT_MAX_PAYLOAD_BYTES + 1);
  assert.throws(() => maxPayloadBytes(), /Unsafe ARWEAVE_MAX_PAYLOAD_BYTES/);
  process.env.ARWEAVE_DAILY_RECORD_CHAIN_UPLOAD_LIMIT = "2";
  assert.throws(
    () => dailyLimit("record_chain_arweave_archive"),
    /Unsafe ARWEAVE_DAILY_RECORD_CHAIN_UPLOAD_LIMIT/
  );
  process.env.ARWEAVE_MINIMUM_REMAINING_AR = "0.249999999999";
  assert.throws(
    () => minimumReserveWinston(),
    /Unsafe ARWEAVE_MINIMUM_REMAINING_AR/
  );
} finally {
  if (oldPayloadLimit === undefined) delete process.env.ARWEAVE_MAX_PAYLOAD_BYTES;
  else process.env.ARWEAVE_MAX_PAYLOAD_BYTES = oldPayloadLimit;
  if (oldDailyLimit === undefined) delete process.env.ARWEAVE_DAILY_RECORD_CHAIN_UPLOAD_LIMIT;
  else process.env.ARWEAVE_DAILY_RECORD_CHAIN_UPLOAD_LIMIT = oldDailyLimit;
  if (oldReserve === undefined) delete process.env.ARWEAVE_MINIMUM_REMAINING_AR;
  else process.env.ARWEAVE_MINIMUM_REMAINING_AR = oldReserve;
}

console.log("PASS: Arweave runtime reward, payload, and rolling-spend helpers fail closed");

// The paper exception is independent of daily limits and uses exact integers.
const {assertPaperBudget, payloadPublicationKeys, publicationKeys} = await import('./research_paper_budget.mjs');
const paper = 'TA-TR-2026-15@10.5281/zenodo.22934654';
const other = 'TA-TR-2026-14@10.5281/zenodo.22886276';
const spent = {entries:[{kind:'research_paper_ots_archive',status:'paid',tx_id:'prior',winston:'60000000000'}]};
assert.equal(dailyLimit('research_paper_ots_archive'), null);
assert.equal(dailyLimit('native_ots_bundle_archive'), 1);
assertPaperBudget([paper], {entries:[]}, 99999999999n, ()=>[]);
assert.throws(()=>assertPaperBudget([paper], {entries:[]}, 100000000000n, ()=>[]), /strictly < 0.1/);
assertPaperBudget([paper], spent, 39999999999n, ()=>[paper]);
assert.throws(()=>assertPaperBudget([paper], spent, 40000000000n, ()=>[paper]), /strictly < 0.1/);
assertPaperBudget([other], spent, 99999999999n, ()=>[paper]);
assert.throws(()=>assertPaperBudget([paper], {entries:[{...spent.entries[0],winston:null}]}, 1n, ()=>[paper]), /Uncertain/);
assert.throws(()=>assertPaperBudget([paper], {entries:[...spent.entries,...spent.entries]}, 1n, ()=>[paper]), /duplicate/);
assert.throws(()=>assertPaperBudget([paper,other], spent, 40000000000n, ()=>[paper,other]), /strictly < 0.1/);
assert.throws(()=>payloadPublicationKeys(Buffer.from('{}')), /schema/);
assert.deepEqual(publicationKeys({paper_count:1,papers:[{report:'TA-TR-2026-15',doi:'10.5281/zenodo.22934654'}]}),[paper]);
console.log('PASS: independent paper budgets, strict boundary, cumulative cost, shared bundles and fail-closed accounting');
