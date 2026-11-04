# Use inside the Composio REMOTE_WORKBENCH kernel, in two separate cells (180 s limit each):
#   cell 1: exec(open('/mnt/files/forecast/run_forecast.py').read()); setup()
#   cell 2: exec(open('/mnt/files/forecast/run_forecast.py').read()); print(produce('today', 'YYYY-MM-DD'))   # or produce('weekend', FRIDAY)
# Needs /mnt/files/forecast/token.txt (SurfTribe forecast API token).
import os, subprocess, json, datetime as _dt, urllib.request
D = '/mnt/files/forecast'
RAW = 'https://raw.githubusercontent.com/dmikonov/volunteer/surftribe-media/forecast/'

def setup():
    os.makedirs(D, exist_ok=True)
    for f in ('make_forecast.py', 'Rubik.ttf', 'bg_lines.jpg', 'run_forecast.py'):
        urllib.request.urlretrieve(f'{RAW}{f}?v={_dt.datetime.now().timestamp()}', f'{D}/{f}')
    try:
        import playwright  # noqa
    except ImportError:
        subprocess.run('pip install -q playwright', shell=True, check=True)
    if not os.path.isdir(os.path.expanduser('~/.cache/ms-playwright')) or not os.listdir(os.path.expanduser('~/.cache/ms-playwright')):
        subprocess.run('python3 -m playwright install chromium', shell=True, check=True, capture_output=True)
    return 'setup ok, token: ' + str(os.path.exists(f'{D}/token.txt'))

def _direct(path):
    res, err = upload_local_file(path)
    if err: raise RuntimeError(err)
    url = res['s3_url']
    class NoRedir(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, *a, **k): return None
    try:
        urllib.request.build_opener(NoRedir).open(urllib.request.Request(url, method='HEAD'))
    except urllib.error.HTTPError as e:
        if e.code in (301, 302, 303, 307, 308): return e.headers['Location']
        raise
    return url

def produce(mode, date):
    out = f'{D}/out/{mode}-{date}'
    args = ['python3', f'{D}/make_forecast.py'] + (['today', date, out] if mode == 'today' else [date, out])
    r = subprocess.run(args, capture_output=True, text=True, timeout=150)
    if r.returncode: return json.dumps({'error': r.stderr[-1500:]})
    if mode == 'today':
        return json.dumps({'story': _direct(f'{out}/today.jpg'), 'data': json.load(open(f'{out}/today.json'))}, ensure_ascii=False)
    return json.dumps({'images': [_direct(f'{out}/HE_{i}.jpg') for i in range(1, 6)], 'story': _direct(f'{out}/story.jpg'),
                       'caption': open(f'{out}/caption.txt', encoding='utf-8').read()}, ensure_ascii=False)
