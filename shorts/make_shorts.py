import subprocess, sys, math, wave
import numpy as np
from PIL import Image, ImageOps, ImageDraw, ImageFont, ImageFilter

UP = "/root/.claude/uploads/cf3fe6e8-bb95-5395-aead-f4ff38ead681/"
OUT = sys.argv[1]
W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"

# (file, caption, sub, zoom direction)
SLIDES = [
    ("8db72fa2", "경복궁 돌담길", "노랗게 물든 은행나무 터널", "in"),
    ("ef52d7ac", "창밖으로 보는 가을", "돌담 위로 쏟아지는 은행잎", "out"),
    ("08869e72", "한복 입고 궁 나들이", "경복궁 앞 한복 거리", "in"),
    ("e980c0e2", "골목 산책", "랜턴이 걸린 자하문로 골목", "out"),
    ("3a55dd37", "작은 책방 '책책'", "It's nice to meet you!", "in"),
    ("eb28d8c3", "은행나무 한 그루", "조용한 주택가 골목", "out"),
    ("fb8c6157", "부암동 가는 길", "단풍 물든 산이 반겨주는 곳", "in"),
    ("37784133", "단풍 속 한옥", "부암동 숲길 산책", "pan"),
    ("0f17b45e", "부암동에서 내려다본 서울", "빨간 지붕 너머 도심", "out"),
    ("da38b62e", "골목 고양이들", "햇살 아래 낮잠 시간", "in"),
    ("0be75bc9", "소품샵 구경", "초록 덩굴 아래 화분 가게", "out"),
    ("85e1051e", "따뜻한 조명 아래", "감성 가득 잡화점", "in"),
    ("88dd6ecf", "꽃 한 아름", "가을 색을 닮은 꽃들", "out"),
    ("66019bb5", "한옥 골목", "좁은 길 끝에 숨은 공간", "in"),
    ("7381d886", "한옥 카페에서 마무리", "효자로 7길", "out"),
]
INTRO, SLIDE, OUTRO, XF = 3.0, 2.4, 2.6, 0.45
SCALE = 1.14

def font(sz): return ImageFont.truetype(FONT, sz)

def cover(img, w, h):
    r = max(w / img.width, h / img.height)
    img = img.resize((math.ceil(img.width * r), math.ceil(img.height * r)), Image.LANCZOS)
    l, t = (img.width - w) // 2, (img.height - h) // 2
    return img.crop((l, t, l + w, t + h))

def load(fid):
    return ImageOps.exif_transpose(Image.open(UP + fid + "-image.jpg")).convert("RGB")

def shadow_text(d_img, xy, text, f, fill, anchor="mm", blur=10, stroke=0):
    layer = Image.new("RGBA", d_img.size, (0, 0, 0, 0))
    ImageDraw.Draw(layer).text(xy, text, font=f, fill=(0, 0, 0, 200), anchor=anchor, stroke_width=stroke + 4, stroke_fill=(0, 0, 0, 200))
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    d_img.alpha_composite(layer)
    ImageDraw.Draw(d_img).text(xy, text, font=f, fill=fill, anchor=anchor, stroke_width=stroke, stroke_fill=(30, 20, 0, 255))

def gradient(h0, h1, top_alpha, bottom_alpha):
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    a = np.zeros((H, W), np.uint8)
    for y in range(h0, h1):
        t = (y - h0) / max(1, h1 - h0)
        a[y, :] = int(top_alpha + (bottom_alpha - top_alpha) * t)
    g.putalpha(Image.fromarray(a))
    return g

def caption_layer(title, sub, idx):
    L = gradient(1250, H, 0, 190)
    shadow_text(L, (W // 2, 1560), title, font(84), (255, 255, 255, 255))
    shadow_text(L, (W // 2, 1670), sub, font(46), (255, 226, 120, 255))
    # top badge
    d = ImageDraw.Draw(L)
    badge = "11월 여행지 · 서울 종로"
    f = font(38)
    bw = d.textlength(badge, font=f) + 60
    d.rounded_rectangle((W // 2 - bw / 2, 150, W // 2 + bw / 2, 222), 36, fill=(0, 0, 0, 120))
    d.text((W // 2, 186), badge, font=f, fill=(255, 255, 255, 235), anchor="mm")
    d.text((W // 2, 1790), f"{idx:02d} / {len(SLIDES):02d}", font=font(30), fill=(255, 255, 255, 170), anchor="mm")
    return L

def intro_layer():
    L = gradient(0, H, 60, 150)
    shadow_text(L, (W // 2, 640), "11월", font(230), (255, 214, 60, 255), blur=16, stroke=3)
    shadow_text(L, (W // 2, 860), "여행지", font(190), (255, 255, 255, 255), blur=16, stroke=3)
    shadow_text(L, (W // 2, 1080), "서울 종로구", font(70), (255, 255, 255, 255))
    shadow_text(L, (W // 2, 1180), "경복궁 & 부암동", font(62), (255, 226, 120, 255))
    return L

def outro_layer():
    L = gradient(0, H, 120, 170)
    shadow_text(L, (W // 2, 820), "이번 11월엔", font(90), (255, 255, 255, 255))
    shadow_text(L, (W // 2, 960), "종로로 떠나요", font(120), (255, 214, 60, 255), stroke=2)
    shadow_text(L, (W // 2, 1110), "경복궁 · 서촌 · 부암동", font(54), (255, 255, 255, 255))
    shadow_text(L, (W // 2, 1300), "저장하고 가을에 꼭 가보세요", font(46), (255, 226, 120, 255))
    return L

def base_for(fid, mode):
    img = load(fid)
    if mode == "pan":  # landscape: fill height, pan horizontally
        r = (H * 1.02) / img.height
        return img.resize((int(img.width * r), int(H * 1.02)), Image.LANCZOS)
    return cover(img, int(W * SCALE), int(H * SCALE))

def frame_from(base, mode, t):  # t in 0..1
    e = 0.5 - 0.5 * math.cos(math.pi * t)
    if mode == "pan":
        x = int((base.width - W) * (0.15 + 0.7 * e))
        return base.crop((x, 10, x + W, 10 + H))
    z = 1 + (SCALE - 1) * (e if mode == "in" else 1 - e) * 0.9
    cw, ch = base.width / z, base.height / z
    l, tp = (base.width - cw) / 2, (base.height - ch) / 2
    return base.resize((W, H), Image.BILINEAR, box=(l, tp, l + cw, tp + ch))

# build segments: (base, mode, overlay, duration)
segs = []
first = base_for(SLIDES[0][0], "in")
segs.append((first, "out", intro_layer(), INTRO))
for i, (fid, title, sub, mode) in enumerate(SLIDES, 1):
    segs.append((base_for(fid, mode), mode, caption_layer(title, sub, i), SLIDE))
segs.append((base_for("37784133", "pan"), "pan", outro_layer(), OUTRO))

total = sum(s[3] for s in segs)
nframes = int(total * FPS)
starts = np.cumsum([0] + [s[3] for s in segs])

def render(si, t_abs):
    base, mode, ov, dur = segs[si]
    lt = (t_abs - starts[si]) / dur
    lt = min(max(lt, 0), 1)
    fr = frame_from(base, mode, lt).convert("RGBA")
    # overlay fade-in
    a = min(1, max(0, (t_abs - starts[si]) / 0.35))
    if a < 1:
        o = ov.copy(); o.putalpha(o.getchannel("A").point(lambda v: int(v * a)))
    else:
        o = ov
    fr.alpha_composite(o)
    return fr.convert("RGB")

audio_path = OUT + ".wav"
# --- simple soft music: arpeggiated pad ---
sr = 44100
N = int(total * sr)
tt = np.arange(N) / sr
chords = [[261.63, 329.63, 392.0, 493.88], [220.0, 261.63, 329.63, 392.0],
          [174.61, 220.0, 261.63, 329.63], [196.0, 246.94, 293.66, 392.0]]
sig = np.zeros(N)
beat = 0.3
bar = beat * 8
for k in range(int(total / beat) + 1):
    ch = chords[int(k * beat / bar) % 4]
    f0 = ch[[0, 1, 2, 3, 2, 1, 3, 2][k % 8]] * 2
    s = int(k * beat * sr); n = int(1.2 * sr)
    seg = tt[:min(n, N - s)] if s < N else tt[:0]
    env = np.exp(-seg * 3.2) * (1 - np.exp(-seg * 200))
    sig[s:s + len(seg)] += 0.16 * env * (np.sin(2 * np.pi * f0 * seg) + 0.3 * np.sin(4 * np.pi * f0 * seg))
for k in range(int(total / bar) + 1):  # pad
    ch = chords[k % 4]
    s = int(k * bar * sr); n = int(bar * sr)
    seg = tt[:min(n, N - s)] if s < N else tt[:0]
    env = np.sin(np.pi * seg / (bar)) ** 2
    for f in ch[:3]:
        sig[s:s + len(seg)] += 0.045 * env * np.sin(2 * np.pi * f / 2 * seg)
fade = np.ones(N); fl = int(1.5 * sr)
fade[:int(0.5 * sr)] = np.linspace(0, 1, int(0.5 * sr)); fade[-fl:] = np.linspace(1, 0, fl)
sig = sig * fade
sig = sig / np.max(np.abs(sig)) * 0.6
with wave.open(audio_path, "wb") as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes((sig * 32767).astype(np.int16).tobytes())

p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                      "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", audio_path,
                      "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                      "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", OUT],
                     stdin=subprocess.PIPE)
for fi in range(nframes):
    t = fi / FPS
    si = min(int(np.searchsorted(starts, t, side="right") - 1), len(segs) - 1)
    img = render(si, t)
    # crossfade into next segment
    if si + 1 < len(segs) and t > starts[si + 1] - XF:
        a = (t - (starts[si + 1] - XF)) / XF
        nxt = render(si + 1, starts[si + 1])
        img = Image.blend(img, nxt, a)
    if fi in (15, int(5 * FPS), int(20 * FPS)):
        img.save(OUT + f".preview{fi}.jpg", quality=80)
    p.stdin.write(img.tobytes())
p.stdin.close(); p.wait()
print("done", total, "s")
