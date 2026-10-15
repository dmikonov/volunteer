# Run inside the Composio REMOTE_WORKBENCH kernel:  exec(open('/mnt/files/forecast/run_week.py').read())
# Needs /mnt/files/forecast/token.txt (SurfTribe forecast API token). Optional: set FRIDAY = 'YYYY-MM-DD' before exec. Prints JSON with caption, image URLs and story URL.
import subprocess, json, os, datetime as _dt, urllib.request
_dir = '/mnt/files/forecast'
os.makedirs(_dir, exist_ok=True)
for _f in ('make_forecast.py', 'Rubik.ttf', 'bg_lines.jpg'):
    urllib.request.urlretrieve(f'https://raw.githubusercontent.com/dmikonov/volunteer/surftribe-media/forecast/{_f}?v={_dt.datetime.now().timestamp()}', f'{_dir}/{_f}')
try:
    import playwright  # noqa
except ImportError:
    subprocess.run('pip install -q playwright', shell=True, check=True)
subprocess.run('python3 -m playwright install chromium', shell=True, check=True, capture_output=True)
if 'FRIDAY' not in globals():
    _t = _dt.date.today(); FRIDAY = (_t + _dt.timedelta(days=(4 - _t.weekday()) % 7)).isoformat()
_out = f'{_dir}/out/{FRIDAY}'
_r = subprocess.run(['python3', f'{_dir}/make_forecast.py', FRIDAY, _out], capture_output=True, text=True)
if _r.returncode: raise SystemExit(_r.stderr[-2000:])
def _direct(path):
    res, err = upload_local_file(path)
    if err: raise SystemExit(err)
    url = res['s3_url']
    req = urllib.request.Request(url, method='HEAD')
    class _NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    try:
        urllib.request.build_opener(_NoRedir).open(req)
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308): return e.headers['Location']
        raise
    return url
_imgs = [_direct(f'{_out}/HE_{i}.jpg') for i in range(1, 6)]
_story = _direct(f'{_out}/story.jpg')
FORECAST = {'friday': FRIDAY, 'caption': open(f'{_out}/caption.txt', encoding='utf-8').read(),
            'images': _imgs, 'story': _story, 'data': json.load(open(f'{_out}/data.json', encoding='utf-8'))}
print(json.dumps(FORECAST, ensure_ascii=False))
