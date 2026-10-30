#!/usr/bin/env python3
"""
SurfTribe Carousel Generator
Editorial standard: 1080x1350, #2D242A plum background, #00CDFE cyan accents, Rubik 800 headlines, body text >= 44 px, margins >= 80 px.
Renders Hebrew (HE) slides for p15, p16, p17 using Headless Chrome.
"""

import os
import sys
import glob
import base64
import subprocess
from PIL import Image

FONTS_DIR = '/home/dmitrii-nikonov/.local/share/fonts'
TOOLS_DIR = '/home/dmitrii-nikonov/volunteer/tools/carousel'
BRAIN_DIR = '/home/dmitrii-nikonov/.gemini/antigravity-ide/brain/b0680885-c0e9-4547-921a-0c33c890d476'
VOLUNTEER_DIR = '/home/dmitrii-nikonov/volunteer'
ASSETS_DIR = os.path.join(VOLUNTEER_DIR, 'assets', 'carousel')
ZIMAGE_GENERATOR = "All photos generated using Z-Image Turbo via Hugging Face (mcp-tools/Z-Image-Turbo)."

def b64_file(p):
    with open(p, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')

# Fonts
RUBIK_REG = b64_file(os.path.join(FONTS_DIR, 'Rubik-Regular.ttf'))
RUBIK_MED = b64_file(os.path.join(FONTS_DIR, 'Rubik-Medium.ttf'))
RUBIK_BOLD = b64_file(os.path.join(FONTS_DIR, 'Rubik-Bold.ttf'))
RUBIK_XBOLD = b64_file(os.path.join(FONTS_DIR, 'RubikExtraBold.ttf'))

CSS_HEAD = f"""<meta charset="utf-8">
<style>
@font-face {{ font-family: 'Rubik'; src: url(data:font/ttf;base64,{RUBIK_REG}); font-weight: 400; }}
@font-face {{ font-family: 'Rubik'; src: url(data:font/ttf;base64,{RUBIK_MED}); font-weight: 500; }}
@font-face {{ font-family: 'Rubik'; src: url(data:font/ttf;base64,{RUBIK_BOLD}); font-weight: 700; }}
@font-face {{ font-family: 'Rubik'; src: url(data:font/ttf;base64,{RUBIK_XBOLD}); font-weight: 800; }}

* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 1080px;
  height: 1350px;
  background: #2D242A;
  color: #F5F1F7;
  font-family: 'Rubik', sans-serif;
  overflow: hidden;
  position: relative;
}}
</style>
"""

def logo_html(lang='HE'):
    return """<div style="font-family: 'Rubik', sans-serif; font-size: 38px; font-weight: 800; line-height: 1; letter-spacing: -0.5px;">
        <span style="color: #F5F1F7;">Surf</span><span style="color: #00CDFE;">Tribe</span>
    </div>"""

def footer_html(lang, slide_num, total_slides, in_panel=False):
    rtl = (lang == 'HE')
    if in_panel:
        return f"""<div style="font-family: 'Rubik', sans-serif; font-size: 24px; font-weight: 500; color: rgba(245, 241, 247, 0.6); direction: rtl; text-align: right;">
            {slide_num}/{total_slides} &bull; &rlm;<bdi dir='ltr'>@surftribe_il</bdi>
        </div>"""
    else:
        return f"""<div style="position: absolute; left: 80px; bottom: 44px; font-family: 'Rubik', sans-serif; font-size: 26px; font-weight: 500; color: rgba(245, 241, 247, 0.6); direction: rtl; text-align: left; z-index: 20;">
            {slide_num}/{total_slides} &bull; &rlm;<bdi dir='ltr'>@surftribe_il</bdi>
        </div>"""

def ai_tag_html(lang='HE', on_right=False, pos=None):
    if pos is None:
        pos = "right: 32px; bottom: 32px;" if on_right else "left: 32px; bottom: 32px;"
    text = "התמונה נוצרה ב-AI"
    return f"""<div style="position: absolute; {pos} font-family: 'Rubik', sans-serif; font-size: 20px; font-weight: 400; color: rgba(255, 255, 255, 0.65); text-shadow: 0 1px 4px rgba(0,0,0,0.9); direction: rtl; pointer-events: none; z-index: 15;">
        {text}
    </div>"""

def render_cover(img_b64, lang, kicker, title, slide_num=1, total_slides=8, balance=False):
    tw = "text-wrap: balance;"
    # balance posts (p20+): AI label on the photo, top-left, so it never collides with the footer
    cover_ai_pos = "left: 32px; top: 32px;"
    rtl = (lang == 'HE')
    logo_pos = "right: 80px; top: 60px;" if rtl else "left: 80px; top: 60px;"
    # Kicker strictly in Rubik 700, font-size 44px (>= 44px)
    kicker_style = "font-family: 'Rubik', sans-serif; font-size: 44px; font-weight: 700;"
    
    return CSS_HEAD + f"""<body>
        <img src="data:image/jpeg;base64,{img_b64}" style="position: absolute; left: 0; top: 0; width: 1080px; height: 1350px; object-fit: cover;">
        <div style="position: absolute; left: 0; right: 0; top: 700px; height: 270px; background: linear-gradient(to bottom, rgba(45,36,42,0) 0%, rgba(45,36,42,0.95) 100%);"></div>
        <div style="position: absolute; left: 0; right: 0; top: 970px; bottom: 0; background: #2D242A;"></div>
        
        <div style="position: absolute; {logo_pos} z-index: 10; filter: drop-shadow(0 2px 3px rgba(45,36,42,0.85)) drop-shadow(0 6px 16px rgba(45,36,42,0.6));">
            {logo_html(lang)}
        </div>
        
        <div style="position: absolute; left: 80px; right: 80px; bottom: 104px; direction: rtl; text-align: right; z-index: 10;">
            <div style="{kicker_style} color: #00CDFE; line-height: 1.15; margin-bottom: 20px;">
                {kicker}
            </div>
            <div style="font-family: 'Rubik', sans-serif; font-weight: 800; font-size: 78px; line-height: 1.05; color: #FFFFFF; {tw}">
                {title}
            </div>
        </div>
        
        {footer_html(lang, slide_num, total_slides)}
        {ai_tag_html(lang, pos=cover_ai_pos)}
    </body>"""

def render_stake(img_b64, lang, stake_text, slide_num=2, total_slides=8, balance=False):
    tw = "text-wrap: balance;"
    # Fix 4: Panel expanded to 510px, photo 570px (1080px total)
    # 29.10: 80px margins on both sides of the text (was 40/60, text stuck to the photo)
    photo_pos = "left: 0; width: 500px;"
    panel_pos = "left: 500px; width: 580px;"
    padding = "70px 80px 50px 80px"
    
    return CSS_HEAD + f"""<body>
        <div style="position: absolute; {photo_pos} top: 0; height: 1350px; overflow: hidden;">
            <img src="data:image/jpeg;base64,{img_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            {ai_tag_html(lang, on_right=False)}
        </div>
        
        <div style="position: absolute; {panel_pos} top: 0; height: 1350px; background: #2D242A; padding: {padding}; display: flex; flex-direction: column; justify-content: space-between; direction: rtl; text-align: right; z-index: 10;">
            <div>
                {logo_html(lang)}
            </div>
            
            <div style="margin-top: -60px;">
                <div style="width: 56px; height: 6px; background: #00CDFE; border-radius: 3px; margin-bottom: 36px; display: inline-block;"></div>
                <div style="font-family: 'Rubik', sans-serif; font-weight: 800; font-size: 50px; line-height: 1.22; color: #FFFFFF; {tw}">
                    {stake_text}
                </div>
            </div>
            
            <div>
                {footer_html(lang, slide_num, total_slides, in_panel=True)}
            </div>
        </div>
    </body>"""

def render_idea(img_b64, lang, num_str, title, body, slide_num, total_slides=8, balance=False):
    # balance=True (opt-in, p20+): no orphan last word in title/body
    tw_title = "text-wrap: balance;"
    tw_body = "text-wrap: pretty;"
    # Fix 4: Panel expanded to 510px, photo 570px (1080px total)
    # 29.10: 80px margins on both sides of the text (was 40/60, text stuck to the photo)
    photo_pos = "left: 0; width: 500px;"
    panel_pos = "left: 500px; width: 580px;"
    padding = "70px 80px 50px 80px"
        
    return CSS_HEAD + f"""<body>
        <div style="position: absolute; {photo_pos} top: 0; height: 1350px; overflow: hidden;">
            <img src="data:image/jpeg;base64,{img_b64}" style="width: 100%; height: 100%; object-fit: cover;">
            {ai_tag_html(lang, on_right=False)}
        </div>
        
        <div style="position: absolute; {panel_pos} top: 0; height: 1350px; background: #2D242A; padding: {padding}; display: flex; flex-direction: column; justify-content: space-between; direction: rtl; text-align: right; z-index: 10;">
            <div>
                {logo_html(lang)}
            </div>
            
            <div style="margin-top: -30px;">
                <div style="font-family: 'Rubik', sans-serif; font-size: 106px; font-weight: 800; color: #00CDFE; line-height: 0.9; margin-bottom: 24px;">
                    {num_str}
                </div>
                <div style="font-family: 'Rubik', sans-serif; font-size: 46px; font-weight: 800; color: #FFFFFF; line-height: 1.15; margin-bottom: 24px; {tw_title}">
                    {title}
                </div>
                <div style="font-family: 'Rubik', sans-serif; font-size: 44px; font-weight: 400; color: rgba(245, 241, 247, 0.92); line-height: 1.28; {tw_body}">
                    {body}
                </div>
            </div>
            
            <div>
                {footer_html(lang, slide_num, total_slides, in_panel=True)}
            </div>
        </div>
    </body>"""

def render_recap(lang, header_title, bullets, slide_num, total_slides, balance=False):
    tw = "text-wrap: pretty;" if balance else ""
    bullet_cards = []
    for b in bullets:
        border_side = "border-right: 6px solid #00CDFE;"
        card = f"""<div style="background: rgba(255, 255, 255, 0.045); border-radius: 20px; {border_side} padding: 34px 40px; margin-bottom: 24px; direction: rtl; text-align: right;">
            <div style="font-family: 'Rubik', sans-serif; font-size: 46px; font-weight: 500; color: #F5F1F7; line-height: 1.32; {tw}">
                {b}
            </div>
        </div>"""
        bullet_cards.append(card)
        
    cards_html = "\n".join(bullet_cards)
    
    return CSS_HEAD + f"""<body>
        <div style="width: 1080px; height: 1350px; background: #2D242A; padding: 70px 80px 50px 80px; display: flex; flex-direction: column; justify-content: space-between; position: relative;">
            <div>
                <div style="text-align: right;">
                    {logo_html(lang)}
                </div>
                <div style="font-family: 'Rubik', sans-serif; font-size: 84px; font-weight: 800; color: #00CDFE; margin-top: 40px; margin-bottom: 40px; direction: rtl; text-align: right;">
                    {header_title}
                </div>
            </div>
            
            <div style="margin-top: -20px;">
                {cards_html}
            </div>
            
            <div>
                {footer_html(lang, slide_num, total_slides)}
            </div>
        </div>
    </body>"""

def render_final(img_b64, lang, save_text, tomorrow_text, slide_num, total_slides, balance=False):
    tw = "text-wrap: balance;"
    pill_content = "עקבו אחרי &rlm;<bdi dir='ltr'>@surftribe_il</bdi>"
    if tomorrow_text:
        tomorrow_html = f"""<div style="font-family: 'Rubik', sans-serif; font-size: 46px; font-weight: 500; color: #00CDFE; line-height: 1.25; margin-bottom: 44px;">
                        {tomorrow_text}
                    </div>"""
    else:
        # No tomorrow topic yet: skip the line, keep the gap before the pill
        tomorrow_html = """<div style="height: 22px;"></div>"""

    return CSS_HEAD + f"""<body>
        <div style="width: 1080px; height: 1350px; background: #2D242A; padding: 60px 80px 44px 80px; display: flex; flex-direction: column; justify-content: space-between; position: relative;">
            <div>
                <div style="width: 920px; height: 460px; border-radius: 28px; overflow: hidden; position: relative; box-shadow: 0 16px 40px rgba(0,0,0,0.45);">
                    <img src="data:image/jpeg;base64,{img_b64}" style="width: 100%; height: 100%; object-fit: cover;">
                    {ai_tag_html(lang, on_right=False)}
                </div>
                
                <div style="direction: rtl; text-align: right; margin-top: 40px;">
                    <div style="font-family: 'Rubik', sans-serif; font-size: 64px; font-weight: 800; color: #FFFFFF; line-height: 1.15; margin-bottom: 22px; {tw}">
                        {save_text}
                    </div>
                    {tomorrow_html}

                    <div style="display: inline-block;">
                        <div style="background: #00CDFE; color: #16101A; font-family: 'Rubik', sans-serif; font-size: 40px; font-weight: 800; padding: 20px 48px; border-radius: 46px; display: inline-flex; align-items: center; justify-content: center; box-shadow: 0 10px 28px rgba(22, 16, 26, 0.45);">
                            {pill_content}
                        </div>
                        <div style="font-family: 'Rubik', sans-serif; font-size: 28px; font-weight: 600; color: rgba(245, 241, 247, 0.6); margin-top: 14px; text-align: inherit;">
                            SurfTribe
                        </div>
                    </div>
                </div>
            </div>
            
            <div>
                {footer_html(lang, slide_num, total_slides)}
            </div>
        </div>
    </body>"""

def chrome_render(html_str, out_path):
    tmp_dir = os.environ.get('CAROUSEL_TMP', '/tmp')  # override when /tmp is full
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_html = os.path.join(tmp_dir, f"render_{os.path.basename(out_path)}.html")
    tmp_png = os.path.join(tmp_dir, f"render_{os.path.basename(out_path)}.png")
    with open(tmp_html, 'w', encoding='utf-8') as f:
        f.write(html_str)
    subprocess.run([
        '/usr/bin/google-chrome',
        '--headless=new',
        '--no-sandbox',
        '--disable-gpu',
        '--hide-scrollbars',
        '--window-size=1080,1350',
        f'--screenshot={tmp_png}',
        tmp_html
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Save as high-quality JPEG
    im = Image.open(tmp_png).convert('RGB')
    im.save(out_path, 'JPEG', quality=95)
    os.remove(tmp_html)
    os.remove(tmp_png)

POSTS = {
    'p15': {
        'total_slides': 8,
        'images': {
            'cover': os.path.join(BRAIN_DIR, 'p15_cover_surf_1793135784228.jpg'),
            'stake': os.path.join(BRAIN_DIR, 'p15_stake_wave_1793135812194.jpg'),
            '01': os.path.join(BRAIN_DIR, 'p15_s01_leash_1793135847143.jpg'),
            '02': os.path.join(BRAIN_DIR, 'p15_s02_female_paddler_1793172584480.jpg'),
            '03': os.path.join(BRAIN_DIR, 'p15_s03_holdrails_1793135911529.jpg'),
            '04': os.path.join(BRAIN_DIR, 'p15_s04_armshead_surfer_1793172607725.jpg'),
            'final': os.path.join(BRAIN_DIR, 'p15_final_card_1793166339746.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic surf photograph of an adult surfer holding a foam surfboard in ocean whitewater, misty morning light, authentic documentary surf photo, no logos, 8k quality',
            'Slide 2 (Stake)': 'Photorealistic vertical surf photo of an adult male surfer in his late 20s tumbling into ocean water with rough waves and spray, dynamic motion, dramatic coastal lighting, no logos on board or wetsuit, documentary surf photo, 8k quality',
            'Slide 3 (Idea 01)': 'Photorealistic vertical surf action photo of a surfboard flying in ocean whitewater and wave crest, the leash stretched tight pulling back toward the water, authentic dynamic sea spray, no logos on board, no recognizable faces, 8k quality',
            'Slide 4 (Idea 02)': 'Photorealistic vertical surf photo of an adult female surfer in her late 20s paddling on a surfboard in ocean water, looking over her shoulder with an alert expression, authentic ocean spray, morning lighting, no logos on wetsuit or board, documentary surf photography, 8k quality',
            'Slide 5 (Idea 03)': 'Photorealistic vertical surf photo of an adult female surfer lying flat on a surfboard gripping the rails tightly as foamy whitewater washes over the deck, calm composed body position, ocean spray, natural morning sunlight, no logos on board, documentary surf photo, 8k quality',
            'Slide 6 (Idea 04)': 'Photorealistic vertical surf photo of an adult male surfer in his late 30s surfacing in choppy ocean whitewater, hands and forearms raised defensively covering his head from floating boards, authentic ocean lighting, documentary surf photo, no logos on wetsuit, 8k quality',
            'Slide 8 (Final)': 'Photorealistic horizontal surf photograph of adult surfers in wetsuits standing on the beach edge watching ocean waves roll in, gentle morning overcast coastal lighting, authentic documentary surf photography, no logos on wetsuits or boards, 8k quality'
        },
        'HE': {
            'cover': ('גל מגיע ואתם עוזבים את הגלשן?', 'הגלשן חוזר. ישר אליכם'),
            'stake': 'מכה מגלשן כואבת יותר מכל גל',
            'ideas': [
                ('01', 'הליש מושך אותו בחזרה', 'הגל זורק את הגלשן, והליש מחזיר אותו לכיוון הראש שלכם'),
                ('02', 'מי שמאחוריכם חוטף', 'גלשן שעף עם הגל פוגע במי שחותר מאחוריכם'),
                ('03', 'קצף? מחזיקים חזק', 'שוכבים על הגלשן, אוחזים בשני הצדדים ונותנים לקצף לעבור מעליכם'),
                ('04', 'אין ברירה? מסתכלים אחורה', 'בודקים שאין אף אחד מאחור, ועולים מהמים עם ידיים מעל הראש'),
            ],
            'recap': ('בקצרה', [
                'בקצף: שוכבים, מחזיקים חזק בצדדים, נותנים לגל לעבור',
                'אין ברירה ועוזבים: קודם מסתכלים שאין אף אחד מאחור',
                'עולים מהמים עם ידיים מעל הראש'
            ]),
            'final': ('שמרו לפני הסשן הבא', 'מחר: גופי או רגולר?'),
        }
    },
    'p16': {
        'total_slides': 7,
        'balance': True,
        'images': {
            'cover': os.path.join(BRAIN_DIR, 'p16_cover_stance_1793172634891.jpg'),
            'stake': os.path.join(BRAIN_DIR, 'p16_stake_offbalance_1793172660599.jpg'),
            '01': os.path.join(BRAIN_DIR, 'p16_s01_regular_zimage.jpg'),
            '02': os.path.join(BRAIN_DIR, 'p16_s02_goofy_zimage.jpg'),
            '03': os.path.join(BRAIN_DIR, 'p16_s03_pushtest_zimage.jpg'),
            'final': os.path.join(BRAIN_DIR, 'p16_final_card_1793166368808.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic surf photograph of an adult surfer riding a clean peeling ocean wave with confident athletic stance, crisp ocean water, sunny coastal lighting, authentic documentary surf photography, no logos, 8k quality',
            'Slide 2 (Stake)': 'Photorealistic vertical surf photo of an adult surfer losing balance on a surfboard in ocean whitewater, awkward unbalanced stance, dynamic water spray, natural lighting, no logos on board or wetsuit, documentary surf photo, 8k quality',
            'Slide 3 (Idea 01)': 'Photorealistic vertical surf photo looking down at a plain unbranded surfboard deck. Regular stance with left foot forward near middle and right foot back on traction pad, natural sunlight, wax texture, clear water, no logos, no text, 8k quality',
            'Slide 4 (Idea 02)': 'Photorealistic vertical surf photo looking down at a plain unbranded surfboard deck. Goofy stance with right foot forward near middle and left foot back on traction pad, natural sunlight, wax texture, clear water, no logos, no text, 8k quality',
            'Slide 5 (Idea 03)': 'Photorealistic vertical surf photo of two adult friends on a sandy beach, one friend lightly pushes the other from behind to test natural balance and front foot stance, spontaneous beach moment, medium distance, sunny day, no logos, 8k quality',
            'Slide 7 (Final)': 'Photorealistic horizontal surf photograph of adult surfers sitting relaxed on coastal grass dunes overlooking an ocean surf spot, golden hour afternoon light, documentary coastal surf photography, no logos on clothing or boards, 8k quality'
        },
        'HE': {
            'cover': ('איזה רגל אצלכם קדימה?', 'גופי או רגולר'),
            'stake': 'עומדים הפוך מהגוף, וכל גל מרגיש לא נוח',
            'ideas': [
                ('01', 'רגולר', 'רגל שמאל קדימה. ככה עומדים רוב הגולשים'),
                ('02', 'גופי', 'רגל ימין קדימה. פשוט ככה אתם עומדים, וזהו'),
                ('03', 'בדיקה של 10 שניות', 'חבר דוחף אתכם קלות מאחור. הרגל שיוצאת קדימה לבד, היא הרגל הקדמית'),
            ],
            'recap': ('בקצרה', [
                'רגולר: רגל שמאל קדימה',
                'גופי: רגל ימין קדימה',
                'הבדיקה: חבר דוחף קלות מאחור, הרגל שיוצאת ראשונה היא הקדמית'
            ]),
            'final': ('שמרו ונסו עם חבר', 'מחר: למה הגל נראה קטן מהחוף'),
        }
    },
    'p17': {
        'total_slides': 7,
        'images': {
            'cover': os.path.join(BRAIN_DIR, 'p17_cover_distance.jpg'),
            'stake': os.path.join(BRAIN_DIR, 'p17_stake_toponly.jpg'),
            '01': os.path.join(BRAIN_DIR, 'p17_s01_distance_shrink.jpg'),
            '02': os.path.join(BRAIN_DIR, 'p17_s02_nocomparison.jpg'),
            '03': '/home/dmitrii-nikonov/volunteer/assets/carousel/p17/p17_s03_onelash_zimage.jpg',  # 29.10: old frame had a leash on both ankles
            # 29.10: replaced the row of seven near-identical men (p17_final_card.jpg)
            'final': os.path.join(ASSETS_DIR, 'p17', 'p17_final_two_surfers_check_waves.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical surf photo taken from a wide sandy beach looking out toward distant ocean waves breaking far offshore, calm coastal horizon, natural light, no logos, 8k quality',
            'Slide 2 (Stake)': 'Photorealistic vertical surf photo from the sand dunes showing only the white spray and topmost crest of an ocean wave breaking behind the horizon line, scale obscured, sunny natural coastal light, 8k quality',
            'Slide 3 (Idea 01)': 'Photorealistic vertical surf photo of an ocean wave breaking 100 meters out at sea, telephoto perspective compressing distance, making the wave appear smaller than it is, documentary surf photo, 8k quality',
            'Slide 4 (Idea 02)': 'Photorealistic vertical surf photo of an empty clean peeling ocean wave with no surfers on it, clean barrel face, ambiguous scale without reference, natural morning ocean lighting, 8k quality',
            'Slide 5 (Idea 03)': 'Z-Image Turbo seed 301029: Documentary surf photograph, telephoto from the beach: an adult male surfer in a plain black wetsuit standing on a white surfboard riding a small green wave in the Mediterranean, the wave face reaches up to his waist, crouched relaxed stance, side view, a single black leash cord attached only to his back ankle, front ankle bare, natural midday light, realistic anatomy, no logos, no text',
            'Slide 7 (Final, Z-Image Turbo, 29.10)': 'Photorealistic horizontal documentary surf photograph: two clearly different adult surfers standing on a sandy Mediterranean beach checking the waves, seen from behind and slightly to the side. On the left a tall man in his 40s with short grey hair and a beard in a black full wetsuit holding a plain white unbranded longboard upright; on the right a shorter woman in her early 30s with a dark ponytail in a navy wetsuit with a plain unbranded shortboard under her arm. Medium-sized waves breaking offshore, warm morning light, natural colors, no text, no logos, no flags, no signs'
        },
        'generator': "Slides 1-5 generated using Google Imagen 3 via Antigravity generate_image tool. Slide 7 (final) replaced 29.10, generated using Z-Image Turbo via Hugging Face (mcp-tools/Z-Image-Turbo).",
        'HE': {
            'cover': ('נראה חצי מטר מהחוף?', 'במים זה יותר'),
            'stake': 'מהחוף רואים רק את החלק העליון של הגל',
            'ideas': [
                ('01', 'המרחק מטעה', 'גל שנשבר 100 מטר מכם נראה נמוך מכפי שהוא'),
                ('02', 'אין עם מה להשוות', 'בלי גולש לידו, קשה להבין את הגודל'),
                ('03', 'בודקים לפי גולש', 'גולש שעומד על הגל: הגל עד המותניים, עד הכתף או מעל הראש'),
            ],
            'recap': ('בקצרה', [
                'מהחוף רואים רק את החלק העליון של הגל',
                'בלי גולש לידו אין עם מה להשוות',
                'בודקים לפי גולש: מותניים, כתף או ראש'
            ]),
            'final': ('שמרו לפני שבודקים את הים', 'מחר: גלישה אחרי 30'),
        }
    },
    'p18': {
        'total_slides': 7,
        'images': {
            'cover': os.path.join(BRAIN_DIR, 'p18_cover_surfer_1793256588767.jpg'),
            'stake': os.path.join(BRAIN_DIR, 'p18_stake_prep_1793256613948.jpg'),
            '01': os.path.join(BRAIN_DIR, 'p18_s01_warmup_1793256638937.jpg'),
            '02': os.path.join(BRAIN_DIR, 'p18_s02_bigboard_1793256680107.jpg'),
            '03': os.path.join(BRAIN_DIR, 'p18_s03_dawnpatrol_1793256709739.jpg'),
            'final': os.path.join(BRAIN_DIR, 'p18_final_card_1793256744257.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical surf photograph of an adult male surfer in his late 30s standing confident on a sandy beach holding an unbranded surfboard under his arm, looking toward gentle ocean waves, morning sunlight, athletic build, authentic documentary coastal surf photography, no logos, no text, 8k quality',
            'Slide 2 (Stake)': 'Photorealistic vertical surf photo of an adult female surfer in her late 30s kneeling on the sand waxing an unbranded surfboard, authentic coastal lighting, focused relaxed expression, clean wetsuit, no logos, documentary surf photography, 8k quality',
            'Slide 3 (Idea 01)': 'Photorealistic vertical surf photo of an adult male surfer in his early 40s doing a dynamic shoulder and torso stretch routine on a sandy beach beside his surfboard, ocean surf in background, authentic morning light, focused routine, clean unbranded wetsuit, documentary surf photography, 8k quality',
            'Slide 4 (Idea 02)': 'Photorealistic vertical surf photo of an adult female surfer in her late 30s carrying a wide rounded high-volume mid-length surfboard walking toward the ocean shoreline, side view, natural morning light, clean surfboard rails and single fin, no logos, documentary surf photo, 8k quality',
            'Slide 5 (Idea 03)': 'Photorealistic vertical surf photo of an adult male surfer in his late 30s riding a clean open wave face during dawn patrol sunrise light, smooth relaxed trimming style, morning glow, ocean mist, no logos, documentary surf photography, 8k quality',
            'Slide 7 (Final)': 'Photorealistic horizontal surf photograph of adult surfers in their 30s and 40s sitting together relaxed on coastal grass dunes with unbranded surfboards watching ocean waves roll in, warm late afternoon sunlight, authentic friendship community surf photography, no logos, no text, 8k quality'
        },
        'HE': {
            'cover': ('מתחילים לגלוש אחרי 30?', 'לא מאוחר מדי'),
            'stake': 'בגיל 30 לומדים קצת אחרת, וזה הכול',
            'ideas': [
                ('01', 'הגוף צריך חימום', 'חמש דקות על החול לפני כל כניסה'),
                ('02', 'גלשן גדול יותר', 'יותר נפח, יותר גלים, פחות תסכול'),
                ('03', 'פחות זמן, יותר פעמים', 'שעה פעמיים בשבוע עדיף על ארבע שעות פעם בחודש'),
            ],
            'recap': ('בקצרה', [
                'חמש דקות חימום לפני כל כניסה',
                'גלשן גדול יותר, יותר גלים',
                'שעה פעמיים בשבוע עדיף על יום ארוך פעם בחודש'
            ]),
            'final': ('שלחו לחבר שאומר שהוא מבוגר מדי', 'מחר: ברקים מעל הים'),
        }
    },
    'p19': {
        'total_slides': 7,
        'images': {
            'cover': os.path.join(BRAIN_DIR, 'p19_cover_storm_1793256792133.jpg'),
            'stake': os.path.join(BRAIN_DIR, 'p19_stake_highest_1793256829066.jpg'),
            '01': os.path.join(BRAIN_DIR, 'p19_s01_thunder_1793256865942.jpg'),
            '02': os.path.join(BRAIN_DIR, 'p19_s02_exitbeach_1793256908557.jpg'),
            '03': os.path.join(BRAIN_DIR, 'p19_s03_wait30min_1793256953872.jpg'),
            'final': os.path.join(BRAIN_DIR, 'p19_final_card_1793257000096.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical surf photo of a dramatic dark storm front over the ocean with a distant bolt of lightning flashing near the stormy horizon, dark moody sea spray, stormy coastal seascape, dramatic authentic nature photography, no text, no logos, 8k quality',
            'Slide 2 (Stake)': 'Photorealistic vertical surf photo of a solitary adult surfer in a dark wetsuit sitting upright on an unbranded surfboard in open dark ocean water under an immense dark stormy sky, wide view showing the surfer as the only high point above the flat water horizon, moody overcast, documentary coastal photo, 8k quality',
            'Slide 3 (Idea 01)': 'Photorealistic vertical surf photo of an adult female surfer sitting on her board in choppy coastal waters, turning her head back looking with concern at heavy dark rain clouds gathering over the coastline, moody ocean atmosphere, no logos, documentary surf photography, 8k quality',
            'Slide 4 (Idea 02)': 'Photorealistic vertical surf photo of an adult male surfer in a wet black wetsuit carrying his surfboard under his arm walking briskly out of ocean foam onto dark wet sand, overcast stormy sky and rain in background, authentic determined exit from the water, no logos, documentary surf photo, 8k quality',
            'Slide 5 (Idea 03)': 'Photorealistic vertical surf photo of an adult female surfer in a dry warm fleece jacket standing beside an open vehicle tailgate in a coastal parking lot, looking out at rain falling over the dark ocean waves, patiently waiting, authentic coastal weather, no logos, documentary photography, 8k quality',
            'Slide 7 (Final)': 'Photorealistic horizontal surf photograph of an authentic coastal headland and surf beach with dark moody rain squall clearing over the ocean, wet reflective beach sand, authentic documentary storm surf landscape, no people close up, no logos, 8k quality'
        },
        'HE': {
            'cover': ('רואים ברק מעל הים?', 'יוצאים מהמים עכשיו'),
            'stake': 'במים אתם הנקודה הכי גבוהה מסביב',
            'ideas': [
                ('01', 'שומעים רעם', 'הברק קרוב מספיק כדי לפגוע. לא מחכים לגל האחרון'),
                ('02', 'יוצאים לחוף', 'לא נשארים במים "רק עוד קצת"'),
                ('03', 'מחכים חצי שעה', 'אחרי הרעם האחרון, ורק אז חוזרים'),
            ],
            'recap': ('בקצרה', [
                'שומעים רעם? יוצאים מהמים',
                'לא מחכים לגל האחרון',
                'חוזרים רק חצי שעה אחרי הרעם האחרון'
            ]),
            'final': ('שמרו לחורף', 'מחר: תקועים באותה רמה?'),
        }
    },
    'p20': {
        'total_slides': 7,
        'generator': ZIMAGE_GENERATOR,
        'balance': True,
        'images': {
            'cover': os.path.join(ASSETS_DIR, 'p20', 'p20_cover_waiting_lineup.jpg'),
            'stake': os.path.join(ASSETS_DIR, 'p20', 'p20_stake_walking_out_thinking.jpg'),
            '01': os.path.join(ASSETS_DIR, 'p20', 'p20_s01_foam_rider.jpg'),
            '02': os.path.join(ASSETS_DIR, 'p20', 'p20_s02_filming_friend.jpg'),
            '03': os.path.join(ASSETS_DIR, 'p20', 'p20_s03_green_wave.jpg'),
            'final': os.path.join(ASSETS_DIR, 'p20', 'p20_final_walk_to_sea_sunrise.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical documentary surf photograph: a man in his late 30s with a shaved head and stubble, stocky build, in a plain black wetsuit with no logos, sitting on a plain white surfboard in the calm lineup beyond the breaking waves, seen from the side, looking at the horizon thoughtfully waiting for a wave, Mediterranean sea, soft overcast winter light, subject centered, no text, no logos',
            'Slide 2 (Stake)': 'Photorealistic vertical documentary surf photograph: an older man in his early 50s with grey curly hair and a grey beard, lean build, in a plain black wetsuit, walking slowly out of the sea onto a sandy Mediterranean beach carrying a plain white surfboard under his arm with the fins pointing back behind him, head tilted down thinking, tired after a session, soft golden late afternoon light, subject centered, realistic anatomy, no text, no logos',
            'Slide 3 (Idea 01)': 'Photorealistic vertical documentary surf photograph: an adult woman in her early 30s with curly brown hair in a black unbranded wetsuit riding a soft-top beginner surfboard standing up in white foam whitewater close to shore, small broken wave, Mediterranean sandy beach, warm late afternoon light, subject centered in frame, realistic hands and feet, single surfboard with leash on ankle, no text, no logos',
            'Slide 4 (Idea 02)': "Photorealistic vertical documentary photograph on a sandy beach: a woman in her mid 40s with short blonde hair in a plain navy wetsuit with no logos, standing on the sand at the water's edge holding a smartphone with both hands, filming a friend surfing out in the sea, seen from behind over her shoulder, the phone screen not visible, waves breaking in the background with a small distant surfer, soft afternoon light, realistic hands, no text, no logos",
            'Slide 5 (Idea 03)': 'Photorealistic vertical documentary surf photograph: a slim young man in his late 20s with long dark hair tied back, in a grey unbranded wetsuit, standing on a plain unbranded surfboard riding a small clean unbroken green wave face, the wave shoulder still green and glassy, white water only behind him, warm morning light, Mediterranean sea, subject centered in frame, realistic anatomy, no text, no logos',
            'Slide 7 (Final)': 'Photorealistic horizontal documentary surf photograph: a young woman in her late 20s with a long black braid and darker skin, in a plain black wetsuit, walking across a wide sandy Mediterranean beach toward the sea at sunrise carrying a plain unbranded mid-length surfboard under her arm, seen from behind at a distance, small clean waves, warm golden light, wide calm composition, no text, no logos, no flags',
        },
        'HE': {
            'cover': ('חצי שנה באותה רמה?', 'זה רק שלב'),
            'stake': 'כמעט כל גולש נתקע אחרי כמה חודשים הראשונים',
            'ideas': [
                ('01', 'אותם גלים', 'תופסים רק קצף או רק את הגלים הקלים. נסו גל ירוק אחד בכל סשן'),
                ('02', 'אותה טעות', 'אין לכם מושג מה לתקן. צלמו גל אחד ותראו'),
                ('03', 'הכול ביחד', 'מנסים לתקן חמישה דברים. בחרו אחד לכל סשן'),
            ],
            'recap': ('בקצרה', [
                'נסו גל ירוק אחד בכל סשן',
                'צלמו גל ותראו מה באמת קורה',
                'תקנו דבר אחד בכל פעם, לא חמישה'
            ]),
            'final': ('שמרו לסשן הבא', 'מחר: מה זה סנייקינג'),
        }
    },
    'p21': {
        'total_slides': 7,
        'generator': ZIMAGE_GENERATOR,
        'balance': True,
        'images': {
            'cover': os.path.join(ASSETS_DIR, 'p21', 'p21_cover_annoyed_surfer.jpg'),
            'stake': os.path.join(ASSETS_DIR, 'p21', 'p21_stake_beginner_in_lineup.jpg'),
            '01': os.path.join(ASSETS_DIR, 'p21', 'p21_s01_paddling_around.jpg'),
            '02': os.path.join(ASSETS_DIR, 'p21', 'p21_s02_wave_taken.jpg'),
            '03': os.path.join(ASSETS_DIR, 'p21', 'p21_s03_waiting_turn.jpg'),
            'final': os.path.join(ASSETS_DIR, 'p21', 'p21_final_peeling_wave_golden.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical documentary surf photograph in calm deep water beyond the breaking waves: a man in his mid 40s with a short dark beard and tanned skin, in a plain black wetsuit, sitting upright astride a plain white surfboard with legs dangling in the water on both sides, turning his head over his shoulder toward the camera with an irritated frowning look, both hands resting on the board, smooth swell behind him, Mediterranean morning light, subject centered, realistic anatomy, no text, no logos',
            'Slide 2 (Stake)': 'Photorealistic vertical documentary surf photograph: a beginner surfer, a woman in her early 30s with dark wavy hair and olive skin, sitting on a large soft-top surfboard in the lineup, looking around a little unsure and curious at the other surfers in the distance, calm green water, soft late afternoon light, Mediterranean sea, subject centered, realistic anatomy, plain wetsuit, no text, no logos',
            'Slide 3 (Idea 01)': 'Photorealistic vertical documentary surf photograph at water level in calm deep water: in the foreground a middle-aged woman with short grey hair sits astride her white surfboard waiting, seen from the side; just behind her a young man with long blond hair lies prone on a blue surfboard paddling fast past her on the outside, both people clearly different, two separate boards, gentle swell, Mediterranean morning light, no text, no logos',
            'Slide 4 (Idea 02)': 'Photorealistic vertical documentary surf photograph: a slim surfer in his 30s with a buzz cut stands on a plain surfboard riding down the green face of a small wave, while in the foreground a different surfer, a broad-shouldered man in his 50s with a grey ponytail, sits on his board in the water behind the wave watching it go with his arms spread in disbelief, Mediterranean sea, bright midday light, two clearly different people, realistic anatomy and boards, no text, no logos',
            'Slide 5 (Idea 03)': 'Photorealistic vertical documentary surf photograph: a surf lineup seen from the water at eye level, three very different adults sitting astride plain unbranded surfboards spaced apart in deep calm water beyond the waves, all looking out to sea: a young woman with a red-brown bun, an older bald man with a white beard, and a heavy-set man in his 30s with black curly hair and no hat, plain wetsuits without logos, a swell rising on the horizon, soft morning light, no text, no logos, no caps',
            'Slide 7 (Final)': 'Photorealistic horizontal documentary surf photograph at golden hour: a single clean peeling wave breaking along a sandy Mediterranean beach with one surfer riding it in the distance, the wave peak glowing in warm backlight, empty calm water around, wide calm composition, no other people, no text, no logos, no flags, no signs',
        },
        'HE': {
            'cover': ('מישהו כועס עליכם בליינאפ?', 'אולי עשיתם סנייקינג'),
            'stake': 'זו עוד מילה מהליינאפ שמתחילים לא מכירים',
            'ideas': [
                ('01', 'מה זה', 'חותרים מסביב לגולש שמחכה, ונכנסים לפניו לגל'),
                ('02', 'איך זה נראה', 'הוא היה פה ראשון, אתם עקפתם אותו מהצד'),
                ('03', 'מה עושים', 'מחכים בתור. הגולש שמחכה הכי הרבה זמן ליד הפיק, הוא הבא'),
            ],
            'recap': ('בקצרה', [
                'סנייקינג: חותרים מסביב למישהו שמחכה ותופסים את הגל לפניו',
                'מי שמחכה הכי הרבה ליד הפיק, הוא הבא',
                'מחכים בתור, גם כשהגל נראה מושלם'
            ]),
            'final': ('שמרו ושלחו לחבר מהליינאפ', 'מחר: למה פה גלים ושם שטוח'),
        }
    },
    'p22': {
        'total_slides': 7,
        'generator': ZIMAGE_GENERATOR,
        'balance': True,
        'images': {
            'cover': os.path.join(ASSETS_DIR, 'p22', 'p22_cover_waves_then_flat_aerial.jpg'),
            'stake': os.path.join(ASSETS_DIR, 'p22', 'p22_stake_wave_over_sand_topdown.jpg'),
            '01': os.path.join(ASSETS_DIR, 'p22', 'p22_s01_sandbar_peak.jpg'),
            '02': os.path.join(ASSETS_DIR, 'p22', 'p22_s02_breakwater.jpg'),
            '03': os.path.join(ASSETS_DIR, 'p22', 'p22_s03_beach_facing_swell.jpg'),
            'final': os.path.join(ASSETS_DIR, 'p22', 'p22_final_checking_coastline.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical high aerial drone photograph looking down along a sandy Mediterranean coastline: in the lower half of the frame a sandbar offshore makes several white lines of breaking waves with tiny surfers on them, in the upper half of the frame the same coastline continues with deep dark blue water and no waves at all, completely flat, clear visual contrast, natural midday light, no text, no logos',
            'Slide 2 (Stake)': 'Photorealistic vertical top-down aerial drone photograph of clear turquoise Mediterranean water over a sandy bottom: a lighter shallow sandbar is visible under the water and a wave is breaking white exactly over the sandbar, while the darker deeper water on either side stays unbroken, natural colors, documentary nature photography, no people, no text, no logos',
            'Slide 3 (Idea 01)': 'Photorealistic vertical documentary surf photograph from the water: a clean A-frame wave peak about chest high breaking over a shallow sandbar, the lighter sand bottom visible through clear green water in front of the wave, nobody on it, Mediterranean morning light, offshore wind spray from the lip, no people, no text, no logos',
            'Slide 4 (Idea 02)': 'Photorealistic vertical aerial drone photograph of a Mediterranean beach with a rock breakwater made of large boulders extending into the sea: behind the breakwater the water is calm, flat and protected, while on the open side waves break and a channel of darker choppy water with sandy streaks runs out to sea alongside the rocks, nobody in the water, no text, no logos, no signs, natural light',
            'Slide 5 (Idea 03)': 'Photorealistic vertical documentary photograph from a low dune looking straight out to sea from an open sandy Mediterranean beach: several evenly spaced swell lines rolling in head-on toward the beach and breaking cleanly, the beach faces the swell directly, a single surfer in the middle distance, late afternoon light, no text, no logos, no signs',
            'Slide 7 (Final)': 'Photorealistic horizontal documentary photograph of a woman in her late 30s with short red hair and freckles, wearing a hoodie, standing on a low sandy bluff above a Mediterranean beach with her surfboard leaning beside her, looking along the coastline comparing two parts of the beach, waves breaking in one part of the bay, calmer water further away, warm morning light, no text, no logos, no flags, no signs',
        },
        'HE': {
            'cover': ('אותו חוף, 500 מטר משם', 'גלים כאן, שטוח שם'),
            'stake': 'הגל תלוי במה שיש מתחת למים',
            'ideas': [
                ('01', 'שרטון חול', 'איפה שהקרקעית רדודה, הגל נשבר. אין שרטון, אין גל'),
                ('02', 'שובר גלים', 'מאחוריו מוגן ושטוח. לידו נוצר זרם, לא נכנסים'),
                ('03', 'הכיוון של הגלים', 'חוף שפונה לכיוון הגלים מקבל יותר'),
            ],
            'recap': ('בקצרה', [
                'שרטון חול מתחת למים עושה את הגל',
                'מאחורי שובר גלים מוגן ושטוח, לידו זרם',
                'חוף שפונה לגלים מקבל יותר'
            ]),
            'final': ('שמרו לפני שבוחרים חוף', 'מחר: אמת או מיתוס'),
        }
    },
    'p23': {
        'total_slides': 8,
        'generator': ZIMAGE_GENERATOR,
        'balance': True,
        'images': {
            'cover': os.path.join(ASSETS_DIR, 'p23', 'p23_cover_skeptical_surfer.jpg'),
            'stake': os.path.join(ASSETS_DIR, 'p23', 'p23_stake_thinking_on_beach.jpg'),
            '01': os.path.join(ASSETS_DIR, 'p23', 'p23_s01_swell_set.jpg'),
            '02': os.path.join(ASSETS_DIR, 'p23', 'p23_s02_paddling.jpg'),
            '03': os.path.join(ASSETS_DIR, 'p23', 'p23_s03_longboard.jpg'),
            '04': os.path.join(ASSETS_DIR, 'p23', 'p23_s04_winter_wave.jpg'),
            'final': os.path.join(ASSETS_DIR, 'p23', 'p23_final_winter_beach_walk.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical documentary surf photograph: a woman in her mid 50s with long silver hair tied back and sun-tanned skin, in a plain dark green wetsuit, standing on a sandy Mediterranean beach holding a plain white surfboard under her arm, smiling skeptically as she looks toward the camera, waves breaking behind her, warm morning light, subject centered, realistic anatomy, no text, no logos',
            'Slide 2 (Stake)': 'Photorealistic vertical documentary photograph: a young man in his late 20s with a thick black beard and glasses pushed up on his head, wearing a plain grey t-shirt and board shorts, sitting on the sand beside his surfboard with his chin on his hand, thinking hard while watching the waves, Mediterranean beach, soft afternoon light, subject centered, realistic hands, no text, no logos',
            'Slide 3 (Idea 01)': 'Photorealistic vertical documentary photograph of the open sea: a set of several big parallel swell lines approaching the coast one after another, each wave a slightly different size, dark blue water and white crests, stormy winter Mediterranean light with breaks of sun, no people, no text, no logos',
            'Slide 4 (Idea 02)': 'Photorealistic vertical documentary surf photograph, side view at water level: an experienced surfer in his 40s with a shaved head and dark skin, plain black wetsuit, lying prone on a plain shortboard paddling out, chest slightly raised, head up, calm blue water with a small wave behind, bright light, subject centered, realistic anatomy, no text, no logos',
            'Slide 5 (Idea 03)': 'Photorealistic vertical documentary surf photograph: a man in his 60s with a white moustache and a sun hat strapped under his chin, in a plain navy long-sleeve rash vest and board shorts, standing upright and relaxed on a very long plain cream-colored longboard, gliding along a small gentle green wave, Mediterranean sea, warm morning light, subject centered, realistic anatomy, no text, no logos',
            'Slide 6 (Idea 04)': 'Photorealistic vertical documentary surf photograph on a winter day: a surfer in a full black winter wetsuit with a hood riding a large powerful head-high grey-green wave, dark dramatic storm clouds over the Mediterranean sea, wind spray off the lip, cold winter light, realistic board and anatomy, no text, no logos',
            'Slide 8 (Final)': 'Photorealistic horizontal documentary photograph of a quiet sandy Mediterranean beach in winter: clean grey-green waves breaking under soft broken clouds with sunbeams, two surfers far away walking along the waterline with boards, wide empty shore, wet sand reflections, calm moody light, no text, no logos, no flags, no signs',
        },
        'HE': {
            # Plan text verbatim. NB: kicker says 5 sentences, the plan has 4 items (caption says 4).
            'cover': ('4 משפטים על גלישה', 'אמת או מיתוס?'),
            'stake': 'נחשו לפני שמחליקים לתשובה',
            'ideas': [
                ('01', '"הגל השביעי הכי גדול"', 'מיתוס. אין מספר קבוע, סופרים את הסט בעיניים'),
                ('02', '"גולשים טובים חותרים פחות"', 'מיתוס. הם חותרים הרבה, פשוט חכם יותר'),
                ('03', '"גלשן ארוך יותר תופס יותר גלים"', 'אמת. יותר נפח, יותר מהירות בחתירה'),
                ('04', '"בחורף אין גלים בישראל"', 'מיתוס. החורף זו העונה הכי טובה'),
            ],
            'recap': ('בקצרה', [
                'הגל השביעי הכי גדול: מיתוס',
                'גולשים טובים חותרים פחות: מיתוס',
                'גלשן ארוך תופס יותר גלים: אמת',
                'בחורף אין גלים: מיתוס'
            ]),
            'final': ('כמה ניחשתם נכון? כתבו בתגובות', 'מחר: החוף אחרי סערה'),
        }
    },
    'p24': {
        'total_slides': 7,
        'generator': ZIMAGE_GENERATOR,
        'balance': True,
        'images': {
            'cover': os.path.join(ASSETS_DIR, 'p24', 'p24_cover_beach_after_storm.jpg'),
            'stake': os.path.join(ASSETS_DIR, 'p24', 'p24_stake_storm_sandy_water.jpg'),
            '01': os.path.join(ASSETS_DIR, 'p24', 'p24_s01_watching_10min.jpg'),
            '02': os.path.join(ASSETS_DIR, 'p24', 'p24_s02_channel_gap.jpg'),
            '03': os.path.join(ASSETS_DIR, 'p24', 'p24_s03_new_sandbar_wave.jpg'),
            'final': os.path.join(ASSETS_DIR, 'p24', 'p24_final_calm_after_storm.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical documentary photograph of a Mediterranean sandy beach the morning after a winter storm: the shoreline reshaped with a fresh sand cliff step, piles of seaweed and driftwood, wet churned sand, waves still rolling in under clearing clouds, a lone surfer, a tall thin man in his 30s with a ginger beard holding his board, standing small in the middle distance looking at the changed beach, no text, no logos, no signs',
            'Slide 2 (Stake)': 'Photorealistic vertical documentary photograph of heavy winter storm waves crashing near a Mediterranean beach, the water churned brown and murky with suspended sand, thick foam, dark grey sky, strong wind, no people, no text, no logos',
            'Slide 3 (Idea 01)': 'Photorealistic vertical documentary photograph: a woman in her 40s with a short grey-streaked black pixie cut and brown skin, in a plain black wetsuit, standing on the beach with her surfboard planted upright in the sand beside her, arms crossed, patiently watching the waves to see where they break, seen from behind and slightly to the side, Mediterranean coast, clear morning after a storm, subject centered, realistic anatomy, no text, no logos',
            'Slide 4 (Idea 02)': 'Photorealistic vertical photograph from a high sand dune overlooking a Mediterranean beach: waves break white on the left side and on the right side, and in the middle there is a smooth darker strip of water without breaking waves leading out to sea, cloudy sky, coastal landscape photography, no people',
            'Slide 5 (Idea 03)': 'Photorealistic vertical documentary surf photograph on a crisp clear morning after a storm: a long clean glassy green wave peeling perfectly over a new sandbar, a single surfer, a curly-haired woman in her late 20s in a plain black wetsuit, riding down the open face, blue sky, Mediterranean sea, realistic anatomy and board, no text, no logos',
            'Slide 7 (Final)': 'Photorealistic horizontal documentary photograph of a Mediterranean sandy beach on a calm clear morning a few days after a winter storm: smooth clean waves, a line of dried seaweed along the high-tide mark, fresh sand terraces, soft golden light, empty beach with no people, no text, no logos, no flags, no signs',
        },
        'HE': {
            'cover': ('הייתם פה בשבוע שעבר?', 'החוף כבר לא אותו חוף'),
            'stake': 'סערה אחת מזיזה את החול מתחת למים',
            'ideas': [
                ('01', 'הפיק זז', 'המקום שבו הגל נשבר עבר. מסתכלים 10&nbsp;דקות לפני שנכנסים'),
                ('02', 'בורות ותעלות', 'יש עכשיו מקומות עמוקים ליד החוף, ושם יכול להיות זרם'),
                ('03', 'לפעמים טוב יותר', 'שרטון חדש יכול לתת גל יפה יותר מקודם'),
            ],
            'recap': ('בקצרה', [
                'הפיק כבר לא באותו מקום, מסתכלים 10&nbsp;דקות לפני',
                'יש בורות ותעלות חדשים, ובהם זרם',
                'לפעמים יוצא שרטון טוב יותר מקודם'
            ]),
            'final': ('שמרו לסערה הבאה', 'מחר: דבר אחד בכל סשן'),
        }
    },
    'p25': {
        'total_slides': 7,
        'generator': ZIMAGE_GENERATOR,
        'balance': True,
        'images': {
            'cover': os.path.join(ASSETS_DIR, 'p25', 'p25_cover_calm_focus.jpg'),
            'stake': os.path.join(ASSETS_DIR, 'p25', 'p25_stake_awkward_ride.jpg'),
            '01': os.path.join(ASSETS_DIR, 'p25', 'p25_s01_one_fix_stance.jpg'),
            '02': os.path.join(ASSETS_DIR, 'p25', 'p25_s02_focused_paddle.jpg'),
            '03': os.path.join(ASSETS_DIR, 'p25', 'p25_s03_phone_tripod.jpg'),
            'final': os.path.join(ASSETS_DIR, 'p25', 'p25_final_after_session_sunset.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical documentary surf photograph: a man in his early 30s with a short afro and dark brown skin, in a plain black wetsuit, sitting calmly on a plain surfboard in the lineup with eyes closed for a moment, taking a slow breath, focused and calm, soft morning light on glassy Mediterranean water, small waves behind him, subject centered, realistic anatomy, no text, no logos',
            'Slide 2 (Stake)': 'Photorealistic vertical documentary surf photograph: a woman in her late 30s with a blonde braid in a plain grey wetsuit, off balance on her surfboard in small whitewater, body tilted, splash, one leash on her back ankle only, Mediterranean beach break, bright light, realistic anatomy, no text, no logos',
            'Slide 3 (Idea 01)': 'Photorealistic vertical documentary surf photograph: a man in his late 40s with salt-and-pepper short hair and a stubble beard, in a plain navy wetsuit, standing up on a plain white surfboard on a small green wave right after the pop-up, Mediterranean sea, warm afternoon light, subject centered, realistic anatomy and board, no text, no logos',
            'Slide 4 (Idea 02)': 'Photorealistic vertical documentary surf photograph, front view: a young man in his late 20s with a red buzz cut and freckles, in a plain black wetsuit, lying prone on a plain white surfboard paddling hard into an approaching wave, intense focused eyes looking forward, Mediterranean sea, late afternoon light, subject centered, realistic anatomy, no text, no logos',
            'Slide 5 (Idea 03)': 'Photorealistic vertical documentary photograph on a sandy beach at sunset: a smartphone mounted on a small black tripod standing in the sand in the foreground, pointing at the sea, and far out a small surfer riding a wave in warm golden light, shallow depth of field, no text, no logos',
            'Slide 7 (Final)': 'Photorealistic horizontal documentary photograph at sunset on a Mediterranean beach: a woman in her 50s with short white hair wrapped in a beige towel poncho sitting on the sand after a surf session, smiling quietly and looking at the sea, her surfboard standing upright stuck in the sand behind her, warm golden light, small waves, calm mood, no text, no logos, no flags, no signs',
        },
        'HE': {
            'cover': ('מנסים לתקן הכול בבת אחת?', 'דבר אחד בכל סשן'),
            'stake': 'כשחושבים על חמישה דברים, לא עושים אף אחד',
            'ideas': [
                ('01', 'בוחרים אחד', 'הדבר שהכי מפריע לכם עכשיו: הקימה, המבט,&nbsp;הברכיים'),
                ('02', 'עשרה גלים', 'כל גל בסשן חושבים רק עליו'),
                ('03', 'בודקים בסוף', 'צלמו גל אחד בסוף הסשן ותראו אם זה השתנה'),
            ],
            'recap': ('בקצרה', [
                'בוחרים דבר אחד שהכי מפריע',
                'כל הסשן חושבים רק עליו',
                'בסוף מצלמים גל ובודקים'
            ]),
            'final': ('שמרו ובחרו את הדבר שלכם', 'מחר: איך קמים לגלוש בבוקר קר'),
        }
    },
    'p26': {
        'total_slides': 7,
        'generator': ZIMAGE_GENERATOR,
        'balance': True,
        'images': {
            'cover': os.path.join(ASSETS_DIR, 'p26', 'p26_cover_dawn_car_coffee.jpg'),
            'stake': os.path.join(ASSETS_DIR, 'p26', 'p26_stake_winter_sunrise.jpg'),
            '01': os.path.join(ASSETS_DIR, 'p26', 'p26_s01_gear_by_door.jpg'),
            '02': os.path.join(ASSETS_DIR, 'p26', 'p26_s02_friends_meet_dawn.jpg'),
            '03': os.path.join(ASSETS_DIR, 'p26', 'p26_s03_forecast_evening.jpg'),
            'final': os.path.join(ASSETS_DIR, 'p26', 'p26_final_sunrise_ride.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical documentary photograph at dawn in winter: a man in his late 30s with a dark beanie and a thick dark beard, wearing a warm hooded changing poncho over his wetsuit, standing by the open back of an old hatchback car in a beach parking lot, holding a hot drink with steam rising, visible breath in the cold air, first blue light of dawn over the Mediterranean sea behind, surfboard leaning on the car, no text, no logos, no license plate',
            'Slide 2 (Stake)': 'Photorealistic vertical documentary photograph of a cold clear winter sunrise over a Mediterranean beach: perfect glassy waves peeling in soft pink and orange light, light mist over the water, frosty cold atmosphere, empty beach, no people, no text, no logos',
            'Slide 3 (Idea 01)': 'Photorealistic vertical documentary interior photograph at night: a hallway by an apartment front door, a plain white surfboard leaning against the wall with its bottom side facing the camera and three small fins near the tail, a black wetsuit with no logos hanging on a hook, a rolled grey towel on a wooden bench, car keys on the bench, warm lamp light, ready for an early morning, no people, no text, no logos, no labels',
            'Slide 4 (Idea 02)': 'Photorealistic vertical documentary photograph at dawn in a beach parking lot: two clearly different friends meeting, a woman in her 40s with curly grey hair in a warm jacket next to her surfboard and a man in his 30s with a ponytail in a hoodie, smiling and bumping fists, cold blue morning light, the sea in the background, no text, no logos, no license plates',
            'Slide 5 (Idea 03)': "Photorealistic vertical documentary photograph in the evening at home: a woman in her early 30s with long straight black hair and glasses, wearing a cozy sweater, sitting on a sofa under a warm lamp looking at her phone to check tomorrow's surf forecast, a surfboard leaning against the wall in the background, calm evening mood, realistic hands, no text, no logos",
            'Slide 7 (Final)': 'Photorealistic horizontal documentary surf photograph at winter sunrise: a single surfer silhouette on a glassy sea riding a small clean wave, warm orange sky and light mist, cold calm morning, wide composition, Mediterranean coast, no text, no logos, no flags',
        },
        'HE': {
            'cover': ('6 בבוקר, קר, והשעון מצלצל', 'ככה יוצאים בכל זאת'),
            'stake': 'הבקרים הכי טובים של החורף הם גם הכי קרים',
            'ideas': [
                ('01', 'מכינים בערב', 'החליפה, המגבת והגלשן ליד הדלת'),
                ('02', 'קובעים עם חבר', 'קשה לבטל כשמישהו מחכה בחוף'),
                ('03', 'בודקים תחזית בערב', 'יודעים מראש שזה שווה את זה'),
            ],
            'recap': ('בקצרה', [
                'מכינים הכול בערב, ליד הדלת',
                'קובעים עם חבר בחוף',
                'בודקים את התחזית מראש'
            ]),
            'final': ('שלחו לחבר שתגלשו איתו מחר', 'מחר: סימנים במים'),
        }
    },
    'p27': {
        'total_slides': 7,
        'generator': ZIMAGE_GENERATOR,
        'balance': True,
        'images': {
            'cover': os.path.join(ASSETS_DIR, 'p27', 'p27_cover_arm_raised_signal.jpg'),
            'stake': os.path.join(ASSETS_DIR, 'p27', 'p27_stake_lifeguard_watching.jpg'),
            '01': os.path.join(ASSETS_DIR, 'p27', 'p27_s01_waving_for_help.jpg'),
            '02': os.path.join(ASSETS_DIR, 'p27', 'p27_s02_hand_on_head_ok.jpg'),
            '03': os.path.join(ASSETS_DIR, 'p27', 'p27_s03_stay_with_board.jpg'),
            'final': os.path.join(ASSETS_DIR, 'p27', 'p27_final_friends_after_surf.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical documentary surf photograph: a woman in her 30s with a dark bun and olive skin, in a plain black wetsuit, sitting on her surfboard in moderate sea, calmly raising one arm straight up high above her head to signal toward the beach, composed face, other hand holding the board rail, Mediterranean sea, overcast light, subject centered, realistic anatomy, exactly two arms, no text, no logos',
            'Slide 2 (Stake)': 'Photorealistic vertical documentary photograph: a lifeguard, a man in his 40s with a grey crew cut, wearing a plain red t-shirt with no print and a sun hat, standing on a wooden lifeguard tower on a Mediterranean beach watching the surfers in the sea through binoculars, waves and small surfers in the distance, windy day, no text, no logos, no signs, no flags',
            'Slide 3 (Idea 01)': 'Photorealistic vertical documentary photograph taken with a telephoto lens: a surfer, a man in his 30s with long dark hair, sitting on his surfboard, waving one arm high above his head from side to side, looking toward the shore, the other hand on the board, Mediterranean sea, soft overcast light, subject centered, plain black wetsuit, realistic anatomy, no text, no logos',
            'Slide 4 (Idea 02)': 'Photorealistic vertical documentary surf photograph: a man in his late 40s with a white beard and a tanned bald head, in a plain black wetsuit, sitting on his surfboard in calm water, smiling, with only his right hand resting flat on the top of his head and the elbow pointing out to the side, his left hand resting on the board, Mediterranean sea, bright light, subject centered, realistic anatomy, exactly two arms, no text, no logos',
            'Slide 5 (Idea 03)': 'Photorealistic vertical documentary surf photograph: a woman with short bleached hair, in a plain black wetsuit, calmly floating in the water holding onto her surfboard with both arms draped over the deck, chin up, relaxed breathing, leash attached to her ankle, calm sea behind, Mediterranean light, subject centered, realistic anatomy, no text, no logos',
            'Slide 7 (Final)': 'Photorealistic horizontal documentary surf photograph: two clearly different friends sitting side by side on the sand after surfing, a tall man in his 50s with grey hair and a younger woman in her 30s with a black ponytail, both in plain black wetsuits, laughing together, their two surfboards on the sand, calm sea with small waves behind, warm late afternoon light, no text, no logos, no flags',
        },
        'HE': {
            'cover': ('צריכים עזרה במים?', 'ככה מסמנים'),
            'stake': 'בים לא שומעים&nbsp;צעקות, רואים סימנים',
            'ideas': [
                ('01', 'יד אחת למעלה, מנופפת', 'אני צריך עזרה'),
                ('02', 'יד על הראש', 'אני בסדר'),
                ('03', 'נשארים עם הגלשן', 'הוא צף, ואתם איתו'),
            ],
            'recap': ('בקצרה', [
                'יד מנופפת למעלה: צריך עזרה',
                'יד על הראש: אני בסדר',
                'לא עוזבים את הגלשן, הוא צף'
            ]),
            'final': ('שמרו ושלחו לחבר שגולש איתכם', 'מחר: מתי לצאת מהמים בקור'),
        }
    },
    'p28': {
        'total_slides': 7,
        'generator': ZIMAGE_GENERATOR,
        'balance': True,
        'images': {
            'cover': os.path.join(ASSETS_DIR, 'p28', 'p28_cover_walking_out_cold.jpg'),
            'stake': os.path.join(ASSETS_DIR, 'p28', 'p28_stake_cold_hands_on_deck.jpg'),
            '01': os.path.join(ASSETS_DIR, 'p28', 'p28_s01_weak_grip_rail.jpg'),
            '02': os.path.join(ASSETS_DIR, 'p28', 'p28_s02_warming_in_poncho.jpg'),
            '03': os.path.join(ASSETS_DIR, 'p28', 'p28_s03_paddling_in.jpg'),
            'final': os.path.join(ASSETS_DIR, 'p28', 'p28_final_robe_walk_home.jpg'),
        },
        'prompts': {
            'Slide 1 (Cover)': 'Photorealistic vertical documentary surf photograph on a cold grey winter day: a woman in her 40s with a thick winter wetsuit and hood, cheeks red from cold, walking out of the sea onto the beach with her surfboard under her arm, determined and calm, heading to get warm, dark winter clouds over the Mediterranean, subject centered, realistic anatomy, no text, no logos',
            'Slide 2 (Stake)': 'Photorealistic vertical close-up documentary photograph: two cold wet hands of an adult surfer with reddish stiff fingers on the deck of a plain white surfboard in grey winter sea water, water droplets, black wetsuit sleeves at the wrists, cold winter light, exactly two hands with five fingers each, realistic anatomy, no text, no logos',
            'Slide 3 (Idea 01)': 'Photorealistic vertical extreme close-up documentary photograph: one cold pale wet adult hand with stiff half-bent fingers trying to grip the edge of a white surfboard rail in grey winter water, black wetsuit cuff at the wrist, water droplets, shallow depth of field, cold blue light, exactly one hand with five fingers, realistic anatomy, no text, no logos',
            'Slide 4 (Idea 02)': 'Photorealistic vertical documentary photograph on a winter beach: a young man in his late 20s with wet dark curly hair and a thin moustache, after surfing, wrapped in a thick hooded towel poncho, warming up, holding a steaming cup, his surfboard on the sand beside him, grey sea behind, cool overcast light, subject centered, realistic anatomy, no text, no logos',
            'Slide 5 (Idea 03)': 'Photorealistic vertical documentary surf photograph on a cold winter day: a surfer, a lean man in his 50s with a grey goatee in a hooded winter wetsuit, lying prone on his surfboard and paddling calmly toward the beach in small whitewater, heading in to end the session, grey sky, Mediterranean winter sea, subject centered, realistic anatomy, no text, no logos',
            'Slide 7 (Final)': 'Photorealistic horizontal documentary photograph of a winter Mediterranean beach at late afternoon: a surfer seen from behind walking away along the sand toward the dunes wrapped in a long warm hooded changing robe, carrying a surfboard under one arm, grey-blue sea with clean waves on the left, low warm sun breaking through clouds, calm cozy mood, no text, no logos, no flags, no signs',
        },
        'HE': {
            'cover': ('רועדים במים?', 'הגוף אומר לצאת'),
            'stake': 'כשקר, הגוף לוקח כוח מהידיים ומהרגליים',
            'ideas': [
                ('01', 'ידיים לא נסגרות', 'קשה לאחוז בגלשן. זה הסימן הראשון'),
                ('02', 'רעד חזק שלא עובר', 'הגוף כבר לא מצליח להתחמם'),
                ('03', 'הקימה נהיית איטית', 'הגוף לא מגיב. יוצאים, לא "עוד גל אחד"'),
            ],
            'recap': ('בקצרה', [
                'ידיים שלא נסגרות על הגלשן',
                'רעד שלא נגמר',
                'קימה איטית מהרגיל'
            ]),
            # No tomorrow topic in the plan yet: empty string skips the line
            'final': ('שמרו לחורף', ''),
        }
    },
}

def render_post(post_id):
    post = POSTS[post_id]
    out_dir = os.path.join(VOLUNTEER_DIR, post_id)
    os.makedirs(out_dir, exist_ok=True)
    
    # Remove old EN slides from directory to enforce HE ONLY directive
    for old_en in glob.glob(os.path.join(out_dir, "EN_*.jpg")):
        os.remove(old_en)
        
    print(f"=== Rendering {post_id} (HE Hebrew Only) ===")
    
    total_slides = post.get('total_slides', 8)
    imgs = {k: b64_file(p) for k, p in post['images'].items() if os.path.exists(p)}
    
    lang = 'HE'
    lang_data = post[lang]
    bal = post.get('balance', False)
    
    # Slide 1: Cover
    print(f"  Rendering Slide 1 (Cover)...")
    h1 = render_cover(imgs['cover'], lang, lang_data['cover'][0], lang_data['cover'][1], 1, total_slides, balance=bal)
    chrome_render(h1, os.path.join(out_dir, f"{lang}_1.jpg"))
    
    # Slide 2: Stake
    print(f"  Rendering Slide 2 (Stake)...")
    h2 = render_stake(imgs['stake'], lang, lang_data['stake'], 2, total_slides, balance=bal)
    chrome_render(h2, os.path.join(out_dir, f"{lang}_2.jpg"))
    
    # Slides 3 to (3 + len(ideas) - 1): Ideas
    num_ideas = len(lang_data['ideas'])
    for idx, idea in enumerate(lang_data['ideas']):
        slide_no = idx + 3
        img_key = f"0{idx+1}"
        print(f"  Rendering Slide {slide_no} (Idea {idea[0]})...")
        h_idea = render_idea(imgs[img_key], lang, idea[0], idea[1], idea[2], slide_no, total_slides, balance=bal)
        chrome_render(h_idea, os.path.join(out_dir, f"{lang}_{slide_no}.jpg"))
        
    # Recap Slide
    recap_slide_num = num_ideas + 3
    print(f"  Rendering Slide {recap_slide_num} (Recap)...")
    h_recap = render_recap(lang, lang_data['recap'][0], lang_data['recap'][1], recap_slide_num, total_slides, balance=bal)
    chrome_render(h_recap, os.path.join(out_dir, f"{lang}_{recap_slide_num}.jpg"))
    
    # Final Slide
    final_slide_num = recap_slide_num + 1
    print(f"  Rendering Slide {final_slide_num} (Final)...")
    h_final = render_final(imgs['final'], lang, lang_data['final'][0], lang_data['final'][1], final_slide_num, total_slides, balance=bal)
    chrome_render(h_final, os.path.join(out_dir, f"{lang}_{final_slide_num}.jpg"))
    
    # Write SOURCES.txt
    sources_path = os.path.join(out_dir, "SOURCES.txt")
    with open(sources_path, "w", encoding="utf-8") as f:
        f.write(f"SOURCES for {post_id} (Generated {post_id.upper()} Hebrew Carousel Images)\n")
        f.write("=" * 60 + "\n\n")
        f.write(post.get('generator', "All photos generated using Google Imagen 3 via Antigravity generate_image tool.") + "\n")
        f.write("Licence: Clean generated assets, 100% rights, no third-party copyright, no celebrities, adults 25+.\n")
        f.write("Language: Hebrew (HE) Only per directive (Claude & Dima 28.10.2026).\n\n")
        f.write("IMAGE PROMPTS AND ROLES:\n")
        f.write("-" * 60 + "\n")
        for slide_name, prompt in post['prompts'].items():
            f.write(f"{slide_name}:\nPrompt: \"{prompt}\"\n\n")
    print(f"  SOURCES.txt written to {sources_path}")
    print(f"=== {post_id} Complete! ===\n")

if __name__ == '__main__':
    # Render p15
    render_post('p15')
    print("p15 RENDER COMPLETE!")
