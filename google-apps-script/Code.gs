/**
 * 마더보드Lab 상담 신청 폼 → Google Sheets 저장용 Apps Script
 *
 * 사용법 (README.md 7-2 섹션 참고):
 * 1. 구글 스프레드시트를 새로 만들고, 첫 행에 아래 헤더를 입력합니다.
 *    제출일시 | 이름 | 연락처 | 이메일 | 관심 서비스 | 문의 내용
 * 2. 확장 프로그램 → Apps Script 에서 기본 코드를 지우고 이 파일 내용을 붙여넣습니다.
 * 3. NOTIFY_EMAIL 값을 상담 알림을 받을 이메일 주소로 바꿉니다.
 * 4. 배포 → 새 배포 → 유형: 웹 앱
 *    - 실행 계정: 나
 *    - 액세스 권한이 있는 사용자: 모든 사용자
 *    로 배포하고, 발급된 웹 앱 URL을 복사합니다.
 * 5. 그 URL을 js/main.js의 GOOGLE_SHEETS_ENDPOINT 값에 붙여넣습니다.
 */

var NOTIFY_EMAIL = 'your-email@example.com'; // 상담 알림을 받을 이메일 주소로 교체

function doPost(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  var p = e.parameter;

  var name = p.name || '';
  var phone = p.phone || '';
  var email = p.email || '';
  var serviceInterest = p.service_interest || '';
  var message = p.message || '';

  sheet.appendRow([
    new Date(),
    name,
    phone,
    email,
    serviceInterest,
    message
  ]);

  if (NOTIFY_EMAIL && NOTIFY_EMAIL.indexOf('@') > -1) {
    MailApp.sendEmail({
      to: NOTIFY_EMAIL,
      subject: '[마더보드Lab] 새 상담 신청: ' + name,
      body:
        '이름: ' + name + '\n' +
        '연락처: ' + phone + '\n' +
        '이메일: ' + email + '\n' +
        '관심 서비스: ' + serviceInterest + '\n' +
        '문의 내용:\n' + message
    });
  }

  return ContentService.createTextOutput(JSON.stringify({ result: 'success' }))
    .setMimeType(ContentService.MimeType.JSON);
}
