"""Test the real source in a temporary harness after separately testing the bundle.
The harness exposes no production API and is deleted before publication.
"""
import json,os,pathlib,re,shutil,subprocess,time
from playwright.sync_api import sync_playwright
P=pathlib.Path(__file__).resolve().parents[1];D=P/'dist';OUT=pathlib.Path(os.environ.get('MUSEUM_QA_OUTPUT','/tmp/presentation-qa'));OUT.mkdir(parents=True,exist_ok=True)
js=D/'__presentation_qa.js';html=D/'__presentation_qa.html'
harness='''
window.__presentationQA={
 get state(){return {ready:spatialReady,room:roomIndex,selected:selectedExhibit,touring,elapsed:tourElapsed,walkable:spatialReady&&isWalkable(galleryLayout,camera.position),camera:camera?.position.toArray(),yaw,voice:recordedGuide.track?.file,flaw:flawIndex};},
 station(i){stopTour();reduced=true;tourElapsed=tourStops.slice(0,i).reduce((a,s)=>a+s.seconds,0);guideResume=null;startTour(true);},
 focus(id){stopTour();reduced=true;focusExhibit(id);},
 inspect(i){return showFlaw(i);},
 closePhoto(){silenceGuide();closeFlaws();},
 settle(){if(motion){camera.position.copy(motion.end);yaw=motion.endYaw;pitch=motion.endPitch;motion=null;}},
 music(){stopTour();focusExhibit('eth-070');return playTrack(exhibits.get('eth-049'),exhibits.get('eth-070'),false);},
 lyricTime(){return lyricCues[0]?.words?.[0]?.start;},
 finish(){stopTour();reduced=true;roomIndex=5;waitingView();touring=true;tourElapsed=tourDuration;tourTick(performance.now());}
};
'''
js.write_text((D/'museum.js').read_text()+harness)
text=(D/'index.html').read_text();text=re.sub(r'<script defer src="\./boot-loader\.js[^\"]*"></script>','<script type="module" src="./__presentation_qa.js"></script>',text);html.write_text(text)
server=subprocess.Popen(['python','-m','http.server','8766','--bind','127.0.0.1','--directory',str(D)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);report=[]
try:
 time.sleep(1)
 with sync_playwright() as p:
  chrome=shutil.which('google-chrome') or shutil.which('chromium')
  b=p.chromium.launch(**({'executable_path':chrome} if chrome else {}),headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  for label,w,h in [('desktop',1440,900),('mobile',390,844)]:
   if os.environ.get('MUSEUM_QA_VIEWPORT') not in [None,label]:continue
   print('START_VIEWPORT',label,flush=True)
   page=b.new_page(viewport={'width':w,'height':h},is_mobile=label=='mobile',has_touch=label=='mobile',reduced_motion='reduce');errors=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('console',lambda m:print('BROWSER_CONSOLE',m.type,m.text,flush=True) if m.type in ['error','warning'] else None)
   page.goto('http://127.0.0.1:8766/__presentation_qa.html?lang=en#entrance',wait_until='networkidle')
   page.wait_for_function('window.__presentationQA?.state.ready');page.wait_for_selector('#scene-status',state='hidden')
   # A focused button, caps lock and arrows must not swallow walking or exit guidance.
   page.locator('#tour').click()
   if page.locator('#guide-audio-prompt').is_visible():page.locator('#guide-audio-start').click()
   page.wait_for_function("!document.getElementById('narration').paused")
   page.locator('#guide-speed').click()
   before=page.evaluate('window.__presentationQA.state')
   page.keyboard.down('w')
   page.wait_for_function('before=>JSON.stringify(window.__presentationQA.state.camera)!==JSON.stringify(before)',arg=before['camera'],timeout=10000)
   page.keyboard.up('w')
   after=page.evaluate('window.__presentationQA.state')
   assert after['touring'] and before['camera']!=after['camera'],(before,after)
   page.keyboard.press('Escape');assert page.evaluate('window.__presentationQA.state.touring')
   # Hover moves only the cursor; dragging turns, without cancelling guidance.
   before=page.evaluate('window.__presentationQA.state')
   page.mouse.move(w*.35,h*.3);page.mouse.move(w*.65,h*.3,steps=10)
   after=page.evaluate('window.__presentationQA.state')
   assert before['yaw']==after['yaw'],(before,after)
   page.mouse.down();page.mouse.move(w*.4,h*.3,steps=10);page.mouse.up()
   after=page.evaluate('window.__presentationQA.state');assert after['touring'] and after['yaw']!=before['yaw']
   page.locator('#tour').click();assert not page.evaluate('window.__presentationQA.state.touring')
   states=[]
   for index in [0,1,2,3,4,5,6,7]:
    page.evaluate('(i)=>window.__presentationQA.station(i)',index)
    page.wait_for_function("document.getElementById('narration').readyState>=1")
    if page.locator('#guide-audio-prompt').is_visible():page.locator('#guide-audio-start').click()
    page.wait_for_function("!document.getElementById('narration').paused")
    state=page.evaluate('window.__presentationQA.state');assert state['walkable'],state
    assert 'guides-expressive/' in state['voice'],state
    states.append(state);print('STATION_RENDERED',label,index,flush=True)
    page.evaluate('window.__presentationQA.settle()');page.wait_for_timeout(200)
    if label=='desktop' or index in [1,4,5,6,7]:page.screenshot(path=str(OUT/f'{label}-station-{index}.png'))
   for eid in ['canon-1','canon-2','canon-3']:
    page.evaluate('(id)=>window.__presentationQA.focus(id)',eid);page.evaluate('window.__presentationQA.settle()');page.wait_for_timeout(300)
    assert page.evaluate('window.__presentationQA.state.walkable')
    if label=='desktop':page.screenshot(path=str(OUT/(label+'-'+eid+'.png')))
   for flaw in range(3):
    page.evaluate('(i)=>window.__presentationQA.inspect(i)',flaw)
    page.wait_for_function("document.querySelector('#flaw-view img')?.complete && document.querySelector('#flaw-view img').naturalWidth>0")
    assert page.locator('#flaw-view img').count()==1
    expected=json.loads((D/'data/public-flaws.json').read_text())['items'][flaw]['file']
    assert page.locator('#flaw-view img').get_attribute('src')==expected
    if flaw==0:page.screenshot(path=str(OUT/(label+'-original-flaw.png')))
    page.evaluate('window.__presentationQA.closePhoto()')
   page.evaluate('window.__presentationQA.music()');page.evaluate('window.__presentationQA.settle()')
   page.wait_for_function('window.__presentationQA.lyricTime()!==undefined')
   if page.locator('#guide-audio-prompt').is_visible():page.locator('#guide-audio-start').click()
   page.evaluate("document.getElementById('music').currentTime=window.__presentationQA.lyricTime()+.1")
   page.wait_for_function("document.querySelector('#subtitle-lines [data-word]') && document.querySelector('#subtitle-lines .subtitle-zh')")
   page.screenshot(path=str(OUT/(label+'-original-music-lyrics.png')))
   page.evaluate('window.__presentationQA.finish()');page.evaluate('window.__presentationQA.settle()');page.wait_for_timeout(300)
   assert page.evaluate('window.__presentationQA.state.elapsed')==580
   assert page.evaluate('window.__presentationQA.state.touring') is False
   assert page.locator('body').get_attribute('data-presentation')=='true'
   assert not page.locator('#exhibit-strip').is_visible()
   page.screenshot(path=str(OUT/(label+'-finished-sky.png')))
   page.locator('#rooms [data-room="1"]').click(force=True)
   assert page.locator('#exhibit-strip').count()==0,'Numbered song strip stays removed'
   assert page.locator('#walk-controls').is_visible(),'Walking controls remain usable'
   assert not errors,errors
   report.append(dict(viewport=label,stations=states,originalPanels=3,unalteredMicroscopeImages=3,originalLyricsBothLanguages=True,completedSeconds=580,restoredManualControls=True,pageErrors=errors,scope='Accelerated state checks and rendered frames; not nine minutes of uninterrupted real-time playback or physical-device listening certification.'))
   page.close()
  b.close()
finally:
 server.terminate();js.unlink(missing_ok=True);html.unlink(missing_ok=True);(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('PRESENTATION_ACCEPTANCE',len(report),'viewports',flush=True)
