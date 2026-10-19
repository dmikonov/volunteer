# Статусы рилс (ведёт ночная сборка)

| Дата | Тема | Файлы | Превью | Статус |
|---|---|---|---|---|
| Пн 19.10 | Смотри вперёд | reel_look_he.mp4, reel_look_en.mp4 | review/reel_look_*.mp4 | HE: ок Димы 18.10, ОПУБЛИКОВАН пробным 18.10 17:12 (media 18061159301795431, https://www.instagram.com/reel/Deo3nxbiQzZ/, graduation MANUAL). Повторно НЕ публиковать: 19.10 утром Дима сам переводит в профиль. EN: ждёт ок Димы |
| Вт 20.10 | Согнутые колени | reel_knees_he.mp4, reel_knees_en.mp4 | review/reel_knees_*.mp4 | собран 18.10 (v5, ревизор: готово), ждёт ок Димы |
| Ср 21.10 | Грести раньше (2 ИИ-кадра) | reel_paddle_he.mp4, reel_paddle_en.mp4 | review/reel_paddle_*.mp4 | собран 18.10 (v5, ревизор: готово), ждёт ок Димы |
| Чт 22.10 | Отбойное течение (rip) | reel_rip_he.mp4, reel_rip_en.mp4 | HE https://share.descript.com/view/kzHpRnSO1v8 , EN https://share.descript.com/view/y0q4NxpYf7p (Descript, unlisted) | собран 19.10 ночью (v3, слепой зритель: доработан контур течения и кадр с рукой), ждёт ок Димы. Интеграция заменена: прогноз → загрузка/разбор видео (21.10 уже прогноз, две одинаковые подряд нельзя). Мастер-файлы: Composio /mnt/files/reels/reel_rip_{he,en}.mp4 (HE 21.65 с, EN 22.28 с, -14.5 LUFS); HF-песочница 19.10 отвечает 402 Payment Required |
| без даты | 5 вещей до выхода в воду (HE-версия EN-рилса Demc-jyDzi6) | drafts tips/reel_beginners5_he.mp4 | review/reel_beginners5_he.mp4 | v2 18.10: пересобран из чистых исходников Coverr/Mixkit 1080p, подписи в стиле EN, голос F5-TTS Hebrew (голос 3 по выбору Димы, по фразам, лучший из 5 дублей), монтаж под голос. Ревизор: PASS. ОПУБЛИКОВАН пробным 18.10 21:00 по просьбе Димы (media 18021697727941162, https://www.instagram.com/reel/DepRuvpCPw7/, graduation MANUAL). Повторно НЕ публиковать. Сборка: tools/reel/dub/build_he.py + beginners5_he_v2.json |
| без даты | 5 вещей, вариант B (быстрый хук, 16 с) | out/reel_beginners5_he_B.mp4 (commit 189e1db) | Composio sl/R-QBsQvIr9 | 19.10: собран на GitHub Actions (бесплатно), голос F5 voice 3 с ручной огласовкой (הסטים=сетим, שעווה, ציון=циюн), ревизор: PASS. Ждёт ок Димы на пробный в @surftribe_il |

## Клипы по рилсам (не повторять в течение недели)
v3 (18.10, после ревизора): реальные клипы 17.10 не используем (повтор с «Как падать» v11 и техника в кадре не совпадала с советом). Все кадры сёрфинга сгенерированы (Z-Image Turbo + Wan 2.2), /s17/gen2/.
| Рилс | Сгенерированные |
|---|---|
| 19.10 look | l_down, l_nose, l_chin, l_along, l_along2, l_turn, l_turn2, l_recap |
| 20.10 knees | k_stiff, k_low, k_center, k_arms (gen2), k_arms (gen, FLUX) |
| 21.10 paddle | p_under, p_start, p_long, p_catch, p_ride |
| 22.10 rip | r_hook, r_wide, r_watch, r_stay, r_par, r_hand2 (Z-Image Turbo + Wan 2.2, 19.10) |
