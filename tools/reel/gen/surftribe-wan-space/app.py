# surftribe-wan: Wan 2.2 I2V A14B (Lightning/lightx2v, fp8 + AoTI) and SeedVR2-3B
# upscale in one private ZeroGPU Space, tuned to spend as little daily ZeroGPU
# quota per clip as possible.
#
# Wan part: zerogpu-aoti/wan2-2-fp8da-aoti-faster (same weights, LoRA fuse,
# fp8 quantization and AoTI blocks). SeedVR2 part: ymo2017/seedvr2-upscale
# (same chunked 5-frame path; its code tree is pulled from that Space at
# startup, byte-exact, see SEEDVR_CODE_REPO).
#
# Rules followed here:
# - Every @spaces.GPU function gets exactly the arrays it needs; all decoding,
#   resizing, mp4 encoding and the dataset upload run on CPU outside the GPU
#   window.
# - Each GPU function has its own duration formula (see the GPU-time model
#   constants), computed from the real frame count and size, which the CPU
#   wrapper passes in explicitly. gpu_secs > 0 overrides it.
# - Measured GPU-side time of every run goes into diag() so the constants can
#   be calibrated.

import gc
import hashlib
import io
import json
import math
import os
import random
import re
import sys
import tempfile
import time
import traceback
from pathlib import Path

import spaces  # must be imported before torch on ZeroGPU
import torch
import numpy as np
import gradio as gr
import requests
import cv2
import imageio
from PIL import Image
from huggingface_hub import HfApi, hf_hub_download, snapshot_download

APP_DIR = Path(__file__).resolve().parent
os.chdir(APP_DIR)
if str(APP_DIR) not in sys.path:
    sys.path.insert(0, str(APP_DIR))

T_BOOT = time.time()
STARTUP = {}  # name -> traceback text (or "ok")
CACHE = Path(tempfile.gettempdir()) / "stw"
CACHE.mkdir(parents=True, exist_ok=True)
RUNLOG = CACHE / "runs.jsonl"

DATASET = os.environ.get("OUT_DATASET", "dmikonov/surftribe-gen-inputs")
OUT_PREFIX = os.environ.get("OUT_PREFIX", "gen")

# ---------------------------------------------------------------------------
# GPU-time model, seconds on ZeroGPU "large" (half RTX Pro 6000 Blackwell).
# Reference point for Wan: the AoTI repo's own job measured 125.85 s for
# 81 frames 624x832, 20 steps on a FULL RTX Pro 6000 (about 5.7 s/step); half
# a card is about 2x slower, so ~11.5 s/step at the reference size.
# Calibrate with diag() -> runs[].gpu_elapsed after the first real runs.
# ---------------------------------------------------------------------------
WAN_REF = 81 * 832 * 624
WAN_FIXED = float(os.environ.get("WAN_FIXED", 4.0))  # attach + text/image encode
WAN_VAE = float(os.environ.get("WAN_VAE", 8.0))  # VAE enc/dec at reference size
WAN_STEP = float(os.environ.get("WAN_STEP", 12.5))  # one DiT step at reference size
SV_REF_AREA = 1280 * 720
SV_FIXED = float(os.environ.get("SV_FIXED", 10.0))  # runner build (3B DiT + VAE)
SV_CHUNK = float(os.environ.get("SV_CHUNK", 3.8))  # one 5-frame chunk at 1280x720 area
MARGIN = float(os.environ.get("GPU_MARGIN", 1.12))
QUOTA = 2400  # PRO daily ZeroGPU quota, seconds

ZERO = str(os.environ.get("SPACES_ZERO_GPU", "")).lower() in ("1", "true", "yes")


def _has_gpu():
    if ZERO:
        return True
    try:
        return torch.cuda.is_available()
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Wan 2.2 I2V A14B (copied from zerogpu-aoti/wan2-2-fp8da-aoti-faster)
# ---------------------------------------------------------------------------
MODEL_ID = "Wan-AI/Wan2.2-I2V-A14B-Diffusers"
FPS = 16
MIN_FRAMES = 9
MAX_FRAMES = 81
RES = {
    "480x832": (480, 832),
    "832x480": (832, 480),
    "640x640": (640, 640),
    "720x1280": (720, 1280),
    "1280x720": (1280, 720),
}
DEFAULT_NEG = "色调艳丽, 过曝, 静态, 细节模糊不清, 字幕, 风格, 作品, 画作, 画面, 静止, 整体发灰, 最差质量, 低质量, JPEG压缩残留, 丑陋的, 残缺的, 多余的手指, 画得不好的手部, 画得不好的脸部, 畸形的, 毁容的, 形态畸形的肢体, 手指融合, 静止不动的画面, 杂乱的背景, 三条腿, 背景人很多, 倒着走"

pipe = None
if not _has_gpu():
    STARTUP["wan"] = "skipped: no ZeroGPU/CUDA in this container (Space hardware is not ZeroGPU?)"
else:
    try:
        from diffusers.pipelines.wan.pipeline_wan_i2v import WanImageToVideoPipeline
        from diffusers.models.transformers.transformer_wan import WanTransformer3DModel
        from torchao.quantization import quantize_
        from torchao.quantization import Float8DynamicActivationFloat8WeightConfig
        from torchao.quantization import Int8WeightOnlyConfig

        pipe = WanImageToVideoPipeline.from_pretrained(
            MODEL_ID,
            transformer=WanTransformer3DModel.from_pretrained(
                "cbensimon/Wan2.2-I2V-A14B-bf16-Diffusers",
                subfolder="transformer",
                torch_dtype=torch.bfloat16,
                device_map="cuda",
            ),
            transformer_2=WanTransformer3DModel.from_pretrained(
                "cbensimon/Wan2.2-I2V-A14B-bf16-Diffusers",
                subfolder="transformer_2",
                torch_dtype=torch.bfloat16,
                device_map="cuda",
            ),
            torch_dtype=torch.bfloat16,
        ).to("cuda")

        pipe.load_lora_weights(
            "Kijai/WanVideo_comfy",
            weight_name="Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank128_bf16.safetensors",
            adapter_name="lightx2v",
        )
        pipe.load_lora_weights(
            "Kijai/WanVideo_comfy",
            weight_name="Lightx2v/lightx2v_I2V_14B_480p_cfg_step_distill_rank128_bf16.safetensors",
            adapter_name="lightx2v_2",
            load_into_transformer_2=True,
        )
        pipe.set_adapters(["lightx2v", "lightx2v_2"], adapter_weights=[1.0, 1.0])
        pipe.fuse_lora(adapter_names=["lightx2v"], lora_scale=3.0, components=["transformer"])
        pipe.fuse_lora(adapter_names=["lightx2v_2"], lora_scale=1.0, components=["transformer_2"])
        pipe.unload_lora_weights()

        quantize_(pipe.text_encoder, Int8WeightOnlyConfig())
        quantize_(pipe.transformer, Float8DynamicActivationFloat8WeightConfig())
        quantize_(pipe.transformer_2, Float8DynamicActivationFloat8WeightConfig())

        spaces.aoti_load(module=pipe.transformer, repo_id="cbensimon/WanTransformer3DModel-sm120-cu130-raa")
        spaces.aoti_load(module=pipe.transformer_2, repo_id="cbensimon/WanTransformer3DModel-sm120-cu130-raa")
        STARTUP["wan"] = "ok"
    except Exception:
        pipe = None
        STARTUP["wan"] = traceback.format_exc()[-3000:]
    gc.collect()

# ---------------------------------------------------------------------------
# SeedVR2-3B (from ymo2017/seedvr2-upscale)
# ---------------------------------------------------------------------------
SEEDVR_CODE_REPO = os.environ.get("SEEDVR_CODE_REPO", "ymo2017/seedvr2-upscale")
SV_WEIGHTS = "ByteDance-Seed/SeedVR2-3B"
SV_CHUNK_FRAMES = 5  # measured limit on ZeroGPU (larger chunks trip the NVML assert)
SV_MAX_FRAMES = 161
SV_MAX_AREA = 2560 * 1440
SV_MODE_SCALE = {"restore": 1.0, "1.5x": 2.25, "2x": 4.0}
SV_INPUT_NOISE = 0.0
SV_OK = False
_runner = None

for k, v in (("MASTER_ADDR", "127.0.0.1"), ("MASTER_PORT", "12355"), ("RANK", "0"), ("WORLD_SIZE", "1"), ("LOCAL_RANK", "0")):
    os.environ.setdefault(k, v)

try:
    if not (APP_DIR / "projects" / "video_diffusion_sr" / "infer.py").exists():
        snapshot_download(
            repo_id=SEEDVR_CODE_REPO,
            repo_type="space",
            local_dir=str(APP_DIR),
            allow_patterns=["common/*", "configs_3b/*", "data/*", "models/*", "projects/*"],
        )
    from einops import rearrange
    from omegaconf import OmegaConf
    from torchvision.transforms import Compose, Lambda, Normalize
    from data.image.transforms.divisible_crop import DivisibleCrop
    from data.image.transforms.na_resize import NaResize
    from data.video.transforms.rearrange import Rearrange
    from common.config import load_config
    from common.distributed import init_torch
    from common.seed import set_seed
    from projects.video_diffusion_sr.infer import VideoDiffusionInfer
    from projects.video_diffusion_sr.color_fix import wavelet_reconstruction

    CKPT_DIR = APP_DIR / "ckpts"
    CKPT_DIR.mkdir(exist_ok=True)

    def _fetch(filename, target):
        if target.exists():
            return str(target)
        target.symlink_to(hf_hub_download(repo_id=SV_WEIGHTS, filename=filename))
        return str(target)

    DIT_CKPT = _fetch("seedvr2_ema_3b.pth", CKPT_DIR / "seedvr2_ema_3b.pth")
    VAE_CKPT = _fetch("ema_vae.pth", CKPT_DIR / "ema_vae.pth")
    POS_EMB = _fetch("pos_emb.pt", APP_DIR / "pos_emb.pt")
    NEG_EMB = _fetch("neg_emb.pt", APP_DIR / "neg_emb.pt")
    SV_OK = True
    STARTUP["seedvr"] = "ok"
except Exception:
    STARTUP["seedvr"] = traceback.format_exc()[-3000:]


# ---------------------------------------------------------------------------
# helpers (CPU)
# ---------------------------------------------------------------------------
def _num_frames(seconds):
    n = int(round(float(seconds) * FPS))
    n = (n // 4) * 4 + 1  # Wan needs (frames - 1) % 4 == 0
    return int(min(MAX_FRAMES, max(MIN_FRAMES, n)))


def wan_secs(w, h, frames, steps):
    f = frames * w * h / WAN_REF
    return int(math.ceil((WAN_FIXED + WAN_VAE * f + int(steps) * WAN_STEP * f ** 1.5) * MARGIN))


def _sv_area(w, h, mode):
    return int(min(w * h * SV_MODE_SCALE[mode], SV_MAX_AREA))


def sv_secs(frames, w, h, mode):
    chunks = math.ceil(frames / SV_CHUNK_FRAMES)
    a = _sv_area(w, h, mode) / SV_REF_AREA
    return int(math.ceil((SV_FIXED + chunks * SV_CHUNK * a) * MARGIN))


def _fit(img, w, h):
    img = img.convert("RGB")
    W, H = img.size
    tr = w / h
    if W / H > tr:
        nw = int(round(H * tr))
        left = (W - nw) // 2
        img = img.crop((left, 0, left + nw, H))
    else:
        nh = int(round(W / tr))
        top = (H - nh) // 2
        img = img.crop((0, top, W, top + nh))
    return img.resize((w, h), Image.LANCZOS)


def _dataset_url(path):
    return f"https://huggingface.co/datasets/{DATASET}/resolve/main/{path}"


def _download(url):
    key = hashlib.sha1(url.encode()).hexdigest()
    ext = os.path.splitext(url.split("?")[0])[1][:6] or ".bin"
    dst = CACHE / f"dl_{key}{ext}"
    if dst.exists() and dst.stat().st_size > 100:
        return str(dst)
    errs = []
    for u in (url, re.sub(r"/--replicas/[^/]+", "", url)):
        try:
            r = requests.get(u, timeout=180, headers={"User-Agent": "surftribe-wan"}, allow_redirects=True)
            if r.status_code == 200 and len(r.content) > 100:
                dst.write_bytes(r.content)
                return str(dst)
            errs.append(f"{r.status_code} {u[:160]}")
        except Exception as e:
            errs.append(repr(e)[:200])
    raise RuntimeError("download failed: " + " | ".join(errs))


def _resolve(src):
    """cache:<id> | http(s) URL | path inside the output dataset (e.g. gen/x.mp4) | local path."""
    src = (src or "").strip()
    if not src:
        raise ValueError("empty source")
    if src.startswith("cache:"):
        p = CACHE / (src[6:].split()[0] + ".mp4")
        if not p.exists():
            raise RuntimeError("cache miss (Space restarted?) " + src)
        return str(p)
    if src.startswith("http://") or src.startswith("https://"):
        return _download(src)
    if os.path.exists(src):
        return src
    return _download(_dataset_url(src.lstrip("/")))


def _read_video(path, max_frames):
    cap = cv2.VideoCapture(path)
    fps = cap.get(cv2.CAP_PROP_FPS) or float(FPS)
    out = []
    while len(out) < max_frames:
        ok, fr = cap.read()
        if not ok:
            break
        out.append(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB))
    cap.release()
    if not out:
        raise RuntimeError("no frames decoded from " + path)
    return np.stack(out), fps


def _write_mp4(frames, fps, path, crf=16):
    wr = imageio.get_writer(
        path,
        fps=fps,
        codec="libx264",
        quality=None,
        macro_block_size=1,
        ffmpeg_params=["-crf", str(int(crf)), "-preset", "medium", "-movflags", "+faststart"],
    )
    for f in frames:
        wr.append_data(f)
    wr.close()
    return path


def _token(request):
    t = os.environ.get("HF_TOKEN")
    if t:
        return t, "secret"
    try:
        a = request.headers.get("authorization") if request is not None else None
        if a and a.lower().startswith("bearer "):
            return a.split(" ", 1)[1].strip(), "caller"
    except Exception:
        pass
    return None, None


def _clean_name(name, default):
    name = re.sub(r"[^A-Za-z0-9._-]", "_", (name or "").strip())[:80].strip("._")
    if name.endswith(".mp4"):
        name = name[:-4]
    return name or default


def _upload(path, name, request):
    tok, src = _token(request)
    if not tok:
        return None, "no token: add Space secret HF_TOKEN (write access to the dataset)"
    try:
        HfApi(token=tok).upload_file(
            path_or_fileobj=path,
            path_in_repo=f"{OUT_PREFIX}/{name}.mp4",
            repo_id=DATASET,
            repo_type="dataset",
            commit_message=f"surftribe-wan: {name}",
        )
        return _dataset_url(f"{OUT_PREFIX}/{name}.mp4"), None
    except Exception as e:
        return None, f"upload failed (token from {src}): {repr(e)[:400]}"


def _log(rec):
    try:
        with open(RUNLOG, "a") as f:
            f.write(json.dumps(rec) + "\n")
    except Exception:
        pass


def _mem():
    try:
        return round(torch.cuda.max_memory_allocated() / 2**30, 2)
    except Exception:
        return None


# ---------------------------------------------------------------------------
# GPU functions (only tensor work inside)
# ---------------------------------------------------------------------------
def _wan_dur(img, prompt, neg, w, h, frames, steps, seed, gpu_secs):
    if gpu_secs and int(gpu_secs) > 0:
        return int(gpu_secs)
    return wan_secs(w, h, frames, steps)


@spaces.GPU(duration=_wan_dur)
def _wan_gpu(img, prompt, neg, w, h, frames, steps, seed, gpu_secs):
    t0 = time.perf_counter()
    out = pipe(
        image=img,
        prompt=prompt,
        negative_prompt=neg,
        height=int(h),
        width=int(w),
        num_frames=int(frames),
        guidance_scale=1.0,
        guidance_scale_2=1.0,
        num_inference_steps=int(steps),
        generator=torch.Generator(device="cuda").manual_seed(int(seed)),
    ).frames[0]
    fr = (np.clip(np.asarray(out, dtype=np.float32), 0.0, 1.0) * 255.0).round().astype(np.uint8)
    return fr, time.perf_counter() - t0, _mem()


def _ensure_runner():
    global _runner
    if _runner is not None:
        return _runner
    if not torch.distributed.is_initialized():
        init_torch(cudnn_benchmark=False)
    runner = VideoDiffusionInfer(load_config(os.path.join("./configs_3b", "main.yaml")))
    OmegaConf.set_readonly(runner.config, False)
    runner.configure_dit_model(device="cuda", checkpoint=DIT_CKPT)
    runner.configure_vae_model()
    try:
        runner.vae.set_causal_slicing(split_size=None, memory_device="same")
    except Exception as exc:
        print(f"[vae] could not disable slicing: {exc}", flush=True)
    if hasattr(runner.vae, "set_memory_limit"):
        runner.vae.set_memory_limit(**runner.config.vae.memory_limit)
    _runner = runner
    return _runner


def _sv_window(runner, raw, transform, text_embeds):
    t = torch.from_numpy(np.ascontiguousarray(raw)).to("cuda").float().div_(255.0).permute(0, 3, 1, 2)
    ori_t = t.size(0)
    need = (5 - ori_t) if ori_t <= 4 else ((4 - ((ori_t - 1) % 4)) % 4)
    if need:
        t = torch.cat([t, t[-1:].repeat(need, 1, 1, 1)], dim=0)
    cond = transform(t)
    reference = rearrange(cond, "c t h w -> t c h w")
    latents = runner.vae_encode([cond])
    noise = [torch.randn_like(x) for x in latents]
    aug = [torch.randn_like(x) for x in latents]

    def _add_noise(x, a):
        tt = torch.tensor([1000.0], device="cuda") * SV_INPUT_NOISE
        shape = torch.tensor(x.shape[1:], device="cuda")[None]
        return runner.schedule.forward(x, a, runner.timestep_transform(tt, shape))

    conditions = [runner.get_condition(n, task="sr", latent_blur=_add_noise(l, a)) for n, a, l in zip(noise, aug, latents)]
    with torch.autocast("cuda", torch.bfloat16, enabled=True):
        videos = runner.inference(noises=noise, conditions=conditions, dit_offload=False, **text_embeds)
    s = videos[0]
    s = rearrange(s[:, None], "c t h w -> t c h w") if s.ndim == 3 else rearrange(s, "c t h w -> t c h w")
    s = wavelet_reconstruction(s.float(), reference[: s.size(0)].float())  # color fix on GPU
    s = s[:ori_t]
    s = rearrange(s, "t c h w -> t h w c").clamp(-1, 1).mul_(0.5).add_(0.5).mul_(255).round().to(torch.uint8)
    return s.cpu().numpy()


def _sv_dur(frames_np, mode, steps, seed, gpu_secs):
    if gpu_secs and int(gpu_secs) > 0:
        return int(gpu_secs)
    n, h, w = frames_np.shape[0], frames_np.shape[1], frames_np.shape[2]
    return sv_secs(n, w, h, mode)


_SV_KW = {"size": os.environ["SV_GPU_SIZE"]} if os.environ.get("SV_GPU_SIZE") else {}


@spaces.GPU(duration=_sv_dur, **_SV_KW)
@torch.no_grad()
def _sv_gpu(frames_np, mode, steps, seed, gpu_secs):
    t0 = time.perf_counter()
    mem0 = round(torch.cuda.memory_allocated() / 2**30, 2)
    runner = _ensure_runner()
    t_build = time.perf_counter() - t0
    runner.config.diffusion.cfg.scale = 1.0
    runner.config.diffusion.cfg.rescale = 0.0
    runner.config.diffusion.timesteps.sampling.steps = int(steps)
    runner.configure_diffusion()
    set_seed(int(seed) % (2**32), same_across_ranks=True)
    text_embeds = {
        "texts_pos": [torch.load(POS_EMB).to("cuda")],
        "texts_neg": [torch.load(NEG_EMB).to("cuda")],
    }
    h, w = frames_np.shape[1], frames_np.shape[2]
    area = _sv_area(w, h, mode)
    transform = Compose([
        NaResize(resolution=area ** 0.5, mode="area", downsample_only=False),
        Lambda(lambda x: torch.clamp(x, 0.0, 1.0)),
        DivisibleCrop((16, 16)),
        Normalize(0.5, 0.5),
        Rearrange("t c h w -> c t h w"),
    ])
    outs = []
    for s in range(0, frames_np.shape[0], SV_CHUNK_FRAMES):
        outs.append(_sv_window(runner, frames_np[s : s + SV_CHUNK_FRAMES], transform, text_embeds))
        gc.collect()
        torch.cuda.empty_cache()
    out = np.concatenate(outs, axis=0)
    return out, time.perf_counter() - t0, {"build": round(t_build, 2), "mem_before_gb": mem0, "max_mem_gb": _mem()}


# ---------------------------------------------------------------------------
# public endpoints (CPU wrappers)
# ---------------------------------------------------------------------------
def _gen_core(image_url, image, prompt, seconds, res, steps, seed, negative_prompt, gpu_secs):
    if pipe is None:
        raise RuntimeError("Wan pipeline not loaded: " + str(STARTUP.get("wan"))[-600:])
    if res not in RES:
        raise ValueError(f"res must be one of {list(RES)}")
    w, h = RES[res]
    if image is not None and str(image).strip():
        src = image if not isinstance(image, dict) else (image.get("path") or image.get("url"))
        img = Image.open(_resolve(str(src)))
    else:
        img = Image.open(_resolve(image_url))
    img = _fit(img, w, h)
    frames = _num_frames(seconds)
    seed = int(seed)
    if seed < 0:
        seed = random.randint(0, 2**31 - 1)
    req = _wan_dur(None, None, None, w, h, frames, steps, seed, gpu_secs)
    t0 = time.time()
    fr, gpu_el, mem = _wan_gpu(img, prompt or "", negative_prompt or DEFAULT_NEG, w, h, frames, int(steps), seed, int(gpu_secs or 0))
    wall = time.time() - t0
    rec = {"fn": "gen", "t": time.strftime("%Y-%m-%d %H:%M:%S"), "res": res, "frames": frames, "steps": int(steps),
           "gpu_requested": req, "gpu_elapsed": round(gpu_el, 2), "wall": round(wall, 2), "max_mem_gb": mem}
    _log(rec)
    return fr, seed, rec


def _save_and_upload(frames, fps, key, name, upload, request):
    path = str(CACHE / f"{key}.mp4")
    _write_mp4(frames, fps, path)
    url, err = (None, "upload disabled")
    if upload:
        url, err = _upload(path, name, request)
    return path, url, err


def gen(image_url: str = "", image: str = None, prompt: str = "", seconds: float = 4.0, res: str = "480x832",
        steps: int = 4, seed: int = -1, negative_prompt: str = "", upload: bool = True, out_name: str = "",
        gpu_secs: int = 0, request: gr.Request = None):
    """Wan 2.2 I2V A14B (Lightning, 4 steps): animate a start image into a 16 fps clip, save it to the dataset.

    Args:
        image_url: start image, http(s) URL or a path inside dmikonov/surftribe-gen-inputs (e.g. gen_start/1921oct/k_low.webp)
        image: optional uploaded start image (used instead of image_url)
        prompt: motion prompt
        seconds: clip length, 0.5-5 s at 16 fps (4 s = 65 frames)
        res: 480x832 (default, vertical), 832x480, 640x640, 720x1280, 1280x720
        steps: denoising steps, 4 is the Lightning default (6-8 for a bit more detail)
        seed: -1 for random
        negative_prompt: empty for the default Wan negative prompt
        upload: upload the mp4 to dmikonov/surftribe-gen-inputs/gen/<out_name>.mp4
        out_name: file name without extension (default: timestamp + seed)
        gpu_secs: override the ZeroGPU duration request, 0 = formula
    Returns:
        the mp4 and a JSON string with url, cache id, seed and measured GPU time.
    """
    try:
        fr, seed, rec = _gen_core(image_url, image, prompt, seconds, res, steps, seed, negative_prompt, gpu_secs)
        key = hashlib.sha1(f"gen|{image_url}|{prompt}|{res}|{fr.shape[0]}|{steps}|{seed}".encode()).hexdigest()[:16]
        name = _clean_name(out_name, time.strftime("%m%d_%H%M%S") + f"_s{seed}")
        path, url, err = _save_and_upload(fr, FPS, key, name, upload, request)
        info = dict(ok=True, url=url, upload_error=err, cache=f"cache:{key}", seed=seed,
                    w=int(fr.shape[2]), h=int(fr.shape[1]), **{k: rec[k] for k in ("frames", "steps", "gpu_requested", "gpu_elapsed", "wall", "max_mem_gb")})
        return path, json.dumps(info)
    except Exception:
        return None, json.dumps({"ok": False, "error": traceback.format_exc()[-1500:]})


def _up_core(path, mode, steps, seed, gpu_secs):
    if not SV_OK:
        raise RuntimeError("SeedVR2 not loaded: " + str(STARTUP.get("seedvr"))[-600:])
    if mode not in SV_MODE_SCALE:
        raise ValueError(f"mode must be one of {list(SV_MODE_SCALE)}")
    frames_np, fps = _read_video(path, SV_MAX_FRAMES)
    n, h, w = frames_np.shape[:3]
    req = sv_secs(n, w, h, mode) if not (gpu_secs and int(gpu_secs) > 0) else int(gpu_secs)
    t0 = time.time()
    out, gpu_el, extra = _sv_gpu(frames_np, mode, int(steps), int(seed), int(gpu_secs or 0))
    wall = time.time() - t0
    rec = {"fn": "upscale", "t": time.strftime("%Y-%m-%d %H:%M:%S"), "mode": mode, "frames": int(n), "in": f"{w}x{h}",
           "out": f"{out.shape[2]}x{out.shape[1]}", "gpu_requested": req, "gpu_elapsed": round(gpu_el, 2), "wall": round(wall, 2), **extra}
    _log(rec)
    return out, fps, rec


def upscale(video_url: str, mode: str = "1.5x", steps: int = 1, seed: int = 666, upload: bool = True,
            out_name: str = "", gpu_secs: int = 0, request: gr.Request = None):
    """SeedVR2-3B one-step video upscale (5-frame chunks), save the result to the dataset.

    Args:
        video_url: cache:<id> from gen, http(s) mp4 URL, or a path inside dmikonov/surftribe-gen-inputs (e.g. gen/x.mp4)
        mode: 1.5x (default, 480x832 -> 720x1248), 2x, or restore (same size)
        steps: 1-4, 1 is the SeedVR2 default
        seed: random seed
        upload: upload the mp4 to dmikonov/surftribe-gen-inputs/gen/<out_name>.mp4
        out_name: file name without extension (default: timestamp + _up)
        gpu_secs: override the ZeroGPU duration request, 0 = formula
    Returns:
        the mp4 and a JSON string with url, cache id and measured GPU time.
    """
    try:
        path = _resolve(video_url)
        out, fps, rec = _up_core(path, mode, steps, seed, gpu_secs)
        key = hashlib.sha1(f"up|{video_url}|{mode}|{steps}|{seed}".encode()).hexdigest()[:16]
        name = _clean_name(out_name, time.strftime("%m%d_%H%M%S") + "_up")
        p, url, err = _save_and_upload(out, fps, key, name, upload, request)
        return p, json.dumps(dict(ok=True, url=url, upload_error=err, cache=f"cache:{key}", **rec))
    except Exception:
        return None, json.dumps({"ok": False, "error": traceback.format_exc()[-1500:]})


def gen_up(image_url: str = "", image: str = None, prompt: str = "", seconds: float = 4.0, res: str = "480x832",
           steps: int = 4, seed: int = -1, negative_prompt: str = "", mode: str = "1.5x", upload: bool = True,
           out_name: str = "", keep_raw: bool = False, gpu_secs: int = 0, request: gr.Request = None):
    """Full cycle in one call: Wan 2.2 clip, then SeedVR2 upscale (two separate GPU windows, each with its own duration).

    Args:
        image_url: start image, http(s) URL or a path inside dmikonov/surftribe-gen-inputs
        image: optional uploaded start image (used instead of image_url)
        prompt: motion prompt
        seconds: clip length, 0.5-5 s at 16 fps
        res: 480x832 (default), 832x480, 640x640, 720x1280, 1280x720
        steps: Wan denoising steps (4)
        seed: -1 for random
        negative_prompt: empty for the default
        mode: SeedVR2 mode, 1.5x (default), 2x, restore
        upload: upload the upscaled mp4 to gen/<out_name>.mp4
        out_name: file name without extension (default: timestamp + seed)
        keep_raw: also upload the raw Wan clip as gen/<out_name>_raw.mp4
        gpu_secs: override for the Wan GPU window only, 0 = formula
    Returns:
        the upscaled mp4 and a JSON string with both steps' info.
    """
    try:
        fr, seed, rec_g = _gen_core(image_url, image, prompt, seconds, res, steps, seed, negative_prompt, gpu_secs)
        base = hashlib.sha1(f"gen|{image_url}|{prompt}|{res}|{fr.shape[0]}|{steps}|{seed}".encode()).hexdigest()[:16]
        name = _clean_name(out_name, time.strftime("%m%d_%H%M%S") + f"_s{seed}")
        raw_path, raw_url, raw_err = _save_and_upload(fr, FPS, base, name + "_raw", bool(upload and keep_raw), request)
        out, fps, rec_u = _up_core(raw_path, mode, 1, 666, 0)
        key = hashlib.sha1(f"up|cache:{base}|{mode}".encode()).hexdigest()[:16]
        p, url, err = _save_and_upload(out, fps, key, name, upload, request)
        return p, json.dumps(dict(ok=True, url=url, upload_error=err, cache=f"cache:{key}", raw_cache=f"cache:{base}",
                                  raw_url=raw_url, seed=seed, gen=rec_g, upscale=rec_u,
                                  gpu_requested_total=rec_g["gpu_requested"] + rec_u["gpu_requested"],
                                  gpu_elapsed_total=round(rec_g["gpu_elapsed"] + rec_u["gpu_elapsed"], 2)))
    except Exception:
        return None, json.dumps({"ok": False, "error": traceback.format_exc()[-1500:]})


def pack(video_url: str, start: int = 0, count: int = 16, cols: int = 4, quality: int = 95) -> str:
    """Full-resolution frames [start, start+count) tiled cols per row into one high-quality JPEG (4:4:4).

    Args:
        video_url: cache:<id>, http(s) mp4 URL, or a path inside dmikonov/surftribe-gen-inputs
        start: first frame index
        count: number of frames
        cols: frames per row
        quality: JPEG quality
    """
    fr, _ = _read_video(_resolve(video_url), 100000)
    sel = fr[int(start): int(start) + int(count)]
    h, w = sel[0].shape[:2]
    cols = int(cols)
    rows = (len(sel) + cols - 1) // cols
    canvas = Image.new("RGB", (cols * w, rows * h), (0, 0, 0))
    for k, a in enumerate(sel):
        canvas.paste(Image.fromarray(a), ((k % cols) * w, (k // cols) * h))
    out = CACHE / ("pack_" + hashlib.sha1(f"{video_url}|{start}|{count}|{cols}".encode()).hexdigest()[:10] + ".jpg")
    canvas.save(out, quality=int(quality), subsampling=0)
    return str(out)


def probe(video_url: str) -> str:
    """Size, fps, frame count and duration of a video (cache:<id>, URL or dataset path).

    Args:
        video_url: cache:<id>, http(s) mp4 URL, or a path inside dmikonov/surftribe-gen-inputs
    """
    try:
        p = _resolve(video_url)
        fr, fps = _read_video(p, 100000)
        n, h, w = fr.shape[:3]
        return f"{w}x{h} fps={fps:.3f} frames={n} dur={n / fps:.3f}s bytes={os.path.getsize(p)}"
    except Exception:
        return "ERR " + traceback.format_exc()[-900:]


def estimate(seconds: float = 4.0, res: str = "480x832", steps: int = 4, mode: str = "1.5x") -> str:
    """CPU only: the ZeroGPU durations this Space will request and how many runs fit into the 40 min PRO quota.

    Args:
        seconds: clip length
        res: Wan resolution
        steps: Wan steps
        mode: SeedVR2 mode
    """
    w, h = RES[res]
    n = _num_frames(seconds)
    g = wan_secs(w, h, n, steps)
    if mode in SV_MODE_SCALE:
        u = sv_secs(n, w, h, mode)
    else:
        u = 0
    return json.dumps({"frames": n, "gen_secs": g, "upscale_secs": u, "cycle_secs": g + u,
                       "gens_per_quota": QUOTA // g, "cycles_per_quota": QUOTA // max(1, g + u)})


def diag() -> str:
    """CPU only: startup status (errors), versions, token availability and the last 30 measured runs."""
    runs = []
    try:
        runs = [json.loads(x) for x in RUNLOG.read_text().splitlines()[-30:]]
    except Exception:
        pass
    vers = {}
    for m in ("torch", "diffusers", "transformers", "torchao", "gradio", "spaces", "huggingface_hub", "peft"):
        try:
            vers[m] = __import__(m).__version__
        except Exception as e:
            vers[m] = repr(e)[:80]
    return json.dumps({"uptime_s": int(time.time() - T_BOOT), "zero_gpu_env": ZERO, "startup": STARTUP,
                       "wan_loaded": pipe is not None, "seedvr_ready": SV_OK, "hf_token_secret": bool(os.environ.get("HF_TOKEN")),
                       "dataset": DATASET, "model": {"WAN_FIXED": WAN_FIXED, "WAN_VAE": WAN_VAE, "WAN_STEP": WAN_STEP,
                       "SV_FIXED": SV_FIXED, "SV_CHUNK": SV_CHUNK, "MARGIN": MARGIN}, "versions": vers, "runs": runs})


def upload_check(request: gr.Request = None) -> str:
    """CPU only: checks that the Space can write to the output dataset (uploads a tiny gen/_selftest.txt)."""
    names = []
    try:
        names = sorted(k.lower() for k in request.headers.keys()) if request is not None else []
    except Exception:
        pass
    tok, src = _token(request)
    if not tok:
        return json.dumps({"ok": False, "error": "no token (no HF_TOKEN secret, no Authorization header)", "headers": names})
    try:
        HfApi(token=tok).upload_file(
            path_or_fileobj=io.BytesIO(time.strftime("%Y-%m-%d %H:%M:%S").encode()),
            path_in_repo=f"{OUT_PREFIX}/_selftest.txt",
            repo_id=DATASET,
            repo_type="dataset",
            commit_message="surftribe-wan: upload check",
        )
        return json.dumps({"ok": True, "token_from": src, "url": _dataset_url(f"{OUT_PREFIX}/_selftest.txt")})
    except Exception as e:
        return json.dumps({"ok": False, "token_from": src, "error": repr(e)[:500], "headers": names})


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="surftribe wan") as demo:
    gr.Markdown("### surftribe-wan: Wan 2.2 I2V (4 steps) + SeedVR2 1.5x, results go to the dataset")
    with gr.Row():
        with gr.Column():
            i_url = gr.Textbox(label="image_url (URL or dataset path)")
            i_img = gr.Image(type="filepath", label="or upload start image")
            i_prompt = gr.Textbox(label="prompt", lines=3)
            with gr.Row():
                i_sec = gr.Number(value=4.0, label="seconds")
                i_res = gr.Dropdown(list(RES), value="480x832", label="res")
                i_steps = gr.Number(value=4, precision=0, label="steps")
                i_seed = gr.Number(value=-1, precision=0, label="seed")
            i_neg = gr.Textbox(label="negative prompt (empty = default)")
            with gr.Row():
                i_mode = gr.Dropdown(list(SV_MODE_SCALE), value="1.5x", label="upscale mode")
                i_upl = gr.Checkbox(value=True, label="upload to dataset")
                i_raw = gr.Checkbox(value=False, label="keep raw (gen_up)")
                i_name = gr.Textbox(label="out_name")
                i_gpu = gr.Number(value=0, precision=0, label="gpu_secs override")
            with gr.Row():
                b_gen = gr.Button("gen", variant="primary")
                b_gu = gr.Button("gen + upscale")
                b_est = gr.Button("estimate")
                b_diag = gr.Button("diag")
        with gr.Column():
            o_vid = gr.Video(label="result")
            o_info = gr.Textbox(label="info", lines=8)
    with gr.Row():
        u_src = gr.Textbox(label="video (cache:<id>, URL, dataset path)")
        u_steps = gr.Number(value=1, precision=0, label="upscale steps")
        u_seed = gr.Number(value=666, precision=0, label="upscale seed")
        b_up = gr.Button("upscale")
    with gr.Row():
        p_start = gr.Number(value=0, precision=0, label="start")
        p_count = gr.Number(value=16, precision=0, label="count")
        p_cols = gr.Number(value=4, precision=0, label="cols")
        p_q = gr.Number(value=95, precision=0, label="quality")
        b_pack = gr.Button("pack")
        b_probe = gr.Button("probe")
    o_pack = gr.Image(type="filepath", label="pack")

    b_gen.click(gen, [i_url, i_img, i_prompt, i_sec, i_res, i_steps, i_seed, i_neg, i_upl, i_name, i_gpu],
                [o_vid, o_info], api_name="gen", concurrency_limit=1)
    b_gu.click(gen_up, [i_url, i_img, i_prompt, i_sec, i_res, i_steps, i_seed, i_neg, i_mode, i_upl, i_name, i_raw, i_gpu],
               [o_vid, o_info], api_name="gen_up", concurrency_limit=1)
    b_up.click(upscale, [u_src, i_mode, u_steps, u_seed, i_upl, i_name, i_gpu], [o_vid, o_info],
               api_name="upscale", concurrency_limit=1)
    b_pack.click(pack, [u_src, p_start, p_count, p_cols, p_q], [o_pack], api_name="pack")
    b_probe.click(probe, [u_src], [o_info], api_name="probe")
    b_est.click(estimate, [i_sec, i_res, i_steps, i_mode], [o_info], api_name="estimate")
    b_diag.click(diag, [], [o_info], api_name="diag")
    gr.Button("upload check").click(upload_check, [], [o_info], api_name="upload_check")

demo.queue().launch(mcp_server=True, ssr_mode=False, show_error=True)
