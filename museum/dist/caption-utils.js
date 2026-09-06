// Derived display text only: preserved NFT records remain unchanged.
const section = /^(?:\[(?:verse|chorus|bridge|outro|intro|pre[- ]chorus|instrumental)[^\]]*\]|\((?:verse|chorus|bridge|outro|intro|pre[- ]chorus|instrumental)[^)]*\)|(?:verse(?:\s+\d+)?|chorus|bridge|outro|intro|pre[- ]chorus|instrumental)\s*:)/i;
const normalize = s => String(s || '').toLowerCase().replace(/[^\p{L}\p{N}]/gu, '');
export function cleanLyrics(text, title = '') {
  const rows = [];
  for (let line of String(text || '').split(/\r?\n/)) {
    line = line.trim();
    if (/^(?:The song vividly portrays|Significance of this NFT\s*:|Looking Ahead\s*:|Disclaimer\s*:)/i.test(line)) break;
    if (/^(?:(?:original|song)\s+)?lyrics?\s*:/i.test(line)) continue;
    // The archive sometimes joins the title, section label and first sung line.
    if (!rows.length) {
      line = line.replace(/^《[^》]+》\s*/, '');
      if (title && normalize(line) === normalize(title)) continue;
    }
    while (section.test(line)) line = line.replace(section, '').trim();
    if (/^(?:verse(?:\s+\d+)?|chorus|bridge|outro|intro|pre[- ]chorus|instrumental)$/i.test(line)) continue;
    if (line) rows.push(line);
  }
  return rows;
}

export function extractRecordLyrics(text, title) {
  if (!title) return '';
  const rows = String(text).split(/\r?\n/), needle = title.toLowerCase();
  let start = rows.findIndex(r => r.trim().toLowerCase() === needle);
  if (start < 0) start = rows.findIndex(r => r.trim().toLowerCase().includes(needle));
  if (start < 0) return '';
  const out = [];
  for (const row of rows.slice(start + 1)) {
    if (/^[-—_]{10,}\s*$/.test(row.trim())) break;
    out.push(row);
  }
  return out.join('\n').trim();
}

// These are explicitly estimated cues, not claimed audio/word alignment.
export function estimateCues(rows, duration) {
  if (!rows.length || !Number.isFinite(duration) || duration <= 0) return [];
  const intro = Math.min(10, Math.max(4.5, duration * .035));
  const end = duration - Math.min(8, Math.max(3, duration * .025));
  const weights = rows.map(line => Math.max(1, line.split(/\s+/).length));
  const total = weights.reduce((a, b) => a + b, 0);
  let time = intro;
  return rows.map((line, index) => {
    const start = time;
    time += (end - intro) * weights[index] / total;
    return {index, time: start, end: time};
  });
}

// Wrap by actual font metrics, then page rather than clipping or ellipsizing.
export function captionPages(text, width, measure) {
  if (width <= 0) return [];
  const lines = []; let line = '';
  for (const word of String(text).trim().split(/\s+/).filter(Boolean)) {
    const joined = line ? line + ' ' + word : word;
    if (measure(joined) <= width) { line = joined; continue; }
    if (line) { lines.push(line); line = ''; }
    for (const char of word) {
      if (line && measure(line + char) > width) { lines.push(line); line = ''; }
      line += char;
    }
  }
  if (line) lines.push(line);
  const pages = [];
  for (let i = 0; i < lines.length; i += 2) pages.push(lines.slice(i, i + 2).join('\n'));
  return pages;
}

export function captionAt(cues, time) {
  return cues.find(c => time >= c.time && time < c.end) || null;
}

// Walking uses elapsed seconds, including slow frames, but never background gaps.
export function frameSeconds(now, previous) {
  const elapsed = (now - previous) / 1000;
  return previous && elapsed > 0 && elapsed <= .25 ? elapsed : 0;
}
