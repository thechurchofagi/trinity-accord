"""Render the source bound by runtime-build.json; check real walking separately at a CPU-friendly viewport.
Large screenshots settle the camera explicitly and are not claimed as walking footage.
"""
import json,os,pathlib,re,subprocess,time
from playwright.sync_api import sync_playwright
P=pathlib.Path(__file__).resolve().parents[1];D=P/'dist';OUT=pathlib.Path(os.environ.get('MUSEUM_QA_OUTPUT','/tmp/museum-design'));OUT.mkdir(parents=True,exist_ok=True)
js=D/'__design_qa.js';html=D/'__design_qa.html'
harness='''
window.__designQA={
 get state(){return {camera:camera.position.toArray(),moving:!!motion,travelled:motion?.travelled,length:motion?.route&&routeLength(motion.route),hidden:document.hidden,panelOpen:$('panel').open,walkable:isWalkable(galleryLayout,camera.position),eye:camera.position.y-floorAt(galleryLayout,camera.position),selected:selectedExhibit,crystal:!!floatingCrystal};},
 async focus(id,settle=true){stopTour();manualUntil=0;pendingTourView=null;if(id==='physical-alpha')await loadCrystal();focusExhibit(id);if(settle&&motion){camera.position.copy(motion.end);camera.position.y=floorAt(galleryLayout,camera.position)+galleryLayout.eyeHeight;yaw=motion.endYaw;pitch=motion.endPitch;motion=null;}},
 async sky(){stopTour();manualUntil=0;pendingTourView=null;roomIndex=4;waitingView();if(motion){camera.position.copy(motion.end);yaw=motion.endYaw;pitch=motion.endPitch;motion=null;}updateUI();},
 trace:[]
};
const originalAnimate=animate;animate=function(now){originalAnimate(now);if(window.__traceWalk)window.__designQA.trace.push({now,p:camera.position.toArray(),eye:camera.position.y-floorAt(galleryLayout,camera.position)});};
'''
js.write_text((D/'museum.js').read_text()+harness)
html.write_text(re.sub(r'<script defer src="\./boot-loader\.js[^\"]*"></script>','<script type="module" src="./__design_qa.js"></script>',(D/'index.html').read_text()))
server=subprocess.Popen(['python','-m','http.server','8767','--bind','127.0.0.1','--directory',str(D)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);report=[]
try:
 time.sleep(.5)
 with sync_playwright() as p:
  b=p.chromium.launch(headless=True,args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
  viewport=os.environ['MUSEUM_QA_VIEWPORT'];mobile=viewport=='mobile';page=b.new_page(viewport={'width':390 if mobile else 1440,'height':844 if mobile else 900},is_mobile=mobile,has_touch=mobile);errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto('http://127.0.0.1:8767/__design_qa.html?lang=en#entrance',wait_until='networkidle');page.wait_for_selector('body[data-museum-ready="true"]');page.wait_for_selector('#scene-status',state='hidden',timeout=90000)
  assert not page.locator('#fallback-gallery').is_visible();assert page.locator('#rooms button').count()==5
  for eid in ['eth-070','proto-protocol','canon-1','physical-alpha','authority-boundary','first-contact']:
   page.evaluate('(id)=>window.__designQA.focus(id)',eid);page.wait_for_timeout(600)
   state=page.evaluate('window.__designQA.state');assert state['walkable'],state;assert abs(state['eye']-1.65)<1e-6,state
   page.screenshot(path=str(OUT/f'{viewport}-{eid}.png'),timeout=90000);report.append(state);print('DESIGN_CAPTURE',viewport,eid,flush=True)
  page.evaluate('window.__designQA.sky()');page.wait_for_timeout(600);page.screenshot(path=str(OUT/f'{viewport}-gold-sky.png'),timeout=90000)
  if not mobile:
   page.set_viewport_size({'width':480,'height':320});page.evaluate("window.__designQA.focus('project-intro')");page.evaluate("window.__traceWalk=true;window.__designQA.focus('canon-1',false)")
   try:
    page.wait_for_function('!window.__designQA.state.moving',timeout=300000)
   finally:
    trace=page.evaluate('window.__traceWalk=false;window.__designQA.trace');state=page.evaluate('window.__designQA.state')
    (OUT/'walking-diagnostic.json').write_text(json.dumps({'state':state,'samples':trace}))
    print('WALK_DIAGNOSTIC',state,'frames',len(trace),flush=True)
   assert len(trace)>100
   travelled=0
   for a,z in zip(trace,trace[1:]):
    delta=((z['p'][0]-a['p'][0])**2+(z['p'][2]-a['p'][2])**2)**.5;travelled+=delta
    assert delta<=.1251,(a,z)
    assert abs(z['eye']-1.65)<1e-6,z
   assert travelled>35,travelled
   (OUT/'walking-trace.json').write_text(json.dumps({'samples':trace,'travelledMetres':travelled,'scope':'Actual animation frames; no camera settle or time acceleration during this walk.'}))
  assert not errors,errors;page.close();b.close()
finally:
 server.terminate();js.unlink(missing_ok=True);html.unlink(missing_ok=True);(OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print('DESIGN_ACCEPTANCE',len(report),flush=True)
