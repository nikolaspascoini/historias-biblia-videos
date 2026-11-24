# Shared drawing helpers for the Bible-story series (exec'd into davi.py's globals).

def poly(ctx, pts, rgba):
    ctx.move_to(*pts[0])
    for p in pts[1:]: ctx.line_to(*p)
    ctx.close_path(); ctx.set_source_rgba(*rgba); ctx.fill()

def sea(ctx, y, t, color="#16314f", amp=18, layers=3, speed=1.0, light="#9fd0ff", top_alpha=0.35):
    for i in range(layers):
        yy = y + i * 55; a = amp * (1 + i * 0.4); ph = t * speed * (1.2 + i * 0.5) + i * 2.1
        ctx.move_to(0, H)
        for x in range(0, W + 21, 20):
            ctx.line_to(x, yy + a * math.sin(x * 0.012 + ph) + a * 0.5 * math.sin(x * 0.031 - ph * 1.3))
        ctx.line_to(W, H); ctx.close_path()
        c = hexc(color); k = 1 - i * 0.18
        ctx.set_source_rgba(c[0] * k, c[1] * k, c[2] * k, 1); ctx.fill()
        ctx.set_line_width(4); ctx.set_source_rgba(*hexc(light, top_alpha * (1 - i * 0.25)))
        for x in range(0, W + 21, 20):
            py = yy + a * math.sin(x * 0.012 + ph) + a * 0.5 * math.sin(x * 0.031 - ph * 1.3)
            (ctx.move_to if x == 0 else ctx.line_to)(x, py)
        ctx.stroke()

def rain(ctx, t, n=160, a=0.35, slant=0.25, seed=5):
    rnd = random.Random(seed); ctx.set_line_width(3); ctx.set_source_rgba(0.75, 0.82, 0.95, a)
    for _ in range(n):
        x0, y0, sp = rnd.uniform(-200, W + 200), rnd.uniform(0, H), rnd.uniform(1500, 2400)
        y = (y0 + t * sp) % (H + 200) - 100; x = x0 - slant * (y - y0)
        x = x % (W + 200) - 100
        ctx.move_to(x, y); ctx.line_to(x - 60 * slant, y + 60); ctx.stroke()

def lightning(ctx, t, at, x=640, seed=2):
    d = t - at
    if d < 0 or d > 0.35: return
    k = 1 - d / 0.35
    ctx.set_source_rgba(1, 1, 1, 0.55 * k); ctx.rectangle(-50, -50, W + 100, H + 100); ctx.fill()
    rnd = random.Random(seed); px, py = x, 0
    ctx.set_source_rgba(1, 1, 1, k); ctx.set_line_width(8); ctx.move_to(px, py)
    while py < 1000:
        px += rnd.uniform(-70, 70); py += rnd.uniform(60, 120); ctx.line_to(px, py)
    ctx.stroke()

def boat(ctx, x, y, s, a=1.0, rock=0.0, sail=True, sail_col=None):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rock); ctx.scale(s, s)
    ink(ctx, a)
    ctx.move_to(-1.0, -0.25); ctx.curve_to(-0.8, 0.15, 0.8, 0.15, 1.05, -0.3); ctx.line_to(0.9, -0.12); ctx.line_to(-0.85, -0.12); ctx.close_path(); ctx.fill()
    ctx.move_to(-1.0, -0.25); ctx.line_to(-0.85, -0.12); ctx.line_to(0.9, -0.12); ctx.line_to(1.05, -0.3); ctx.line_to(1.05, -0.2); ctx.line_to(-1.0, -0.17); ctx.close_path(); ctx.fill()
    if sail:
        ctx.set_line_width(0.04); ctx.move_to(0, -0.12); ctx.line_to(0, -1.3); ctx.stroke()
        if sail_col: ctx.set_source_rgba(*sail_col)
        ctx.move_to(0.03, -1.25); ctx.curve_to(0.55, -0.9, 0.55, -0.5, 0.03, -0.25); ctx.close_path(); ctx.fill()
    ctx.restore()

def fish(ctx, x, y, s, a=1.0, mouth=0.15, t=0.0, eye=True):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(0.04 * math.sin(t * 2))
    ctx.set_source_rgba(0.04, 0.05, 0.1, a)
    ctx.move_to(-1.0, 0); ctx.curve_to(-0.9, -0.55, 0.5, -0.6, 0.95, -0.05 - mouth); ctx.line_to(0.35, 0.0)
    ctx.line_to(0.95, 0.05 + mouth); ctx.curve_to(0.5, 0.55, -0.9, 0.5, -1.0, 0); ctx.close_path(); ctx.fill()
    tw = 0.15 * math.sin(t * 3)
    ctx.move_to(-0.95, 0); ctx.line_to(-1.55, -0.45 + tw); ctx.line_to(-1.4, 0); ctx.line_to(-1.55, 0.45 + tw); ctx.close_path(); ctx.fill()
    if eye: ctx.set_source_rgba(0.95, 0.9, 0.7, a); ctx.arc(0.55, -0.22, 0.04, 0, 6.3); ctx.fill()
    ctx.restore()

def lion(ctx, x, y, s, face=1, a=1.0, mouth=0.0, t=0.0, walk=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s * face, s); ink(ctx, a)
    for lx, ph in [(-0.45, 0), (-0.3, 1.5), (0.35, 0.8), (0.5, 2.3)]:
        ctx.set_line_width(0.1); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(lx, -0.35); ctx.line_to(lx + 0.06 * math.sin(t * 6 + ph) * walk, 0); ctx.stroke()
    ctx.save(); ctx.translate(0, -0.45); ctx.scale(0.62, 0.22); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.set_line_width(0.05); ctx.move_to(-0.6, -0.5); ctx.curve_to(-0.9, -0.6, -0.85, -0.2, -1.0, -0.3); ctx.stroke()
    ctx.arc(-1.0, -0.3, 0.06, 0, 6.3); ctx.fill()
    ctx.arc(0.62, -0.65, 0.3, 0, 6.3); ctx.fill()  # mane
    ctx.save(); ctx.translate(0.82, -0.6); ctx.scale(0.17, 0.13); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    if mouth > 0:
        ctx.set_source_rgba(0.5, 0.1, 0.1, a); ctx.move_to(0.88, -0.58); ctx.line_to(1.02, -0.62 + 0.0); ctx.line_to(1.0, -0.5 + 0.12 * mouth); ctx.close_path(); ctx.fill()
    ctx.restore()

def ark(ctx, x, y, s, a=1.0, door=1.0, rock=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(rock); ctx.scale(s, s)
    ctx.set_source_rgba(0.16, 0.09, 0.07, a)
    ctx.move_to(-1.0, -0.35); ctx.line_to(1.0, -0.35); ctx.curve_to(0.95, 0.0, 0.7, 0.1, 0.5, 0.1); ctx.line_to(-0.5, 0.1); ctx.curve_to(-0.7, 0.1, -0.95, 0.0, -1.0, -0.35); ctx.close_path(); ctx.fill()
    ctx.rectangle(-0.6, -0.72, 1.2, 0.38); ctx.fill()
    ctx.move_to(-0.7, -0.72); ctx.line_to(0, -0.95); ctx.line_to(0.7, -0.72); ctx.close_path(); ctx.fill()
    ctx.set_source_rgba(0.35, 0.22, 0.14, a * 0.8); ctx.set_line_width(0.012)
    for yy in (-0.25, -0.15, -0.05, 0.03): ctx.move_to(-0.95, yy); ctx.line_to(0.95, yy); ctx.stroke()
    ctx.set_source_rgba(1, 0.82, 0.5, a * 0.9 * door); ctx.rectangle(-0.1, -0.66, 0.2, 0.3 * door); ctx.fill()
    for wx in (-0.42, 0.32): ctx.set_source_rgba(1, 0.82, 0.5, a * 0.8); ctx.rectangle(wx, -0.62, 0.1, 0.08); ctx.fill()
    ctx.restore()

def rainbow(ctx, x, y, r, a=1.0, prog=1.0):
    cols = ["#e74c3c", "#f39c12", "#f1c40f", "#2ecc71", "#3498db", "#8e44ad"]
    ctx.set_line_width(r * 0.06)
    for i, c in enumerate(cols):
        ctx.set_source_rgba(*hexc(c, 0.75 * a)); ctx.new_path()
        ctx.arc(x, y, r - i * r * 0.06, math.pi, math.pi + math.pi * prog); ctx.stroke()

def bird(ctx, x, y, s, t, a=1.0, color=(1, 1, 1), branch=False):
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s)
    flap = math.sin(t * 12)
    ctx.set_source_rgba(color[0], color[1], color[2], a)
    ctx.save(); ctx.scale(0.5, 0.2); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.arc(0.5, -0.08, 0.13, 0, 6.3); ctx.fill()
    ctx.move_to(-0.1, 0); ctx.line_to(0.15, -0.9 * flap); ctx.line_to(0.3, 0); ctx.close_path(); ctx.fill()
    ctx.move_to(-0.45, 0); ctx.line_to(-0.8, -0.15); ctx.line_to(-0.75, 0.12); ctx.close_path(); ctx.fill()
    if branch:
        ctx.set_source_rgba(0.35, 0.55, 0.2, a); ctx.set_line_width(0.05); ctx.move_to(0.6, -0.02); ctx.line_to(0.95, 0.15); ctx.stroke()
        for k in range(3):
            ctx.save(); ctx.translate(0.7 + k * 0.1, 0.03 + k * 0.05); ctx.rotate(0.6); ctx.scale(0.07, 0.03); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.restore()

def animal_pair(ctx, kind, x, y, s, t, a=1.0):
    ink(ctx, a)
    for j, dx in enumerate((0, 0.9)):
        ctx.save(); ctx.translate(x + dx * s, y); ctx.scale(s * (1 - 0.1 * j), s * (1 - 0.1 * j)); ink(ctx, a)
        b = 0.02 * math.sin(t * 6 + j)
        if kind == "elefante":
            for lx in (-0.3, -0.15, 0.15, 0.3): ctx.rectangle(lx - 0.05, -0.35, 0.1, 0.35); ctx.fill()
            ctx.save(); ctx.translate(0, -0.55 + b); ctx.scale(0.45, 0.28); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
            ctx.arc(0.45, -0.7 + b, 0.18, 0, 6.3); ctx.fill()
            ctx.set_line_width(0.07); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(0.6, -0.65 + b); ctx.curve_to(0.7, -0.4, 0.62, -0.2, 0.7, -0.15); ctx.stroke()
        elif kind == "girafa":
            ctx.set_line_width(0.05)
            for lx in (-0.18, -0.08, 0.1, 0.2): ctx.move_to(lx, -0.45); ctx.line_to(lx, 0); ctx.stroke()
            ctx.save(); ctx.translate(0, -0.52); ctx.scale(0.28, 0.12); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
            ctx.set_line_width(0.07); ctx.move_to(0.2, -0.55); ctx.line_to(0.38, -1.15 + b); ctx.stroke()
            ctx.save(); ctx.translate(0.45, -1.17 + b); ctx.scale(0.12, 0.06); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
        else:  # ovelha
            sheep(ctx, 0, 0, 0.9, a, step=t * 6)
        ctx.restore()

def crowd(ctx, x0, x1, y, h, n, t, face=1, a=1.0, seed=1, walk=False, panic=0.0):
    rnd = random.Random(seed)
    for i in range(n):
        x = x0 + (x1 - x0) * (i + rnd.uniform(-0.3, 0.3)) / max(n - 1, 1); hh = h * rnd.uniform(0.85, 1.1)
        yy = y + rnd.uniform(-h * 0.08, h * 0.12)
        st = 0.25 * math.sin(t * 6 + i) if walk else 0.06
        arm = (-2.6 + 0.4 * math.sin(t * 8 + i)) if panic > 0.5 and i % 2 else rnd.uniform(-0.2, 0.3)
        person(ctx, x, yy, hh, face=face if rnd.random() > 0.15 else -face, robe=rnd.random() < 0.5, stride=st, armF=arm, a=a, bob=0.01 * abs(math.sin(t * 6 + i)) if walk else 0)

def chariot(ctx, x, y, s, t, face=1, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s * face, s); ink(ctx, a)
    # horse
    g = math.sin(t * 9)
    for lx, ph in [(0.55, 0), (0.7, 1.6), (1.05, 0.8), (1.2, 2.4)]:
        ctx.set_line_width(0.06); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
        ctx.move_to(lx, -0.45); ctx.line_to(lx + 0.12 * math.sin(t * 9 + ph), -0.02); ctx.stroke()
    ctx.save(); ctx.translate(0.88, -0.55); ctx.scale(0.42, 0.16); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.set_line_width(0.12); ctx.move_to(1.2, -0.6); ctx.line_to(1.4, -0.95 + 0.03 * g); ctx.stroke()
    ctx.save(); ctx.translate(1.48, -0.95 + 0.03 * g); ctx.rotate(0.5); ctx.scale(0.16, 0.07); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.set_line_width(0.03); ctx.move_to(0.1, -0.5); ctx.line_to(0.5, -0.55); ctx.stroke()
    # car + wheel + rider
    ctx.rectangle(-0.25, -0.75, 0.4, 0.35); ctx.fill()
    ctx.set_line_width(0.035); ctx.arc(-0.05, -0.3, 0.28, 0, 6.3); ctx.stroke()
    for k in range(6):
        ang = k * 1.047 + t * 8; ctx.move_to(-0.05, -0.3); ctx.line_to(-0.05 + 0.28 * math.cos(ang), -0.3 + 0.28 * math.sin(ang)); ctx.stroke()
    ctx.restore()
    person(ctx, x - 0.05 * s * face, y - 0.62 * s, s * 0.7, face=face, armF=1.2, helmet=True, spear=True, a=a)

def city(ctx, y, a=1.0, seed=9, col=None):
    rnd = random.Random(seed); ctx.set_source_rgba(*(col or (0.09, 0.05, 0.09, a)))
    x = -20
    while x < W + 20:
        w = rnd.uniform(60, 130); h = rnd.uniform(80, 260)
        ctx.rectangle(x, y - h, w, h + 5); ctx.fill()
        if rnd.random() < 0.35: ctx.arc(x + w / 2, y - h, w * 0.38, math.pi, 0); ctx.fill()
        if rnd.random() < 0.2: ctx.rectangle(x + w * 0.4, y - h - 120, w * 0.2, 120); ctx.fill()
        x += w + rnd.uniform(-10, 15)

def water_wall(ctx, x0, x1, top, bottom, t, a=1.0):
    g = cairo.LinearGradient(0, top, 0, bottom)
    g.add_color_stop_rgba(0, 0.45, 0.75, 0.9, a); g.add_color_stop_rgba(1, 0.05, 0.18, 0.32, a)
    ctx.move_to(x0, bottom)
    for x in range(int(x0), int(x1) + 11, 10):
        ctx.line_to(x, top + 18 * math.sin(x * 0.03 + t * 3))
    ctx.line_to(x1, bottom); ctx.close_path(); ctx.set_source(g); ctx.fill()
    ctx.set_source_rgba(1, 1, 1, 0.35 * a); ctx.set_line_width(5)
    for x in range(int(x0), int(x1) + 11, 10):
        (ctx.move_to if x == int(x0) else ctx.line_to)(x, top + 18 * math.sin(x * 0.03 + t * 3))
    ctx.stroke()

def window_frame(ctx, x, y, w, h, light="#ffd98a", a=1.0):
    ctx.set_source_rgba(*hexc(light, a)); ctx.rectangle(x, y, w, h); ctx.fill()
    ink(ctx, a); ctx.set_line_width(14); ctx.rectangle(x, y, w, h); ctx.stroke()
    ctx.set_line_width(8); ctx.move_to(x + w / 2, y); ctx.line_to(x + w / 2, y + h); ctx.stroke()
    ctx.move_to(x, y + h / 2); ctx.line_to(x + w, y + h / 2); ctx.stroke()

def angel(ctx, x, y, h, a=1.0, t=0.0):
    rg = cairo.RadialGradient(x, y - h * 0.55, 0, x, y - h * 0.55, h)
    rg.add_color_stop_rgba(0, 1, 0.98, 0.85, 0.9 * a); rg.add_color_stop_rgba(1, 1, 0.98, 0.85, 0)
    ctx.set_source(rg); ctx.arc(x, y - h * 0.55, h, 0, 6.3); ctx.fill()
    ctx.set_source_rgba(1, 0.98, 0.9, 0.9 * a)
    for sgn in (-1, 1):
        f = 0.08 * math.sin(t * 3)
        ctx.move_to(x, y - h * 0.75); ctx.curve_to(x + sgn * h * 0.6, y - h * (1.2 + f), x + sgn * h * 0.7, y - h * 0.6, x + sgn * h * 0.15, y - h * 0.45); ctx.close_path(); ctx.fill()
    ctx.move_to(x - h * 0.1, y - h * 0.8); ctx.line_to(x + h * 0.1, y - h * 0.8); ctx.line_to(x + h * 0.2, y); ctx.line_to(x - h * 0.2, y); ctx.close_path(); ctx.fill()
    ctx.arc(x, y - h * 0.9, h * 0.08, 0, 6.3); ctx.fill()

def scroll(ctx, x, y, w, h, a=1.0):
    ctx.set_source_rgba(0.93, 0.85, 0.66, a); ctx.rectangle(x, y, w, h); ctx.fill()
    ctx.set_source_rgba(0.6, 0.45, 0.28, a)
    for yy in (y, y + h): ctx.save(); ctx.translate(x + w / 2, yy); ctx.scale(w / 2 + 14, 16); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.set_source_rgba(0.35, 0.25, 0.15, 0.6 * a); ctx.set_line_width(5)
    for i in range(6): ctx.move_to(x + 30, y + 40 + i * (h - 70) / 5); ctx.line_to(x + w - 30 - (i % 2) * 60, y + 40 + i * (h - 70) / 5); ctx.stroke()

def cta_scene(ctx, t, D, mood="dawn", fig=None):
    sky(ctx, mood, (540, 1230), 280); rays(ctx, 540, 1230, 18, 0.08, rot=t * 0.04)
    hills(ctx, 1320, layers=("#6b4a7e", "#3a2752", "#1b1226")); ground(ctx, GY + 30)
    (fig or (lambda c: person(c, 540, GY + 40, 420, face=1, staff=True, armF=0.15, a=0.9)))(ctx)
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

def title_scene(ctx, t, D, word, mood, fig):
    zoom(ctx, t, D, 1.0, 1.08, cy=900)
    sky(ctx, mood, (540, 1000), 300, horizon=1750)
    rays(ctx, 540, 1000, 16, 0.10, rot=t * 0.05)
    fig(ctx)
    serif_title(ctx, word, 520, 200 if len(word) <= 6 else 160, P(t, 0.15, 0.5))

def two_line_title(ctx, l1, l2, a, size=92):
    serif_title(ctx, l1, 450, size, a, spacing=0.06); serif_title(ctx, l2, 570, size, a, spacing=0.06)

# default music/sfx hooks (stories override)
MUSIC = {}
def story_sfx(S, fx): pass

# ---------- extra helpers (series 2)
def woman(ctx, x, y, h, **k):
    kw = dict(face=1, robe=True, long_hair=True, armF=0.15); kw.update(k)
    person(ctx, x, y, h, **kw)

def flames(ctx, x0, x1, base, height, t, a=1.0, seed=3, n=None):
    rnd = random.Random(seed); n = n or int((x1 - x0) / 40)
    for layer, (col, hk) in enumerate([("#c0392b", 1.0), ("#e67e22", 0.75), ("#f9d56e", 0.45)]):
        c = hexc(col, a)
        for i in range(n):
            x = x0 + (x1 - x0) * (i + 0.5) / n + rnd.uniform(-15, 15)
            w = (x1 - x0) / n * 1.4
            hh = height * hk * (0.6 + 0.4 * abs(math.sin(t * (3 + rnd.random() * 3) + i)))
            sway = 18 * math.sin(t * 4 + i * 1.7)
            ctx.move_to(x - w / 2, base); ctx.curve_to(x - w / 2, base - hh * 0.5, x + sway - w * 0.1, base - hh * 0.8, x + sway, base - hh)
            ctx.curve_to(x + sway + w * 0.1, base - hh * 0.8, x + w / 2, base - hh * 0.5, x + w / 2, base); ctx.close_path()
            ctx.set_source_rgba(*c); ctx.fill()

def glow_box(ctx, x, y, r, col=(1, 0.6, 0.2), a=0.6):
    rg = cairo.RadialGradient(x, y, 0, x, y, r); rg.add_color_stop_rgba(0, col[0], col[1], col[2], a); rg.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
    ctx.set_source(rg); ctx.arc(x, y, r, 0, 6.3); ctx.fill()

def golden_statue(ctx, x, y, h, a=1.0):
    ctx.set_source_rgba(0.35, 0.25, 0.08, a); ctx.rectangle(x - h * 0.16, y - h * 0.08, h * 0.32, h * 0.08); ctx.fill()
    g = cairo.LinearGradient(x - h * 0.2, 0, x + h * 0.2, 0)
    g.add_color_stop_rgba(0, 0.6, 0.42, 0.08, a); g.add_color_stop_rgba(0.5, 1, 0.85, 0.35, a); g.add_color_stop_rgba(1, 0.55, 0.38, 0.06, a)
    ctx.save(); ctx.translate(x, y - h * 0.08); ctx.scale(h * 0.92, h * 0.92)
    ctx.move_to(-0.12, -0.82); ctx.line_to(0.12, -0.82); ctx.line_to(0.17, 0); ctx.line_to(-0.17, 0); ctx.close_path()
    ctx.arc(0, -0.92, 0.08, 0, 6.3)
    ctx.move_to(-0.12, -0.8); ctx.line_to(-0.25, -0.98); ctx.line_to(-0.21, -1.01); ctx.line_to(-0.09, -0.86); ctx.close_path()
    ctx.move_to(0.12, -0.8); ctx.line_to(0.25, -0.98); ctx.line_to(0.21, -1.01); ctx.line_to(0.09, -0.86); ctx.close_path()
    ctx.restore(); ctx.set_source(g); ctx.fill()

def pillar(ctx, x, top, bottom, w, a=1.0, col=(0.16, 0.1, 0.12), tilt=0.0):
    ctx.save(); ctx.translate(x, bottom); ctx.rotate(tilt)
    ctx.set_source_rgba(col[0], col[1], col[2], a)
    ctx.rectangle(-w / 2, top - bottom, w, bottom - top); ctx.fill()
    ctx.rectangle(-w * 0.7, top - bottom - 30, w * 1.4, 34); ctx.fill(); ctx.rectangle(-w * 0.7, -30, w * 1.4, 30); ctx.fill()
    ctx.restore()

def well(ctx, x, y, w, a=1.0):
    ctx.set_source_rgba(0.25, 0.17, 0.12, a); ctx.save(); ctx.translate(x, y); ctx.scale(w / 2, w / 7); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.set_source_rgba(0.04, 0.02, 0.03, a); ctx.save(); ctx.translate(x, y); ctx.scale(w / 2.4, w / 9); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.set_source_rgba(0.25, 0.17, 0.12, a); ctx.rectangle(x - w / 2, y, w, w * 0.35); ctx.fill()

def torch(ctx, x, y, s, t, a=1.0):
    ctx.set_source_rgba(0.2, 0.12, 0.08, a); ctx.rectangle(x - s * 0.04, y - s * 0.5, s * 0.08, s * 0.5); ctx.fill()
    glow_box(ctx, x, y - s * 0.6, s * 0.6, a=0.5 * a)
    flames(ctx, x - s * 0.12, x + s * 0.12, y - s * 0.48, s * 0.4, t, a=a, seed=int(x) % 97, n=2)

def jar(ctx, x, y, s, a=1.0, broken=0.0):
    ctx.set_source_rgba(0.55, 0.32, 0.18, a)
    if broken <= 0:
        ctx.save(); ctx.translate(x, y - s * 0.35); ctx.scale(s * 0.28, s * 0.35); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
        ctx.rectangle(x - s * 0.1, y - s * 0.78, s * 0.2, s * 0.15); ctx.fill()
    else:
        for i, (dx, dy, r) in enumerate([(-1, -0.6, -1.0), (1, -0.8, 1.2), (-0.5, 0.2, 0.6), (0.6, 0.1, -0.5)]):
            ctx.save(); ctx.translate(x + dx * s * 0.4 * broken, y - s * 0.35 + dy * s * 0.4 * broken); ctx.rotate(r * broken)
            ctx.move_to(-s * 0.12, 0); ctx.line_to(s * 0.1, -s * 0.05); ctx.line_to(s * 0.04, s * 0.12); ctx.close_path(); ctx.fill(); ctx.restore()

def trumpet(ctx, x, y, s, ang=-0.6, a=1.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.set_source_rgba(0.85, 0.7, 0.35, a)
    ctx.move_to(0, -s * 0.02); ctx.line_to(s * 0.6, -s * 0.03); ctx.line_to(s * 0.8, -s * 0.12); ctx.line_to(s * 0.8, s * 0.12); ctx.line_to(s * 0.6, s * 0.03); ctx.line_to(0, s * 0.02); ctx.close_path(); ctx.fill()
    ctx.restore()

def altar(ctx, x, y, w, h, a=1.0, wet=0.0, wood=True):
    for r in range(4):
        for c in range(5):
            ctx.set_source_rgba(0.32 + 0.04 * ((r + c) % 2), 0.28, 0.26, a)
            ctx.rectangle(x - w / 2 + c * w / 5 + (r % 2) * 8, y - (r + 1) * h / 4, w / 5 - 6, h / 4 - 6); ctx.fill()
    if wood:
        ctx.set_source_rgba(0.35, 0.2, 0.1, a)
        for i in range(5): ctx.save(); ctx.translate(x, y - h - 12 - i * 14); ctx.rotate(0.15 * (-1) ** i); ctx.rectangle(-w * 0.42, -6, w * 0.84, 12); ctx.restore(); ctx.fill()
    if wet > 0:
        ctx.set_source_rgba(0.45, 0.7, 0.95, 0.45 * wet); ctx.rectangle(x - w / 2 - 40, y - 14, w + 80, 22); ctx.fill()
        ctx.set_source_rgba(0.6, 0.85, 1, 0.25 * wet); ctx.rectangle(x - w / 2, y - h - 70, w, h + 60); ctx.fill()

def city_wall(ctx, x0, x1, y, h, a=1.0, crack=0.0, t=0.0):
    rnd = random.Random(5); bw = 70; bh = 38
    for r in range(int(h / bh)):
        for c in range(int((x1 - x0) / bw) + 1):
            fall = crack * rnd.uniform(0.3, 1.0)
            xx = x0 + c * bw + (r % 2) * bw / 2 + rnd.uniform(-60, 60) * crack
            yy = y - (r + 1) * bh + fall * (h - r * bh) * 1.2 + 0
            ctx.save(); ctx.translate(xx + bw / 2, yy + bh / 2); ctx.rotate(rnd.uniform(-1, 1) * crack)
            ctx.set_source_rgba(0.42 + rnd.uniform(-0.04, 0.04), 0.3, 0.22, a); ctx.rectangle(-bw / 2 + 2, -bh / 2 + 2, bw - 4, bh - 4); ctx.fill(); ctx.restore()
    if crack < 0.2:
        for c in range(int((x1 - x0) / 90) + 1):
            ctx.set_source_rgba(0.42, 0.3, 0.22, a); ctx.rectangle(x0 + c * 90, y - h - 40, 50, 42); ctx.fill()

def pig(ctx, x, y, s, t, a=1.0, face=1):
    ctx.save(); ctx.translate(x, y); ctx.scale(s * face, s); ctx.set_source_rgba(0.2, 0.1, 0.12, a)
    for lx in (-0.3, -0.15, 0.2, 0.35): ctx.rectangle(lx - 0.04, -0.25, 0.08, 0.25); ctx.fill()
    ctx.save(); ctx.translate(0, -0.42); ctx.scale(0.5, 0.25); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.arc(0.5, -0.45, 0.17, 0, 6.3); ctx.fill(); ctx.rectangle(0.6, -0.48, 0.14, 0.1); ctx.fill()
    ctx.move_to(0.42, -0.6); ctx.line_to(0.46, -0.72); ctx.line_to(0.52, -0.6); ctx.close_path(); ctx.fill()
    ctx.restore()

def tree(ctx, x, y, h, a=1.0, t=0.0):
    ctx.set_source_rgba(0.12, 0.07, 0.07, a); ctx.move_to(x - h * 0.06, y); ctx.line_to(x - h * 0.035, y - h * 0.55); ctx.line_to(x + h * 0.035, y - h * 0.55); ctx.line_to(x + h * 0.06, y); ctx.close_path(); ctx.fill()
    ctx.set_line_width(h * 0.03); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    for bx, by in [(-0.25, -0.75), (0.28, -0.72), (0.05, -0.85)]: ctx.move_to(x, y - h * 0.5); ctx.line_to(x + bx * h, y + by * h); ctx.stroke()
    ctx.set_source_rgba(0.1, 0.2, 0.12, a)
    for cx, cy, r in [(-0.25, -0.8, 0.2), (0.28, -0.78, 0.2), (0.0, -0.95, 0.25), (-0.1, -0.72, 0.2), (0.14, -0.7, 0.2)]:
        ctx.arc(x + cx * h + 4 * math.sin(t + cx * 9), y + cy * h, r * h, 0, 6.3); ctx.fill()

def donkey(ctx, x, y, s, t, a=1.0, face=1, walk=0.0):
    ctx.save(); ctx.translate(x, y); ctx.scale(s * face, s); ink(ctx, a)
    for lx, ph in [(-0.35, 0), (-0.22, 1.6), (0.25, 0.8), (0.38, 2.4)]:
        ctx.set_line_width(0.07); ctx.set_line_cap(cairo.LINE_CAP_ROUND); ctx.move_to(lx, -0.42); ctx.line_to(lx + 0.08 * math.sin(t * 6 + ph) * walk, 0); ctx.stroke()
    ctx.save(); ctx.translate(0, -0.52); ctx.scale(0.5, 0.18); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.set_line_width(0.13); ctx.move_to(0.42, -0.58); ctx.line_to(0.6, -0.85); ctx.stroke()
    ctx.save(); ctx.translate(0.68, -0.88); ctx.rotate(0.6); ctx.scale(0.16, 0.08); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    for ex in (0.56, 0.62): ctx.move_to(ex, -0.95); ctx.line_to(ex - 0.03, -1.15); ctx.line_to(ex + 0.04, -0.98); ctx.close_path(); ctx.fill()
    ctx.restore()

def dragon(ctx, x, y, s, t, a=1.0, face=1, fall=0.0):
    ctx.save(); ctx.translate(x, y); ctx.rotate(fall * 1.2); ctx.scale(s * face, s)
    ctx.set_source_rgba(0.12, 0.03, 0.05, a)
    w = math.sin(t * 5) * 0.25
    ctx.move_to(-0.1, -0.1); ctx.curve_to(-0.6, -0.9 - w, -1.3, -0.6 - w, -1.6, -0.2 - w * 0.5); ctx.line_to(-0.9, -0.25); ctx.line_to(-1.2, 0.0); ctx.line_to(-0.5, -0.05); ctx.close_path(); ctx.fill()
    ctx.move_to(-0.6, 0.05); ctx.curve_to(-0.3, -0.25, 0.4, -0.25, 0.6, -0.1); ctx.curve_to(0.4, 0.2, -0.2, 0.2, -0.6, 0.05); ctx.close_path(); ctx.fill()
    ctx.set_line_width(0.12); ctx.set_line_cap(cairo.LINE_CAP_ROUND)
    ctx.move_to(0.5, -0.12); ctx.curve_to(0.75, -0.3, 0.8, -0.55, 0.95, -0.6); ctx.stroke()
    ctx.move_to(0.9, -0.72); ctx.line_to(1.25, -0.6); ctx.line_to(0.95, -0.5); ctx.close_path(); ctx.fill()
    ctx.move_to(0.95, -0.72); ctx.line_to(0.88, -0.88); ctx.line_to(1.02, -0.74); ctx.close_path(); ctx.fill()
    ctx.set_line_width(0.06); ctx.move_to(-0.6, 0.02); ctx.curve_to(-1.0, 0.3, -1.3, 0.1, -1.6, 0.35 + 0.1 * math.sin(t * 3)); ctx.stroke()
    ctx.set_source_rgba(1, 0.3, 0.1, a); ctx.arc(1.0, -0.64, 0.025, 0, 6.3); ctx.fill()
    ctx.restore()

def archangel(ctx, x, y, h, t, a=1.0, sword_up=0.0, shield=False, glow=1.0):
    rg = cairo.RadialGradient(x, y - h * 0.55, 0, x, y - h * 0.55, h * 1.1)
    rg.add_color_stop_rgba(0, 1, 0.95, 0.75, 0.75 * glow * a); rg.add_color_stop_rgba(1, 1, 0.95, 0.75, 0)
    ctx.set_source(rg); ctx.arc(x, y - h * 0.55, h * 1.1, 0, 6.3); ctx.fill()
    f = 0.06 * math.sin(t * 3)
    for sgn in (-1, 1):
        ctx.set_source_rgba(1, 0.97, 0.88, 0.95 * a)
        ctx.move_to(x, y - h * 0.78); ctx.curve_to(x + sgn * h * 0.7, y - h * (1.35 + f), x + sgn * h * 0.85, y - h * 0.7, x + sgn * h * 0.2, y - h * 0.45); ctx.close_path(); ctx.fill()
        ctx.set_source_rgba(0.85, 0.75, 0.55, 0.6 * a); ctx.set_line_width(4)
        for k in range(4):
            ctx.move_to(x + sgn * h * 0.1, y - h * 0.7); ctx.line_to(x + sgn * h * (0.35 + 0.12 * k), y - h * (1.05 - 0.1 * k + f)); ctx.stroke()
    person(ctx, x, y, h, face=1, robe=True, long_hair=True, armF=-2.6 * sword_up - 0.5 * (1 - sword_up), armB=0.5, shield=shield, a=a)
    ang = -2.6 * sword_up - 0.5 * (1 - sword_up)
    hx = x + h * (0.04 + 0.38 * math.sin(ang)); hy = y - h * 0.78 + h * 0.38 * math.cos(ang)
    ctx.save(); ctx.translate(hx, hy); ctx.rotate(-ang + math.pi)
    ctx.set_source_rgba(1, 0.98, 0.85, a); ctx.move_to(-h * 0.018, 0); ctx.line_to(h * 0.018, 0); ctx.line_to(h * 0.008, h * 0.55); ctx.line_to(0, h * 0.6); ctx.line_to(-h * 0.008, h * 0.55); ctx.close_path(); ctx.fill()
    ctx.set_source_rgba(0.85, 0.7, 0.3, a); ctx.rectangle(-h * 0.06, -h * 0.01, h * 0.12, h * 0.025); ctx.fill()
    ctx.restore()
    glow_box(ctx, hx + h * 0.3 * math.sin(-ang + math.pi + 3.14) , hy, h * 0.25, col=(1, 0.95, 0.7), a=0.25 * sword_up)
