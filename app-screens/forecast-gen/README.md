# Экран прогноза SurfTribe для интеграций в рилс

Точная копия экрана «תחזית / Forecast» из кода приложения (репозиторий dmikonov/-------, src/screens/ForecastScreen.tsx и компоненты), отрисованная в HTML с реальными данными и записанная в видео 1080x2338, как запись экрана телефона.

Логика оценки (computeSurfQuality, peakSurfWindow, summarizeDayQuality, localCoachAdvice, shoreVerdict) берётся из кода приложения при сборке и в этот публичный репозиторий не кладётся.

## Как собрать (ночная сессия)
1. add_repo dmikonov/------- (read), git clone --depth 1 в /home/claude/-------.
2. В этой папке: npm init -y; npm i esbuild@0.24.0 @mdi/js@7.4.47; cp /home/claude/-------/assets/fonts/Rubik-*.ttf .; node build.mjs (создаёт logic.js; пути в entry2.ts указывают на /home/claude/-------).
3. Данные: через Composio COMPOSIO_REMOTE_BASH_TOOL запросить Open-Meteo (marine + forecast, 7 дней, timezone спота) и вывести компактный JSON {t0, H:[[wave_height, wave_period, swell_period, swell_height, wave_dir, sea_temp, wind_ms, wind_dir, gusts_ms, air_temp, uv]...], sun:[[sunrise, sunset]...]}; сохранить в data.json. Рабочая папка до open-meteo сама не достучится.
   - HE: Тель-Авив 32.08, 34.76, timezone Asia/Jerusalem, spot «הילטון ימית תל אביב».
   - EN (без Израиля): Bali 8.66 ю.ш., 115.13 в.д., Asia/Makassar, spot «Bali - Canggu Batu Bolong», facing 230.
4. cfg.json: {lang, skill, day, hour, minute, clock, spot, facing (EN), focus: water|best|height|period|wind|chart, scrollAt, hlAt, dur, data}. Примеры: cfg_he_water.json и т.д.
5. python3 record.py cfg.json out.mp4 (кадры через Playwright, 30 fps). Для проверки: --still s.png --at 5.

Отличие от приложения: «лучшее окно» считается только по светлым часам (от восхода до заката), чтобы не показывать 04:00.
