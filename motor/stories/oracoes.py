# Serie "Oracoes" (lote 3). Um arquivo por video define ORACAO = "<chave>" e executa este.
import json as _json
TEXT = _json.load(open(f"{BASE}/stories/lote3.json"))[ORACAO]
DISP = []
HEADER = "ORAÇÃO DE HOJE"
MUSIC = {"style": "piano"}


def story_sfx(S, fx):
    a, D = S(0); fx["chime"](a + 0.05, 0.35)


def _fit(text, size, maxw=960):
    sf = cairo.ImageSurface(cairo.FORMAT_ARGB32, 10, 10); c = cairo.Context(sf)
    c.select_font_face("Noto Serif CJK HK", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
    while size > 40:
        c.set_font_size(size); w = sum(c.text_extents(ch).x_advance for ch in text) + 0.06 * size * (len(text) - 1)
        if w <= maxw: break
        size -= 4
    return size


def two_line_title(ctx, l1, l2, a, size=92):
    s = min(_fit(l1, size), _fit(l2, size))
    serif_title(ctx, l1, 450, s, a, spacing=0.06); serif_title(ctx, l2, 450 + int(s * 1.3), s, a, spacing=0.06)


# ---------------------------------------------------------------- elementos
def motes(ctx, t, n=40, seed=11, col=(1, 0.92, 0.7), a=0.55):
    """Particulas de luz subindo (da vida a todas as cenas)."""
    rnd = random.Random(seed)
    for i in range(n):
        x0, sp, r, ph = rnd.uniform(0, W), rnd.uniform(25, 70), rnd.uniform(2, 6), rnd.uniform(0, 6.3)
        y = (rnd.uniform(0, H) - t * sp) % H
        x = x0 + 18 * math.sin(t * 0.7 + ph)
        al = a * (0.35 + 0.65 * abs(math.sin(t * 1.3 + ph)))
        g = cairo.RadialGradient(x, y, 0, x, y, r * 4)
        g.add_color_stop_rgba(0, col[0], col[1], col[2], al); g.add_color_stop_rgba(1, col[0], col[1], col[2], 0)
        ctx.set_source(g); ctx.arc(x, y, r * 4, 0, 6.3); ctx.fill()


def vignette(ctx, a=0.55):
    g = cairo.RadialGradient(W / 2, H * 0.55, H * 0.25, W / 2, H * 0.55, H * 0.75)
    g.add_color_stop_rgba(0, 0, 0, 0, 0); g.add_color_stop_rgba(1, 0, 0, 0, a)
    ctx.set_source(g); ctx.rectangle(0, 0, W, H); ctx.fill()


def beam(ctx, x, top, bottom, w0, w1, t, a=0.35, col=(1, 0.95, 0.78)):
    g = cairo.LinearGradient(0, top, 0, bottom)
    al = a * (0.85 + 0.15 * math.sin(t * 2))
    g.add_color_stop_rgba(0, col[0], col[1], col[2], al); g.add_color_stop_rgba(1, col[0], col[1], col[2], al * 0.15)
    ctx.move_to(x - w0 / 2, top); ctx.line_to(x + w0 / 2, top); ctx.line_to(x + w1 / 2, bottom); ctx.line_to(x - w1 / 2, bottom); ctx.close_path()
    ctx.set_source(g); ctx.fill()


def candle(ctx, x, y, s, t, a=1.0):
    glow_box(ctx, x, y - s * 1.25, s * 2.6, col=(1, 0.72, 0.3), a=0.55 * a * (0.9 + 0.1 * math.sin(t * 9)))
    ctx.set_source_rgba(0.93, 0.88, 0.78, a); ctx.rectangle(x - s * 0.22, y - s, s * 0.44, s); ctx.fill()
    ctx.set_source_rgba(0.2, 0.15, 0.1, a); ctx.set_line_width(s * 0.03); ctx.move_to(x, y - s); ctx.line_to(x, y - s * 1.06); ctx.stroke()
    fl = 1 + 0.08 * math.sin(t * 13) + 0.05 * math.sin(t * 7.3)
    sw = 0.04 * math.sin(t * 5)
    for k, (c, sc) in enumerate((((1, 0.6, 0.15), 1.0), ((1, 0.92, 0.55), 0.6))):
        ctx.save(); ctx.translate(x, y - s * 1.06); ctx.rotate(sw); ctx.scale(s * 0.11 * sc, s * 0.36 * sc * fl)
        ctx.move_to(0, 0); ctx.curve_to(1.2, -0.3, 0.6, -0.8, 0, -1.25); ctx.curve_to(-0.6, -0.8, -1.2, -0.3, 0, 0)
        ctx.restore(); ctx.set_source_rgba(c[0], c[1], c[2], a * 0.95); ctx.fill()


def house(ctx, x, y, s, light=1.0, a=1.0):
    ctx.set_source_rgba(0.06, 0.04, 0.08, a)
    ctx.rectangle(x - s * 0.5, y - s * 0.55, s, s * 0.55); ctx.fill()
    ctx.move_to(x - s * 0.62, y - s * 0.55); ctx.line_to(x, y - s * 0.95); ctx.line_to(x + s * 0.62, y - s * 0.55); ctx.close_path(); ctx.fill()
    for wx in (-0.27, 0.15):
        window_frame(ctx, x + wx * s, y - s * 0.42, s * 0.16, s * 0.16, a=light * a)
    ctx.set_source_rgba(1, 0.82, 0.45, 0.85 * light * a); ctx.rectangle(x - s * 0.06, y - s * 0.3, s * 0.12, s * 0.3); ctx.fill()


def bed(ctx, x, y, s, a=1.0):
    ctx.set_source_rgba(0.08, 0.06, 0.1, a)
    ctx.rectangle(x - s * 0.6, y - s * 0.25, s * 1.2, s * 0.12); ctx.fill()
    ctx.rectangle(x - s * 0.6, y - s * 0.45, s * 0.06, s * 0.45); ctx.fill(); ctx.rectangle(x + s * 0.54, y - s * 0.32, s * 0.06, s * 0.32); ctx.fill()
    ctx.set_source_rgba(0.85, 0.85, 0.9, 0.9 * a); ctx.save(); ctx.translate(x - s * 0.42, y - s * 0.31); ctx.scale(s * 0.12, s * 0.05); ctx.arc(0, 0, 1, 0, 6.3); ctx.restore(); ctx.fill()
    ctx.set_source_rgba(0.55, 0.6, 0.75, 0.9 * a); ctx.rectangle(x - s * 0.3, y - s * 0.34, s * 0.85, s * 0.1); ctx.fill()


def door(ctx, x, y, w, h, open_, t, a=1.0):
    beam(ctx, x, y - h, y + 260, w, w * 2.6, t, a=0.3 * open_)
    ctx.set_source_rgba(1, 0.9, 0.6, 0.95 * open_ * a); ctx.rectangle(x - w / 2, y - h, w, h); ctx.fill()
    ctx.set_source_rgba(0.12, 0.08, 0.06, a)
    ctx.rectangle(x - w / 2 - 22, y - h - 22, w + 44, 22); ctx.fill(); ctx.rectangle(x - w / 2 - 22, y - h, 22, h); ctx.fill(); ctx.rectangle(x + w / 2, y - h, 22, h); ctx.fill()
    pw = w * (1 - open_ * 0.85)
    ctx.set_source_rgba(0.2, 0.13, 0.09, a); ctx.rectangle(x - w / 2, y - h, pw, h); ctx.fill()


def bg(ctx, mood, t, D, z=(1.0, 1.07), cy=1100, sun=None, sun_r=0):
    zoom(ctx, t, D, z[0], z[1], cy=cy)
    sky(ctx, mood, sun, sun_r, horizon=1500)
    if mood in ("moon", "night", "storm"): stars(ctx, 0.6 if mood != "storm" else 0.15)


# ---------------------------------------------------------------- cenas (fabricas)
def S_hook(l1, l2, mood="night"):
    def f(ctx, t, D):
        k = 1 + 0.03 * math.sin(t * 2.2)
        zoom(ctx, t, D, 1.12, 1.0, cy=900)
        sky(ctx, mood, (540, 1050), 180, horizon=1800)
        rays(ctx, 540, 1050, 22, 0.12 * k, rot=t * 0.08)
        glow_box(ctx, 540, 1050, 520, col=(1, 0.85, 0.55), a=0.45 * k)
        person(ctx, 540, 1900, 820, face=1, kneel=True, robe=True, armF=-2.5, armB=-2.3, head_tilt=-0.3, glow=0.4)
        motes(ctx, t, 55)
        vignette(ctx)
        two_line_title(ctx, l1, l2, P(t, 0.0, 0.35), size=96)
    return f


def S_kneel(mood="moon", light=True):
    def f(ctx, t, D):
        bg(ctx, mood, t, D, sun=(780, 360) if mood == "moon" else (540, 1250), sun_r=80 if mood == "moon" else 240)
        hills(ctx, 1380, layers=("#1d1b3a", "#141229", "#0a0916")); ground(ctx, GY + 40)
        if light: beam(ctx, 540, 0, GY + 60, 120, 520, t)
        person(ctx, 540, GY + 60, 640, face=1, kneel=True, robe=True, armF=-1.9, armB=-1.7, head_tilt=0.35, glow=0.35 if light else 0)
        motes(ctx, t); vignette(ctx)
    return f


def S_candle(mood="night"):
    def f(ctx, t, D):
        zoom(ctx, t, D, 1.0, 1.1, cy=1250)
        ctx.set_source_rgba(*hexc("#07050a")); ctx.rectangle(0, 0, W, H); ctx.fill()
        glow_box(ctx, 540, 1150, 900, col=(1, 0.55, 0.2), a=0.18)
        for i, (x, s) in enumerate(((330, 230), (540, 330), (760, 260))):
            candle(ctx, x, 1560 - (i % 2) * 40, s, t + i * 1.7)
        ctx.set_source_rgba(0.04, 0.03, 0.05, 1); ctx.rectangle(0, 1560, W, H); ctx.fill()
        motes(ctx, t, 30, col=(1, 0.75, 0.4)); vignette(ctx, 0.7)
    return f


def S_verse(l1, l2, ref, mood="dawn"):
    def f(ctx, t, D):
        bg(ctx, mood, t, D, z=(1.0, 1.06), cy=1300, sun=(540, 1300), sun_r=260)
        rays(ctx, 540, 1300, 18, 0.10, rot=t * 0.05)
        hills(ctx, 1420, layers=("#6b4a7e", "#3a2752", "#1b1226")); ground(ctx, GY + 80)
        scroll(ctx, 540, 1640, 520, 150, a=0.95)
        motes(ctx, t)
        two_line_title(ctx, l1, l2, P(t, 0.1, 0.5), size=78)
        serif_title(ctx, ref, 700, 48, P(t, 0.6, 0.5), color="#ffd64a", spacing=0.08)
    return f


def S_sunrise(arms=True):
    def f(ctx, t, D):
        bg(ctx, "dawn", t, D, cy=1250, sun=(540, 1330 - 60 * clamp(t / D)), sun_r=250)
        rays(ctx, 540, 1300, 20, 0.12, rot=t * 0.05)
        hills(ctx, 1380, layers=("#8a5a7e", "#4a2f5e", "#22142e")); ground(ctx, GY + 40)
        person(ctx, 540, GY + 50, 600, face=1, robe=True, armF=-2.6 if arms else 0.2, armB=-2.4 if arms else -0.2, head_tilt=-0.25)
        motes(ctx, t); vignette(ctx, 0.4)
    return f


def S_storm(alone=True):
    def f(ctx, t, D):
        sh = 2 * math.sin(t * 19); ctx.translate(sh, 0)
        bg(ctx, "storm", t, D, cy=1200)
        hills(ctx, 1380, layers=("#1a1f2a", "#11151e", "#080a10")); ground(ctx, GY + 40)
        rain(ctx, t, n=200, a=0.4)
        lightning(ctx, t, D * 0.45, x=760, seed=5)
        person(ctx, 520, GY + 60, 560, face=1, robe=True, hood=True, armF=0.6, armB=0.5, head_tilt=0.45, lean=0.08)
        vignette(ctx, 0.65)
    return f


def S_presence():
    """Pessoa na chuva com uma luz/figura ao lado (Deus presente na tempestade)."""
    def f(ctx, t, D):
        bg(ctx, "storm", t, D, cy=1200)
        hills(ctx, 1380, layers=("#1a1f2a", "#11151e", "#080a10")); ground(ctx, GY + 40)
        rain(ctx, t, n=160, a=0.3)
        k = P(t, 0.2, 0.8)
        beam(ctx, 600, 0, GY + 60, 160, 700, t, a=0.4 * k)
        person(ctx, 470, GY + 60, 560, face=1, robe=True, hood=True, armF=0.5, head_tilt=0.3)
        person(ctx, 660, GY + 60, 620, face=-1, robe=True, long_hair=True, beard=True, armF=1.5 * k, glow=0.9 * k, a=0.9 * k)
        motes(ctx, t, 30); vignette(ctx, 0.55)
    return f


def S_burden():
    def f(ctx, t, D):
        bg(ctx, "dusk", t, D, cy=1250, sun=(300, 1250), sun_r=200)
        hills(ctx, 1380); ground(ctx, GY + 40)
        st, aF, aB, bob = walking(t, 3)
        x = 300 + 120 * clamp(t / D)
        ctx.set_source_rgba(0.1, 0.07, 0.09, 1); ctx.arc(x - 40, GY - 470, 150, 0, 6.3); ctx.fill()  # fardo nas costas
        person(ctx, x, GY + 50, 560, face=1, robe=True, stride=st * 0.6, bob=bob, lean=0.25, head_tilt=0.4, armF=0.4)
        motes(ctx, t, 20); vignette(ctx, 0.6)
    return f


def S_light_on():
    def f(ctx, t, D):
        bg(ctx, "moon", t, D, cy=1200, sun=(820, 330), sun_r=70)
        hills(ctx, 1380, layers=("#1d1b3a", "#141229", "#0a0916")); ground(ctx, GY + 40)
        k = P(t, 0.15, 0.7)
        beam(ctx, 540, 0, GY + 60, 140, 600, t, a=0.5 * k)
        person(ctx, 540, GY + 60, 600, face=1, robe=True, armF=-2.2 * k + 0.2, armB=-2.0 * k, head_tilt=-0.35 * k, glow=0.6 * k)
        motes(ctx, t, 50); vignette(ctx, 0.5)
    return f


def S_family(n=4, mood="dusk", house_=True):
    def f(ctx, t, D):
        bg(ctx, mood, t, D, cy=1250, sun=(540, 1260) if mood != "moon" else (820, 330), sun_r=230 if mood != "moon" else 70)
        hills(ctx, 1380); ground(ctx, GY + 40)
        if house_: house(ctx, 540, GY - 220, 520)
        hs = [560, 520, 330, 280, 360][:n]; xs = [300, 470, 640, 780, 900][:n]
        for i, (x, h) in enumerate(zip(xs, hs)):
            kw = dict(face=1 if i % 2 == 0 else -1, armF=1.4, armB=-1.4, robe=True)
            if i == 1: kw["long_hair"] = True
            person(ctx, x, GY + 70, h, **kw)
        beam(ctx, 540, 0, GY + 80, 200, 900, t, a=0.18)
        motes(ctx, t); vignette(ctx, 0.5)
    return f


def S_parent_child(mood="dawn"):
    def f(ctx, t, D):
        bg(ctx, mood, t, D, cy=1250, sun=(780, 1250), sun_r=220)
        hills(ctx, 1380); ground(ctx, GY + 40)
        st, aF, aB, bob = walking(t, 4)
        dx = 80 * clamp(t / D)
        person(ctx, 420 + dx, GY + 60, 600, face=1, robe=True, long_hair=True, stride=st * 0.6, bob=bob, armF=0.9)
        person(ctx, 600 + dx, GY + 60, 330, face=1, stride=st * 0.6, bob=bob, armB=-0.9)
        motes(ctx, t); vignette(ctx, 0.45)
    return f


def S_bedroom(sick=False):
    def f(ctx, t, D):
        zoom(ctx, t, D, 1.0, 1.08, cy=1300)
        ctx.set_source_rgba(*hexc("#0b0c18")); ctx.rectangle(0, 0, W, H); ctx.fill()
        window_frame(ctx, 760, 620, 260, 320, light="#9fb4ff")
        beam(ctx, 760, 780, 1650, 260, 520, t, a=0.22, col=(0.7, 0.8, 1))
        bed(ctx, 500, 1600, 760)
        if sick:
            person(ctx, 820, 1620, 560, face=-1, robe=True, long_hair=True, kneel=True, armF=-1.8, armB=-1.6, head_tilt=0.3)
        motes(ctx, t, 25, col=(0.8, 0.85, 1)); vignette(ctx, 0.6)
    return f


def S_house_angels():
    def f(ctx, t, D):
        bg(ctx, "moon", t, D, cy=1200, sun=(820, 320), sun_r=70)
        hills(ctx, 1380, layers=("#1d1b3a", "#141229", "#0a0916")); ground(ctx, GY + 40)
        house(ctx, 540, GY + 20, 560)
        k = P(t, 0.2, 0.8)
        for i, x in enumerate((170, 910)):
            angel(ctx, x, GY - 40 + 12 * math.sin(t * 1.5 + i), 520, a=0.9 * k, t=t)
        motes(ctx, t, 40); vignette(ctx, 0.55)
    return f


def S_shelter():
    """Debaixo das asas: grande anjo/asas cobrindo uma pessoa."""
    def f(ctx, t, D):
        bg(ctx, "night", t, D, cy=1100)
        rays(ctx, 540, 900, 18, 0.08, rot=t * 0.04)
        archangel(ctx, 540, 1700, 1250, t, sword_up=0.0, shield=True, glow=0.8)
        person(ctx, 540, 1760, 420, face=1, kneel=True, robe=True, armF=-1.9, armB=-1.7, head_tilt=0.3)
        motes(ctx, t, 50); vignette(ctx, 0.5)
    return f


def S_door():
    def f(ctx, t, D):
        bg(ctx, "night", t, D, cy=1250)
        ctx.set_source_rgba(*hexc("#0c0a12")); ctx.rectangle(0, 0, W, H); ctx.fill()
        door(ctx, 600, 1560, 300, 640, P(t, 0.2, D * 0.6), t)
        person(ctx, 330, 1600, 560, face=1, robe=True, armF=0.6, head_tilt=-0.1)
        ctx.set_source_rgba(0.03, 0.02, 0.04, 1); ctx.rectangle(0, 1580, W, H); ctx.fill()
        motes(ctx, t, 30); vignette(ctx, 0.55)
    return f


def S_bills():
    def f(ctx, t, D):
        zoom(ctx, t, D, 1.0, 1.06, cy=1300)
        ctx.set_source_rgba(*hexc("#100c10")); ctx.rectangle(0, 0, W, H); ctx.fill()
        glow_box(ctx, 540, 1150, 520, col=(1, 0.8, 0.45), a=0.35)
        rnd = random.Random(4)
        for i in range(9):
            x, y, r = 240 + rnd.uniform(0, 600), 1180 + rnd.uniform(0, 260), rnd.uniform(-0.5, 0.5)
            ctx.save(); ctx.translate(x, y + 30 * P(t, i * 0.15, 0.5)); ctx.rotate(r)
            ctx.set_source_rgba(0.95, 0.93, 0.88, 0.95); ctx.rectangle(-90, -120, 180, 240); ctx.fill()
            ctx.set_source_rgba(0.6, 0.6, 0.6, 1)
            for ln in range(6): ctx.rectangle(-65, -90 + ln * 30, 130 if ln % 2 else 90, 8); ctx.fill()
            ctx.restore()
        person(ctx, 540, 1950, 900, face=1, robe=True, armF=-2.6, armB=-2.5, head_tilt=0.5)
        vignette(ctx, 0.7)
    return f


def S_amen(mood="dawn"):
    def f(ctx, t, D):
        bg(ctx, mood, t, D, z=(1.0, 1.1), cy=1000, sun=(540, 1050), sun_r=280)
        rays(ctx, 540, 1050, 22, 0.14, rot=t * 0.06)
        glow_box(ctx, 540, 1050, 560, col=(1, 0.9, 0.6), a=0.5)
        hills(ctx, 1480, layers=("#6b4a7e", "#3a2752", "#1b1226")); ground(ctx, GY + 120)
        motes(ctx, t, 60)
        pop = 1 + 0.25 * (1 - P(t, 0, 0.5))
        serif_title(ctx, "AMÉM", 560, int(210 * pop), P(t, 0, 0.3))
    return f


def S_cta(mood="dawn"):
    def f(ctx, t, D):
        cta_scene(ctx, t, D, mood=mood, fig=lambda c: person(c, 540, GY + 40, 420, face=1, kneel=True, robe=True, armF=-1.9, armB=-1.7, head_tilt=0.3, a=0.9))
        motes(ctx, t, 35)
    return f


def S_words(l1, l2, mood="night", fig="kneel"):
    """Frase forte na tela sobre um fundo."""
    base = {"kneel": S_kneel(mood, True), "sunrise": S_sunrise(), "storm": S_storm(), "light": S_light_on()}[fig]
    def f(ctx, t, D):
        base(ctx, t, D)
        two_line_title(ctx, l1, l2, P(t, 0.05, 0.4), size=84)
    return f


# ---------------------------------------------------------------- roteiros
_R = {
    "deus_fala": [(S_hook("PARE UM", "MINUTO"), 0), (S_light_on(), 1), (S_burden(), 2), (S_storm(), 4), (S_words("MAS DEUS", "VÊ", "night", "light"), 5),
                  (S_verse("VINDE A MIM,", "OS CANSADOS", "MATEUS 11:28"), 6), (S_presence(), 7), (S_words("ELE NÃO", "DESISTIU", "dawn", "sunrise"), 9),
                  (S_kneel("moon"), 11), (S_candle(), 13), (S_cta(), 15)],
    "dormir": [(S_hook("ORAÇÃO", "PARA DORMIR", "moon"), 0), (S_bedroom(), 1), (S_candle(), 3), (S_kneel("moon"), 5),
               (S_verse("EM PAZ", "ME DEITO", "SALMO 4:8", "moon"), 6), (S_family(4, "moon"), 7), (S_house_angels(), 9), (S_sunrise(), 11), (S_amen("moon"), 12), (S_cta("moon"), 13)],
    "ansiedade": [(S_hook("RESPIRA", "FUNDO", "night"), 0), (S_storm(), 1), (S_verse("NÃO ANDEIS", "ANSIOSOS", "FILIPENSES 4:6"), 3), (S_light_on(), 5),
                  (S_bills(), 6), (S_family(3, "dusk", False), 9), (S_kneel("moon"), 10), (S_candle(), 12), (S_amen(), 14), (S_cta(), 15)],
    "salmo91": [(S_hook("SALMO 91", "PROTEÇÃO", "night"), 0), (S_kneel("moon"), 1), (S_shelter(), 2), (S_verse("MEU REFÚGIO,", "MINHA FORTALEZA", "SALMO 91:2"), 3),
                (S_storm(), 4), (S_shelter(), 5), (S_house_angels(), 6), (S_words("NÃO SERÁS", "ATINGIDO", "night", "light"), 7), (S_house_angels(), 8), (S_cta(), 9)],
    "familia": [(S_hook("PELA SUA", "FAMÍLIA", "dusk"), 0), (S_kneel("dusk"), 1), (S_family(4, "dusk"), 2), (S_parent_child(), 4), (S_family(2, "dawn", False), 6),
                (S_light_on(), 7), (S_house_angels(), 10), (S_verse("EU E A MINHA CASA", "SERVIREMOS AO SENHOR", "JOSUÉ 24:15"), 11), (S_amen(), 13), (S_cta(), 14)],
    "filhos": [(S_hook("PELOS SEUS", "FILHOS", "dawn"), 0), (S_kneel("dusk"), 1), (S_parent_child(), 2), (S_storm(), 4), (S_sunrise(), 5), (S_presence(), 6),
               (S_family(4, "dawn"), 8), (S_verse("ENSINA A", "CRIANÇA", "PROVÉRBIOS 22:6"), 9), (S_amen(), 10), (S_cta(), 11)],
    "manha": [(S_hook("ANTES DO", "CELULAR", "dawn"), 0), (S_sunrise(False), 1), (S_sunrise(True), 2), (S_parent_child("day"), 5), (S_door(), 6), (S_light_on(), 8),
              (S_verse("ESTE É O DIA", "QUE O SENHOR FEZ", "SALMO 118:24", "day"), 10), (S_words("SEJA", "LUZ", "dawn", "sunrise"), 11), (S_amen("day"), 12), (S_cta("day"), 13)],
    "conversa": [(S_hook("UMA CONVERSA", "COM DEUS", "night"), 0), (S_storm(), 1), (S_light_on(), 3), (S_words("EU OUVI", "CADA ORAÇÃO", "night", "light"), 4), (S_kneel("moon", False), 6),
                 (S_presence(), 7), (S_words("EU TE AMO", "DO MESMO JEITO", "dawn", "sunrise"), 9), (S_sunrise(False), 11), (S_verse("NÃO TE", "DEIXAREI", "HEBREUS 13:5"), 14),
                 (S_presence(), 15), (S_cta(), 17)],
    "trabalho": [(S_hook("ORAÇÃO PELO", "TRABALHO", "night"), 0), (S_kneel("moon"), 1), (S_bills(), 2), (S_candle(), 4), (S_door(), 6), (S_sunrise(), 8),
                 (S_verse("DEUS SUPRIRÁ", "TUDO", "FILIPENSES 4:19"), 9), (S_amen(), 11), (S_cta(), 12)],
    "saude": [(S_hook("ORAÇÃO", "PELA SAÚDE", "night"), 0), (S_light_on(), 1), (S_bedroom(True), 2), (S_family(3, "dusk", False), 4), (S_candle(), 6),
              (S_verse("PELAS SUAS FERIDAS", "FOMOS SARADOS", "ISAÍAS 53:5"), 8), (S_presence(), 9), (S_amen(), 10), (S_cta(), 11)],
}
SCENES = _R[ORACAO]
