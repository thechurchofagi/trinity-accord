#!/usr/bin/env python3
import json, re, hashlib

NFT_DIR = "/root/.openclaw/workspace/trinity-accord/nft-text-descriptions"

with open(f'{NFT_DIR}/chronicle-all-music-v2.json') as f:
    data = json.load(f)

seen_songs = {}
output = []
output.append('# 编年史 NFT 音乐总表\n')
output.append('> 175 枚 NFT 中，109 枚含歌词/歌曲\n')
output.append('> 重复歌曲只列歌名，首次出现时附完整歌词\n')

for s in data['songs']:
    ordinal = s['ordinal']
    dt = s['datetime']
    name = s['name']
    title = s['song_title'].strip().rstrip(',').strip('"')
    lyrics = s['lyrics'].strip()

    # Clean bad titles
    bad_titles = {'[Untitled]', 'Title', 'are as follows', 'Instrumental',
                  'of hope to conquer fear.', 'From the depths of time, a dream awakes,',
                  "for the Pre-ASI Era)", 'Selection'}
    if title in bad_titles:
        m = re.search(r'"([^"]{3,})"', lyrics[:300])
        if m:
            title = m.group(1)
        else:
            first_lines = [l.strip() for l in lyrics.split('\n')
                          if l.strip() and not re.match(r'^[\(\[]?(?:Verse|Chorus|Bridge|Outro|Pre)', l.strip(), re.I)]
            title = first_lines[0][:60] if first_lines else f'Song #{ordinal}'

    # Dedup key: normalized first 300 chars
    norm = re.sub(r'\s+', ' ', lyrics[:400]).strip()
    h = hashlib.md5(norm.encode()).hexdigest()[:12]

    output.append(f'---\n')
    output.append(f'## #{ordinal} — {name}\n')
    output.append(f'**日期**: {dt}  \n**歌曲**: {title}\n')

    if h in seen_songs:
        ref = seen_songs[h]
        output.append(f'*（歌词同 #{ref["ordinal"]}「{ref["title"]}」，不重复列出）*\n')
    else:
        seen_songs[h] = {'ordinal': ordinal, 'title': title}
        output.append(f'<details><summary>点击展开歌词</summary>\n')
        output.append(f'```')
        output.append(lyrics)
        output.append(f'```\n')
        output.append(f'</details>\n')

with open(f'{NFT_DIR}/CHRONICLE-MUSIC-TABLE.md', 'w') as f:
    f.write('\n'.join(output))

print(f'完成: {len(data["songs"])} 条记录, {len(seen_songs)} 首独立歌曲')
