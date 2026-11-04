# surftribe-wan: свой ZeroGPU Space для клипов

## СНАЧАЛА (руками, 2 клика, API этого не умеет)

1. https://huggingface.co/spaces/dmikonov/surftribe-wan/settings -> Space hardware ->
   **ZeroGPU** (бесплатно для PRO). Сейчас Space стоит на cpu-basic: ключ
   `hardware: zero-a10g` в README железо не переключил, `diag` показывает
   `zero_gpu_env: false`, Wan не загружен. После переключения Space перезапустится
   и будет качать около 70 ГБ весов (до 30-60 мин, таймаут старта 1 ч).
2. Там же Variables and secrets -> New secret `HF_TOKEN` (fine-grained, write на
   `dmikonov/surftribe-gen-inputs`). Проверено: через MCP заголовок Authorization
   в Space не приходит (только `x-ip-token`), так что без секрета загрузка в
   датасет не работает. Проверка: `upload_check` должен вернуть `ok: true`.

Space: `dmikonov/surftribe-wan` (приватный, ZeroGPU, gradio 6.14).
Код: Wan 2.2 I2V A14B + Lightning (lightx2v) LoRA, fp8 + AoTI из
`zerogpu-aoti/wan2-2-fp8da-aoti-faster`; апскейл SeedVR2-3B из
`ymo2017/seedvr2-upscale` (код SeedVR2 Space сам скачивает из этого
Space при старте, веса из `ByteDance-Seed/SeedVR2-3B`).
Результаты: `dmikonov/surftribe-gen-inputs/gen/<out_name>.mp4`.
Копия исходников Space: `tools/reel/gen/surftribe-wan-space/` (правка: менять
файл и заливать через `hf_fs_write put hf://spaces/dmikonov/surftribe-wan/app.py`).

## Функции (api_name, MCP-имя `surftribe_wan_<api_name>`)

| api | что делает | GPU |
|---|---|---|
| `gen` | клип Wan 2.2 из стартовой картинки | да, своя формула |
| `upscale` | SeedVR2 1.5x / 2x / restore готового mp4 | да, своя формула |
| `gen_up` | gen + upscale подряд, два отдельных GPU-окна | да |
| `pack` | кадры целиком в один JPEG (как в vidgen-peek) | нет |
| `probe` | размер, fps, кадры | нет |
| `estimate` | сколько секунд GPU попросит вызов и сколько вызовов влезет в 40 мин | нет |
| `diag` | ошибки старта, версии, замеры последних 30 прогонов | нет |
| `upload_check` | пробная запись `gen/_selftest.txt` в датасет | нет |

### gen
`image_url` (URL или путь в датасете, напр. `gen_start/1921oct/k_low.webp`),
`image` (необязательная загрузка), `prompt`, `seconds=4` (16 fps, 4 с = 65 кадров,
максимум 5 с = 81), `res="480x832"` (ещё 832x480, 640x640, 720x1280, 1280x720),
`steps=4`, `seed=-1`, `negative_prompt=""` (пусто = стандартный),
`upload=True`, `out_name=""`, `gpu_secs=0` (0 = формула, иначе ручной duration).
Возвращает mp4 и JSON: `url` (прямая ссылка resolve/main/gen/...),
`cache` (`cache:<id>` для upscale/pack), `seed`, `frames`, `gpu_requested`,
`gpu_elapsed` (реальное время внутри GPU), `max_mem_gb`.

### upscale
`video_url` (`cache:<id>`, URL или путь в датасете), `mode="1.5x"`, `steps=1`,
`seed=666`, `upload=True`, `out_name=""`, `gpu_secs=0`.
480x832 -> 720x1248. Чанки по 5 кадров (больше падает на ZeroGPU).

### gen_up
Параметры gen + `mode`, `keep_raw=False` (сырой клип тоже в датасет как
`<out_name>_raw.mp4`). Возвращает апскейл и JSON с обоими замерами.

## Duration (формулы в app.py, константы можно менять через Variables Space)

- gen: `(4 + 8*f + steps*12.5*f^1.5) * 1.12`, где `f = frames*w*h / (81*832*624)`
- upscale: `(10 + ceil(frames/5) * 3.8 * area/(1280*720)) * 1.12`

| вариант | gen | upscale | цикл | на 2400 с |
|---|---|---|---|---|
| 480x832, 4 с, 4 шага | 38 с | 66 с | 104 с | 63 клипа без апскейла / 23 с апскейлом |
| 480x832, 3 с, 4 шага | 27 с | 53 с | 80 с | 88 / 30 |
| 480x832, 4 с, 6 шагов | 51 с | 66 с | 117 с | 47 / 20 |
| 720x1280, 4 с, 4 шага | 113 с | (не нужен) | 113 с | 21 |

Было: чужой Wan около 102 с + ymo2017 60 с = 162 с, около 14 циклов в день.
Цифры формул пока оценка (по замеру AoTI-репо: 125.85 с на 81 кадр 624x832,
20 шагов на целой RTX Pro 6000; ZeroGPU large = половина карты). Первый ночной
прогон уточнит: смотреть `gpu_elapsed` в ответе или `diag`.

Важно: по документации HF квота списывается по фактическому (effective)
времени, а duration проверяется заранее: вызов не стартует, если просит больше,
чем осталось квоты, и меньший duration даёт приоритет в очереди. Если реальное
время превысит duration, задачу могут оборвать, поэтому запас 12%.

## Как вызывать

MCP (из чата): `dynamic_space` invoke, space `dmikonov/surftribe-wan`,
tool `surftribe_wan_gen` / `surftribe_wan_upscale` / `surftribe_wan_gen_up` /
`surftribe_wan_pack` / `surftribe_wan_diag` / `surftribe_wan_estimate`.

gradio_client (GitHub Actions, нужен HF_TOKEN владельца, Space приватный):

```python
from gradio_client import Client
import json, os
c = Client("dmikonov/surftribe-wan", hf_token=os.environ["HF_TOKEN"])
vid, info = c.predict("gen_start/1921oct/k_low.webp", None, "surfer pops up and rides the wave",
                      4.0, "480x832", 4, -1, "", True, "k_low_v1", 0, api_name="/gen")
info = json.loads(info)            # info["url"] -> mp4 в датасете
vid, info2 = c.predict(info["cache"], "1.5x", 1, 666, True, "k_low_v1_up", 0, api_name="/upscale")
```

Скачать в CI: `curl -sSfLo out.mp4 https://huggingface.co/datasets/dmikonov/surftribe-gen-inputs/resolve/main/gen/k_low_v1_up.mp4`

## Токен для загрузки в датасет

Space берёт `HF_TOKEN` из секретов Space, а если его нет, то токен вызывающего
(заголовок Authorization; через MCP он не приходит, через gradio_client с
hf_token, скорее всего, приходит, но не проверено). Без токена клип всё равно
возвращается и лежит в `cache:<id>` до рестарта Space, его можно забрать через `pack`.

Квота ZeroGPU списывается с аккаунта вызывающего (Space получает `x-ip-token`),
то есть с PRO-квоты dmikonov.

## Ночная проверка (после сброса квоты около 01:00 по Израилю)

0. Сделано ли «СНАЧАЛА» (ZeroGPU + секрет), `upload_check` -> `ok: true`.
1. `diag`: `startup.wan == "ok"`, `startup.seedvr == "ok"`, `zero_gpu_env == true`.
   Если в `startup.wan` трейсбек, чинить по нему (GPU он не тратит).
2. Первый `gen` с запасом: `gpu_secs=60`, 480x832, 4 с, 4 шага. Записать `gpu_elapsed`.
3. Первый `upscale` с `gpu_secs=90` на `cache:` из шага 2. Записать `gpu_elapsed`,
   `build`, `max_mem_gb` (если OOM: Wan держит около 35 ГБ из 48 ГБ, тогда
   переменная Space `SV_GPU_SIZE=xlarge`, но это x2 квоты, или отдельный Space).
4. Подогнать `WAN_STEP` / `WAN_FIXED` / `SV_CHUNK` / `SV_FIXED` (Variables Space)
   под замер плюс 10%, дальше звать с `gpu_secs=0`.
5. Проверить, что `url` открывается и mp4 скачивается curl.
