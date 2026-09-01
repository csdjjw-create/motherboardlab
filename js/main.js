// ===================== 마더보드Lab 홈페이지 스크립트 =====================

document.addEventListener('DOMContentLoaded', function () {

  /* ---------- 모바일 메뉴 토글 ---------- */
  var menuBtn = document.getElementById('mobile-menu-btn');
  var menuPanel = document.getElementById('mobile-menu-panel');

  if (menuBtn && menuPanel) {
    menuBtn.addEventListener('click', function () {
      var isHidden = menuPanel.classList.contains('hidden');
      if (isHidden) {
        menuPanel.classList.remove('hidden');
        menuBtn.innerHTML = '<i class="fa-solid fa-xmark"></i>';
      } else {
        menuPanel.classList.add('hidden');
        menuBtn.innerHTML = '<i class="fa-solid fa-bars"></i>';
      }
    });

    // 모바일 메뉴 링크 클릭 시 메뉴 닫기
    var mobileLinks = document.querySelectorAll('.mobile-nav-link');
    mobileLinks.forEach(function (link) {
      link.addEventListener('click', function () {
        menuPanel.classList.add('hidden');
        menuBtn.innerHTML = '<i class="fa-solid fa-bars"></i>';
      });
    });
  }

  /* ---------- 헤더 스크롤 시 그림자 ---------- */
  var header = document.getElementById('site-header');
  window.addEventListener('scroll', function () {
    if (window.scrollY > 10) {
      header.classList.add('scrolled');
    } else {
      header.classList.remove('scrolled');
    }
  });

  /* ---------- FAQ 아코디언 ---------- */
  var faqItems = document.querySelectorAll('.faq-item');
  faqItems.forEach(function (item) {
    var question = item.querySelector('.faq-question');
    var answer = item.querySelector('.faq-answer');

    question.addEventListener('click', function () {
      var isOpen = item.classList.contains('open');

      // 다른 항목 닫기 (아코디언 방식)
      faqItems.forEach(function (other) {
        other.classList.remove('open');
        other.querySelector('.faq-answer').style.maxHeight = null;
      });

      if (!isOpen) {
        item.classList.add('open');
        answer.style.maxHeight = answer.scrollHeight + 40 + 'px';
      }
    });
  });

  /* ---------- 상담 신청 폼 제출 ---------- */
  var form = document.getElementById('consultation-form');
  var submitBtn = document.getElementById('submit-btn');
  var submitBtnText = document.getElementById('submit-btn-text');
  var feedback = document.getElementById('form-feedback');

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var name = document.getElementById('input-name').value.trim();
      var phone = document.getElementById('input-phone').value.trim();
      var email = document.getElementById('input-email').value.trim();
      var message = document.getElementById('input-message').value.trim();
      var serviceRadio = form.querySelector('input[name="service_interest"]:checked');
      var serviceInterest = serviceRadio ? serviceRadio.value : '아직 잘 모르겠어요';

      if (!name || !phone) {
        showFeedback('이름과 연락처는 필수 입력 항목입니다.', 'error');
        return;
      }

      submitBtn.disabled = true;
      submitBtnText.textContent = '전송 중...';

      fetch('tables/consultation_requests', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name,
          phone: phone,
          email: email,
          service_interest: serviceInterest,
          message: message,
          status: 'new'
        })
      })
        .then(function (res) {
          if (!res.ok) { throw new Error('전송 실패'); }
          return res.json();
        })
        .then(function () {
          showFeedback('상담 신청이 정상적으로 접수되었습니다. 빠르게 확인 후 연락드리겠습니다.', 'success');
          form.reset();
        })
        .catch(function () {
          showFeedback('전송 중 문제가 발생했습니다. 잠시 후 다시 시도해주시거나 카카오톡 채널로 문의해주세요.', 'error');
        })
        .finally(function () {
          submitBtn.disabled = false;
          submitBtnText.textContent = '무료 상담 신청하기';
        });
    });
  }

  function showFeedback(msg, type) {
    feedback.textContent = msg;
    feedback.classList.remove('hidden', 'success', 'error');
    feedback.classList.add(type);
    feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

});
