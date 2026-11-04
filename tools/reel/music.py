"""Real surf music bed from assets/music/library.json -> $S17/tip1/music.wav. usage: music.py <seconds> [track_id]
Picks spec/arg track, else rotates approved tracks by day (neighbours differ). Called by audio_fx.py, so every build gets it."""
import json, os, sys, subprocess as sp, urllib.request, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
O = os.environ.get('S17', '/s17') + '/tip1'; os.makedirs(O, exist_ok=True)
T = float(sys.argv[1]) if len(sys.argv) > 1 else 24.0
lib = json.load(open(f'{ROOT}/assets/music/library.json'))['tracks']
pool = [t for t in lib if t.get('approved')] or [t for t in lib if t.get('temp')]
want = sys.argv[2] if len(sys.argv) > 2 else os.environ.get('REEL_MUSIC')
tr = next((t for t in lib if t['id'] == want), None) or pool[dt.date.today().toordinal() % len(pool)]
src = f'/tmp/music_{tr["id"]}.mp3'
try:
    if not os.path.exists(src):
        open(src, 'wb').write(urllib.request.urlopen(urllib.request.Request(tr['url'], headers={'User-Agent': 'Mozilla/5.0'}), timeout=60).read())
    dur = float(sp.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', src], capture_output=True, text=True).stdout.strip())
    st = min(dur * tr.get('start', 0.25), max(0, dur - T - 3))
    sp.run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{st:.2f}', '-t', f'{T + 2:.2f}', '-i', src, '-af', f'afade=t=in:d=0.4,afade=t=out:st={max(0, T - 1.0):.2f}:d=1.4,loudnorm=I=-16:TP=-2',
            '-ar', '48000', '-ac', '2', f'{O}/music.wav'], check=True)
    json.dump(tr, open(f'{O}/music_track.json', 'w'), ensure_ascii=False); print('music:', tr['id'], tr['title'], 'from', round(st, 1))
except Exception as e:
    print('MUSIC FAIL (no music in this reel, report it):', tr['url'], e)
    sp.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', f'anullsrc=r=48000:cl=stereo', '-t', f'{T + 2:.2f}', f'{O}/music.wav'], check=True)
