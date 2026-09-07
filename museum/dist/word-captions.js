// All times are seconds in the original HTMLMediaElement timeline.
export function validTimeline(data, track) {
  if (data?.schemaVersion !== 'word-alignment-v2' || data.exhibitId !== track.exhibitId || data.audioSha256 !== track.audioSha256 || Math.abs(data.duration-track.duration)>.1 || !Array.isArray(data.lines) || !data.lines.length) return false;
  let previous=0;
  return data.lines.every(line => Array.isArray(line.words) && line.words.length && line.start===line.words[0].start && line.end===line.words.at(-1).end && line.words.every(w => {
    const ok=typeof w.text==='string' && w.text.trim() && Number.isFinite(w.start) && Number.isFinite(w.end) && w.start>=previous && w.end>w.start && w.end<=data.duration;
    previous=w.end;return ok;
  }));
}
export function lineAt(lines, time) {
  let lo=0,hi=lines.length-1;
  while(lo<=hi){const mid=(lo+hi)>>1,line=lines[mid];if(time<line.start)hi=mid-1;else if(time>=line.end)lo=mid+1;else return mid;}
  return -1;
}
export function wordAt(words, time) { return words.findIndex(w=>time>=w.start && time<w.end); }
// Page boundaries follow actual word indices, never a fraction of line duration.
export function wordPages(words, width, measure) {
  if(width<=0)return [];
  const rows=[];let row=[],text='';
  words.forEach((word,index)=>{const joined=text?text+' '+word.text:word.text;
    if(row.length && measure(joined)>width){rows.push(row);row=[];text='';}
    row.push(index);text=text?text+' '+word.text:word.text;
  });
  if(row.length)rows.push(row);
  const pages=[];for(let i=0;i<rows.length;i+=2)pages.push(rows.slice(i,i+2));return pages;
}
export function pageAt(pages, words, time) {
  let index=0;for(let i=1;i<pages.length;i++)if(time>=words[pages[i][0][0]].start)index=i;return index;
}
