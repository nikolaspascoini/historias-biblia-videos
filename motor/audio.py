"""Original soundtrack + sound effects, synthesized with numpy, timed to the video's timeline."""
import json, math, subprocess, sys, wave
import numpy as np
import os
sys.path.insert(0, os.environ.get("BIBLIA_BASE", "/home/claude/biblia"))
import davi

SR = 44100
st, vd, starts, ends = davi.timeline()
TOTAL = ends[-1]
N = int(TOTAL * SR) + SR
rng = np.random.default_rng(7)

def t_(d): return np.arange(int(d * SR)) / SR
def add(buf, x, at, g=1.0):
    i = int(at * SR); j = min(len(buf), i + len(x))
    if j > i: buf[i:j] += g * x[: j - i]
def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)
def _unused(x, cut):
    a = math.exp(-2 * math.pi * cut / SR); y = np.empty_like(x); acc = 0.0
    # vectorised one-pole via lfilter-like cumulative approach (chunked python loop is ok for short sfx)
    for i in range(len(x)): acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y
def lp_fft(x, cut):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= 1 / (1 + (f / cut) ** 4); return np.fft.irfft(X, len(x))
def bp_fft(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X *= (1 / (1 + (f / hi) ** 4)) * (1 / (1 + (lo / np.maximum(f, 1)) ** 4)); return np.fft.irfft(X, len(x))

# ------------------------------------------------------------------ music
music = np.zeros((N, 2))
def pad(notes, at, d, g, bright=6):
    tt = t_(d); env = np.minimum(1, tt / 1.6) * np.minimum(1, (d - tt) / 1.6).clip(0, 1)
    for m in notes:
        f = mtof(m)
        for ch, det in ((0, 0.997), (1, 1.003)):
            s = np.zeros_like(tt)
            for n in range(1, bright + 1):
                s += np.sin(2 * np.pi * f * det * n * tt + n * 0.7) / n ** 1.3
            s *= (1 + 0.15 * np.sin(2 * np.pi * 0.21 * tt + ch))
            add(music[:, ch], s * env, at, g / len(notes))

def drum(at, g=1.0, f0=95, f1=45):
    tt = t_(1.2); f = f1 + (f0 - f1) * np.exp(-tt * 9)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 3.2)
    s += 0.25 * lp_fft(rng.standard_normal(len(tt)), 900) * np.exp(-tt * 18)
    for ch in (0, 1): add(music[:, ch], s, at, g)

# sections (from the story's MUSIC config; defaults = Davi e Golias)
MC = getattr(davi, "MUSIC", None) or {"tension": 12, "land": (16, 0.55), "hope": 17, "fast": 14}
t_face = starts[MC["tension"]]; t_land = starts[MC["land"][0]] + (ends[MC["land"][0]] - starts[MC["land"][0]]) * MC["land"][1]; t_msg = starts[MC["hope"]]
t_fast = starts[MC.get("fast", MC["tension"])]
def piano(m, at, d, g):
    f = mtof(m); tt = t_(d)
    s = np.zeros_like(tt)
    for n, amp in ((1, 1.0), (2, 0.45), (3, 0.22), (4, 0.12), (5, 0.06)):
        s += amp * np.sin(2 * np.pi * f * n * tt) * np.exp(-tt * (1.6 + 0.9 * n))
    s *= np.minimum(1, tt / 0.004)
    pan = 0.5 + 0.35 * math.sin(m)
    add(music[:, 0], s * (1.1 - pan), at, g); add(music[:, 1], s * (0.1 + pan), at, g)

if MC.get("style") == "piano":
    # piano + cordas: Am F C G (vi-IV-I-V), ~70 bpm, arpejo em colcheias
    prog = [[57, 60, 64], [53, 57, 60], [48, 52, 55], [55, 59, 62]]
    bass = [45, 41, 48, 43]
    beat = 60 / 70; bar = beat * 4; t = 0.0; i = 0
    while t < TOTAL + bar:
        ch = prog[i % 4]
        grow = min(1.0, 0.45 + 0.55 * t / max(1.0, TOTAL * 0.6))
        pad(ch + [ch[0] + 12], t, bar + 1.6, 0.42 * grow, bright=5)          # cordas
        pad([bass[i % 4] - 12], t, bar + 1.6, 0.35, bright=3)
        piano(bass[i % 4], t, 3.0, 0.32)
        arp = [ch[0], ch[1], ch[2], ch[0] + 12, ch[2], ch[1], ch[0] + 12, ch[1] + 12]
        for j, m in enumerate(arp):
            piano(m + 12, t + j * beat / 2, 2.2, 0.20 * (1.0 if j == 0 else 0.8))
        if t > TOTAL * 0.45 and i % 2 == 0:  # melodia simples na segunda metade
            piano(ch[2] + 24, t + beat * 2, 2.5, 0.16)
        t += bar; i += 1
else:
    dark = [[50, 53, 57], [46, 50, 53], [48, 52, 55], [45, 48, 52]]          # Dm Bb C A(m)
    hope = [[46, 50, 53, 58], [53, 57, 60, 65], [48, 52, 55, 60], [50, 54, 57, 62]]  # Bb F C D
    cl = 4.0
    t = 0.0; i = 0
    while t < t_face - 0.5:
        pad(dark[i % 4], t, cl + 1.6, 0.55); pad([dark[i % 4][0] - 12], t, cl + 1.6, 0.5, bright=3); t += cl; i += 1
    t = t_face - 0.5; i = 0
    while t < t_land:
        pad([m + 0 for m in dark[(i // 2) % 2]], t, 2.0 + 1.6, 0.7, bright=8); pad([38], t, 3.6, 0.6, bright=3); t += 2.0; i += 1
    beat = 0.6; t = t_face
    while t < t_land - 0.1:
        drum(t, 0.9 if (round((t - t_face) / beat) % 2 == 0) else 0.55); t += beat
        if t > t_fast: beat = 0.4
    drum(t_land, 1.6, 120, 35)
    t = t_msg - 1.0; i = 0
    while t < TOTAL:
        pad(hope[i % 4], t, cl + 1.6, 0.6, bright=7); pad([hope[i % 4][0] - 12], t, cl + 1.6, 0.45, bright=3); t += cl; i += 1

# fade in / out
fade = np.ones(N); fi = int(1.5 * SR); fade[:fi] = np.linspace(0, 1, fi)
fo = int(2.0 * SR); e = int(TOTAL * SR); fade[e - fo:e] = np.linspace(1, 0, fo); fade[e:] = 0
music *= fade[:, None]

# ------------------------------------------------------------------ sfx
sfx = np.zeros((N, 2))
def stereo(x, at, g=1.0, pan=0.0):
    add(sfx[:, 0], x, at, g * (1 - max(0, pan))); add(sfx[:, 1], x, at, g * (1 + min(0, pan)))

def whoosh(at, d=0.55, g=0.35):
    tt = t_(d); n = rng.standard_normal(len(tt))
    env = np.sin(np.pi * tt / d) ** 2
    x = bp_fft(n, 300, 2500) * env
    stereo(x, at - d * 0.5, g)

def boom(at, g=0.9, f0=70, dec=2.0):
    tt = t_(3.0); f = 32 + (f0 - 32) * np.exp(-tt * 4)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * dec)
    x += 0.5 * lp_fft(rng.standard_normal(len(tt)), 250) * np.exp(-tt * 2.5)
    stereo(x, at, g)

def clank(at, g=0.35, pan=0.0):
    tt = t_(1.2); x = np.zeros_like(tt)
    for f, a in [(523, 1), (1247, .7), (1968, .5), (2780, .35), (3611, .25)]:
        x += a * np.sin(2 * np.pi * f * tt) * np.exp(-tt * (5 + f / 900))
    x += 0.6 * rng.standard_normal(len(tt)) * np.exp(-tt * 60)
    stereo(x / 2.5, at, g, pan)

def tok(at, g=0.4):
    tt = t_(0.25); x = np.sin(2 * np.pi * 900 * tt * np.exp(-tt * 6)) * np.exp(-tt * 35)
    stereo(x, at, g)

def chime(at, g=0.25):
    tt = t_(2.0); x = np.zeros_like(tt)
    for f in (1318.5, 1975.5, 2637): x += np.sin(2 * np.pi * f * tt) * np.exp(-tt * 3)
    stereo(x / 3, at, g)

def whir(at, d, g=0.35):
    tt = t_(d); n = bp_fft(rng.standard_normal(len(tt)), 400, 1800)
    rate = 1.6 + 1.8 * tt / d
    am = 0.5 + 0.5 * np.sin(2 * np.pi * np.cumsum(rate) / SR) ** 8
    stereo(n * am * np.minimum(1, tt / 0.4), at, g)

def impact(at, g=0.8):
    tt = t_(0.6); x = rng.standard_normal(len(tt)) * np.exp(-tt * 25)
    x = bp_fft(x, 800, 6000) + 1.5 * np.sin(2 * np.pi * 60 * tt) * np.exp(-tt * 8)
    stereo(x, at, g)

# ambience: wind through the whole piece
wind_d = TOTAL; tt = t_(wind_d)
w = bp_fft(rng.standard_normal(len(tt)), 150, 900) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * tt) ** 2)
stereo(w, 0, 0.12)

# transitions
for k in range(1, len(starts)): whoosh(starts[k], g=0.22)

def S(k): return starts[k], ends[k] - starts[k]
def thunder(at, g=0.8):
    tt = t_(3.5); n = lp_fft(rng.standard_normal(len(tt)), 400)
    env = np.exp(-tt * 1.2) * (0.6 + 0.4 * np.sin(2 * np.pi * 3 * tt) ** 2)
    x = n * env; x[: int(0.05 * SR)] *= np.linspace(0, 1, int(0.05 * SR))
    x += 0.6 * bp_fft(rng.standard_normal(len(tt)), 1500, 6000) * np.exp(-tt * 14)
    stereo(x, at, g)
def roar(at, d=1.6, g=0.6):
    tt = t_(d); f = 90 + 40 * np.sin(np.pi * tt / d)
    x = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.4 + bp_fft(rng.standard_normal(len(tt)), 150, 1200)
    x = lp_fft(x, 900) * np.sin(np.pi * tt / d) ** 0.6
    stereo(x, at, g)
def splash(at, g=0.7):
    tt = t_(1.5); x = bp_fft(rng.standard_normal(len(tt)), 300, 7000) * np.exp(-tt * 4) * np.minimum(1, tt / 0.02)
    x += 0.8 * np.sin(2 * np.pi * 70 * tt) * np.exp(-tt * 10)
    stereo(x, at, g)
def hammer(at, g=0.5):
    tt = t_(0.35); x = np.sin(2 * np.pi * 220 * tt) * np.exp(-tt * 30) + 0.6 * rng.standard_normal(len(tt)) * np.exp(-tt * 70)
    stereo(lp_fft(x, 3000), at, g)
def bed(a, d, kind="water", g=0.18):
    tt = t_(d)
    if kind == "water": x = bp_fft(rng.standard_normal(len(tt)), 500, 4000) * 0.5
    elif kind == "storm": x = lp_fft(rng.standard_normal(len(tt)), 700) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * tt) ** 2)
    elif kind == "rain": x = bp_fft(rng.standard_normal(len(tt)), 1500, 9000) * 0.6
    else: x = bp_fft(rng.standard_normal(len(tt)), 150, 900)
    stereo(x * np.minimum(1, tt / 0.6) * np.minimum(1, (d - tt) / 0.6).clip(0, 1), a, g)
def stone_roll(at, d=1.2, g=0.5):
    tt = t_(d); x = lp_fft(rng.standard_normal(len(tt)), 250) * (0.7 + 0.3 * np.sin(2 * np.pi * 9 * tt)) * np.sin(np.pi * tt / d)
    stereo(x, at, g); boom(at + d - 0.1, g * 0.6, 60, 4)

FX = dict(whoosh=whoosh, boom=boom, clank=clank, tok=tok, chime=chime, whir=whir, impact=impact, thunder=thunder, roar=roar,
          splash=splash, hammer=hammer, bed=bed, stone_roll=stone_roll, land=t_land)
if getattr(davi, "STORY", None):
    davi.story_sfx(S, FX)
else:
    a, D = S(2); boom(a, 0.7)
    a, D = S(7); chime(a, 0.3)
    a, D = S(10); clank(a + 1.0, 0.45, -0.3); clank(a + 1.15, 0.35, 0.3)
    a, D = S(11); bed(a, D, "water"); [tok(a + D * 0.35 + i * D * 0.11, 0.5) for i in range(5)]
    a, D = S(14); rel = D * 0.62; whir(a, rel, 0.4); whoosh(a + rel + 0.15, 0.4, 0.6)
    a, D = S(15); impact(a, 0.9)
    boom(t_land, 1.0, 80, 1.6)
    a, D = S(18); chime(a + 0.1, 0.25); chime(a + D * 0.25, 0.2); chime(a + D * 0.45, 0.25)

# ------------------------------------------------------------------ write
def wr(name, x, peak):
    x = x / (np.abs(x).max() + 1e-9) * peak
    with wave.open(name, "wb") as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((x[: int(TOTAL * SR)] * 32767).astype("<i2").tobytes())
wr(f"{davi.OUT}/music.wav", music, 0.8)
wr(f"{davi.OUT}/sfx.wav", sfx, 0.9)
print("total", round(TOTAL, 2), "face", round(t_face, 1), "land", round(t_land, 1))
