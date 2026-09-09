"""Rendered Chromium acceptance; diagnostic viewports, not physical-device certification."""
import json,os,pathlib,shutil,subprocess,time
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
guides=json.loads((ROOT/'dist/data/guide-audio.json').read_text())
intro={lang:next(t['file'] for t in guides['tracks'] if t['stop']==0 and t['language']=='en') for lang in ['en','zh']}
OUT=pathlib.Path(os.environ.get('MUSEUM_QA_OUTPUT','/tmp/museum-browser-qa'));OUT.mkdir(parents=True,exist_ok=True)
server=subprocess.Popen(['python','-m','http.server','8765','--bind','127.0.0.1','--directory',str(ROOT/'dist')],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
report=[]
try:
 time.sleep(1)
 with sync_playwright() as p:
  chrome=shutil.which('google-chrome') or shutil.which('chromium')
  b=p.chromium.launch(**({'executable_path':chrome} if chrome else {}),headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  for label,width,height in [('desktop',1440,900),('mobile',390,844)]:
   if os.environ.get('MUSEUM_QA_VIEWPORT') not in [None,label]:continue
   print('START_VIEWPORT',label,flush=True)
   page=b.new_page(viewport={'width':width,'height':height},is_mobile=label=='mobile',has_touch=label=='mobile',reduced_motion='reduce')
   errors=[];failed=[]
   page.on('console',lambda m:print('BROWSER_CONSOLE',m.type,m.text,flush=True) if m.type in ['error','warning'] else None)
   page.on('pageerror',lambda e:errors.append(str(e)))
   page.on('response',lambda r:failed.append({'status':r.status,'url':r.url}) if r.status>=400 and '/assets/' in r.url else None)
   page.goto('http://127.0.0.1:8765/?lang=en#entrance',wait_until='networkidle')
   page.wait_for_selector('body[data-museum-ready="true"]',timeout=30000)
   page.wait_for_selector('#scene-status',state='hidden',timeout=30000)
   assert page.locator('#rooms button').count()==5
   assert not page.locator('#fallback-gallery').is_visible(),'Flat fallback is not WebGL acceptance'
   for i in range(5):
    page.locator(f'#rooms [data-room="{i}"]').click(force=True);page.wait_for_function("document.getElementById('world').dataset.cameraMoving==='false'",timeout=300000)
    assert page.locator(f'#rooms [data-room="{i}"]').get_attribute('aria-current')=='true'
    page.screenshot(timeout=90000,path=str(OUT/f'{label}-{i}.png'));print('ROOM_RENDERED',label,i,flush=True)
   page.locator('#focus-art').click();page.wait_for_timeout(200)
   assert 'Guardian' in page.locator('#panel-content').inner_text()
   assert page.locator('#panel-content a[href="./data/records/guardian-charter-103635270.txt"]').count()==1
   page.locator('#close-panel').click()
   # Approach each key object through the public controls, not a hidden debug API.
   for room,eid in [(1,'eth-070'),(1,'eth-122'),(3,'canon-1'),(3,'canon-2'),(3,'canon-3'),(3,'physical-alpha'),(4,'authority-boundary')]:
    page.locator(f'#rooms [data-room="{room}"]').click(force=True)
    page.locator('#room-works').click()
    page.locator(f'#panel-content [data-exhibit="{eid}"]').click()
    page.wait_for_function("document.getElementById('world').dataset.cameraMoving==='false'",timeout=300000)
    if page.locator('#guide-audio-prompt').is_visible():page.locator('#guide-audio-start').click()
    page.screenshot(timeout=90000,path=str(OUT/f'{label}-focus-{eid}.png'));print('WORK_RENDERED',label,eid,flush=True)
   page.locator('#language').click();page.wait_for_timeout(200)
   assert page.locator('html').get_attribute('lang')=='zh-CN'
   page.locator('#focus-art').click()
   assert '守护者' in page.locator('#panel-content').inner_text()
   page.screenshot(timeout=90000,path=str(OUT/f'{label}-guardian-zh.png'))
   page.locator('#close-panel').click()
   page.locator('#rooms [data-room="0"]').click(force=True)
   page.locator('#tour').click()
   page.wait_for_function("file => document.getElementById('narration').currentSrc.endsWith(file) && document.getElementById('narration').readyState>=1",arg=intro['zh'])
   page.locator('#language').click()
   page.wait_for_function("file => document.getElementById('narration').currentSrc.endsWith(file) && document.getElementById('narration').readyState>=1",arg=intro['en'])
   if page.locator('#guide-audio-prompt').is_visible():page.locator('#guide-audio-start').click()
   page.wait_for_function("!document.getElementById('narration').paused")
   page.locator('#tour').click()
   assert not errors,errors
   assert not failed,failed
   report.append(dict(viewport=label,width=width,height=height,rooms=5,closeViews=7,renderedModel=True,guardianLinks=True,bilingualAudioLoaded=True,pageErrors=errors,assetFailures=failed))
   page.close()
  b.close()
finally:
 server.terminate();(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report))
