"""MiniMax 음성으로 호두강정 릴스 나레이션 6개 파일을 만듭니다.

PC에서 실행:
    set MINIMAX_API_KEY=발급받은키        (Windows)
    export MINIMAX_API_KEY=발급받은키     (Mac)
    python make_narration.py

결과: narration/narr_1.mp3 ~ narr_6.mp3  -> 이 폴더째 채팅에 올려주세요.
목소리를 바꾸려면 VOICE_ID 를 MiniMax 콘솔의 한국어 목소리 ID로 바꾸세요.
"""
import json, os, urllib.request

VOICE_ID = os.environ.get("MINIMAX_VOICE_ID", "Korean_SweetGirl")
MODEL = "speech-02-hd"
SPEED = 1.05

# (장면, 문장) — 장면 길이 안에 들어가도록 짧게 썼어요.
LINES = [
    ("1 인물(0~5초)",        "선물 고민 중이세요? 제가 직접 굽는 호두강정 보여드릴게요."),
    ("2 호두(5~8초)",        "튀기지 않고, 오븐에 구워서 담백해요."),
    ("3 과정(8~14초)",       "좋은 호두를 데치고, 씻고, 구운 다음 유기농 설탕으로 조려 한 번 더 구워요."),
    ("4 병·선물세트(14~19초)", "유리병 세 개에 정성껏 담은 프리미엄 선물세트예요."),
    ("5 포장(19~22초)",      "복덕만래 금박택 포장도 해드려요."),
    ("6 인물 마무리(22초~)",   "댓글에 호두 남겨주시면, 구매링크 바로 보내드릴게요!"),
]

key = os.environ["MINIMAX_API_KEY"]
os.makedirs("narration", exist_ok=True)
for i, (scene, text) in enumerate(LINES, 1):
    body = {
        "model": MODEL, "text": text, "stream": False, "language_boost": "Korean",
        "voice_setting": {"voice_id": VOICE_ID, "speed": SPEED, "vol": 1.0, "pitch": 0},
        "audio_setting": {"sample_rate": 44100, "bitrate": 128000, "format": "mp3", "channel": 1},
    }
    req = urllib.request.Request("https://api.minimax.io/v1/t2a_v2", data=json.dumps(body).encode(),
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    res = json.load(urllib.request.urlopen(req))
    if res.get("base_resp", {}).get("status_code") != 0:
        raise SystemExit(f"{scene} 실패: {res.get('base_resp')}")
    with open(f"narration/narr_{i}.mp3", "wb") as f:
        f.write(bytes.fromhex(res["data"]["audio"]))
    print("완료:", scene, text)
