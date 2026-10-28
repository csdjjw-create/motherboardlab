import subprocess, sys, math
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

UP = "/root/.claude/uploads/b4aac147-e611-5f14-bbea-fa1bd888fd38/"
SP = "/tmp/claude-0/-home-user-motherboardlab/b4aac147-e611-5f14-bbea-fa1bd888fd38/scratchpad/"
FONT_B = SP + "fonts/package/dist/public/static/Pretendard-ExtraBold.otf"
FONT_S = SP + "fonts/package/dist/public/static/Pretendard-SemiBold.otf"
OUT = sys.argv[1]

W, H, FPS = 1080, 1920, 30
CLIP, XF = 2.0, 0.4  # 6 clips -> 6*2.0 - 5*0.4 = 10.0s

# (file, motion, caption, subcaption, blur boxes in display coords 1500x2000)
CLIPS = [
    ("9d904965-image.jpg", "zoom_in",   "10월, 어디 갈까?",   None, []),
    ("5c12bdee-image.jpg", "pan_up",    "하늘이 가장 높은 계절", None, []),
    ("d142b01d-image.jpg", "pan_right", "유럽 같은 골목",       "일산 정발산 주택가", [(415, 1700, 490, 1760)]),
    ("23cfd10c-image.jpg", "zoom_out",  "붉은 벽돌과 담쟁이",    None, []),
    ("4af47532-image.jpg", "pan_left",  "동화 속 성 같은 집들",  None, []),
    ("5de343da-image.jpg", "zoom_in",   "10월엔, 일산",        "정발산 주택가 산책", []),
]

BASE_W, BASE_H = 1296, 2304  # 1.2x of output for motion headroom


def prep(fn, blurs):
    im = ImageOps.exif_transpose(Image.open(UP + fn)).convert("RGB")
    sx = im.width / 1500
    for (x0, y0, x1, y1) in blurs:
        box = tuple(int(v * sx) for v in (x0, y0, x1, y1))
        im.paste(im.crop(box).filter(ImageFilter.GaussianBlur(25)), box)
    cw = im.height * 9 / 16
    left = (im.width - cw) / 2
    im = im.crop((int(left), 0, int(left + cw), im.height))
    return im.resize((BASE_W, BASE_H), Image.LANCZOS)


def ease(t):
    return t * t * (3 - 2 * t)


def frame_of(base, motion, t):
    """t in 0..1 over the clip; returns W x H frame via subpixel crop."""
    e = ease(t)
    if motion == "zoom_in":
        z = 1.0 + 0.12 * e
    elif motion == "zoom_out":
        z = 1.12 - 0.12 * e
    else:
        z = 1.06
    # z=1 shows the whole base; pans need headroom so they use z=1.06
    cw, ch = BASE_W / z, BASE_H / z
    cx, cy = BASE_W / 2, BASE_H / 2
    mx, my = (BASE_W - cw) / 2, (BASE_H - ch) / 2
    if motion == "pan_right":
        cx = BASE_W / 2 - mx + 2 * mx * e
    elif motion == "pan_left":
        cx = BASE_W / 2 + mx - 2 * mx * e
    elif motion == "pan_up":
        cy = BASE_H / 2 + my - 2 * my * e
    box = (cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2)
    return base.resize((W, H), Image.BICUBIC, box=box)


fb = ImageFont.truetype(FONT_B, 104)
fs = ImageFont.truetype(FONT_S, 54)
ftag = ImageFont.truetype(FONT_B, 46)


def text_layer(caption, sub, a, dy):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if a <= 0:
        return layer
    d = ImageDraw.Draw(layer)
    y = 470 + dy
    tw = d.textlength(caption, font=fb)
    x = (W - tw) / 2
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.text((x, y + 6), caption, font=fb, fill=(0, 0, 0, int(170 * a)))
    if sub:
        sw = sd.textlength(sub, font=fs)
        sd.text(((W - sw) / 2, y + 150 + 4), sub, font=fs, fill=(0, 0, 0, int(170 * a)))
    sh = sh.filter(ImageFilter.GaussianBlur(10))
    layer.alpha_composite(sh)
    d.text((x, y), caption, font=fb, fill=(255, 255, 255, int(255 * a)),
           stroke_width=3, stroke_fill=(0, 0, 0, int(90 * a)))
    if sub:
        sw = d.textlength(sub, font=fs)
        d.text(((W - sw) / 2, y + 150), sub, font=fs, fill=(255, 236, 200, int(255 * a)),
               stroke_width=2, stroke_fill=(0, 0, 0, int(90 * a)))
    return layer


def tag_layer():
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    label = "10월 여행지 추천"
    tw = d.textlength(label, font=ftag)
    pw, ph = tw + 70, 84
    x0, y0 = (W - pw) / 2, 300
    d.rounded_rectangle((x0, y0, x0 + pw, y0 + ph), radius=42, fill=(232, 106, 38, 235))
    d.text((x0 + 35, y0 + 14), label, font=ftag, fill=(255, 255, 255, 255))
    return layer


bases = [prep(f, b) for f, _, _, _, b in CLIPS]
TAG = tag_layer()
starts = [i * (CLIP - XF) for i in range(len(CLIPS))]
total = int(round((starts[-1] + CLIP) * FPS))

ff = subprocess.Popen([
    "ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
    "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
    "-f", "lavfi", "-t", f"{total / FPS}", "-i", "anullsrc=r=48000:cl=stereo",
    "-map", "0:v", "-map", "1:a", "-shortest",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", OUT,
], stdin=subprocess.PIPE)

for n in range(total):
    t = n / FPS
    frame = None
    for i, (f, motion, cap, sub, _) in enumerate(CLIPS):
        lt = t - starts[i]
        if lt < 0 or lt > CLIP:
            continue
        img = frame_of(bases[i], motion, lt / CLIP).convert("RGBA")
        # caption: fades in 0.15-0.45s, out over the last 0.3s (last clip stays)
        a_in = min(1, max(0, (lt - 0.15) / 0.3))
        a_out = 1 if i == len(CLIPS) - 1 else min(1, max(0, (CLIP - 0.05 - lt) / 0.3))
        a = a_in * a_out
        img.alpha_composite(text_layer(cap, sub, a, int(30 * (1 - ease(a_in)))))
        if frame is None:
            frame = img
        else:
            mix = min(1, lt / XF)
            frame = Image.blend(frame, img, mix)
    frame.alpha_composite(TAG)
    # gentle fade from/to black at the very ends
    edge = min(1, t / 0.25, (total / FPS - t) / 0.3)
    if edge < 1:
        frame = Image.blend(Image.new("RGBA", (W, H), (0, 0, 0, 255)), frame, max(0, edge))
    ff.stdin.write(frame.convert("RGB").tobytes())

ff.stdin.close()
sys.exit(ff.wait())
