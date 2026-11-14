#!/usr/bin/env python3
"""Teaser story (1080x1920) for a HE carousel: blurred cover, pill with the post time, cover card, follow line.

Usage: python3 make_teaser.py p17 [p18 ...]
Output: volunteer/stories/he_teaser_1900/HE_<post>.jpg
"""
import base64
import os
import subprocess
import sys
import tempfile

import generate_carousel as g

OUT_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'stories', 'he_teaser_1900')
POST_TIME = '19:00'


def teaser_html(img_b64, kicker, title):
    return g.CSS_HEAD.replace('1350px', '1920px') + f'''<body style="margin:0;width:1080px;height:1920px;overflow:hidden;background:#141014;position:relative">
<img src="data:image/jpeg;base64,{img_b64}" style="position:absolute;inset:-60px;width:1200px;height:2040px;object-fit:cover;filter:blur(40px) brightness(.45)">
<div style="position:absolute;left:0;right:0;bottom:0;height:700px;background:linear-gradient(to bottom,rgba(20,16,20,0),rgba(20,16,20,.95))"></div>
<div style="position:absolute;top:250px;left:0;right:0;text-align:center">
 <span dir="rtl" style="display:inline-block;background:#00CDFE;color:#141014;font-family:Rubik,sans-serif;font-weight:700;font-size:38px;padding:16px 34px;border-radius:40px">פוסט חדש היום &bull; <bdi dir="ltr">{POST_TIME}</bdi></span></div>
<div style="position:absolute;left:100px;top:380px;width:880px;height:1050px;border-radius:28px;overflow:hidden;box-shadow:0 30px 80px rgba(0,0,0,.6);background:#2D242A;display:flex;flex-direction:column">
 <div style="position:relative;flex:1;min-height:0">
  <img src="data:image/jpeg;base64,{img_b64}" style="position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:60% 40%">
  <div style="position:absolute;left:0;right:0;bottom:0;height:160px;background:linear-gradient(to bottom,rgba(45,36,42,0),#2D242A)"></div>
  <div style="position:absolute;right:48px;top:40px;filter:drop-shadow(0 2px 3px rgba(45,36,42,.85)) drop-shadow(0 6px 16px rgba(45,36,42,.6))">{g.logo_html('HE')}</div>
  <div style="position:absolute;left:24px;top:22px;font-family:Rubik,sans-serif;font-size:18px;color:rgba(255,255,255,.75);text-shadow:0 1px 4px rgba(0,0,0,.9)" dir="rtl">התמונה נוצרה ב-AI</div>
 </div>
 <div dir="rtl" style="padding:10px 64px 64px;text-align:right">
  <div style="font-family:Rubik,sans-serif;font-weight:700;font-size:44px;color:#00CDFE;margin-bottom:14px;text-wrap:balance">{kicker}</div>
  <div style="font-family:Rubik,sans-serif;font-weight:800;font-size:96px;line-height:1.05;color:#fff;text-wrap:balance">{title}</div>
 </div></div>
<div dir="rtl" style="position:absolute;top:1500px;left:80px;right:80px;text-align:center;font-family:Rubik,sans-serif;font-weight:500;font-size:44px;color:#F5F1F7">עקבו אחרי <bdi dir="ltr">@surftribe_il</bdi> כדי לא לפספס</div>
</body></html>'''


def make(post_id):
    post = g.POSTS[post_id]
    kicker, title = post['HE']['cover']
    with open(post['images']['cover'], 'rb') as f:
        img_b64 = base64.b64encode(f.read()).decode()
    with tempfile.TemporaryDirectory() as tmp:
        html_path = os.path.join(tmp, 'teaser.html')
        png_path = os.path.join(tmp, 'teaser.png')
        with open(html_path, 'w') as f:
            f.write(teaser_html(img_b64, kicker, title))
        subprocess.run(['/usr/bin/google-chrome', '--headless=new', '--disable-gpu', '--hide-scrollbars',
                        '--window-size=1080,1920', f'--screenshot={png_path}', f'file://{html_path}'],
                       capture_output=True, timeout=90, check=True)
        out = os.path.abspath(os.path.join(OUT_DIR, f'HE_{post_id}.jpg'))
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', png_path, '-q:v', '2', out], check=True)
    print(out)


if __name__ == '__main__':
    for p in sys.argv[1:]:
        make(p)
