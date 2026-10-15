"""SurfTribe weekly weekend forecast (Hebrew) for @surftribe_il.
Usage: python3 make_forecast.py [FRIDAY_YYYY-MM-DD] [OUTDIR]
Fetches Open-Meteo marine + weather (the same source the SurfTribe app uses), renders
a 5-slide carousel (1080x1350) + a story (1080x1920), and writes caption.txt and summary.json.
Needs: requests, playwright (chromium). Assets (Rubik.ttf, bg_lines.jpg) next to this file.
"""
import sys, json, math, base64, datetime as dt
from pathlib import Path
import urllib.request

HERE = Path(__file__).resolve().parent
TZ = 'Asia/Jerusalem'
SPOTS = [  # name, lat, lon (slightly offshore so the marine grid has data)
    ('נתניה', 32.33, 34.83),
    ('הרצליה', 32.17, 34.78),
    ('תל אביב', 32.09, 34.75),
    ('בת ים', 32.02, 34.72),
    ('אשקלון', 31.68, 34.53),
]
HOURS = range(6, 12)   # morning session 06:00-11:00
CYAN, CORAL, GREEN, FOAM, GREY = '#00CDFE', '#FF5150', '#68C090', '#F5F1F7', '#9A8F98'
DAYS_HE = ['שני', 'שלישי', 'רביעי', 'חמישי', 'שישי', 'שבת', 'ראשון']


def get(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read().decode())


def fetch(lat, lon, d0, d1):
    m = get(f'https://marine-api.open-meteo.com/v1/marine?latitude={lat}&longitude={lon}'
            f'&hourly=wave_height,wave_period,sea_surface_temperature&timezone={TZ}&start_date={d0}&end_date={d1}')
    w = get(f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}'
            f'&hourly=wind_speed_10m,wind_direction_10m,wind_gusts_10m&wind_speed_unit=kmh&timezone={TZ}&start_date={d0}&end_date={d1}')
    return m['hourly'], w['hourly']


def summarize(m, w, day):
    idx = [i for i, t in enumerate(m['time']) if t.startswith(day) and int(t[11:13]) in HOURS]
    hs = [m['wave_height'][i] for i in idx if m['wave_height'][i] is not None]
    per = [m['wave_period'][i] for i in idx if m['wave_period'][i] is not None]
    sst = [m['sea_surface_temperature'][i] for i in idx if m['sea_surface_temperature'][i] is not None]
    widx = [i for i, t in enumerate(w['time']) if t.startswith(day) and int(t[11:13]) in HOURS]
    ws = [w['wind_speed_10m'][i] for i in widx]
    wd = [w['wind_direction_10m'][i] for i in widx]
    gu = [w['wind_gusts_10m'][i] for i in widx]
    sx = sum(math.sin(math.radians(a)) for a in wd); cx = sum(math.cos(math.radians(a)) for a in wd)
    wdir = (math.degrees(math.atan2(sx, cx)) + 360) % 360
    r = dict(hs_min=min(hs), hs_max=max(hs), hs_mean=sum(hs) / len(hs), per=sum(per) / len(per),
             wind=sum(ws) / len(ws), gust=max(gu), wdir=wdir, sst=(sum(sst) / len(sst)) if sst else None)
    # Israeli coast faces west: wind from the east is offshore
    if 45 <= wdir <= 135: r['wtype'] = 'אופשור'
    elif 225 <= wdir <= 315: r['wtype'] = 'אונשור'
    else: r['wtype'] = 'רוח צד'
    if r['hs_max'] < 0.35:
        r['label'], r['col'] = 'פלאט', GREY
    elif r['wind'] >= 30 or r['hs_max'] > 2.0:
        r['label'], r['col'] = 'סוער', CORAL
    elif r['hs_max'] <= 1.0 and r['wind'] < 20:
        r['label'], r['col'] = 'למתחילים', GREEN
    else:
        r['label'], r['col'] = 'למתקדמים', CYAN
    ok = r['label'] in ('למתחילים', 'למתקדמים')
    r['score'] = (-abs(r['hs_mean'] - 0.9) - r['wind'] / 40 + (0.3 if r['wtype'] == 'אופשור' else 0)
                  - (0.3 if r['wtype'] == 'אונשור' else 0)) if ok else -99
    return r


def fmt_h(a, b):
    a, b = round(a, 1), round(b, 1)
    return f'{a:.1f}' if a == b else f'{a:.1f}-{b:.1f}'


def b64(p):
    return base64.b64encode(Path(p).read_bytes()).decode()


CSS = None
def css():
    global CSS
    if CSS is None:
        CSS = (f"@font-face{{font-family:Rubik;src:url(data:font/ttf;base64,{b64(HERE / 'Rubik.ttf')})}}"
               "*{margin:0;padding:0;box-sizing:border-box}"
               f"body{{width:1080px;height:1350px;background:#2D242A;font-family:Rubik;color:{FOAM}}}"
               ".s{position:relative;width:1080px;height:1350px;overflow:hidden;background:linear-gradient(180deg,#2D242A,#3A2331)}"
               f".k{{font-size:30px;font-weight:700;color:{CYAN};letter-spacing:.5px}}"
               ".h{font-weight:900;line-height:1.02;letter-spacing:-1px}"
               ".mark{position:absolute;top:44px;right:80px;font-weight:800;font-size:32px}.mark b{color:#00CDFE}")
    return CSS


def page(body, idx, total, h=1350):
    ft = (f'<div dir=ltr style="position:absolute;left:44px;bottom:30px;font:500 23px Rubik;opacity:.82">'
          f'{idx}/{total}&nbsp;&nbsp;·&nbsp;&nbsp;@surftribe_il</div>') if idx else ''
    return (f'<!doctype html><html><head><meta charset=utf-8><style>{css()}</style></head><body style="height:{h}px">'
            f'<div class=s dir=rtl lang=he style="height:{h}px">{body}{ft}</div></body></html>')


def mark():
    return '<div class=mark dir=ltr>Surf<b>Tribe</b></div>'


def build(friday, outdir, from_summary=None):
    fri = dt.date.fromisoformat(friday); sat = fri + dt.timedelta(days=1)
    days = [fri.isoformat(), sat.isoformat()]
    data = {}
    if from_summary:
        data = json.loads(Path(from_summary).read_text(encoding='utf-8'))['spots']
    else:
        for name, lat, lon in SPOTS:
            m, w = fetch(lat, lon, days[0], days[1])
            data[name] = {d: summarize(m, w, d) for d in days}
    dlabel = {d: f'{DAYS_HE[dt.date.fromisoformat(d).weekday()]} {dt.date.fromisoformat(d):%d.%m}' for d in days}
    best = {d: max(SPOTS, key=lambda s: data[s[0]][d]['score'])[0] for d in days}
    best = {d: (b if data[b][d]['score'] > -99 else None) for d, b in best.items()}
    ssts = [data[s[0]][d]['sst'] for s in SPOTS for d in days if data[s[0]][d]['sst']]
    sst = round(sum(ssts) / len(ssts)) if ssts else None
    total = 5
    bg = b64(HERE / 'bg_lines.jpg')
    pages = []
    # 1 cover
    pages.append(page(
        f'<div style="position:absolute;inset:0;background:url(data:image/jpeg;base64,{bg}) center/cover"></div>'
        '<div style="position:absolute;left:0;right:0;top:640px;bottom:0;background:linear-gradient(180deg,rgba(45,36,42,0),#2D242A 55%)"></div>'
        + mark() +
        '<div style="position:absolute;left:80px;right:80px;bottom:100px">'
        '<div class=h style="font-size:118px">תחזית לסופ״ש</div>'
        f'<div class=k style="font-size:40px;margin-top:26px">{dlabel[days[0]]} · {dlabel[days[1]]}</div>'
        '<div style="font-size:40px;margin-top:18px">איפה גולשים בבוקר, חוף אחרי חוף</div></div>', 1, total))
    # 2-3 day tables
    for n, d in enumerate(days):
        rows = ''
        for name, _, _ in SPOTS:
            r = data[name][d]
            rows += ('<div style="padding:36px 0;border-top:2px solid rgba(245,241,247,.14)">'
                     '<div style="display:flex;justify-content:space-between;align-items:center">'
                     f'<div class=h style="font-size:58px">{name}</div>'
                     f'<div style="font-size:30px;font-weight:700;color:#2D242A;background:{r["col"]};padding:10px 22px;border-radius:999px">{r["label"]}</div></div>'
                     f'<div style="font-size:37px;margin-top:14px;opacity:.92">גלים <span dir=ltr>{fmt_h(r["hs_min"], r["hs_max"])}</span> מ׳ · '
                     f'פריוד <span dir=ltr>{round(r["per"])}</span> שנ׳ · רוח <span dir=ltr>{round(r["wind"])}</span> קמ״ש, {r["wtype"]}</div></div>')
        pages.append(page(
            mark() + '<div style="position:absolute;left:80px;right:80px;top:120px">'
            f'<div class=k>{dlabel[d]} · בוקר <span dir=ltr>06:00-11:00</span></div>'
            f'<div class=h style="font-size:80px;margin:12px 0 30px">{"שישי" if n == 0 else "שבת"} בים</div>'
            f'{rows}<div style="border-top:2px solid rgba(245,241,247,.14)"></div></div>', n + 2, total))
    # 4 best picks
    picks = ''
    for d in days:
        b = best[d]
        if b:
            r = data[b][d]
            why = f'<span dir=ltr>{fmt_h(r["hs_min"], r["hs_max"])}</span> מ׳, {r["wtype"]}, {r["label"]}'
        else:
            b, why = 'אין חוף מומלץ', 'ים שטוח או סוער. יום טוב לאימון על הרצפה'
        picks += (f'<div style="padding:40px 0;border-top:2px solid rgba(245,241,247,.14)">'
                  f'<div class=k>{dlabel[d]}</div>'
                  f'<div class=h style="font-size:96px;margin:10px 0 14px;color:{CYAN}">{b}</div>'
                  f'<div style="font-size:38px">{why}</div></div>')
    sst_line = f'<div style="font-size:36px;margin-top:40px">טמפרטורת מים: <span dir=ltr>{sst}°C</span></div>' if sst else ''
    pages.append(page(
        mark() + '<div style="position:absolute;left:80px;right:80px;top:140px">'
        '<div class=k>הבחירה שלנו</div><div class=h style="font-size:84px;margin:12px 0 30px">לאן הולכים</div>'
        f'{picks}<div style="border-top:2px solid rgba(245,241,247,.14)"></div>{sst_line}'
        '<div style="font-size:26px;margin-top:40px;opacity:.6">נתונים: Open-Meteo. התחזית משתנה, בדקו שוב לפני שיוצאים</div></div>', 4, total))
    # 5 CTA
    pages.append(page(
        mark() + '<div style="position:absolute;left:80px;right:80px;top:0;bottom:0;display:flex;flex-direction:column;justify-content:center">'
        '<div class=h style="font-size:92px">שמרו ובדקו שוב בבוקר</div>'
        '<div style="font-size:42px;margin-top:30px;line-height:1.3">תחזית חדשה כל יום חמישי. עקבו כדי לא לפספס</div>'
        '<div style="margin-top:44px"><span style="font-size:32px;font-weight:700;color:#2D242A;background:#00CDFE;padding:16px 28px;border-radius:999px">'
        'עקבו אחרי <span dir=ltr>@surftribe_il</span></span></div>'
        '<div style="font-size:34px;margin-top:40px;opacity:.85">תחזית לפי הרמה שלכם, שעה אחרי שעה, באפליקציית SurfTribe. הקישור בביו</div></div>', 5, total))
    # story
    sp = ''.join(f'<div style="margin-top:50px"><div class=k style="font-size:46px">{dlabel[d]}</div>'
                 f'<div class=h style="font-size:130px;color:{CYAN};margin-top:8px">{best[d] or "ים שקט"}</div></div>' for d in days)
    story = page(
        f'<div style="position:absolute;inset:0;background:url(data:image/jpeg;base64,{bg}) center/cover;filter:brightness(.4)"></div>'
        '<div style="position:absolute;left:80px;right:80px;top:300px">'
        '<div class=h style="font-size:140px">תחזית לסופ״ש</div>'
        f'<div style="font-size:52px;margin-top:24px">הבחירה שלנו לבוקר:</div>{sp}'
        '<div style="font-size:54px;font-weight:700;margin-top:100px">התחזית המלאה בפוסט האחרון</div>'
        '<div style="font-size:46px;margin-top:20px">עקבו אחרי <span dir=ltr>@surftribe_il</span></div></div>', 0, 0, h=1920)
    # render
    from playwright.sync_api import sync_playwright
    out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    files = []
    with sync_playwright() as p:
        br = p.chromium.launch()
        for i, html in enumerate(pages, 1):
            pg = br.new_page(viewport={'width': 1080, 'height': 1350}); pg.set_content(html); pg.wait_for_timeout(300)
            f = out / f'HE_{i}.jpg'; pg.screenshot(path=str(f), type='jpeg', quality=92); files.append(str(f)); pg.close()
        pg = br.new_page(viewport={'width': 1080, 'height': 1920}); pg.set_content(story); pg.wait_for_timeout(300)
        pg.screenshot(path=str(out / 'story.jpg'), type='jpeg', quality=92); br.close()
    # caption
    lines = [f'תחזית לסופ״ש, {dlabel[days[0]]} ו{dlabel[days[1]]}. איפה גולשים בבוקר?', '']
    for d in days:
        b = best[d]
        if b:
            r = data[b][d]
            lines.append(f'{dlabel[d]}: {b}. גלים {fmt_h(r["hs_min"], r["hs_max"])} מ׳, פריוד {round(r["per"])} שנ׳, {r["wtype"]}.')
        else:
            lines.append(f'{dlabel[d]}: ים שטוח או סוער. יום טוב לאימון על הרצפה.')
    if sst: lines.append(f'טמפרטורת מים: {sst}°C.')
    lines += ['', 'כל החופים בשקופיות. נתונים: Open-Meteo, התחזית משתנה, בדקו שוב בבוקר.', '',
              'שמרו את הפוסט ושלחו לחבר שגולש איתכם.', 'עקבו אחרי @surftribe_il לתחזית חדשה כל יום חמישי.',
              'תחזית לפי הרמה שלכם, שעה אחרי שעה, ב-SurfTribe. הקישור בביו.', '', 'התמונה נוצרה ב-AI', '',
              '#גלישה #תחזיתגלים #surfisrael #גלישהבישראל #surftribe_il']
    (out / 'caption.txt').write_text('\n'.join(lines), encoding='utf-8')
    summary = {'friday': days[0], 'best': best, 'sst': sst,
               'spots': {n: {d: {k: (round(v, 2) if isinstance(v, float) else v) for k, v in data[n][d].items()} for d in days} for n, _, _ in SPOTS}}
    (out / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding='utf-8')
    return files + [str(out / 'story.jpg')]


if __name__ == '__main__':
    today = dt.date.today()
    fri = today + dt.timedelta(days=(4 - today.weekday()) % 7)
    friday = sys.argv[1] if len(sys.argv) > 1 else fri.isoformat()
    outdir = sys.argv[2] if len(sys.argv) > 2 else str(HERE / 'out' / friday)
    print(json.dumps(build(friday, outdir, sys.argv[3] if len(sys.argv) > 3 else None)))
