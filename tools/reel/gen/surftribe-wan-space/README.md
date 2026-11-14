---
title: surftribe wan
sdk: gradio
sdk_version: 6.14.0
app_file: app.py
hardware: zero-a10g
suggested_hardware: zero-a10g
startup_duration_timeout: 1h
pinned: false
license: apache-2.0
---

Private ZeroGPU Space: Wan 2.2 I2V A14B (Lightning 4 steps, fp8 + AoTI, from
zerogpu-aoti/wan2-2-fp8da-aoti-faster) and SeedVR2-3B upscale (from
ymo2017/seedvr2-upscale, Apache-2.0) with tight per-function GPU durations.
Endpoints: gen, upscale, gen_up, pack, probe, estimate, diag.
Results are uploaded to dmikonov/surftribe-gen-inputs/gen/.
