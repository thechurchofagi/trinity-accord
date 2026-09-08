"""Independent acoustic review of new speech; no historical audio is edited."""
from pathlib import Path
import argparse, difflib, hashlib, json, re, subprocess
import numpy as np

H=lambda b:hashlib.sha256(b).hexdigest()
def normal(text):
    from num2words import num2words
    text=text.lower().replace('’',"'").replace('centre','center')
    text=re.sub(r'20(\d\d)',lambda m:'twenty '+num2words(int(m[1])),text)
    text=re.sub(r'\d+(?:\.\d+)?',lambda m:num2words(m[0]).replace(' and ',' '),text)
    return re.findall(r"[a-z]+(?:'[a-z]+)?",text)

def main():
    from faster_whisper import WhisperModel
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--dist',required=True);args=parser.parse_args()
    source=Path(args.input);D=Path(args.dist);out=D/'assets/guides-expressive';out.mkdir(parents=True,exist_ok=True)
    guides=json.loads((D/'data/guide-audio.json').read_text());reports=[];updates={}
    recognizer=WhisperModel('small.en',device='cpu',compute_type='int8',cpu_threads=4,num_workers=1)
    def hear(audio):
        segments,_=recognizer.transcribe(audio,language='en',beam_size=5,word_timestamps=True,vad_filter=True,vad_parameters={'min_silence_duration_ms':500,'speech_pad_ms':150},condition_on_previous_text=False,hallucination_silence_threshold=1.0)
        words=[w for s in segments for w in (s.words or [])];tokens=[];times=[]
        for w in words:
            for token in normal(w.word):tokens.append(token);times.append((w.start,w.end))
        return words,tokens,times
    for meta in sorted(source.rglob('*-en.json')):
        t=json.loads(meta.read_text());mp3=meta.with_suffix('.mp3');assert H(mp3.read_bytes())==t['sha256']
        audio=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(mp3),'-f','f32le','-ar','16000','-ac','1','-']),dtype=np.float32).copy()
        expected=normal(t['text']);words,actual,times=hear(audio);before=' '.join(w.word.strip() for w in words)
        edits=[]
        for tag,i,j,k,l in difflib.SequenceMatcher(None,expected,actual,autojunk=False).get_opcodes():
            if tag!='insert' or k==l:continue
            if i==len(expected) and k>0 and times[k-1][1]+.12<times[k][0]:
                edits.append((times[k-1][1]+.12,len(audio)/16000,'unrequested ending: '+' '.join(actual[k:l])))
            elif l-k==1 and ((k>0 and actual[k]==actual[k-1]) or (l<len(actual) and actual[k]==actual[l])):
                lo,hi=times[k]
                if hi>lo and (k==0 or lo>=times[k-1][1]-.02) and (l==len(actual) or hi<=times[l][0]+.02):edits.append((max(0,lo-.005),hi+.005,'adjacent repeated word: '+actual[k]))
        for lo,hi,_ in sorted(edits,reverse=True):audio=np.concatenate([audio[:round(lo*16000)],audio[round(hi*16000):]])
        if edits:words,actual,times=hear(audio)
        match=difflib.SequenceMatcher(None,expected,actual,autojunk=False);coverage=sum(b.size for b in match.get_matching_blocks())/max(1,len(expected))
        differences=[dict(kind=tag,expected=expected[i:j],recognised=actual[k:l]) for tag,i,j,k,l in match.get_opcodes() if tag!='equal']
        extra=sum(len(d['recognised']) for d in differences if d['kind']=='insert')
        accepted=coverage>=.94 and extra<=1 and not any(len(d['expected'])>3 or len(d['recognised'])>3 for d in differences)
        audit=dict(textSha256=t['textSha256'],method='Independent Whisper small.en + VAD word timings; exact source text retained; unmatched word timing interpolated',inputAudioSha256=t['sha256'],previousAudit=t.get('captionAudit'),firstTranscript=before,transcript=' '.join(w.word.strip() for w in words),normalisedTokenCoverage=coverage,extraTokens=extra,differences=differences,edits=[dict(start=l,end=h,reason=r) for l,h,r in edits],accepted=accepted,humanListeningReview=False)
        reports.append(audit);print(json.dumps(dict(file=meta.name,coverage=coverage,extra=extra,accepted=accepted,differences=differences,edits=edits)),flush=True)
        if not accepted:continue
        spans=list(re.finditer(r'\S+',t['text']));flat=[];ranges=[]
        for span in spans:
            lo=len(flat);flat+=normal(span.group());ranges.append((lo,len(flat)))
        aligned={}
        for block in difflib.SequenceMatcher(None,flat,actual,autojunk=False).get_matching_blocks():
            for off in range(block.size):aligned[block.a+off]=times[block.b+off]
        duration=len(audio)/16000;intervals=[]
        for lo,hi in ranges:
            hit=[aligned[i] for i in range(lo,hi) if i in aligned]
            if hit:start,end=hit[0][0],hit[-1][1]
            else:
                left=max((i for i in aligned if i<lo),default=-1);right=min((i for i in aligned if i>=hi),default=len(flat));a=aligned[left][1] if left>=0 else 0;b=aligned[right][0] if right<len(flat) else duration-.12
                start=a+(b-a)*max(0,lo-left-1)/max(1,right-left);end=a+(b-a)*max(1,hi-left-1)/max(1,right-left)
            start=max(intervals[-1][1] if intervals else 0,start);end=min(duration-.01,max(start+.004,end));intervals.append((start,end))
        cues=[];i=0
        while i<len(spans):
            j=i+1
            while j<len(spans) and spans[j].end()-spans[i].start()<=64 and not re.search(r'[.!?]$',spans[j-1].group()):j+=1
            cues.append(dict(start=round(intervals[i][0],3),end=round(intervals[j-1][1],3),text=t['text'][spans[i].start():spans[j-1].end()]));i=j
        dest=out/(t['textSha256'][:12]+'-en.mp3')
        subprocess.run(['ffmpeg','-y','-v','error','-f','f32le','-ar','16000','-ac','1','-i','pipe:0','-ar','24000','-b:a','128k',str(dest)],input=audio.tobytes(),check=True)
        duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','default=noprint_wrappers=1:nokey=1',str(dest)]))
        t.update(file=str(dest.relative_to(D)),sha256=H(dest.read_bytes()),bytes=dest.stat().st_size,duration=duration,cues=cues,captionAudit=audit);updates[t['textSha256']]=t
    (D/'data/expressive-audio-audit.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
    assert len(updates)==8,f'Only {len(updates)}/8 speech tracks passed; existing manifest unchanged'
    for i,t in enumerate(guides['tracks']):
        if t['language']=='en':
            new=updates[t['textSha256']];new['stop']=t['stop'];guides['tracks'][i]=new
    guides['defaultPlaybackRate']=1.0;guides['voiceReview']='English Chatterbox Turbo built-in synthetic voice, independently inspected with Whisper small.en + VAD; differences and any edits recorded. No human listening certification. Chinese retains Xiaoxiao.'
    (D/'data/guide-audio.json').write_text(json.dumps(guides,ensure_ascii=False,indent=2)+'\n')
    print('ENGLISH_NARRATION_BOUND_BY_TEXT_HASH',flush=True)
if __name__=='__main__':main()
