# 마더보드Lab 홈페이지

블로그 글쓰기 코칭 및 대행 서비스를 제공하는 **마더보드Lab**의 원페이지(One-Page) 홈페이지입니다.
`docs/plan.md` 기획안의 11개 섹션 구성과 5대 필수 요건(FAQ, 근거자료, 추천/예외 상황, 맥락 중심 서술, 광고표시법 준수)을 반영하여 제작했습니다.

> 이 저장소는 원래 다른 플랫폼(노코드 빌더)에서 만들어진 사이트를 그대로 옮겨온 뒤, 정적 사이트 환경에 맞게 업그레이드한 버전입니다. 업그레이드 내역은 [8. 업그레이드 내역](#8-업그레이드-내역)을 참고해주세요.

## 1. 완료된 기능

- **반응형 원페이지 레이아웃**: 데스크톱 / 모바일(햄버거 메뉴) 모두 지원
- **11개 섹션 구성**
  1. 메인(Hero) — 과정 중심 카피, 결과 단정 표현 제거
  2. 브랜드 스토리(About) — 대표자 실무 경력 서사, 미확정 수치 미게시
  3. 왜 지금인가 — 6개월 이내 통계(2026.3, 2025.12 발표) + 출처 병기
  4. 서비스 소개(코칭/대행) — 스펙 나열 대신 맥락 중심 서술 + **추천 대상 / 사전 상담 필요(예외) 대상** 명시
  5. 프로세스(5단계) — "감이 아닌 데이터"류 과장 표현 완화
  6. 왜 마더보드Lab인가 — "성과 10배·비용 50%절감" 등 근거 없는 비교광고 표현 삭제, 정성적 강점으로 대체
  7. 성과/근거 → "우리가 참고하는 접근 방식" — 검증 안 된 타사 사례 삭제
  8. 요금제/패키지 — 맥락 중심 설명 + 추천/예외 상황, 확정 금액 미게시(상담 안내)
  9. 고객 후기 → "신뢰 근거" — 허위 후기 형식 미사용, 초기 브랜드임을 투명하게 안내
  10. FAQ — 10문항, 효과·보장성 표현 광고법 준수 문구로 작성, 아코디언 UI
  11. 문의/상담 신청(Contact) — 폼 + 카카오톡 채널 안내
  - **근거자료 섹션** — 출처/발행일 병기 표, 6개월 초과 자료 제외 안내, 자료 갱신일 표기
- **상담 신청 폼 → Table API 연동**: 제출 시 `consultation_requests` 테이블에 저장
- **FAQ 아코디언, 모바일 메뉴, 스크롤 스무딩 등 인터랙션**

## 2. 페이지 구조 및 진입점

- `index.html` — 단일 페이지, 앵커(`#hero-section`, `#about-section`, `#services-section`, `#process-section`, `#why-us-section`, `#proof-section`, `#pricing-section`, `#testimonials-section`, `#faq-section`, `#evidence-section`, `#contact-section`)로 구성
- `css/style.css` — 브랜드 컬러(다크퍼플 #450C3F, 다바오그린 #B9D175) 및 커스텀 스타일
- `js/main.js` — 모바일 메뉴, FAQ 아코디언, 상담 폼 제출(Table API) 로직

### 데이터 모델 — `consultation_requests` 테이블

| 필드 | 타입 | 설명 |
|---|---|---|
| id | text | 고유 ID (자동) |
| name | text | 신청자 이름 |
| phone | text | 연락처 |
| email | text | 이메일 |
| service_interest | text (코칭/대행/아직 잘 모르겠어요) | 관심 서비스 |
| message | rich_text | 문의 내용 |
| status | text (new/contacted/closed) | 처리 상태 |

API 엔드포인트: `GET/POST tables/consultation_requests`, `GET/PUT/PATCH/DELETE tables/consultation_requests/{id}`

## 3. 아직 구현되지 않은 항목 (기획안 기준 후속 작업)

1. **대표자 실제 성과 수치**(연간매출 LFL, 전환율 등) — 확정 전까지 게시 보류 중
2. **요금제 실제 금액** — 현재는 "상담 시 안내" 문구로 대체, 원가/마진 확정 후 반영 필요
3. **한경협·모노리서치 등 발행일 미확인 자료** — 정확한 발행일 확인 후 6개월 기준 재판단 필요
4. **실제 고객 후기/사례** — 1~2건 확보 후 "신뢰 근거"·"우리가 참고하는 접근 방식" 섹션 교체 필요
5. **카카오톡 채널 실제 연결 링크** — 현재 `#` placeholder, 실제 채널 URL 연동 필요
6. **상담 접수 관리자 화면** — 현재는 Table API에 저장만 되며, 별도 관리자 대시보드는 미구현

## 4. 다음 단계 제안

- 카카오톡 채널 실제 URL 연결
- 대표자/패키지 확정 정보 반영 후 재검토
- 첫 고객 사례 확보 시 9번(신뢰 근거), 7번(접근 방식) 섹션을 실제 후기로 교체
- 게시 직전 기획안 4장의 **광고표시법 체크리스트** 재확인
- 상담 신청 접수 확인을 위한 관리자 페이지 또는 알림(이메일/슬랙 등) 연동 검토 — 단, 이는 서버 기능이 필요하므로 별도 백엔드 연동 방안 논의 필요

## 5. 공개 URL

- 미리보기: 프로젝트 Preview 탭에서 확인 가능
- 배포: **Publish 탭**에서 원클릭 배포 시 실제 서비스 URL 발급 (본 대화에서는 배포를 수행하지 않았습니다)

## 6. 사용 기술

- HTML5 / Tailwind CSS (빌드된 정적 CSS) / 커스텀 CSS
- Vanilla JavaScript (프레임워크 없음)
- Font Awesome 아이콘, Google Fonts(Noto Sans KR, Gowun Batang)
- Formspree — 상담 신청 폼 제출 처리 (아래 7번 참고)

## 7. 로컬 개발 · 배포 준비

### 7-1. CSS 빌드

기존에는 Tailwind CDN 런타임 컴파일러(`cdn.tailwindcss.com`)를 사용했습니다. 이 방식은 Tailwind 공식 문서에서도 **프로덕션 사용을 권장하지 않으며**(매 요청마다 브라우저에서 CSS를 실시간 컴파일하므로 느림), 이번 업그레이드에서 빌드 타임에 미리 컴파일된 정적 CSS(`css/tailwind.css`)로 교체했습니다.

```bash
npm install        # 최초 1회
npm run build:css  # css/tailwind.css 생성 (배포 전 필수)
npm run watch:css   # 개발 중 index.html 클래스 변경 시 자동 재빌드
```

`index.html`의 Tailwind 클래스를 수정했다면 배포 전 반드시 `npm run build:css`를 다시 실행해야 변경 사항이 `css/tailwind.css`에 반영됩니다. 이 파일은 저장소에 커밋되어 있으므로, 빌드 없이 정적 파일만 올려도 사이트는 정상 동작합니다.

### 7-2. 상담 신청 폼 (Formspree) 연동

기존 사이트는 노코드 빌더 전용 백엔드(`tables/consultation_requests` Table API)를 사용했는데, 이 저장소로 옮기면서 해당 API가 더 이상 존재하지 않습니다. 별도 백엔드 없이 폼을 받을 수 있도록 [Formspree](https://formspree.io)로 교체했습니다.

1. [formspree.io](https://formspree.io)에서 무료 계정을 만들고 새 폼을 생성합니다.
2. 발급받은 폼 엔드포인트(`https://formspree.io/f/xxxxxxxx`)를 복사합니다.
3. `js/main.js` 최상단의 `FORMSPREE_ENDPOINT` 값을 실제 엔드포인트로 교체합니다.

```js
var FORMSPREE_ENDPOINT = 'https://formspree.io/f/xxxxxxxx';
```

교체 전까지는 폼 제출 시 전송 실패 메시지가 표시됩니다. 실제 서비스 배포 전에 반드시 교체해주세요.

### 7-3. 배포 (GitHub Pages 예시)

이 저장소는 순수 정적 파일(`index.html`, `css/`, `js/`)로 구성되어 있어 별도 서버 없이 바로 호스팅할 수 있습니다.

1. GitHub 저장소 **Settings → Pages**에서 배포 브랜치를 지정합니다.
2. 배포 전 `index.html`, `robots.txt`, `sitemap.xml` 내 `https://motherboardlab.com/` 부분을 실제 도메인으로 교체합니다 (현재는 placeholder 도메인입니다).
3. `og-image.png`(소셜 공유 미리보기 이미지, 1200×630px 권장)를 준비해 저장소 루트에 추가하면 카카오톡·SNS 공유 시 썸네일이 표시됩니다.

## 8. 업그레이드 내역

이번 작업에서 기존 소스를 그대로 옮겨온 뒤 아래 항목을 개선했습니다. 카피·정보 구조·광고법 준수 원칙(기획안 4장 체크리스트)은 그대로 유지했습니다.

- **성능**: Tailwind CDN 런타임 컴파일러 → 빌드 타임 정적 CSS(약 16KB, minify)로 전환
- **SEO**: Open Graph/Twitter Card 메타태그, canonical, JSON-LD(ProfessionalService) 구조화 데이터, `robots.txt`, `sitemap.xml`, 파비콘 추가
- **접근성**: 본문 바로가기(skip link), 모바일 메뉴/FAQ 아코디언 `aria-expanded` 상태 연결, 장식용 아이콘 `aria-hidden` 처리, 폼 라디오 그룹 `fieldset/legend`, 폼 상태 메시지 `aria-live` 처리
- **폼 처리**: 존재하지 않는 Table API 호출 → Formspree 연동으로 교체 (7-2 참고)
- **UX**: 스크롤 시 섹션별 페이드인 애니메이션, 현재 위치 내비게이션 하이라이트, 맨 위로 이동 버튼, 모바일 메뉴 Esc/바깥 클릭 닫기
- **견고성**: 아이콘 폰트 로드 실패 시에도 모바일 메뉴 버튼이 크기를 잃지 않도록 명시적 크기 지정
