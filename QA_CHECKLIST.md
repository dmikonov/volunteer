# SurfTribe SMM QA checklist (reviewer must answer every line PASS / FAIL with evidence)

Source: Dima's own rules from chats and memory. A visual or reel is shown to Dima or published only when every line is PASS.
The reviewer checks THESE rules first, general quality second. "Looks good" is not an answer: each line needs a measurement, a frame number or a quote.

## A. Text on screen (OCR every frame or every overlay PNG, list every string)
1. No full stop at the end of any headline, title, card, pill or on-screen line. (Captions under the post may use normal punctuation.)
2. No em dash or en dash anywhere, on screen or in caption. Hyphen-minus only.
3. No emoji anywhere.
4. Headlines in Rubik weight 800 (not 900). Same font in every reel. Subtitles must really render in Rubik: check the renderer log for font fallback (libass falls back to DejaVu with the variable Rubik file and Bold=-1; use the static RubikExtraBold.ttf).
5. Body text at least 44 px on the 1080 canvas; nothing smaller except the @handle footer. This includes text inside app screens and cards: do not paste raw app screenshots with small text, rebuild the card large.
6. Safe zone for reels: key text inside y 230-1440 and x 70-850 (right 230 px is the like/share rail). Measure with getBoundingClientRect, report numbers.
7. Text never covers a face or the key detail of the beat (the gear the line talks about). Subtitles over a torso or legs are acceptable; over a face never. Report bbox of text vs faces (Haar or similar) and vs the key detail.
8. Coral #FF5150 only as an accent, never the dominant colour of a frame.
9. Texts sound human: no "unlock, master, level up, game changer", no AI phrasing.

## B. Brand and message
10. It is clear who we are within the first 3 seconds (SurfTribe name or logo on screen) and again at the end (voice or text).
11. Exactly one ask (save, follow, or DM keyword).
12. Reels: hook taken from Dima's 10 hook formulas (memory, design-and-production.md), adapted without dashes. On screen at frame 0.
13. Facts checked against a named source (temps, numbers, gear). Units match the account (EN: °F with °C, HE: °C).
14. EN account never mentions Israel. HE account uses approved surf Hebrew (חרטום, לחרטם, לגלוש, ריילים, פייס, שולדר, קצף, טרטל רול, גלשן סופט).
15. GAL described only as "own surf AI, built from scratch, coming soon". No retreat content. No Ben (C0088/C0089), C0120 or Yarden photos.

## C. Picture
16. Real video for reels (live clips and montage), never a slideshow of slides.
17. Every shot checked at 0.1 s steps for AI artifacts: extra limbs, fingers, morphing boards, fins on the deck, leash attached to nobody, objects or people popping in, logos or text on clothes, melting foam, fake droplets.
18. People look 25+ and do not resemble a real celebrity.
19. No shot longer than about 2.5 s without a change; first frame has motion and the hook text.
20. Loop: last frame vs frame 0 SSIM (not pixel difference) at least 0.95 on the background region, and no double exposure during the crossfade.

## D. Sound
21. Voice natural, not robotic, not hoarse or "generated" sounding. Dima approves the voice before the full build.
22. Music quiet under the voice: voice at least 16 dB over music on every line, no pumping, no swell in pauses.
23. Music segment chosen by RMS analysis (highest-energy window), not simply the start of the track. Licence allows commercial use.
24. Loudness -14 LUFS (two-pass), true peak at most -1 dBTP, no clipping, audio covers the whole video.
25. Every spoken line matches the on-screen text of that beat.

## E. Publishing
26. AI label: caption line "AI-generated" and isAiGenerated flag where the tool supports it.
27. Location: Malibu, California for @surftribe_world, Tel Aviv for @surftribe_il (where the tool supports it; otherwise say so).
28. Caption: hook in the first 125 characters, max 5 hashtags, no emoji, no dashes.
29. Any date in copy verified with the clock tool and written with its weekday.
30. Nothing is published without Dima's explicit OK for that exact version.

## F. Lessons from rejected versions (do not repeat)
31. Slideshow of carousel slides is not a reel (rejected 15 Oct).
32. Loud music under the voice (rejected 15 Oct).
33. Fake-looking AI clip (zipping a wetsuit) shown to Dima (rejected 15 Oct). Hand to mouth reads as smoking.
34. Full stops in reel headlines (rejected 15 Oct).
35. Hoarse generic voice (rejected 15 Oct); voice is chosen by Dima from samples before the build.
36. No mention of who we are (rejected 15 Oct).
37. Burned-in subtitles are mandatory on reels (most viewers watch muted).
38. Subtitles sit where subtitles belong: horizontally centred (centre x = 540, measure left and right margins, difference at most 20 px) and at ONE fixed height for the whole reel (same y on every line, lower third, around y 1360). Never shifted to the left, never jumping between beats (rejected 15 Oct). Measure the bbox of every subtitle line and report.
39. No dead air: no gap in the voice longer than 0.6 s anywhere between the first and the last word, and no beat that holds a card longer than 0.6 s after the voice ends (rejected 15 Oct: 2 s of silence after "Save this"). Measure voice gaps on the voice-only track and report the longest one.
40. No clock time on @surftribe_world creatives (worldwide audience, "6 PM" means nothing): story pill says "NEW POST TODAY" with no time (rejected 15 Oct, EN story p02). Times are fine on @surftribe_il (one time zone). Open fix: GitHub issue dmikonov/volunteer#1 (EN_p03 to EN_p14).
