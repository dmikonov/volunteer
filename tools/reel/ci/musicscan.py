"""Scan Mixkit free music (license allows social video) for surf-vibe tracks -> out/ci/music/catalog.json + 22 s preview snippets."""
import re, json, html, subprocess as sp, urllib.request, os
O = 'out/ci/music'; os.makedirs(f'{O}/snip', exist_ok=True)
PAGES = ['https://mixkit.co/free-stock-music/surf/'] + [f'https://mixkit.co/free-stock-music/tag/{t}/?page={p}' for t in ('surf', 'summer', 'beach') for p in (1, 2, 3, 4)] + \
        [f'https://mixkit.co/free-stock-music/rock/?page={p}' for p in (1, 2)] + [f'https://mixkit.co/free-stock-music/tag/{t}/' for t in ('surfing', 'indie', 'guitar', 'reggae', 'ska')]
def get(u):
    try: return urllib.request.urlopen(urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'}), timeout=30).read().decode('utf-8', 'ignore')
    except Exception as e: print('GET FAIL', u, e); return ''
cat = {}
for u in PAGES:
    h = get(u)
    if u == PAGES[0]: open(f'{O}/sample_page.html', 'w').write(h[:400000])
    for chunk in re.split(r'(?=<div[^>]+class="item-grid-card[ "])', h)[1:]:
        m = re.search(r'https://assets\.mixkit\.co/[^"\'\s]+?\.mp3', chunk)
        if not m: continue
        url = m.group(0)
        t = re.search(r'item-grid-card__title[^>]*>\s*(.*?)\s*<', chunk, re.S)
        a = re.search(r'item-grid-card__description[^>]*>\s*(.*?)\s*<', chunk, re.S)
        d = re.search(r'(\d+:\d\d)', chunk)
        tags = sorted(set(html.unescape(x).strip() for x in re.findall(r'/free-stock-music/(?:tag/)?[a-z0-9-]+/"[^>]*>\s*([^<]{2,30}?)\s*<', chunk)))
        cat.setdefault(url, {'url': url, 'title': html.unescape(t.group(1)) if t else '', 'artist': html.unescape(a.group(1)) if a else '', 'dur': d.group(1) if d else '', 'tags': tags, 'pages': []})['pages'].append(u)
print('tracks', len(cat))
GOOD = re.compile(r'surf|rock|guitar|indie|summer|ska|reggae|beach|garage|punk|acoustic|happy|carefree|upbeat|fun', re.I)
BAD = re.compile(r'edm|house|lounge|sensual|sexy|children|corporate|trap|hip hop|disco|cinematic|ambient|classical|horror', re.I)
for c in cat.values():
    s = ' '.join(c['tags'] + [c['title']] + c['pages'])
    c['score'] = len(GOOD.findall(s)) - 3 * len(BAD.findall(s)) + (5 if '/surf' in ' '.join(c['pages']) else 0)
top = sorted(cat.values(), key=lambda c: -c['score'])[:24]
for i, c in enumerate(top, 1):
    fn = f'/tmp/m{i}.mp3'
    try:
        urllib.request.urlretrieve(c['url'], fn)
        dur = float(sp.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', fn], capture_output=True, text=True).stdout or 60)
        st = max(0, dur * 0.3)
        c['snip'] = f'{O}/snip/{i:02d}.mp3'
        sp.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st:.1f}', '-t', '22', '-i', fn, '-af', 'afade=t=in:d=0.5,afade=t=out:st=20.5:d=1.5,loudnorm=I=-16', '-b:a', '128k', c['snip']], check=True)
        c['full_dur'] = round(dur, 1)
    except Exception as e: print('DL FAIL', c['url'], e)
json.dump({'all': list(cat.values()), 'top': top}, open(f'{O}/catalog.json', 'w'), ensure_ascii=False, indent=1)
for i, c in enumerate(top, 1): print(i, c['score'], c['title'], '|', c['artist'], '|', c['dur'], '|', ', '.join(c['tags'][:8]))
