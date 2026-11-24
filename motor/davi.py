import math, os, re, subprocess, sys, json, random
import numpy as np
import cairo
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1080, 1920, 30
BASE = os.environ.get("BIBLIA_BASE", "/home/claude/biblia")
OUT = f"{BASE}/out"
VOICE = f"{BASE}/voz.mp3"
LEAD = 0.15
XF = 0.35
os.makedirs(OUT, exist_ok=True)

TEXT = ("O maior guerreiro do exército inimigo tinha quase três metros de altura. Durante quarenta dias, ele desafiou Israel inteiro. "
        "Seu nome era Golias. Todo dia ele gritava: mandem um homem para lutar comigo. E ninguém tinha coragem. Até que um garoto chegou ao acampamento. "
        "Ele não era soldado. Era um pastor de ovelhas, que só tinha ido levar comida para os irmãos. O nome dele era Davi. Davi ouviu o desafio e disse: eu vou. "
        "O rei tentou vestir nele a própria armadura, mas era pesada demais. Então Davi tirou tudo. Pegou o cajado, a funda, e escolheu cinco pedras lisas no riacho. "
        "Quando viu o menino, Golias riu. E Davi respondeu: você vem contra mim com espada e lança. Eu vou contra você em nome do Senhor. "
        "Davi correu, girou a funda e soltou uma única pedra. Ela acertou a testa do gigante. E Golias caiu com o rosto no chão. "
        "Às vezes, o gigante na sua frente parece grande demais. Mas você não luta sozinho. Gostou dessa história? Curte e compartilha. "
        "E se você quiser ajudar as orações a chegarem em mais pessoas, clique no link da bio.")
SENTS = re.split(r'(?<=[.?!])\s+', TEXT)
DISP = [("três metros", "3 metros"), ("quarenta dias", "40 dias"), ("cinco pedras", "5 pedras")]

# ---------------------------------------------------------------- timing
def dur(p):
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", p]).decode())

def silences(p):
    e = subprocess.run(["ffmpeg", "-hide_banner", "-i", p, "-af", "silencedetect=noise=-32dB:d=0.22", "-f", "null", "-"], capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", e)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", e)]
    return [(a, b) for a, b in zip(st, en)]

def sentence_times():
    D = dur(VOICE); sil = silences(VOICE)
    mids = [(a + b) / 2 for a, b in sil]
    tot = sum(len(s) for s in SENTS); acc = 0; ends = []
    for s in SENTS[:-1]:
        acc += len(s); est = D * acc / tot
        cand = [m for m in mids if abs(m - est) < 2.2 and (not ends or m > ends[-1] + 0.4)]
        ends.append(min(cand, key=lambda m: abs(m - est)) if cand else est)
    ends.append(D)
    starts = [0.0] + ends[:-1]
    return [(LEAD + a, LEAD + b) for a, b in zip(starts, ends)], D

# ---------------------------------------------------------------- drawing helpers
INK = (0.07, 0.04, 0.07)

def hexc(h, a=1.0):
    h = h.lstrip('#'); return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def P(t, s, d): return ease((t - s) / d)

SKIES = {
    "dusk":  ["#1c1236", "#5a2a5e", "#c9573e", "#f3a54f", "#ffd98a"],
    "night": ["#05060f", "#0f1636", "#25305e", "#3d3f74", "#5b4f7c"],
    "dawn":  ["#2a2f6b", "#7a5aa8", "#f08a5d", "#ffc97a", "#fff1c4"],
    "storm": ["#07090f", "#121a28", "#1f2a3a", "#2f3b4c", "#46505f"],
    "day":   ["#2f5f9e", "#4f86c6", "#86b4e3", "#c7e0f4", "#fff4d8"],
    "moon":  ["#04050c", "#0b1230", "#18245a", "#2b3a78", "#53609c"],
    "red":   ["#1a0710", "#4a0f1f", "#9b1d24", "#e0532e", "#ffb15a"],
}

def sky(ctx, mood="dusk", sun=(540, 1240), sun_r=260, horizon=1300):
    cols = SKIES[mood]
    g = cairo.LinearGradient(0, 0, 0, horizon)
    for i, c in enumerate(cols): g.add_color_stop_rgba(i / (len(cols) - 1), *hexc(c))
    ctx.set_source(g); ctx.rectangle(0, 0, W, horizon + 2); ctx.fill()
    if sun:
        x, y = sun
        rg = cairo.RadialGradient(x, y, 0, x, y, sun_r * 3.2)
        rg.add_color_stop_rgba(0, *hexc(cols[-1], 0.85)); rg.add_color_stop_rgba(0.3, *hexc(cols[-2], 0.35)); rg.add_color_stop_rgba(1, *hexc(cols[-2], 0))
        ctx.set_source(rg); ctx.rectangle(0, 0, W, horizon + 2); ctx.fill()
        ctx.set_source_rgba(*hexc("#fff4d6", 0.95 if mood != "night" else 0.9)); ctx.arc(x, y, sun_r, 0, 2 * math.pi); ctx.fill()

def stars(ctx, a=1.0, seed=3):
    rnd = random.Random(seed)
    for _ in range(140):
        x, y, r = rnd.uniform(0, W), rnd.uniform(0, 1100), rnd.uniform(1, 3)
        ctx.set_source_rgba(1, 1, 1, a * rnd.uniform(0.3, 0.9)); ctx.arc(x, y, r, 0, 6.3); ctx.fill()

def hills(ctx, horizon=1300, shift=0.0, layers=("#3a1f3d", "#24142a", "#140a16")):
    for i, c in enumerate(layers):
        base = horizon + i * 70; amp = 60 + i * 25; f = 0.004 + i * 0.0015; ph = shift * (0.3 + i * 0.5) + i * 1.7
        ctx.move_to(0, H)
        for x in range(0, W + 21, 20):
            y = base - amp * (0.5 + 0.5 * math.sin(x * f + ph)) - 25 * math.sin(x * f * 2.7 + ph * 1.3)
            ctx.line_to(x, y)
        ctx.line_to(W, H); ctx.close_path(); ctx.set_source_rgba(*hexc(c)); ctx.fill()

def ground(ctx, y=1480):
    g = cairo.LinearGradient(0, y - 40, 0, H)
    g.add_color_stop_rgba(0, *hexc("#120810")); g.add_color_stop_rgba(1, *hexc("#050205"))
    ctx.set_source(g); ctx.rectangle(0, y - 40, W, H); ctx.fill()

def rays(ctx, x, y, n=14, a=0.18, rot=0.0, length=2600, color="#fff3c4"):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rot)
    for i in range(n):
        ang = i * 2 * math.pi / n
        ctx.move_to(0, 0); ctx.arc(0, 0, length, ang - 0.07, ang + 0.07); ctx.close_path()
        ctx.set_source_rgba(*hexc(color, a)); ctx.fill()
    ctx.restore()

def ink(ctx, a=1.0): ctx.set_source_rgba(INK[0], INK[1], INK[2], a)

def limb(ctx, x0, y0, ang, L, w):
    x1, y1 = x0 + L * math.sin(ang), y0 + L * math.cos(ang)
    ctx.set_line_width(w); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(x0, y0); ctx.line_to(x1, y1); ctx.stroke()
    return x1, y1

def person(ctx, x, y, h, face=1, armF=0.2, armB=-0.15, stride=0.08, lean=0.0, giant=False, staff=False, sling=None,
           spear=False, shield=False, helmet=False, armor=0.0, a=1.0, bob=0.0, head_tilt=0.0, mouth=0.0,
           robe=False, crown=False, kneel=False, beard=False, glow=0.0, hood=False, long_hair=False):
    """Unit figure: feet at (0,0), head top at about -1. face=1 looks right."""
    if glow > 0:
        rg = cairo.RadialGradient(x, y - h * 0.55, 0, x, y - h * 0.55, h * 0.9)
        rg.add_color_stop_rgba(0, 1, 0.96, 0.8, 0.55 * glow); rg.add_color_stop_rgba(1, 1, 0.96, 0.8, 0)
        ctx.set_source(rg); ctx.arc(x, y - h * 0.55, h * 0.9, 0, 6.3); ctx.fill()
    ctx.save(); ctx.translate(x, y); ctx.rotate(lean); ctx.scale(h * face, h)
    ctx.translate(0, -bob)
    ink(ctx, a)
    bw = 1.35 if giant else 1.0
    if kneel:
        ctx.translate(0, 0.30)
        ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.set_line_width(0.08)
        ctx.move_to(0, -0.42); ctx.line_to(0.16, -0.32); ctx.line_to(-0.2, -0.31); ctx.stroke()
    elif not robe:
        limb(ctx, -0.04 * bw, -0.42, -stride, 0.43, 0.075 * bw); ink(ctx, a)
        limb(ctx, 0.04 * bw, -0.42, stride, 0.43, 0.075 * bw)
    else:
        limb(ctx, -0.03, -0.2, -stride * 0.6, 0.21, 0.06); ink(ctx, a)
        limb(ctx, 0.03, -0.2, stride * 0.6, 0.21, 0.06)
    # back arm
    sx, sy = -0.02, -0.78
    hbx, hby = limb(ctx, sx, sy, armB, 0.38, 0.06 * bw)
    if shield:
        ctx.save(); ctx.translate(hbx - 0.02, hby - 0.06); ctx.scale(0.16, 0.22); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    # torso / tunic
    if robe:
        ctx.move_to(-0.11, -0.82); ctx.line_to(0.11, -0.82); ctx.line_to(0.19, -0.05 if not kneel else -0.30); ctx.line_to(-0.19, -0.05 if not kneel else -0.30); ctx.close_path(); ctx.fill()
    else:
        ctx.move_to(-0.11 * bw, -0.82); ctx.line_to(0.11 * bw, -0.82); ctx.line_to(0.16 * bw, -0.30); ctx.line_to(-0.16 * bw, -0.30); ctx.close_path(); ctx.fill()
    # head
    ctx.save(); ctx.translate(0.0, -0.92); ctx.rotate(head_tilt)
    if long_hair:
        ctx.move_to(-0.07, -0.05); ctx.curve_to(-0.02, -0.12, 0.06, -0.1, 0.06, -0.03); ctx.line_to(0.0, 0.0)
        ctx.curve_to(-0.02, 0.12, -0.04, 0.2, -0.03, 0.26); ctx.line_to(-0.14, 0.24); ctx.curve_to(-0.13, 0.1, -0.11, 0.0, -0.07, -0.05); ctx.close_path(); ctx.fill()
    ctx.arc(0, 0, 0.075 * (1.1 if giant else 1.0), 0, 6.3); ctx.fill()
    ctx.move_to(0.065, -0.005); ctx.line_to(0.095, 0.015); ctx.line_to(0.07, 0.03); ctx.close_path(); ctx.fill()  # nose
    if giant or beard:
        ctx.move_to(-0.06, 0.02); ctx.curve_to(-0.02, 0.13, 0.05, 0.12, 0.08, 0.03); ctx.close_path(); ctx.fill()  # beard
    if hood:
        ctx.move_to(-0.1, 0.06); ctx.curve_to(-0.12, -0.14, 0.06, -0.15, 0.06, -0.04); ctx.line_to(-0.03, -0.02); ctx.line_to(-0.04, 0.09); ctx.close_path(); ctx.fill()
    elif not giant and not long_hair:
        for cx, cy in [(-0.06, -0.05), (-0.02, -0.075), (0.03, -0.07), (-0.075, 0.0)]:
            ctx.arc(cx, cy, 0.035, 0, 6.3); ctx.fill()  # curly hair
    if crown:
        ctx.move_to(-0.075, -0.05); ctx.line_to(-0.075, -0.15); ctx.line_to(-0.04, -0.1); ctx.line_to(0, -0.17); ctx.line_to(0.04, -0.1); ctx.line_to(0.075, -0.15); ctx.line_to(0.075, -0.05); ctx.close_path(); ctx.fill()
    if helmet:
        ctx.move_to(-0.09, -0.01); ctx.curve_to(-0.09, -0.12, 0.09, -0.12, 0.09, -0.01); ctx.close_path(); ctx.fill()
        ctx.move_to(-0.03, -0.09); ctx.line_to(0.0, -0.2); ctx.line_to(0.03, -0.09); ctx.close_path(); ctx.fill()
    if mouth > 0:
        ctx.set_source_rgba(1, 0.85, 0.6, 0.0)
    ctx.restore(); ink(ctx, a)
    # front arm
    hfx, hfy = limb(ctx, 0.04, sy, armF, 0.38, 0.06 * bw)
    if spear:
        ctx.set_line_width(0.025); ctx.move_to(hfx, hfy + 0.35); ctx.line_to(hfx, hfy - 0.75); ctx.stroke()
        ctx.move_to(hfx - 0.035, hfy - 0.72); ctx.line_to(hfx, hfy - 0.88); ctx.line_to(hfx + 0.035, hfy - 0.72); ctx.close_path(); ctx.fill()
    if staff:
        ctx.set_line_width(0.028); ctx.move_to(hfx + 0.01, hfy + 0.42); ctx.line_to(hfx + 0.02, hfy - 0.55); ctx.stroke()
        ctx.arc_negative(hfx + 0.07, hfy - 0.55, 0.05, math.pi, 0); ctx.stroke()
    if sling is not None:
        r = 0.32; sxp, syp = hfx + r * math.cos(sling), hfy + r * math.sin(sling)
        ctx.set_line_width(0.012); ctx.move_to(hfx, hfy); ctx.line_to(sxp, syp); ctx.stroke()
        ctx.arc(sxp, syp, 0.03, 0, 6.3); ctx.fill()
    if armor > 0:  # oversized armor: helmet + chest plate (drawn in metal colour)
        ctx.set_source_rgba(0.42, 0.40, 0.45, a * armor)
        ctx.rectangle(-0.2, -0.86, 0.4, 0.42); ctx.fill()
        ctx.move_to(-0.13, -0.9); ctx.curve_to(-0.15, -1.13, 0.15, -1.13, 0.13, -0.9); ctx.close_path(); ctx.fill()
        ctx.set_source_rgba(0.75, 0.72, 0.68, a * armor * 0.6); ctx.set_line_width(0.012)
        ctx.rectangle(-0.2, -0.86, 0.4, 0.42); ctx.stroke()
    ctx.restore()

def sheep(ctx, x, y, s, a=1.0, step=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.set_source_rgba(0.13, 0.08, 0.12, a)
    for dx in (-0.25, 0.25):
        for k in (-0.05, 0.05):
            ctx.set_line_width(0.05); ctx.move_to(dx + k, -0.15); ctx.line_to(dx + k + 0.04 * math.sin(step + dx * 9), 0.0); ctx.stroke()
    for cx, cy, r in [(-0.25, -0.3, 0.17), (0, -0.36, 0.2), (0.22, -0.3, 0.17), (-0.1, -0.22, 0.17), (0.1, -0.22, 0.17)]:
        ctx.arc(cx, cy, r, 0, 6.3); ctx.fill()
    ctx.save(); ctx.translate(0.42, -0.38); ctx.scale(0.13, 0.09); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.restore()

def tent(ctx, x, y, w, h, a=1.0):
    ink(ctx, a); ctx.move_to(x - w / 2, y); ctx.line_to(x, y - h); ctx.line_to(x + w / 2, y); ctx.close_path(); ctx.fill()
    ctx.set_source_rgba(0.95, 0.6, 0.3, 0.35 * a); ctx.move_to(x - w * 0.08, y); ctx.line_to(x, y - h * 0.45); ctx.line_to(x + w * 0.08, y); ctx.close_path(); ctx.fill()

def dust(ctx, x, y, p, n=26, seed=1, spread=380):
    rnd = random.Random(seed)
    for _ in range(n):
        ang = rnd.uniform(math.pi * 1.05, math.pi * 1.95); sp = rnd.uniform(0.4, 1.0)
        dx = math.cos(ang) * spread * sp * ease(p); dy = math.sin(ang) * spread * 0.5 * sp * ease(p)
        r = rnd.uniform(20, 55) * (0.5 + p)
        ctx.set_source_rgba(0.55, 0.38, 0.32, 0.55 * (1 - p)); ctx.arc(x + dx, y + dy, r, 0, 6.3); ctx.fill()

def serif_title(ctx, text, y, size, a=1.0, color="#fff3d6", spacing=0.12):
    ctx.select_font_face("Noto Serif CJK HK", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    ctx.set_font_size(size)
    widths = [ctx.text_extents(c).x_advance for c in text]
    total = sum(widths) + spacing * size * (len(text) - 1)
    if text:
        top = y + min(ctx.text_extents(c).y_bearing for c in text)
        if top < 335: y += 335 - top
    x = W / 2 - total / 2
    for c, w in zip(text, widths):
        ctx.move_to(x + 4, y + 5); ctx.set_source_rgba(0, 0, 0, 0.45 * a); ctx.show_text(c)
        ctx.move_to(x, y); ctx.set_source_rgba(*hexc(color, a)); ctx.show_text(c)
        x += w + spacing * size

def zoom(ctx, t, D, z0=1.0, z1=1.06, cx=W / 2, cy=H * 0.62):
    z = z0 + (z1 - z0) * clamp(t / max(D, 0.01))
    ctx.translate(cx, cy); ctx.scale(z, z); ctx.translate(-cx, -cy)

# ---------------------------------------------------------------- scenes  (ctx, t, D)
GY = 1500  # ground line where feet stand

def sc_giant(ctx, t, D):
    zoom(ctx, t, D, 1.12, 1.0, cy=1100)
    sky(ctx, "dusk", (300, 1230), 220); hills(ctx, 1320); ground(ctx, GY + 30)
    for i in range(7):
        person(ctx, 120 + i * 50 + (i % 2) * 12, GY + 20 + (i % 3) * 8, 150, face=1, armF=0.1, shield=True, spear=(i % 2 == 0), a=0.9)
    person(ctx, 760, GY + 40, 980, face=-1, giant=True, helmet=True, spear=True, shield=True, armF=0.25, armB=-0.1, stride=0.06,
           bob=0.004 * math.sin(t * 2))
    a = P(t, 0.4, 0.6)
    ctx.save(); ctx.set_source_rgba(1, 1, 1, 0.7 * a); ctx.set_line_width(4); ctx.move_to(560, 520); ctx.line_to(560, 1520); ctx.stroke()
    for yy in (520, 1520): ctx.move_to(540, yy); ctx.line_to(580, yy); ctx.stroke()
    ctx.restore()

def sc_days(ctx, t, D):
    k = clamp(t / (D * 0.85))
    day = 1 + int(k * 39.999)
    ang = math.pi * (k * 39 % 1.0)
    mood = "night" if math.sin(ang) < 0.25 else "dusk"
    sky(ctx, mood, (540 - 420 * math.cos(ang), 1300 - 700 * math.sin(ang)), 120)
    if mood == "night": stars(ctx, 0.8)
    hills(ctx, 1320, shift=t * 0.2); ground(ctx, GY + 30)
    person(ctx, 540, GY + 30, 760, face=-1, giant=True, helmet=True, spear=True, shield=True, armF=0.2 + 0.1 * math.sin(t * 5), a=1)
    serif_title(ctx, f"DIA {day}", 470, 150, P(t, 0.1, 0.4))

def sc_name_golias(ctx, t, D):
    zoom(ctx, t, D, 1.0, 1.08, cy=900)
    sky(ctx, "red", (540, 900), 330, horizon=1700)
    person(ctx, 540, 2350, 2300, face=-1, giant=True, helmet=True, armF=0.1, shield=False)
    serif_title(ctx, "GOLIAS", 520, 190, P(t, 0.15, 0.5))

def sc_shout(ctx, t, D):
    zoom(ctx, t, D, 1.0, 1.05, cy=1000)
    sky(ctx, "red", (820, 1200), 200); hills(ctx, 1320); ground(ctx, GY + 30)
    person(ctx, 600, GY + 40, 950, face=-1, giant=True, helmet=True, spear=True, shield=True, armF=-2.6 + 0.15 * math.sin(t * 6),
           stride=0.12, bob=0.006 * abs(math.sin(t * 6)))
    for i in range(4):
        p = ((t * 0.9 + i * 0.25) % 1.0)
        ctx.set_source_rgba(1, 0.9, 0.75, 0.55 * (1 - p)); ctx.set_line_width(7)
        ctx.arc(520, 640, 60 + p * 420, math.pi * 0.85, math.pi * 1.25); ctx.stroke()

def sc_hiding(ctx, t, D):
    zoom(ctx, t, D, 1.0, 1.05)
    sky(ctx, "night", (820, 380), 90); stars(ctx, 0.7); hills(ctx, 1320, layers=("#1d1838", "#130f26", "#0a0814")); ground(ctx, GY + 30)
    for i, (x, w) in enumerate([(170, 330), (540, 400), (910, 330)]):
        tent(ctx, x, GY + 10, w, 300 + (i % 2) * 60)
    for i in range(5):
        x = 140 + i * 200
        peek = 0.5 + 0.5 * math.sin(t * 2.2 + i)
        person(ctx, x, GY + 140 - 60 * peek * P(t, 0.2, 0.5), 230, face=1 if i % 2 else -1, shield=True, armB=0.4, a=1)
    ctx.set_source_rgba(0.04, 0.02, 0.05, 1); ctx.rectangle(0, GY + 60, W, H); ctx.fill()

def walking(t, speed=6.0):
    s = math.sin(t * speed); return 0.28 * s, 0.25 * s, -0.25 * s, 0.01 * abs(s)

def sc_boy_arrives(ctx, t, D):
    sky(ctx, "dusk", (820, 1220), 200); hills(ctx, 1320, shift=t * 0.6); ground(ctx, GY + 30)
    for i, (x, w) in enumerate([(980, 260), (1160, 320)]):
        tent(ctx, x - t * 40, GY + 20, w, 240)
    st, aF, aB, bob = walking(t)
    person(ctx, 380 + t * 18, GY + 40, 520, face=1, staff=True, stride=st, armF=0.15, armB=aB, bob=bob)

def sc_shepherd(ctx, t, D):
    zoom(ctx, t, D, 1.0, 1.05)
    sky(ctx, "dawn", (300, 1180), 230); hills(ctx, 1320, layers=("#5a3b6b", "#33224a", "#1b1226")); ground(ctx, GY + 30)
    st, aF, aB, bob = walking(t, 4.0)
    person(ctx, 360, GY + 40, 560, face=1, staff=True, stride=st * 0.7, armF=0.15, armB=aB, bob=bob)
    for i, (x, y, s) in enumerate([(620, GY + 40, 150), (790, GY + 70, 175), (700, GY + 130, 140), (900, GY + 120, 160), (560, GY + 160, 120)]):
        sheep(ctx, x + 6 * math.sin(t * 2 + i), y, s, step=t * 6 + i)
    a = P(t, D * 0.55, 0.5)
    if a > 0:  # bread basket glow
        ctx.set_source_rgba(1, 0.85, 0.5, 0.0)

def sc_name_davi(ctx, t, D):
    zoom(ctx, t, D, 1.0, 1.08, cy=900)
    sky(ctx, "dawn", (540, 1000), 300, horizon=1750)
    rays(ctx, 540, 1000, 16, 0.10, rot=t * 0.05)
    person(ctx, 540, 2450, 2000, face=1, armF=0.1)
    serif_title(ctx, "DAVI", 520, 210, P(t, 0.15, 0.5))

def sc_eu_vou(ctx, t, D):
    sky(ctx, "dusk", (540, 1260), 240); hills(ctx, 1320); ground(ctx, GY + 30)
    rays(ctx, 540, 1260, 16, 0.08 * P(t, D * 0.5, 0.6), rot=t * 0.05)
    for i in range(6):
        person(ctx, 90 + i * 70 + (i > 2) * 520, GY + 60, 330, face=1 if i < 3 else -1, shield=True, a=0.95)
    k = P(t, D * 0.5, 0.7)
    person(ctx, 540, GY + 50 - 40 * k, 430 + 90 * k, face=1, staff=True, armF=0.15 - 0.4 * k, stride=0.05 + 0.1 * k)

def sc_armor(ctx, t, D):
    zoom(ctx, t, D, 1.0, 1.06, cy=1200)
    sky(ctx, "dusk", (850, 1100), 180); hills(ctx, 1320); ground(ctx, GY + 30)
    person(ctx, 820, GY + 40, 820, face=-1, armF=0.6, helmet=True, a=0.95)  # the king
    wob = 0.09 * math.sin(t * 5.0) * P(t, 0.3, 0.4)
    person(ctx, 380, GY + 40, 560, face=1, armor=P(t, 0.0, 0.4), armF=0.45, armB=-0.45, stride=0.14, lean=wob)

def sc_armor_off(ctx, t, D):
    sky(ctx, "dusk", (850, 1100), 180); hills(ctx, 1320); ground(ctx, GY + 30)
    person(ctx, 820, GY + 40, 820, face=-1, armF=0.3, helmet=True, a=0.95)
    k = P(t, 0.15, 0.9)
    person(ctx, 380, GY + 40, 560, face=1, armF=0.15, armB=-0.15, stride=0.08)
    # pieces falling
    ctx.set_source_rgba(0.42, 0.40, 0.45, 1 - clamp(k * 1.3 - 0.3))
    ctx.save(); ctx.translate(380 - 140 * k, GY - 390 + 420 * k * k); ctx.rotate(-1.4 * k); ctx.rectangle(-112, -118, 224, 236); ctx.fill(); ctx.restore()
    ctx.save(); ctx.translate(380 + 150 * k, GY - 560 + 600 * k * k); ctx.rotate(2.2 * k); ctx.move_to(-73, 0); ctx.curve_to(-84, -130, 84, -130, 73, 0); ctx.close_path(); ctx.fill(); ctx.restore()

def sc_stones(ctx, t, D):
    sky(ctx, "dawn", (540, 900), 200, horizon=1000)
    ctx.set_source_rgba(*hexc("#2a3f6a")); ctx.rectangle(0, 1000, W, H); ctx.fill()
    for i in range(14):
        y = 1040 + i * 65
        ctx.set_source_rgba(1, 0.9, 0.7, 0.18); ctx.set_line_width(4)
        for x in range(-40, W, 160):
            xx = x + ((t * 60 + i * 37) % 160)
            ctx.move_to(xx, y); ctx.curve_to(xx + 25, y - 10, xx + 50, y + 10, xx + 75, y); ctx.stroke()
    n = min(5, int(clamp((t - D * 0.35) / (D * 0.55)) * 5.999))
    for i in range(5):
        a = P(t, D * 0.35 + i * D * 0.11, 0.3)
        if a <= 0: continue
        x, y = 220 + i * 160, 1380 + (i % 2) * 70
        ctx.save(); ctx.translate(x, y - 40 * (1 - a)); ctx.scale(70, 50)
        rg = cairo.RadialGradient(-0.3, -0.4, 0.1, 0, 0, 1.1); rg.add_color_stop_rgba(0, 0.95, 0.92, 0.86, a); rg.add_color_stop_rgba(1, 0.45, 0.42, 0.4, a)
        ctx.set_source(rg); ctx.arc(0, 0, 1, 0, 6.3); ctx.fill(); ctx.restore()
    ctx.set_source_rgba(*hexc("#1a0f18")); ctx.move_to(0, 1090); ctx.curve_to(300, 1060, 700, 1120, W, 1080); ctx.line_to(W, 990); ctx.line_to(0, 990); ctx.close_path(); ctx.fill()
    person(ctx, 820, 1085, 440, face=-1, staff=True, armF=0.6, armB=0.3, a=0.95)
    if n > 0: serif_title(ctx, f"{n}", 600, 170, 1.0)

def sc_faceoff(ctx, t, D):
    zoom(ctx, t, D, 1.0, 1.06, cy=1300)
    sky(ctx, "red", (540, 1250), 260); hills(ctx, 1320); ground(ctx, GY + 30)
    laugh = 0.02 * math.sin(t * 22) * P(t, D * 0.3, 0.3)
    person(ctx, 720, GY + 50, 1100, face=-1, giant=True, helmet=True, spear=True, shield=True, armF=0.2, head_tilt=-0.25 * P(t, D * 0.3, 0.3), lean=laugh)
    person(ctx, 230, GY + 50, 360, face=1, staff=True, armF=0.15)
    a = P(t, D * 0.35, 0.3)
    if a > 0:
        serif_title(ctx, "HA  HA  HA", 470 + 8 * math.sin(t * 20), 110, a * 0.95, color="#ffd6b0")

def sc_faith(ctx, t, D):
    zoom(ctx, t, D, 1.0, 1.1, cy=1200)
    sky(ctx, "dusk", (540, 300), 160)
    rays(ctx, 540, 300, 20, 0.07 + 0.05 * P(t, D * 0.5, 1.0), rot=t * 0.03)
    hills(ctx, 1320); ground(ctx, GY + 30)
    ctx.set_source_rgba(1, 0.95, 0.75, 0.10 + 0.12 * P(t, D * 0.5, 1.0)); ctx.move_to(440, 300); ctx.line_to(640, 300); ctx.line_to(820, GY); ctx.line_to(260, GY); ctx.close_path(); ctx.fill()
    person(ctx, 540, GY + 50, 700, face=1, staff=True, armF=0.15, armB=-0.1, head_tilt=-0.15)
    person(ctx, 1000, GY + 60, 1300, face=-1, giant=True, helmet=True, spear=True, a=0.85)

def sc_sling(ctx, t, D):
    sky(ctx, "dusk", (540, 1250), 230); hills(ctx, 1320, shift=t * 1.5); ground(ctx, GY + 30)
    run = P(t, 0, D * 0.4)
    st, aF, aB, bob = walking(t, 12.0)
    release = D * 0.62
    spin = t * 14
    person(ctx, 180 + 200 * run, GY + 50, 520, face=1, stride=st * (1 if t < release else 0.3), armB=aB, bob=bob,
           armF=-2.4 if t < release else -0.6, sling=(spin if t < release else None))
    if t >= release:
        k = clamp((t - release) / (D - release))
        x = 420 + 900 * k; y = 1050 - 260 * k
        for j in range(6):
            ctx.set_source_rgba(1, 0.95, 0.8, 0.5 * (1 - j / 6)); ctx.arc(x - j * 28, y + j * 8, 14 - j * 1.5, 0, 6.3); ctx.fill()
        ctx.set_source_rgba(0.95, 0.93, 0.88, 1); ctx.arc(x, y, 16, 0, 6.3); ctx.fill()
    ctx.set_source_rgba(1, 0.95, 0.8, 0.0)

def sc_impact(ctx, t, D):
    sh = 18 * (1 - P(t, 0, 0.6))
    ctx.translate(sh * math.sin(t * 90), sh * math.cos(t * 77))
    zoom(ctx, t, D, 1.0, 1.06, cy=700)
    sky(ctx, "red", (540, 1100), 260, horizon=1800)
    person(ctx, 540, 2600, 2300, face=-1, giant=True, helmet=True, head_tilt=0.2 * P(t, 0, 0.5), lean=-0.05 * P(t, 0, 0.8))
    fl = 1 - P(t, 0.0, 0.5)
    ctx.set_source_rgba(1, 1, 1, 0.9 * fl); ctx.rectangle(-50, -50, W + 100, H + 100); ctx.fill()
    for i in range(10):
        ang = i * 0.628; r0, r1 = 40 + 400 * P(t, 0, 0.4), 120 + 600 * P(t, 0, 0.4)
        ctx.set_source_rgba(1, 0.95, 0.8, 0.8 * (1 - P(t, 0.1, 0.6))); ctx.set_line_width(10)
        ctx.move_to(560 + r0 * math.cos(ang), 400 + r0 * math.sin(ang)); ctx.line_to(560 + r1 * math.cos(ang), 400 + r1 * math.sin(ang)); ctx.stroke()

def sc_fall(ctx, t, D):
    k = ease(clamp(t / (D * 0.55)) ** 1.6)
    land = D * 0.55
    sh = 22 * (1 - P(t, land, 0.5)) if t > land else 0
    ctx.translate(sh * math.sin(t * 80), sh * math.cos(t * 71))
    sky(ctx, "dusk", (540, 1250), 260); hills(ctx, 1320); ground(ctx, GY + 30)
    person(ctx, 110, GY + 60, 300, face=1, staff=True, armF=-0.5, a=0.95)
    person(ctx, 960, GY + 60, 700, face=-1, giant=True, helmet=True, shield=True, armF=0.6, armB=-0.6, lean=-k * 1.45)
    if t > land: dust(ctx, 520, GY + 60, clamp((t - land) / 1.4), seed=4, spread=520)

def sc_message(ctx, t, D):
    zoom(ctx, t, D, 1.0, 1.08, cy=1250)
    sky(ctx, "dawn", (540, 1230), 280)
    rays(ctx, 540, 1230, 18, 0.10, rot=t * 0.04)
    hills(ctx, 1320, layers=("#6b4a7e", "#3a2752", "#1b1226")); ground(ctx, GY + 30)
    ctx.save(); ctx.set_source_rgba(0.06, 0.03, 0.06, 0.35 * (1 - P(t, D * 0.45, 1.0)))
    ctx.translate(540, GY + 40); ctx.scale(1, 1)
    ctx.restore()
    person(ctx, 540, GY + 40, 520, face=1, staff=True, armF=0.15)
    a = P(t, D * 0.5, 0.7)
    serif_title(ctx, "VOCÊ NÃO", 450, 92, a, spacing=0.06); serif_title(ctx, "LUTA SOZINHO", 570, 92, a, spacing=0.06)

def heart(ctx, x, y, s, a):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    ctx.move_to(0, 0.35); ctx.curve_to(-0.9, -0.25, -0.45, -1.0, 0, -0.45); ctx.curve_to(0.45, -1.0, 0.9, -0.25, 0, 0.35)
    ctx.set_source_rgba(0.95, 0.25, 0.35, a); ctx.fill(); ctx.restore()

def sc_cta(ctx, t, D):
    sky(ctx, "dawn", (540, 1230), 280); rays(ctx, 540, 1230, 18, 0.08, rot=t * 0.04)
    hills(ctx, 1320, layers=("#6b4a7e", "#3a2752", "#1b1226")); ground(ctx, GY + 30)
    person(ctx, 540, GY + 40, 420, face=1, staff=True, armF=0.15, a=0.9)
    p1 = P(t, 0.1, 0.4); pulse = 1 + 0.08 * math.sin(t * 6)
    if p1 > 0.01: heart(ctx, 360, 440, 90 * p1 * pulse, p1)
    p2 = P(t, D * 0.25, 0.4)
    if p2 > 0.01:
        ctx.save(); ctx.translate(720, 420); ctx.scale(p2, p2); ctx.set_source_rgba(1, 1, 1, p2); ctx.set_line_width(14)
        ctx.move_to(-60, 50); ctx.curve_to(-50, -20, 0, -40, 40, -40); ctx.stroke()
        ctx.move_to(20, -80); ctx.line_to(70, -40); ctx.line_to(20, 0); ctx.stroke(); ctx.restore()
    p3 = P(t, D * 0.45, 0.5)
    if p3 > 0:
        ctx.set_source_rgba(1, 0.95, 0.85, 0.95 * p3)
        ctx.new_path(); r = 46; x0, y0, x1, y1 = 240, 560, 840, 652
        ctx.arc(x0 + r, y0 + r, r, math.pi, 1.5 * math.pi); ctx.arc(x1 - r, y0 + r, r, 1.5 * math.pi, 0); ctx.arc(x1 - r, y1 - r, r, 0, 0.5 * math.pi); ctx.arc(x0 + r, y1 - r, r, 0.5 * math.pi, math.pi); ctx.close_path(); ctx.fill()
        ctx.select_font_face("Inter", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD); ctx.set_font_size(52)
        txt = "LINK NA BIO"; e = ctx.text_extents(txt)
        ctx.move_to(540 - e.x_advance / 2, 625); ctx.set_source_rgba(0.35, 0.12, 0.25, p3); ctx.show_text(txt)

SCENES = [  # (function, first sentence index)
    (sc_giant, 0), (sc_days, 1), (sc_name_golias, 2), (sc_shout, 3), (sc_hiding, 4), (sc_boy_arrives, 5), (sc_shepherd, 6),
    (sc_name_davi, 8), (sc_eu_vou, 9), (sc_armor, 10), (sc_armor_off, 11), (sc_stones, 12), (sc_faceoff, 13), (sc_faith, 14),
    (sc_sling, 16), (sc_impact, 17), (sc_fall, 18), (sc_message, 19), (sc_cta, 21)]

# ---------------------------------------------------------------- captions
CF = "/usr/share/fonts/opentype/inter/Inter-Black.otf"
_fonts = {}
def cfont(s):
    if s not in _fonts: _fonts[s] = ImageFont.truetype(CF, s)
    return _fonts[s]

def caption_chunks(st):
    out = []
    for (a, b), s in zip(st, SENTS):
        for x, y in DISP: s = s.replace(x, y)
        words = s.split(); ch = []; cur = []
        for w in words:
            cur.append(w)
            if len(cur) >= 3 or len(" ".join(cur)) >= 15 or w[-1] in ",:": ch.append(cur); cur = []
        if cur:
            if ch and len(cur) == 1 and len(cur[0]) < 5: ch[-1] += cur
            else: ch.append(cur)
        n = sum(len(" ".join(c)) for c in ch); u = a
        for c in ch:
            v = u + (b - a) * len(" ".join(c)) / n
            wt = []; m = sum(len(w) + 1 for w in c); q = u
            for w in c:
                r = q + (v - u) * (len(w) + 1) / m; wt.append((w, q, r)); q = r
            out.append((u, v, wt)); u = v
    return out

def draw_caption(img, chunks, T):
    cur = None
    for u, v, wt in chunks:
        if u <= T < v: cur = (u, v, wt); break
    if not cur: return
    u, v, wt = cur
    pop = 1 + 0.14 * (1 - ease((T - u) / 0.12))
    f = cfont(int(92 * pop))
    d = ImageDraw.Draw(img)
    words = [w.upper() for w, _, _ in wt]
    sp = d.textlength(" ", font=f)
    widths = [d.textlength(w, font=f) for w in words]
    total = sum(widths) + sp * (len(words) - 1)
    lines = [list(range(len(words)))]
    if total > 940 and len(words) > 1:
        lines = [list(range(len(words) - 1)), [len(words) - 1]]
    y = 860 - (len(lines) - 1) * 55
    for ln in lines:
        lw = sum(widths[i] for i in ln) + sp * (len(ln) - 1); x = W / 2 - lw / 2
        for i in ln:
            on = wt[i][1] <= T < wt[i][2] or (i == len(words) - 1 and T >= wt[i][2])
            col = (255, 214, 74) if on else (255, 255, 255)
            d.text((x, y), words[i], font=f, fill=col, stroke_width=9, stroke_fill=(10, 6, 10), anchor="lm")
            x += widths[i] + sp
        y += 110

HEADER = "HISTÓRIAS DA BÍBLIA"
HANDLE = "@padrejoseanthonio"
def draw_header(img):
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 40)
    d.text((W / 2, 230), HEADER, font=f, fill=(255, 240, 210), anchor="mm", stroke_width=4, stroke_fill=(20, 10, 20))
    if HANDLE:
        f2 = ImageFont.truetype("/usr/share/fonts/opentype/inter/Inter-Bold.otf", 38)
        d.text((W / 2, 292), HANDLE, font=f2, fill=(255, 214, 74), anchor="mm", stroke_width=4, stroke_fill=(20, 10, 20))

# ---------------------------------------------------------------- render
def surface_frame(fn, t, D):
    s = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(s); ctx.set_antialias(cairo.ANTIALIAS_GOOD)
    ctx.set_source_rgb(0, 0, 0); ctx.paint()
    fn(ctx, t, D)
    a = np.ndarray((H, W, 4), np.uint8, s.get_data())
    return a[:, :, [2, 1, 0]].copy()

def timeline():
    st, vd = sentence_times()
    starts = [0.0 if k == 0 else st[i][0] for k, (_, i) in enumerate(SCENES)]
    ends = starts[1:] + [LEAD + vd + 1.2]
    return st, vd, starts, ends

def render_scene(k):
    st, vd, starts, ends = timeline()
    chunks = caption_chunks(st)
    fn = SCENES[k][0]; a, b = starts[k], ends[k]
    f0, f1 = round(a * FPS), round(b * FPS)
    tmp, fin = f"{OUT}/s{k:02d}.tmp.mp4", f"{OUT}/s{k:02d}.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "19", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    D = b - a
    for f in range(f0, f1):
        T = f / FPS; tl = T - a
        fr = surface_frame(fn, tl, D)
        if k > 0 and tl < XF:
            pf, pa, pb = SCENES[k - 1][0], starts[k - 1], ends[k - 1]
            prev = surface_frame(pf, T - pa, pb - pa)
            w = ease(tl / XF)
            fr = (prev * (1 - w) + fr * w).astype(np.uint8)
        if k == 0 and tl < 0.3: fr = (fr * (tl / 0.3)).astype(np.uint8)
        if k == len(SCENES) - 1 and b - T < 0.8: fr = (fr * ((b - T) / 0.8)).astype(np.uint8)
        img = Image.fromarray(fr)
        if k < len(SCENES) - 1 or b - T > 0.8: draw_header(img)
        draw_caption(img, chunks, T)
        p.stdin.write(img.tobytes())
    p.stdin.close()
    if p.wait() != 0: raise SystemExit(f"scene {k} failed")
    os.replace(tmp, fin)
    return k

def preview(spec):
    st, vd, starts, ends = timeline()
    chunks = caption_chunks(st)
    print("voice", round(vd, 1), "scenes", [round(e - s, 1) for s, e in zip(starts, ends)])
    for k, frac in spec:
        a, b = starts[k], ends[k]; T = a + (b - a) * frac
        img = Image.fromarray(surface_frame(SCENES[k][0], T - a, b - a)); draw_header(img); draw_caption(img, chunks, T)
        img.save(f"{OUT}/p{k:02d}.png")

STORY = os.environ.get("STORY")
if STORY:
    exec(open(f"{BASE}/stories/common.py").read(), globals())
    exec(open(f"{BASE}/stories/{STORY}.py").read(), globals())
    SENTS = re.split(r'(?<=[.?!])\s+', TEXT)
    VOICE = os.environ.get("VOICE_FILE") or f"{BASE}/voices/{STORY}.mp3"; OUT = f"{BASE}/out_{STORY}"; os.makedirs(OUT, exist_ok=True)

if __name__ == "__main__":
    cmd = sys.argv[1]
    if cmd == "preview":
        ks = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        preview([(k, 0.7) for k in ks])
    elif cmd == "render":
        from multiprocessing import Pool
        ks = [int(x) for x in sys.argv[2:]] or list(range(len(SCENES)))
        with Pool(min(8, os.cpu_count() or 2)) as pool:
            for k in pool.imap_unordered(render_scene, ks): print("ok", k, flush=True)
        st, vd, starts, ends = timeline()
        json.dump({"total": ends[-1], "scenes": list(zip(starts, ends)), "sents": st}, open(f"{OUT}/timeline.json", "w"))
