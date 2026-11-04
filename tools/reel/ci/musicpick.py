"""Surf music candidates: chosen Mixkit tracks + Free Music Archive 'Surf' genre (CC BY / CC0 only) -> out/ci/music/cand/NN.mp3 (22 s) + cand.json"""
import re, json, html, subprocess as sp, urllib.request, os
O = 'out/ci/music/cand'; os.makedirs(O, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/130 Safari/537.36'}
def get(u, b=False):
    r = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=40).read()
    return r if b else r.decode('utf-8', 'ignore')
MIX = [(48, 'Ride the Waves', 'surf rock'), (83, "Surf's Up Dude", 'surf rock'), (1107, "Lovin' Life", 'rock/funk'), (963, 'Just Keep Walking', 'indie pop'),
       (780, 'Okay', 'ska'), (814, 'My Last Mojito', 'reggae'), (1157, 'The Root', 'indie rock'), (1135, 'Dare Me', 'indie rock'),
       (1151, 'Oh My Joe', 'funk rock'), (817, 'The Duel', 'country rock'), (1000, 'I Can Hear Your Heartbeat', 'indie pop'), (1087, 'A Special Feeling', 'indie pop')]
cands = [{'src': 'Mixkit', 'license': 'Mixkit Music Free License (social video ok, no credit needed)', 'url': f'https://assets.mixkit.co/music/{i}/{i}.mp3', 'title': t, 'style': s} for i, t, s in MIX]
# FMA Surf genre
try:
    for page in (1, 2, 3):
        h = get(f'https://freemusicarchive.org/genre/Surf/?sort=track_interest&d=1&page={page}')
        if page == 1: open('out/ci/music/fma_sample.html', 'w').write(h[:300000])
        for m in re.finditer(r"data-track-info='([^']+)'", h):
            try: d = json.loads(html.unescape(m.group(1)))
            except Exception: continue
            lic = (d.get('licenseTitle') or d.get('license') or '') + ' ' + (d.get('licenseUrl') or '')
            if re.search(r'-nc|noncommercial|non-commercial|-nd|noderiv', lic, re.I): continue
            if not re.search(r'by|cc0|zero|public', lic, re.I): continue
            fu = d.get('fileUrl') or d.get('playbackUrl')
            if fu: cands.append({'src': 'FMA', 'license': lic.strip(), 'url': fu, 'title': d.get('title', ''), 'artist': d.get('artistName', ''), 'style': 'surf (FMA)', 'page': d.get('url', '')})
except Exception as e: print('FMA FAIL', e)
seen, out = set(), []
for c in cands:
    if c['url'] in seen or len([x for x in out if x['src'] == 'FMA']) >= 8 and c['src'] == 'FMA': continue
    seen.add(c['url'])
    n = len(out) + 1; fn = f'/tmp/c{n}.mp3'
    try:
        open(fn, 'wb').write(get(c['url'], True))
        dur = float(sp.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', fn], capture_output=True, text=True).stdout.strip() or 60)
        c['full_dur'] = round(dur, 1); c['snip'] = f'{O}/{n:02d}.mp3'
        sp.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{dur * 0.25:.1f}', '-t', '22', '-i', fn, '-af', 'afade=t=in:d=0.4,afade=t=out:st=20.5:d=1.5,loudnorm=I=-16', '-b:a', '128k', c['snip']], check=True)
        out.append(c)
    except Exception as e: print('DL FAIL', c['url'], e)
json.dump(out, open('out/ci/music/cand.json', 'w'), ensure_ascii=False, indent=1)
for i, c in enumerate(out, 1): print(f"{i:02d}", c['src'], '|', c['title'], '|', c.get('artist', ''), '|', c['style'], '|', c['full_dur'], '|', c['license'][:60])
