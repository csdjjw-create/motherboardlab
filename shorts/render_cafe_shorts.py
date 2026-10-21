import math, subprocess, sys, os, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
FD = os.environ.get("PRETENDARD_DIR", os.path.join(HERE, "npmf/package/dist/public/static"))
W, H, FPS, DUR = 1080, 1920, 30, 10.0
N = int(FPS * DUR)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "cafe_shorts.mp4")

def font(w, s): return ImageFont.truetype(f"{FD}/Pretendard-{w}.otf", s)
F_CAP = font("Black", 92)
F_CAP_S = font("ExtraBold", 74)
F_MONO = font("Bold", 46)
F_REC = font("SemiBold", 44)
F_TOT = font("Black", 92)
F_SIGN = font("Black", 64)
F_SMALL = font("Bold", 38)

BG = (18, 18, 22)
YEL = (255, 214, 0)
RED = (240, 60, 60)
WHITE = (255, 255, 255)
GREEN = (60, 200, 120)

def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(t): t = clamp(t); return 1 - (1 - t) ** 3
def ease_back(t):
    t = clamp(t); c1, c3 = 1.70158, 2.70158
    return 1 + c3 * (t - 1) ** 3 + c1 * (t - 1) ** 2

def text_w(d, s, f): return d.textlength(s, font=f)

def caption(img, lines, t_local, y=260):
    """Big caption with black stroke. lines: list of [(text, color, font), ...]"""
    d = ImageDraw.Draw(img)
    pop = ease_back(t_local / 0.25)
    for i, segs in enumerate(lines):
        total = sum(text_w(d, s, f) for s, _, f in segs)
        fh = segs[0][2].size
        layer = Image.new("RGBA", (int(total) + 60, int(fh * 1.5)), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        x = 30
        for s, c, f in segs:
            ld.text((x, 10), s, font=f, fill=c, stroke_width=10, stroke_fill=(0, 0, 0))
            x += text_w(ld, s, f)
        sc = max(0.01, 0.6 + 0.4 * pop)
        lw, lh = max(1, int(layer.width * sc)), max(1, int(layer.height * sc))
        layer = layer.resize((lw, lh), Image.LANCZOS)
        cy = y + i * int(fh * 1.3)
        img.paste(layer, (int(W / 2 - lw / 2), int(cy + (fh * 1.5 - lh) / 2)), layer)

def vignette():
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    a = np.clip((r - 0.6) * 0.9, 0, 0.6)
    return Image.fromarray((a * 255).astype(np.uint8), "L")
VIG = vignette()

def finish(img):
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(black, img, VIG)

# ---------------- scene 1: cafe shutter closing ----------------
def scene1(t):
    img = Image.new("RGB", (W, H), (30, 32, 40))
    d = ImageDraw.Draw(img)
    # street + wall
    d.rectangle([0, 1500, W, H], fill=(45, 45, 50))
    d.rectangle([90, 620, 990, 1500], fill=(120, 84, 60))
    # awning
    for i in range(9):
        c = (200, 50, 50) if i % 2 == 0 else (240, 235, 225)
        d.polygon([(90 + i * 100, 700), (190 + i * 100, 700), (200 + i * 100, 820), (80 + i * 100, 820)], fill=c)
    d.rectangle([90, 640, 990, 700], fill=(60, 40, 30))
    d.text((W / 2, 670), "CAFE", font=F_SIGN, fill=(255, 230, 180), anchor="mm")
    # window interior (empty tables)
    wx0, wy0, wx1, wy1 = 160, 860, 920, 1480
    d.rectangle([wx0, wy0, wx1, wy1], fill=(70, 60, 50))
    for tx in (300, 540, 780):
        d.ellipse([tx - 70, 1240, tx + 70, 1270], fill=(150, 110, 80))
        d.rectangle([tx - 8, 1260, tx + 8, 1400], fill=(100, 70, 50))
        for cx in (tx - 95, tx + 95):
            d.rectangle([cx - 22, 1300, cx + 22, 1320], fill=(90, 60, 45))
            d.rectangle([cx - 4, 1320, cx + 4, 1400], fill=(90, 60, 45))
    # pendant lights flicker off
    on = t < 0.5 or (0.62 < t < 0.7)
    for lx in (300, 540, 780):
        d.line([lx, wy0, lx, 960], fill=(30, 30, 30), width=4)
        d.pieslice([lx - 40, 940, lx + 40, 1010], 180, 360, fill=(255, 220, 140) if on else (60, 55, 50))
    # shutter rolling down
    p = ease_out((t - 0.15) / 1.1)
    sh = int(wy0 + (wy1 - wy0) * p)
    d.rectangle([wx0, wy0, wx1, sh], fill=(150, 155, 160))
    for yy in range(wy0, sh, 26):
        d.line([wx0, yy, wx1, yy], fill=(110, 115, 120), width=5)
    d.rectangle([wx0, sh - 14, wx1, sh], fill=(90, 95, 100))
    # CLOSED tag
    if t > 1.2:
        s = ease_back((t - 1.2) / 0.3)
        tag = Image.new("RGBA", (420, 150), (0, 0, 0, 0))
        td = ImageDraw.Draw(tag)
        td.rounded_rectangle([0, 0, 419, 149], 18, fill=RED)
        td.text((210, 75), "CLOSED", font=F_SIGN, fill=WHITE, anchor="mm")
        tag = tag.rotate(-8, expand=True, resample=Image.BICUBIC)
        tw, th = max(1, int(tag.width * s)), max(1, int(tag.height * s))
        tag = tag.resize((tw, th), Image.LANCZOS)
        img.paste(tag, (int(W / 2 - tw / 2), int(1120 - th / 2)), tag)
    img = finish(img)
    caption(img, [[("카페 ", WHITE, F_CAP), ("3곳 중 2곳", YEL, F_CAP), (",", WHITE, F_CAP)],
                  [("5년 안에 ", WHITE, F_CAP), ("문 닫는다", RED, F_CAP)]], t)
    return img

# ---------------- scene 2: busy -> empty register ----------------
def person(d, x, y, c, s=1.0):
    d.ellipse([x - 38 * s, y - 150 * s, x + 38 * s, y - 74 * s], fill=c)
    d.rounded_rectangle([x - 60 * s, y - 70 * s, x + 60 * s, y + 120 * s], int(40 * s), fill=c)

def counter(d, dark=False):
    d.rectangle([0, 0, W, H], fill=(52, 40, 34) if not dark else (28, 26, 28))
    # menu board
    d.rounded_rectangle([140, 720, 940, 900], 16, fill=(25, 25, 25))
    for i, (m, p) in enumerate([("아메리카노", "4,500"), ("카페라떼", "5,000")]):
        d.text((200, 750 + i * 70), m, font=F_REC, fill=(230, 230, 230))
        d.text((880, 750 + i * 70), p, font=F_REC, fill=(230, 230, 230), anchor="ra")
    d.rectangle([60, 1300, 1020, 1560], fill=(150, 105, 70) if not dark else (80, 62, 50))
    d.rectangle([60, 1290, 1020, 1310], fill=(190, 140, 95) if not dark else (100, 80, 64))

def register(d, x, y, txt, col):
    d.rounded_rectangle([x - 130, y - 120, x + 130, y], 14, fill=(60, 60, 68))
    d.rounded_rectangle([x - 110, y - 105, x + 110, y - 40], 8, fill=(10, 20, 14))
    d.text((x, y - 72), txt, font=F_MONO, fill=col, anchor="mm")

def scene2(t):
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)
    if t < 1.0:
        counter(d)
        register(d, 780, 1290, "₩4,500", GREEN)
        cols = [(220, 120, 90), (90, 150, 220), (240, 190, 80), (140, 200, 140), (200, 120, 200), (110, 200, 210)]
        bob = math.sin(t * 20)
        for i, x in enumerate([140, 300, 460, 620]):
            person(d, x + (6 * bob if i % 2 else -6 * bob), 1340, cols[i], 1.0)
        for i, x in enumerate([220, 380, 540, 700, 860]):
            person(d, x, 1450, cols[(i + 2) % 6], 1.15)
        # "+ ₩" floats
        for i in range(3):
            pt = (t * 1.6 + i / 3) % 1
            d.text((780 + (i - 1) * 90, 1150 - pt * 200), "+₩", font=F_SMALL, fill=(GREEN[0], GREEN[1], GREEN[2]))
    else:
        counter(d, dark=True)
        tl = t - 1.0
        register(d, 540, 1290, "₩0", RED if int(tl * 6) % 2 == 0 else (120, 40, 40))
        # empty wallet / coin falling
        cy = 1000 + ease_out(tl / 0.6) * 260
        d.ellipse([500, cy, 580, cy + 30], fill=(200, 170, 60))
    # wipe transition
    if 0.85 < t < 1.15:
        wp = (t - 0.85) / 0.3
        x = int(-W + 2 * W * wp)
        d.rectangle([x, 0, x + W, H], fill=WHITE)
    img = finish(img)
    caption(img, [[("손님 많아도", WHITE, F_CAP)], [("남는 게 ", WHITE, F_CAP), ("없다", RED, F_CAP)]], t)
    return img

# ---------------- scene 3: receipt ----------------
def fmt(n): return f"{n:,}"

def scene3(t):
    img = Image.new("RGB", (W, H), (36, 30, 26))
    d = ImageDraw.Draw(img)
    # table texture
    for i in range(0, H, 90):
        d.line([0, i, W, i + 40], fill=(42, 35, 30), width=30)
    # receipt (zoom in slightly over time)
    z = 1.0 + 0.04 * clamp(t / 4)
    rw, rh = 680, 860
    rec = Image.new("RGBA", (rw, rh + 30), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rec)
    rd.rectangle([0, 0, rw, rh], fill=(250, 248, 240))
    for i in range(0, rw, 34):  # zigzag tear
        rd.polygon([(i, rh), (i + 17, rh + 24), (i + 34, rh)], fill=(250, 248, 240))
    rd.text((rw / 2, 60), "RECEIPT", font=F_SIGN, fill=(40, 40, 40), anchor="mm")
    rd.line([40, 110, rw - 40, 110], fill=(120, 120, 120), width=3)
    ink = (50, 50, 50)
    rd.text((50, 140), "아메리카노", font=F_REC, fill=ink)
    rd.text((rw - 50, 140), "4,500", font=F_REC, fill=ink, anchor="ra")
    show2 = clamp((t - 1.0) / 0.25)
    if show2 > 0:
        a = int(255 * show2)
        rd.text((50, 215), "+ 디저트 세트", font=F_REC, fill=(30, 140, 80, a))
        rd.text((rw - 50, 215), "5,500", font=F_REC, fill=(30, 140, 80, a), anchor="ra")
    show3 = clamp((t - 2.3) / 0.25)
    if show3 > 0:
        a = int(255 * show3)
        rd.text((50, 290), "1만원 이상 할인", font=F_REC, fill=(220, 50, 50, a))
        rd.text((rw - 50, 290), "-1,000", font=F_REC, fill=(220, 50, 50, a), anchor="ra")
    for x in range(40, rw - 40, 24):
        rd.line([x, 390, x + 12, 390], fill=(120, 120, 120), width=3)
    rd.text((50, 430), "TOTAL", font=F_REC, fill=ink)
    # total counter 4,500 -> 10,000
    cp = ease_out((t - 1.0) / 0.9)
    val = int(round((4500 + (10000 - 4500) * cp) / 100) * 100)
    pop = 1.0 + 0.25 * math.sin(math.pi * clamp((t - 1.9) / 0.35))
    tf = font("Black", int(110 * pop))
    col = (30, 140, 80) if t > 1.9 else (30, 30, 30)
    rd.text((rw / 2, 600), "₩" + fmt(val), font=tf, fill=col, anchor="mm")
    if t > 2.3:
        rd.text((rw / 2, 730), "결제 9,000원 · 객단가 2배", font=F_SMALL, fill=(120, 120, 120), anchor="mm")
    rec = rec.rotate(-3, expand=True, resample=Image.BICUBIC)
    rec = rec.resize((int(rec.width * z), int(rec.height * z)), Image.LANCZOS)
    shadow = Image.new("RGBA", rec.size, (0, 0, 0, 0))
    shadow.paste((0, 0, 0, 140), mask=rec.split()[3])
    shadow = shadow.filter(ImageFilter.GaussianBlur(18))
    px, py = int(W / 2 - rec.width / 2), 760
    img.paste(shadow, (px + 18, py + 24), shadow)
    img.paste(rec, (px, py), rec)
    img = finish(img)
    # caption: X line then O line
    d = ImageDraw.Draw(img)
    pop1 = ease_back(t / 0.25)
    draw_mark_line(img, 300, "x", "전 메뉴 할인", t, strike=t > 0.5)
    if t > 0.9:
        draw_mark_line(img, 450, "o", "1만원 이상 1천원 할인", t - 0.9, hl=True)
    return img

def draw_mark_line(img, y, mark, txt, tl, strike=False, hl=False):
    f = F_CAP_S
    d = ImageDraw.Draw(img)
    tw = text_w(d, txt, f)
    total = 100 + 20 + tw
    layer = Image.new("RGBA", (int(total) + 60, 140), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    cx, cy = 30 + 50, 70
    if mark == "x":
        ld.line([cx - 36, cy - 36, cx + 36, cy + 36], fill=RED, width=18)
        ld.line([cx - 36, cy + 36, cx + 36, cy - 36], fill=RED, width=18)
    else:
        ld.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], outline=RED, width=16)
    tx = 30 + 120
    color = (170, 170, 170) if mark == "x" else YEL
    ld.text((tx, cy), txt, font=f, fill=color, anchor="lm", stroke_width=9, stroke_fill=(0, 0, 0))
    if strike:
        sp = clamp((tl - 0.5) / 0.25)
        ld.line([tx - 10, cy, tx - 10 + (tw + 20) * sp, cy], fill=RED, width=12)
    s = max(0.01, 0.6 + 0.4 * ease_back(tl / 0.25))
    lw, lh = max(1, int(layer.width * s)), max(1, int(layer.height * s))
    layer = layer.resize((lw, lh), Image.LANCZOS)
    img.paste(layer, (int(W / 2 - lw / 2), int(y + (140 - lh) / 2)), layer)

# ---------------- scene 4: blog / 4-step table ----------------
def scene4(t):
    img = Image.new("RGB", (W, H), (24, 26, 34))
    d = ImageDraw.Draw(img)
    slide = ease_out(t / 0.35)
    ox = int((1 - slide) * 300)
    # browser card
    x0, y0, x1, y1 = 110 + ox, 660, 970 + ox, 1460
    d.rounded_rectangle([x0, y0, x1, y1], 28, fill=WHITE)
    d.rounded_rectangle([x0, y0, x1, y0 + 70], 28, fill=(230, 232, 236))
    d.rectangle([x0, y0 + 40, x1, y0 + 70], fill=(230, 232, 236))
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([x0 + 30 + i * 40, y0 + 22, x0 + 56 + i * 40, y0 + 48], fill=c)
    d.text((x0 + 50, y0 + 110), "카페 마케팅 4단계", font=font("Black", 58), fill=(20, 20, 20))
    for i in range(4):
        appear = clamp((t - 0.25 - i * 0.15) / 0.2)
        if appear <= 0: continue
        ry = y0 + 220 + i * 150
        rx = x0 + 40 + int((1 - appear) * 60)
        d.rounded_rectangle([rx, ry, x1 - 40, ry + 120], 18, fill=(245, 246, 250), outline=(225, 228, 235), width=2)
        d.rounded_rectangle([rx + 20, ry + 25, rx + 170, ry + 95], 14, fill=YEL)
        d.text((rx + 95, ry + 60), f"STEP {i + 1}", font=F_SMALL, fill=(20, 20, 20), anchor="mm")
        # blurred teaser bars
        d.rounded_rectangle([rx + 200, ry + 38, rx + 200 + [420, 360, 450, 330][i], ry + 82], 12, fill=(205, 208, 216))
    # lock badge over content (teaser)
    if t > 0.9:
        s = ease_back((t - 0.9) / 0.3)
        b = Image.new("RGBA", (520, 110), (0, 0, 0, 0))
        bd = ImageDraw.Draw(b)
        bd.rounded_rectangle([0, 0, 519, 109], 55, fill=(20, 20, 20, 235))
        bd.text((260, 55), "전체 내용은 링크에서", font=F_SMALL, fill=WHITE, anchor="mm")
        bw, bh = max(1, int(520 * s)), max(1, int(110 * s))
        b = b.resize((bw, bh), Image.LANCZOS)
        img.paste(b, (int(W / 2 - bw / 2 + ox), int(1250 - bh / 2)), b)
    img = finish(img)
    caption(img, [[("카페 마케팅 ", WHITE, F_CAP), ("4단계", YEL, F_CAP)]], t, y=280)
    # CTA pill with bouncing arrow
    d = ImageDraw.Draw(img)
    bounce = abs(math.sin(t * 7)) * 22
    cta = "프로필 링크"
    f = font("Black", 80)
    tw = text_w(d, cta, f)
    pw = tw + 230
    px0 = W / 2 - pw / 2
    d.rounded_rectangle([px0, 440, px0 + pw, 580], 70, fill=YEL)
    ax = px0 + 50 + bounce
    d.polygon([(ax, 485), (ax + 60, 485), (ax + 60, 465), (ax + 110, 510), (ax + 60, 555), (ax + 60, 535), (ax, 535)], fill=(20, 20, 20))
    d.text((px0 + 190, 510), cta, font=f, fill=(20, 20, 20), anchor="lm")
    return img

SCENES = [(0, 2, scene1), (2, 4, scene2), (4, 8, scene3), (8, 10, scene4)]

def frame(i):
    t = i / FPS
    for a, b, fn in SCENES:
        if a <= t < b or (b == DUR and t >= a):
            img = fn(t - a)
            # quick flash at scene starts
            if t - a < 0.08 and a > 0:
                img = Image.blend(img, Image.new("RGB", (W, H), WHITE), 0.5 * (1 - (t - a) / 0.08))
            return img

# ---------------- audio: beat + sfx ----------------
SR = 44100
def make_audio(path):
    n = int(SR * DUR)
    a = np.zeros(n)
    tt = np.arange(n) / SR
    def add(start, sig):
        s = int(start * SR); e = min(n, s + len(sig)); a[s:e] += sig[:e - s]
    def env(L, dec): x = np.arange(int(L * SR)) / SR; return np.exp(-x * dec)
    # kick every 0.5 s, hat on offbeats
    for k in np.arange(0, DUR, 0.5):
        x = np.arange(int(0.3 * SR)) / SR
        f = 120 * np.exp(-x * 25) + 45
        add(k, 0.7 * np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 9))
        add(k + 0.25, 0.08 * np.random.randn(int(0.05 * SR)) * env(0.05, 80))
    # bass line
    notes = [55, 55, 49, 49, 65.4, 65.4, 61.7, 61.7, 55, 55]
    for i, fr in enumerate(notes):
        x = np.arange(int(1.0 * SR)) / SR
        add(i, 0.18 * np.sign(np.sin(2 * np.pi * fr * x)) * np.exp(-x * 2.5))
    # whooshes at transitions
    for ts in (1.9, 2.85, 3.9, 7.9):
        L = 0.35; x = np.arange(int(L * SR)) / SR
        noise = np.random.randn(len(x))
        noise = np.convolve(noise, np.ones(8) / 8, mode="same")
        add(ts, 0.35 * noise * np.sin(np.pi * x / L) ** 2)
    # shutter rattle 0.15-1.25
    x = np.arange(int(1.1 * SR)) / SR
    add(0.15, 0.15 * np.random.randn(len(x)) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 18 * x))) * np.exp(-x * 1.5))
    # cash register ding at 5.9 and 6.3
    for ts, fr in ((5.9, 1568), (6.05, 2093), (6.3, 2637)):
        x = np.arange(int(0.8 * SR)) / SR
        add(ts, 0.25 * (np.sin(2 * np.pi * fr * x) + 0.4 * np.sin(2 * np.pi * fr * 2.01 * x)) * np.exp(-x * 5))
    # fade out
    a[-int(0.4 * SR):] *= np.linspace(1, 0, int(0.4 * SR))
    a = a / np.max(np.abs(a)) * 0.8
    with wave.open(path, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((a * 32767).astype(np.int16).tobytes())

if __name__ == "__main__":
    if "--still" in sys.argv:
        for ts in (1.5, 2.5, 3.5, 4.8, 7.0, 9.5):
            frame(int(ts * FPS)).save(os.path.join(HERE, f"still_{ts}.png"))
        sys.exit()
    wav = os.path.join(HERE, "bgm.wav")
    np.random.seed(1)
    make_audio(wav)
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                          "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
                          "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", OUT],
                         stdin=subprocess.PIPE)
    for i in range(N):
        p.stdin.write(frame(i).tobytes())
    p.stdin.close(); p.wait()
    print("done", OUT)
