"""Synthetic sfx + music bed (copy of surftribe-drafts scripts/tip1/audio_fx.py, 19.10). usage: python3 audio_fx.py <seconds>  (writes $S17/tip1, default /s17/tip1)"""
import numpy as np, wave, sys, os
SR = 48000
O = os.environ.get('S17', '/s17') + '/tip1'; os.makedirs(O, exist_ok=True)
rng = np.random.default_rng(7)
def save(fn, x):
    x = np.clip(x, -1, 1); y = (x * 32767).astype(np.int16)
    if y.ndim == 1: y = np.stack([y, y], 1)
    w = wave.open(fn, 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(y.tobytes()); w.close()
def lp(x, a):
    y = np.zeros_like(x); s = 0.0
    for i in range(len(x)): s += a * (x[i] - s); y[i] = s
    return y
# whoosh: noise through a sweeping one-pole band, 0.45 s
n = int(0.45 * SR); t = np.arange(n) / SR
noise = rng.standard_normal(n)
env = np.sin(np.pi * np.clip(t / 0.45, 0, 1)) ** 2
sweep = 0.02 + 0.25 * (t / 0.45)
y = np.zeros(n); s1 = s2 = 0.0
for i in range(n):
    s1 += sweep[i] * (noise[i] - s1); s2 += 0.02 * (s1 - s2); y[i] = s1 - s2
wh = y / np.abs(y).max() * env * 0.6
save(f'{O}/whoosh.wav', wh)
# impact: low thump + splash noise
n = int(0.9 * SR); t = np.arange(n) / SR
thump = np.sin(2 * np.pi * (70 - 30 * t) * t) * np.exp(-t * 9)
spl = rng.standard_normal(n); spl = spl - lp(spl, 0.05); spl = lp(spl, 0.35) * np.exp(-t * 5) * (1 - np.exp(-t * 200))
imp = 0.8 * thump + 0.5 * spl / np.abs(spl).max()
save(f'{O}/impact.wav', imp / np.abs(imp).max() * 0.8)
# pop for stickers
n = int(0.12 * SR); t = np.arange(n) / SR
pop = np.sin(2 * np.pi * (900 - 2500 * t) * t) * np.exp(-t * 40)
save(f'{O}/pop.wav', pop * 0.5)
# music bed: 96 bpm, Am F C G, soft kick, clap, hats, bass, pad
T = float(sys.argv[1]) if len(sys.argv) > 1 else 24.0
bpm = 96; beat = 60 / bpm; N = int(T * SR); t = np.arange(N) / SR
mus = np.zeros(N)
roots = [57, 53, 48, 55]  # A3 F3 C3 G3 (midi)
chords = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
f = lambda m: 440 * 2 ** ((m - 69) / 12)
bar = 4 * beat
for b in range(int(T / beat) + 1):
    st = int(b * beat * SR)
    if st >= N: break
    k = np.arange(min(int(0.35 * SR), N - st)) / SR
    if b % 2 == 0: mus[st:st + len(k)] += 0.9 * np.sin(2 * np.pi * (110 * np.exp(-k * 18) + 45) * k) * np.exp(-k * 10)
    else:
        nz = rng.standard_normal(len(k)); nz = nz - lp(nz, 0.1); mus[st:st + len(k)] += 0.25 * nz * np.exp(-k * 22)
    for h in (0, 0.5):
        hs = int((b + h) * beat * SR)
        if hs >= N: continue
        kk = np.arange(min(int(0.05 * SR), N - hs)) / SR; nz = rng.standard_normal(len(kk)); nz = nz - lp(nz, 0.5)
        mus[hs:hs + len(kk)] += 0.07 * nz * np.exp(-kk * 80)
for c in range(int(T / bar) + 1):
    st = int(c * bar * SR)
    if st >= N: break
    L = min(int(bar * SR), N - st); k = np.arange(L) / SR; ch = chords[c % 4]
    pad = sum(np.sin(2 * np.pi * f(m) * k) + 0.3 * np.sin(2 * np.pi * 2 * f(m) * k + 0.4) for m in ch) / 3
    env = np.minimum(1, k / 0.25) * np.minimum(1, (bar - k) / 0.3)
    mus[st:st + L] += 0.16 * pad * env
    for q in range(4):
        bs = st + int(q * beat * SR)
        if bs >= N: continue
        kb = np.arange(min(int(beat * 0.9 * SR), N - bs)) / SR
        mus[bs:bs + len(kb)] += 0.35 * np.sin(2 * np.pi * f(roots[c % 4] - 12) * kb) * np.exp(-kb * 3)
fade = np.minimum(1, t / 0.6) * np.minimum(1, (T - t) / 1.2)
mus = mus * fade; mus = mus / np.abs(mus).max() * 0.7
save(f'{O}/music.wav', mus)
print('fx ok', T)
