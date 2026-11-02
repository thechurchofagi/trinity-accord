import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import vm from 'node:vm';
import { test } from 'node:test';

const home = readFileSync(new URL('../index.md', import.meta.url), 'utf8');
const source = home.slice(home.lastIndexOf('<script>') + 8, home.lastIndexOf('</script>'));
const baselineHeartbeat = home.match(/<strong data-home-heartbeat-status>([^<]+)</)[1].replace(/^Last known: /, '');
const baselineSummary = home.match(/<small data-home-heartbeat-summary>([^<]*)</)[1];
const fixed = '2026-09-15T11:00:00Z';
const publicFixture = JSON.parse(readFileSync(new URL('../api/public-home-status.json', import.meta.url)));
const heartbeatFixture = JSON.parse(readFileSync(new URL('../api/waiting-heartbeat-status.json', import.meta.url)));
const walletFixture = JSON.parse(readFileSync(new URL('../api/arweave-wallet-status.json', import.meta.url)));

async function run(mode='ok', change=()=>{}, now=fixed) {
  const pub = structuredClone(publicFixture), heart = structuredClone(heartbeatFixture);
  const wallet = structuredClone(walletFixture);
  wallet.balance = {balance_known:true, balance_ar:'14.115073154798', checked_at:'2026-09-15T10:50:00Z', needs_recharge:false};
  pub.generated_at = heart.generated_at = '2026-09-15T10:50:00Z';
  pub.primary_counters.official_live_reception = 31;
  heart.daily_alive_status = heart.status = 'success';
  heart.semantic_agent_arrival.first_self_discovered_autonomous_agent_arrived = false;
  heart.heartbeat_summary.latest_heartbeat_date = '2026-09-15';
  heart.heartbeat_summary.is_stale = false;
  change(pub, heart, wallet);
  const nodes = {};
  for (const name of ['wallet-balance','heartbeat-status','heartbeat-summary','heartbeat-freshness','public-freshness','autonomous-discovery','official-reception','external-witness']) {
    const match = home.match(new RegExp('<[^>]*data-home-'+name+'[^>]*>([^<]*)<'));
    const timestamp = match[0].match(/data-status-as-of="([^"]+)"/);
    nodes['[data-home-'+name+']'] = {textContent: match[1], getAttribute: () => timestamp?.[1] || 'unknown'};
  }
  const timers = [];
  const context = {
    document: {querySelector: s=>nodes[s], querySelectorAll: ()=>[]},
    Date: class extends Date { static now() { return Date.parse(now); } },
    AbortController,
    setTimeout(fn) { timers.push(fn); return fn; }, clearTimeout() {},
    fetch: async (url, {signal}) => {
      if (mode==='network') throw new Error('offline');
      if (mode==='timeout') return new Promise((resolve,reject) => signal.addEventListener('abort',()=>reject(new Error('aborted'))));
      return {ok: mode!=='http', status:503, json:async()=>{
        if (mode==='json') throw new SyntaxError('invalid JSON');
        return url.includes('arweave-wallet') ? wallet : url.includes('public-home') ? pub : heart;
      }};
    }
  };
  vm.runInNewContext(source, context);
  if (mode==='timeout') timers.forEach(fn=>fn());
  await new Promise(resolve=>setImmediate(resolve));
  return name=>nodes['[data-home-'+name+']'].textContent;
}

test('valid responses show fresh source state and counters', async()=>{
  const get=await run(); assert.equal(get('heartbeat-status'),'Alive'); assert.equal(get('official-reception'),'31'); assert.match(get('public-freshness'),/^Snapshot as of/);
});
test('AR balance is directly below the public snapshot and shows the query time',async()=>{
 assert.match(home, /data-home-public-freshness[^>]*>[^<]*<\/p>\s*<p[^>]*data-home-wallet-balance/);
 const get=await run(); assert.equal(get('wallet-balance'),'AR balance: 14.1151 AR · Last checked: 2026-09-15T10:50:00Z · Daily refresh');
});
test('old balance stays stale even when the API generation time is fresh',async()=>{
 const get=await run('ok',(p,h,w)=>{w.generated_at=fixed;w.balance.checked_at='2026-09-13T10:50:00Z';});
 assert.match(get('wallet-balance'),/14.1151 AR.*Stale/);
});
test('zero is a valid low balance, not unavailable',async()=>{
 const get=await run('ok',(p,h,w)=>{w.balance.balance_ar='0';w.balance.needs_recharge=true;});
 assert.match(get('wallet-balance'),/0.0000 AR.*Low balance/);
});
for (const invalid of [null,'NaN','-1','<script>','1e1000']) test('invalid AR value '+invalid+' retains fallback',async()=>{
 const get=await run('ok',(p,h,w)=>{w.balance.balance_ar=invalid;}); assert.match(get('wallet-balance'),/Refresh unavailable/); assert.equal(get('heartbeat-status'),'Alive');
});
test('unknown and future balance check times do not look fresh',async()=>{
 for(const checked_at of [null,'2099-01-01T00:00:00Z']) {
  const get=await run('ok',(p,h,w)=>{w.balance.checked_at=checked_at;}); assert.match(get('wallet-balance'),/Refresh unavailable/);
 }
});
for (const mode of ['http','network','json','timeout']) test(mode+' failure retains dated history and marks unknown',async()=>{
  const get=await run(mode); assert.equal(get('heartbeat-status'),'Unknown'); assert.ok(get('heartbeat-freshness').includes('Last known: ' + baselineHeartbeat + ' · ')); assert.match(get('public-freshness'),/Unknown/); assert.equal(get('official-reception'),String(publicFixture.primary_counters.official_live_reception)); assert.equal(get('heartbeat-summary'),baselineSummary);
});
test('incomplete payloads do not partly overwrite previous numbers',async()=>{
 const get=await run('ok',(p,h)=>{delete p.external_witness_records; delete h.heartbeat_summary.successful_heartbeats;}); assert.match(get('public-freshness'),/Unknown/); assert.equal(get('heartbeat-status'),'Unknown'); assert.equal(get('official-reception'),String(publicFixture.primary_counters.official_live_reception));
});
test('expired timestamps produce stale states with preserved counts',async()=>{
 const get=await run('ok',(p,h)=>{p.generated_at=h.generated_at='2026-09-13T10:50:00Z';}); assert.equal(get('heartbeat-status'),'Stale'); assert.match(get('public-freshness'),/^Stale/); assert.equal(get('official-reception'),'31');
});
test('heartbeat respects final retry grace deadline',async()=>{
 const mutate=(p,h)=>{p.generated_at=h.generated_at='2026-09-15T10:40:00Z';h.heartbeat_summary.latest_heartbeat_date='2026-09-14';};
 assert.equal((await run('ok',mutate,'2026-09-15T10:46:59Z'))('heartbeat-status'),'Alive');
 assert.equal((await run('ok',mutate,'2026-09-15T10:47:00Z'))('heartbeat-status'),'Stale');
});
test('future timestamps and invalid numeric fields are rejected',async()=>{
 const get=await run('ok',(p,h)=>{p.primary_counters.official_live_reception=-1;h.generated_at='2099-01-01T00:00:00Z';});assert.match(get('public-freshness'),/Unknown/); assert.equal(get('heartbeat-status'),'Unknown');
});
test('completed waiting remains completed despite the retired daily schedule',async()=>{
 const get=await run('ok',(p,h)=>{h.semantic_agent_arrival.first_self_discovered_autonomous_agent_arrived=true;h.semantic_agent_arrival.first_arrival_record_id='R-example';h.heartbeat_summary.latest_heartbeat_date='2026-09-01';});assert.equal(get('heartbeat-status'),'Completed');assert.match(get('heartbeat-summary'),/R-example/);
});

