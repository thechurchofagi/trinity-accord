#!/usr/bin/env python3
"""Extract ALL lyrics from NFT files - fixed version."""
import os, re, json
from pathlib import Path

NFT_DIR = Path("/root/.openclaw/workspace/trinity-accord/nft-text-descriptions")
INDEX_FILE = NFT_DIR / "chronicle-index.json"

def has_lyrics(text):
    """Check if text contains actual song lyrics (verse/chorus structure)."""
    markers = [
        r'\(?Verse\s*[12I]\b', r'\[Verse\s*[12I]\]', r'^Verse\s*[12I][:\s]',
        r'\(?Chorus\)?', r'\[Chorus\]', r'^Chorus[:\s]',
        r'\(?Bridge\)?', r'\[Bridge\]', r'^Bridge[:\s]',
        r'\(?Outro\)?', r'\[Outro\]', r'^Outro[:\s]',
        r'\(?Pre-Chorus\)?', r'\[Pre-Chorus\]',
    ]
    count = 0
    for m in markers:
        count += len(re.findall(m, text, re.MULTILINE | re.IGNORECASE))
    return count >= 2  # at least 2 verse/chorus markers

def extract_lyrics_block(text):
    """Extract the lyrics portion from the text."""
    # Find the first verse/chorus marker
    first_marker = re.search(r'(?:\n|^)(?:\*\*)?(?:\(?Verse\s*[1I]\b|\[Verse\s*[1I]\]|Verse\s*[1I][:.\s])', text, re.IGNORECASE)
    if not first_marker:
        first_marker = re.search(r'(?:\n|^)(?:\*\*)?(?:\(?Chorus\)?|\[Chorus\])', text, re.IGNORECASE)
    if not first_marker:
        return None
    
    start = first_marker.start()
    
    # Find end - next major section
    end_patterns = [
        r'\n(?:##|---|\*\*(?:Disclaimer|Summary|Significance|Cultural|Historical|Note|Acknowledgment|Copyright|Value))',
        r'\nThis\s+NFT\s+(?:is|not|and)\s',
        r'\n(?:The\s+)?(?:song|lyrics?|NFT)\s+(?:gives|vividly|not|captures|reflects|serves|is\s+not)',
        r'\nAs\s+(?:a|the|we|first|AGI)',
        r'\nBy\s+(?:collecting|purchasing)',
    ]
    
    end = len(text)
    for ep in end_patterns:
        m = re.search(ep, text[start+20:], re.IGNORECASE)
        if m:
            end = min(end, start + 20 + m.start())
    
    block = text[start:end].strip()
    if len(block) < 30:
        return None
    return block

def get_song_title(text):
    """Try to extract song title."""
    patterns = [
        r'(?:Original\s+)?(?:Song|Lyrics?)(?:\s+of)?[:\s]*[""]([^""]+)[""]',
        r'(?:Original\s+)?(?:Song|Lyrics?)[:\s]*[""]([^""]+)[""]',
        r'The\s+original\s+song\s+[""]([^""]+)[""]',
        r'song\s+[""]([^""]+)[""]',
        r'[""]([^""]{3,}?)[""]\s*(?:Lyrics?|Song)',
        r'(?:Song|Lyrics?)[:\s]+([A-Z][^\n:]{2,40}?)(?:\n|:)',
    ]
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
    return None

def main():
    with open(INDEX_FILE) as f:
        index = json.load(f)
    
    entries = {e['ordinal']: e for e in index['entries']}
    
    results = []
    for ordinal in sorted(entries.keys()):
        e = entries[ordinal]
        fp = NFT_DIR / e['file']
        if not fp.exists():
            continue
        with open(fp) as f:
            text = f.read()
        
        if has_lyrics(text):
            title = get_song_title(text)
            lyrics = extract_lyrics_block(text)
            if lyrics:
                results.append({
                    'ordinal': ordinal,
                    'datetime': e['datetime'][:10],
                    'name': e['name'],
                    'song_title': title or '[Untitled]',
                    'lyrics': lyrics
                })
    
    print(f"=== 总计: {len(results)} 首歌/歌词 ===\n")
    for r in results:
        # Count verses
        verses = len(re.findall(r'\(?Verse\s*\d|\[Verse\s*\d', r['lyrics'], re.I))
        choruses = len(re.findall(r'\(?Chorus\)?|\[Chorus\]', r['lyrics'], re.I))
        print(f"#{r['ordinal']:3d} {r['datetime']} | {r['song_title'][:50]} | {r['name'][:60]} | {verses}v{choruses}c")
    
    # Save
    out = NFT_DIR / "chronicle-all-music-v2.json"
    with open(out, 'w') as f:
        json.dump({'total': len(results), 'songs': results}, f, ensure_ascii=False, indent=2)
    print(f"\nSaved to: {out}")

if __name__ == '__main__':
    main()
