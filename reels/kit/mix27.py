import json, subprocess as sp, numpy as np
D = '/home/claude/work/series/reels/r27'; A = '/home/claude/work/series/reels/guess25/aud'; SR = 48000; T = 23.4; N = int(T * SR)
def load(fn):
    return np.frombuffer(sp.run(['ffmpeg', '-v', 'error', '-i', fn, '-ac', '2', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout, np.float32).reshape(-1, 2).copy()
def rms(x): return float(np.sqrt(np.mean(x ** 2)) + 1e-9)
vo = load(f'{D}/vo.wav')[:N]; vo = np.pad(vo, ((0, N - len(vo)), (0, 0))); act = np.abs(vo).mean(1) > 0.01; vr = rms(vo[act])
m = load(f'{A}/music.mp3'); m = np.concatenate([m, m[::-1]])[:N]; m = np.pad(m, ((0, N - len(m)), (0, 0)))   # 15 s window, mirrored to cover 22 s
m *= vr / rms(m) * 10 ** (-21 / 20); tt = np.arange(N) / SR
m *= np.clip(tt / 0.2, 0, 1)[:, None] * np.clip((T - tt) / 0.4, 0.2, 1)[:, None]
oc = load(f'{A}/x1195.mp3'); oc = np.tile(oc, (N // len(oc) + 1, 1))[:N]; oc *= vr / rms(oc) * 10 ** (-27 / 20)
mix = vo + m + oc
sp.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', f'{D}/raw.wav'], input=mix.astype(np.float32).tobytes(), check=True)
r = sp.run(['ffmpeg', '-hide_banner', '-i', f'{D}/raw.wav', '-af', 'loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
J = json.loads(r[r.rindex('{'):])
sp.run(['ffmpeg', '-v', 'error', '-y', '-i', f'{D}/raw.wav', '-af', f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={J['input_i']}:measured_TP={J['input_tp']}:measured_LRA={J['input_lra']}:measured_thresh={J['input_thresh']}:offset={J['target_offset']}:linear=true,aresample=48000", f'{D}/mix.wav'], check=True)
print('music under voice dB', round(20 * np.log10(rms(m[act]) / vr), 1))
r = sp.run(['ffmpeg', '-hide_banner', '-i', f'{D}/mix.wav', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
print([l.strip() for l in r.splitlines() if l.strip().startswith(('I:', 'Peak:'))][-2:])
