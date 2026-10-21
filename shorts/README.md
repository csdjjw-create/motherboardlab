# 카페 마케팅 10초 쇼츠

- `cafe-marketing-10s.mp4` — 1080×1920, 30fps, 10초 (배경 비트·효과음 포함, 내레이션 없음)
- `cafe-marketing-10s.srt` — 내레이션 타이밍 (녹음/TTS 시 가이드, 자막 업로드용)
- `render_cafe_shorts.py` — 재렌더링 스크립트 (Pillow, numpy, ffmpeg 필요)

재렌더링: `npm pack pretendard@1.3.9 && tar xzf pretendard-1.3.9.tgz` 후
`PRETENDARD_DIR=package/dist/public/static python3 render_cafe_shorts.py out.mp4`
