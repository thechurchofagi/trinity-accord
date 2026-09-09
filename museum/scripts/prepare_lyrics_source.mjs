// Build the derived lyric input manifest from preserved source records.
// It keeps the original NFT/source records untouched and makes the exact text
// sent to the offline aligner auditable and reproducible.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {cleanLyrics, extractRecordLyrics} from '../dist/caption-utils.js';
import {fallbackLyricsFor} from '../dist/lyrics-fallback.js';

const root = fileURLToPath(new URL('../', import.meta.url));
const dist = path.join(root, 'dist');
const sources = JSON.parse(fs.readFileSync(path.join(dist, 'data/sources.json'), 'utf8'));
const byId = new Map(sources.items.map(item => [item.id, item]));
const digest = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
const textDigest = text => digest(Buffer.from(text, 'utf8'));

function sourceText(item) {
  let raw = item.lyrics || fallbackLyricsFor(item.id) || '';
  if (!raw && item.id === 'eth-010') raw = byId.get('eth-049')?.lyrics || '';
  if (!raw && item.id === 'eth-042') raw = byId.get('eth-001')?.lyrics || '';
  if (!raw && item.localRecord) {
    const file = path.join(dist, item.localRecord);
    if (fs.existsSync(file)) raw = extractRecordLyrics(fs.readFileSync(file, 'utf8'), item.songTitle);
  }
  const lines = cleanLyrics(raw, item.songTitle);
  if (!lines.length) throw new Error(`No lyric text for ${item.id}`);
  return lines;
}

const deferred = new Map([['eth-089','Complete 54:38 cycle: preserve full recording and original track list; no fabricated global word timeline.'],['eth-097','Chinese original recording: source lyrics remain readable; alignment belongs to the following Chinese production phase.']]);
const items = sources.items.filter(item => item.media?.some(media => media.kind === 'audio') && !deferred.has(item.id)).map(item => {
  const audio = item.media.find(media => media.kind === 'audio');
  const lines = sourceText(item);
  const text = lines.join('\n') + '\n';
  return {
    exhibitId: item.id,
    songTitle: item.songTitle,
    audioFile: audio.file,
    audioSha256: audio.sha256,
    duration: audio.duration,
    sourceTextSha256: textDigest(text),
    sourceTextKind: item.lyrics ? 'preserved-nft-description' : fallbackLyricsFor(item.id) ? 'supplemental-display-lyric' : ['eth-010','eth-042'].includes(item.id) ? 'related-record-lyric-copy' : 'preserved-record-copy',
    sourceTextExhibitId: item.id==='eth-010'?'eth-049':item.id==='eth-042'?'eth-001':item.id,
    lines,
    tokenCount: lines.reduce((total, line) => total + line.trim().split(/\s+/).filter(Boolean).length, 0),
    timelineFile: `data/lyrics/${item.id}.json`
  };
});

const out = {
  schemaVersion: 'lyrics-source-v1',
  edition: sources.edition,
  generatedFrom: 'data/sources.json plus preserved local records',
  items,
  deferred: [...deferred].map(([exhibitId,reason])=>({exhibitId,reason}))
};
fs.writeFileSync(path.join(dist, 'data/lyrics-source.json'), JSON.stringify(out, null, 2) + '\n');
console.log(`Prepared ${items.length} audio lyric inputs (${items.reduce((n, item) => n + item.tokenCount, 0)} tokens).`);
