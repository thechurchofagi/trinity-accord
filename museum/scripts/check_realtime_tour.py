"""Play the shipped 3D English tour to its natural end, without seeking.

CI acceptance of timing, media and rendered states; not a human listening review.
"""
import functools
import http.server
import json
import os
import pathlib
import threading
import time

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = pathlib.Path(os.environ.get('MUSEUM_QA_OUTPUT', '/tmp/museum-realtime'))
OUT.mkdir(parents=True, exist_ok=True)
guides = json.loads((ROOT / 'dist/data/guide-audio.json').read_text())
expected = {t['file']: t['stop'] for t in guides['tracks'] if t['language'] == 'en'}
plan = json.loads((ROOT / 'scene/tour-script.json').read_text())
handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(ROOT / 'dist'))
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
threading.Thread(target=server.serve_forever, daemon=True).start()
report = {'scope': 'Unaccelerated production-bundle 3D playback; automated media and visual-state checks.',
          'samples': [], 'pageErrors': [], 'assetFailures': [], 'passed': False}
try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
        # Full-size desktop/mobile frames are covered by check_presentation.py.
        # A 480 × 320 real-time surface keeps software rendering from stalling
        # the presentation clock; never disable 3D or reduce its motion here.
        page = browser.new_page(viewport={'width': 480, 'height': 320})
        page.on('console', lambda m: print('BROWSER_CONSOLE',m.type,m.text,flush=True) if m.type in ['error','warning'] else None)
        page.on('pageerror', lambda e: report['pageErrors'].append(str(e)))
        page.on('response', lambda r: report['assetFailures'].append(r.url) if r.status >= 400 and '/assets/' in r.url else None)
        page.goto(f'http://127.0.0.1:{server.server_port}/?lang=en#entrance', wait_until='load')
        page.locator('body[data-museum-ready="true"]').wait_for(timeout=60000)
        page.locator('#scene-status').wait_for(state='hidden', timeout=60000)
        assert not page.locator('#fallback-gallery').is_visible(), '3D rendering is required'
        page.locator('#tour').click()
        started = time.monotonic()
        seen = set()
        seen_flaws = set()
        inspection_files = {t['file']: t['flaw'] for t in guides['inspectionTracks'] if t['language']=='en'}
        previous = 0
        last_log = -15
        while time.monotonic() - started < 1500:
            sample = page.evaluate('''() => {
              const a=document.getElementById('narration'),m=document.getElementById('music');
              return {progress:document.getElementById('tour-progress').textContent,
                room:document.querySelector('#rooms [aria-current="true"]')?.textContent,
                source:a.getAttribute('src'),audioTime:a.currentTime,playing:!a.paused,
                musicPlaying:!m.paused,musicTime:m.currentTime,musicSource:m.getAttribute('src'),moving:document.getElementById('world').dataset.cameraMoving,caption:document.getElementById('caption-text').textContent,
                inspection:!document.getElementById('flaw-view').hidden,
                blocked:document.getElementById('guide-audio-prompt').open};
            }''')
            sample['wallSeconds'] = round(time.monotonic() - started, 2)
            clock = sample['progress'].split(' / ')[0]
            elapsed = int(clock)
            assert previous <= elapsed <= len(plan), sample
            if sample['musicPlaying']:
                stop=plan[elapsed-1]
                assert sample['musicTime'] <= stop.get('musicOffset',0)+stop.get('musicDuration',30)+.5, sample
            assert not sample['blocked'], 'Uninterrupted playback requested: ' + str(sample)
            assert not (sample['playing'] and sample['musicPlaying']), 'Narration and song overlap'
            if sample['playing'] and sample['source'] in inspection_files:
                seen_flaws.add(inspection_files[sample['source']])
            if sample['playing'] and sample['source'] in expected:
                seen.add(expected[sample['source']])
            if sample['wallSeconds'] - last_log >= 15 or 'complete' in sample['progress']:
                report['samples'].append(sample)
                print('TOUR_PROGRESS', json.dumps(sample), flush=True)
                last_log = sample['wallSeconds']
            previous = elapsed
            if 'complete' in sample['progress']:
                break
            page.wait_for_timeout(1000)
        assert 'complete' in sample['progress'], 'Tour failed to finish within twenty-five wall-clock minutes'
        assert seen_flaws == {0,1,2}, ('Missing audible flaw explanations', seen_flaws)
        assert seen == set(range(len(plan))), ('Missing audible tour tracks', seen)
        assert page.locator('body').get_attribute('data-presentation') == 'true'
        assert not page.locator('#exhibit-strip').is_visible()
        assert 'Replay tour' in page.locator('#tour').inner_text()
        assert 'complete' in page.locator('#tour-progress').inner_text()
        assert not report['pageErrors'], report['pageErrors']
        assert not report['assetFailures'], report['assetFailures']
        # Capture after completion: screenshots must not interrupt this test.
        page.screenshot(path=str(OUT / 'completed-tour.png'), timeout=60000)
        report.update(passed=True, audibleStops=sorted(seen), audibleFlaws=sorted(seen_flaws), completedStops=len(plan),
                      wallSeconds=round(time.monotonic() - started, 2))
        browser.close()
finally:
    server.shutdown()
    (OUT / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
print('REALTIME_TOUR_ACCEPTANCE', report['passed'], flush=True)
