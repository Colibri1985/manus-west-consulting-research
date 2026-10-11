from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).parent
PAGES = ['stage1-home.html','stage1-diagnostic.html','stage1-external-cfo.html','stage1-contact.html','stage1-calculator.html']

def launch(p):
    for opts in ({}, {'executable_path':'/usr/bin/chromium'}):
        try:
            return p.chromium.launch(headless=True, **opts)
        except Exception:
            pass
    raise RuntimeError('Chromium unavailable')

with sync_playwright() as p:
    browser = launch(p)
    for viewport, folder in [({'width':1440,'height':1000}, 'desktop'), ({'width':390,'height':844}, 'mobile')]:
        page = browser.new_page(viewport=viewport, device_scale_factor=1)
        for name in PAGES:
            page.goto((ROOT/'pages'/name).as_uri(), wait_until='networkidle')
            page.screenshot(path=str(ROOT/'screenshots'/folder/name.replace('.html','.png')), full_page=True)
        page.close()
    browser.close()
print('rendered', len(PAGES)*2, 'screenshots')
