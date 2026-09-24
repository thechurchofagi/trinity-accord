// Paper publication budgets are independent of daily upload-count allowances.
import fs from 'node:fs';
import path from 'node:path';

export const PAPER_CAP_WINSTON = 100_000_000_000n; // Strictly less than 0.1 AR.

export function publicationKeys(config) {
  if (!Array.isArray(config?.papers) || !config.papers.length || config.paper_count !== config.papers.length) {
    throw new Error('Invalid paper publication inventory');
  }
  const keys = config.papers.map(p => {
    if (!/^TA-TR-2026-\d{2}(?:-BRIDGE)?$/.test(p.report || '') ||
        !/^10\.5281\/zenodo\.\d+$/.test(p.doi || '')) throw new Error('Invalid paper publication identity');
    return `${p.report}@${p.doi}`;
  });
  if (new Set(keys).size !== keys.length) throw new Error('Duplicate paper publication identity');
  return keys;
}

export function payloadPublicationKeys(data) {
  const bundle = JSON.parse(Buffer.from(data).toString('utf8'));
  if (bundle.schema !== 'trinityaccord.research-paper-ots-bundle.v1') throw new Error('Invalid paper archive schema');
  return publicationKeys(bundle.targets);
}

export function paperPaidWinston(keys, ledger, resolveKeys) {
  if (!Array.isArray(ledger?.entries)) throw new Error('Paper budget ledger is unavailable');
  const totals = Object.fromEntries(keys.map(k => [k, 0n]));
  const seen = new Set();
  for (const entry of ledger.entries) {
    if (entry?.kind !== 'research_paper_ots_archive') continue;
    if (!entry.tx_id || seen.has(entry.tx_id) || entry.status !== 'paid' || !/^\d+$/.test(String(entry.winston ?? ''))) {
      throw new Error('Uncertain or duplicate paper archive spending in ledger');
    }
    if (BigInt(entry.winston) < 1n) throw new Error("Uncertain zero paper archive fee");
    seen.add(entry.tx_id);
    const publications = resolveKeys(entry);
    for (const key of keys) {
      // Conservatively charge a shared bundle's entire fee to each covered paper.
      if (publications.includes(key)) totals[key] += BigInt(entry.winston);
    }
  }
  return totals;
}

export function ledgerPublicationKeys(entry, root = process.cwd()) {
  const source = String(entry.source_path || '');
  if (!/^research\/paper-timestamps\/[^/]+\/arweave-receipt\.json$/.test(source) || source.includes('..')) {
    throw new Error('Cannot bind historical paper spending to publication targets');
  }
  return publicationKeys(JSON.parse(fs.readFileSync(path.join(root, path.dirname(source), 'targets.json'), 'utf8')));
}

export function assertPaperBudget(keys, ledger, reward, resolveKeys = ledgerPublicationKeys) {
  reward = BigInt(reward);
  if (reward < 1n) throw new Error('Paper archive quote must be positive');
  const totals = paperPaidWinston(keys, ledger, resolveKeys);
  for (const key of keys) {
    if (totals[key] + reward >= PAPER_CAP_WINSTON) {
      throw new Error(`Paper publication budget exceeded: ${key}; prior=${totals[key]} quote=${reward}; total must be strictly < 0.1 AR`);
    }
  }
  return totals;
}
