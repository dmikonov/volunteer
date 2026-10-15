"""SurfTribe weekend forecast (Hebrew) for @surftribe_il, from the SurfTribe app's own forecast endpoint.
Usage: python3 make_forecast.py FRIDAY_YYYY-MM-DD OUTDIR [api_json_file]
The API token is read from env FORECAST_TOKEN or /mnt/files/forecast/token.txt (never commit it).
Renders 5 slides (1080x1350) + story (1080x1920), caption.txt, data.json.
"""
import sys, os, json, base64, datetime as dt, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
API = 'https://staging.surftribe.rest/api/story/forecast'
CYAN, CORAL, GREEN, FOAM, GREY, SUN = '#00CDFE', '#FF5150', '#68C090', '#F5F1F7', '#9A8F98', '#FFC857'
DAYS_HE = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']
Q = {'epic': ('אפי', CORAL, 3), 'good': ('טוב', GREEN, 2), 'fair': ('בינוני', SUN, 1), 'flat': ('פלאט', GREY, 0)}
WIND = {'offshore': ('אופשור', 2), 'cross-shore': ('רוח צד', 1), 'onshore': ('אונשור', 0)}


def token():
    t = os.environ.get('FORECAST_TOKEN')
    if not t and Path('/mnt/files/forecast/token.txt').exists():
        t = Path('/mnt/files/forecast/token.txt').read_text().strip()
    if not t: raise SystemExit('no FORECAST_TOKEN')
    return t


def fetch(friday, days=2):
    url = f'{API}?token={token()}&days={days}&start={friday}'
    with urllib.request.urlopen(url, timeout=40) as r:
        return json.loads(r.read().decode())


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


def css():
    return (f"@font-face{{font-family:Rubik;src:url(data:font/ttf;base64,{b64(HERE / 'Rubik.ttf')})}}"
            "*{margin:0;padding:0;box-sizing:border-box}"
            f"body{{width:1080px;background:#2D242A;font-family:Rubik;color:{FOAM}}}"
            ".s{position:relative;width:1080px;overflow:hidden;background:linear-gradient(180deg,#2D242A,#3A2331)}"
            f".k{{font-size:30px;font-weight:700;color:{CYAN};letter-spacing:.5px}}"
            ".h{font-weight:900;line-height:1.02;letter-spacing:-1px}"
            ".mark{position:absolute;top:44px;right:80px;font-weight:800;font-size:32px}.mark b{color:#00CDFE}"
            ".cell{border-top:2px solid rgba(245,241,247,.14);padding:34px 0}"
            ".lbl{font-size:30px;opacity:.7}.val{font-size:74px;font-weight:800;margin-top:6px}")


def page(body, idx, total, h=1350):
    ft = (f'<div dir=ltr style="position:absolute;left:44px;bottom:30px;font:500 23px Rubik;opacity:.82">'
          f'{idx}/{total}&nbsp;&nbsp;·&nbsp;&nbsp;@surftribe_il</div>') if idx else ''
    return (f'<!doctype html><html><head><meta charset=utf-8><style>{css()}</style></head><body style="height:{h}px">'
            f'<div class=s dir=rtl lang=he style="height:{h}px">{body}{ft}</div></body></html>')


MARK = '<div class=mark dir=ltr>Surf<b>Tribe</b></div>'
L = lambda x: f'<span dir=ltr>{x}</span>'


def wh(f):
    return '%.1f' % f['wave_height_m']


def label(d):
    return f'{DAYS_HE[dt.date.fromisoformat(d).weekday()]} {dt.date.fromisoformat(d):%d.%m}'


def rank(f):
    return (Q.get(f['quality'], ('', '', 0))[2], WIND.get(f['wind_kind'], ('', 0))[1], -abs(f['wave_height_m'] - 1.0))


def build(friday, outdir, api_file=None):
    api = json.loads(Path(api_file).read_text(encoding='utf-8')) if api_file else fetch(friday)
    days = [f for f in api['forecast']][:2]
    pick = max(days, key=rank)
    surfable = Q.get(pick['quality'], ('', '', 0))[2] >= 1
    total = 5
    bg = b64(HERE / 'bg_lines.jpg')
    pages = []
    pages.append(page(
        f'<div style="position:absolute;inset:0;background:url(data:image/jpeg;base64,{bg}) center/cover"></div>'
        '<div style="position:absolute;left:0;right:0;top:640px;bottom:0;background:linear-gradient(180deg,rgba(45,36,42,0),#2D242A 55%)"></div>'
        + MARK + '<div style="position:absolute;left:80px;right:80px;bottom:100px">'
        '<div class=h style="font-size:118px">תחזית לסופ״ש</div>'
        f'<div class=k style="font-size:40px;margin-top:26px">{" · ".join(label(f["date"]) for f in days)}</div>'
        '<div style="font-size:40px;margin-top:18px">מה מחכה בים, ומתי הכי כדאי לצאת</div></div>', 1, total))
    for i, f in enumerate(days):
        qn, qc, _ = Q.get(f['quality'], (f['quality'], FOAM, 0))
        wk = WIND.get(f['wind_kind'], (f['wind_kind'], 0))[0]
        uv = (f'<div style="margin-top:30px;font-size:34px;color:{SUN}">UV {L(f["uv_max"])}: קרם הגנה ולייקרה</div>'
              if f.get('uv_max', 0) >= 6 else '')
        grid = (
            '<div style="display:grid;grid-template-columns:1fr 1fr;column-gap:60px;margin-top:40px">'
            f'<div class=cell><div class=lbl>גלים</div><div class=val>{L(wh(f))} מ׳</div></div>'
            f'<div class=cell><div class=lbl>פריוד</div><div class=val>{L(f["wave_period_s"])} שנ׳</div></div>'
            f'<div class=cell><div class=lbl>רוח</div><div class=val>{L(f["wind_kmh"])} קמ״ש</div><div style="font-size:32px;margin-top:6px">{wk}</div></div>'
            f'<div class=cell><div class=lbl>מים</div><div class=val>{L(str(f["water_temp_c"]) + "°C")}</div></div>'
            '</div>')
        pages.append(page(
            MARK + '<div style="position:absolute;left:80px;right:80px;top:110px;bottom:110px;display:flex;flex-direction:column;justify-content:center">'
            f'<div class=k style="font-size:36px">{label(f["date"])}</div>'
            f'<div class=h style="font-size:230px;color:{qc};margin-top:10px">{qn}</div>'
            f'<div style="font-size:42px;margin-top:10px">הכי טוב בסביבות {L(f["best_window"])}</div>'
            f'{grid}{uv}</div>', i + 2, total))
    if surfable:
        pk = (f'<div class=h style="font-size:150px;color:{CYAN};margin:16px 0 20px">{DAYS_HE[dt.date.fromisoformat(pick["date"]).weekday()]}</div>'
              f'<div style="font-size:44px;line-height:1.35">{L(wh(pick))} מ׳, {WIND.get(pick["wind_kind"], ("", 0))[0]}, '
              f'הכי טוב בסביבות {L(pick["best_window"])}</div>')
    else:
        pk = ('<div class=h style="font-size:110px;color:{0};margin:16px 0 20px">ים שקט</div>'.format(GREY) +
              '<div style="font-size:44px">יום טוב לאימון על הרצפה</div>')
    pages.append(page(
        MARK + '<div style="position:absolute;left:80px;right:80px;top:0;bottom:110px;display:flex;flex-direction:column;justify-content:center">'
        '<div class=k>הבחירה שלנו</div><div class=h style="font-size:84px;margin-top:12px">היום של הסופ״ש</div>'
        f'{pk}<div style="font-size:28px;margin-top:60px;opacity:.6">ממוצע לאורך החוף המרכזי, שעות היום. התחזית משתנה, בדקו שוב בבוקר</div></div>', 4, total))
    pages.append(page(
        MARK + '<div style="position:absolute;left:80px;right:80px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center">'
        '<div class=h style="font-size:92px">שמרו ובדקו שוב בבוקר</div>'
        '<div style="font-size:42px;margin-top:30px;line-height:1.3">תחזית חדשה כל יום חמישי. עקבו כדי לא לפספס</div>'
        '<div style="margin-top:44px"><span style="font-size:32px;font-weight:700;color:#2D242A;background:#00CDFE;padding:16px 28px;border-radius:999px">'
        f'עקבו אחרי {L("@surftribe_il")}</span></div>'
        '<div style="font-size:34px;margin-top:40px;opacity:.85">תחזית לחוף שלכם ולפי הרמה שלכם, שעה אחרי שעה, באפליקציית SurfTribe. הקישור בביו</div></div>', 5, total))
    rows = ''.join(
        f'<div style="margin-top:46px"><div class=k style="font-size:46px">{label(f["date"])}</div>'
        f'<div class=h style="font-size:130px;color:{Q.get(f["quality"], ("", FOAM, 0))[1]};margin-top:6px">{Q.get(f["quality"], (f["quality"], "", 0))[0]}</div>'
        f'<div style="font-size:44px;margin-top:6px">{L(wh(f))} מ׳ · {WIND.get(f["wind_kind"], ("", 0))[0]} · {L(f["best_window"])}</div></div>' for f in days)
    story = page(
        f'<div style="position:absolute;inset:0;background:url(data:image/jpeg;base64,{bg}) center/cover;filter:brightness(.38)"></div>'
        '<div style="position:absolute;left:80px;right:80px;top:280px">'
        '<div class=h style="font-size:140px">תחזית לסופ״ש</div>' + rows +
        '<div style="font-size:54px;font-weight:700;margin-top:90px">כל הפרטים בפוסט האחרון</div>'
        f'<div style="font-size:46px;margin-top:20px">עקבו אחרי {L("@surftribe_il")}</div></div>', 0, 0, h=1920)
    from playwright.sync_api import sync_playwright
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        br = p.chromium.launch()
        for i, html in enumerate(pages, 1):
            pg = br.new_page(viewport={'width': 1080, 'height': 1350}); pg.set_content(html); pg.wait_for_timeout(300)
            pg.screenshot(path=str(out / f'HE_{i}.jpg'), type='jpeg', quality=92); pg.close()
        pg = br.new_page(viewport={'width': 1080, 'height': 1920}); pg.set_content(story); pg.wait_for_timeout(300)
        pg.screenshot(path=str(out / 'story.jpg'), type='jpeg', quality=92); br.close()
    lines = [f'תחזית לסופ״ש: {" ו".join(label(f["date"]) for f in days)}. מה מחכה בים?', '']
    for f in days:
        lines.append(f'{label(f["date"])}: {Q.get(f["quality"], (f["quality"],))[0]}. גלים {f["wave_height_m"]:.1f} מ׳, פריוד {f["wave_period_s"]} שנ׳, '
                     f'{WIND.get(f["wind_kind"], ("",))[0]} {f["wind_kmh"]} קמ״ש, מים {f["water_temp_c"]}°C. הכי טוב בסביבות {f["best_window"]}.')
    if surfable:
        lines += ['', f'הבחירה שלנו: {DAYS_HE[dt.date.fromisoformat(pick["date"]).weekday()]} בבוקר.']
    if any(f.get('uv_max', 0) >= 6 for f in days):
        lines.append('UV גבוה, אל תשכחו קרם הגנה.')
    lines += ['', 'ממוצע לאורך החוף המרכזי. התחזית משתנה, בדקו שוב בבוקר.', '',
              'שמרו את הפוסט ושלחו לחבר שגולש איתכם.', 'עקבו אחרי @surftribe_il לתחזית חדשה כל יום חמישי.',
              'תחזית לחוף שלכם, שעה אחרי שעה, ב-SurfTribe. הקישור בביו.', '', 'התמונה נוצרה ב-AI', '',
              '#גלישה #תחזיתגלים #surfisrael #גלישהבישראל #surftribe_il']
    (out / 'caption.txt').write_text('\n'.join(lines), encoding='utf-8')
    (out / 'data.json').write_text(json.dumps({'days': days, 'pick': pick['date'] if surfable else None}, ensure_ascii=False), encoding='utf-8')


if __name__ == '__main__':
    build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    print('ok')
