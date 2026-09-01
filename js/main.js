// ===================== 마더보드Lab 홈페이지 스크립트 =====================

// 상담 신청 폼을 Formspree(https://formspree.io)로 전송합니다.
// README.md 안내에 따라 본인의 Formspree 폼 ID로 교체해주세요.
var FORMSPREE_ENDPOINT = 'https://formspree.io/f/YOUR_FORM_ID';

document.addEventListener('DOMContentLoaded', function () {

  /* ---------- 모바일 메뉴 토글 ---------- */
  var menuBtn = document.getElementById('mobile-menu-btn');
  var menuPanel = document.getElementById('mobile-menu-panel');

  function closeMobileMenu() {
    menuPanel.classList.add('hidden');
    menuBtn.setAttribute('aria-expanded', 'false');
    menuBtn.innerHTML = '<i class="fa-solid fa-bars" aria-hidden="true"></i>';
  }

  function openMobileMenu() {
    menuPanel.classList.remove('hidden');
    menuBtn.setAttribute('aria-expanded', 'true');
    menuBtn.innerHTML = '<i class="fa-solid fa-xmark" aria-hidden="true"></i>';
  }

  if (menuBtn && menuPanel) {
    menuBtn.addEventListener('click', function () {
      var isHidden = menuPanel.classList.contains('hidden');
      if (isHidden) {
        openMobileMenu();
      } else {
        closeMobileMenu();
      }
    });

    // 모바일 메뉴 링크 클릭 시 메뉴 닫기
    var mobileLinks = document.querySelectorAll('.mobile-nav-link');
    mobileLinks.forEach(function (link) {
      link.addEventListener('click', closeMobileMenu);
    });

    // Esc 키 또는 메뉴 바깥 클릭 시 닫기
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menuPanel.classList.contains('hidden')) {
        closeMobileMenu();
        menuBtn.focus();
      }
    });
    document.addEventListener('click', function (e) {
      if (menuPanel.classList.contains('hidden')) { return; }
      if (menuPanel.contains(e.target) || menuBtn.contains(e.target)) { return; }
      closeMobileMenu();
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
        other.querySelector('.faq-question').setAttribute('aria-expanded', 'false');
      });

      if (!isOpen) {
        item.classList.add('open');
        answer.style.maxHeight = answer.scrollHeight + 40 + 'px';
        question.setAttribute('aria-expanded', 'true');
      }
    });
  });

  /* ---------- 스크롤 리빌 애니메이션 ---------- */
  var revealEls = document.querySelectorAll('.reveal');
  if (revealEls.length && 'IntersectionObserver' in window) {
    var revealObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('reveal-visible');
          revealObserver.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealEls.forEach(function (el) { revealObserver.observe(el); });
  } else {
    revealEls.forEach(function (el) { el.classList.add('reveal-visible'); });
  }

  /* ---------- 스크롤 위치에 따른 내비게이션 활성 표시 ---------- */
  var navLinks = document.querySelectorAll('.nav-link');
  var navSections = Array.prototype.slice.call(navLinks).map(function (link) {
    return document.querySelector(link.getAttribute('href'));
  }).filter(Boolean);

  if (navSections.length && 'IntersectionObserver' in window) {
    var navObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var id = '#' + entry.target.id;
        var link = document.querySelector('.nav-link[href="' + id + '"]');
        if (!link) { return; }
        if (entry.isIntersecting) {
          navLinks.forEach(function (l) { l.classList.remove('active'); });
          link.classList.add('active');
        }
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    navSections.forEach(function (section) { navObserver.observe(section); });
  }

  /* ---------- 맨 위로 이동 버튼 ---------- */
  var backToTop = document.getElementById('back-to-top');
  if (backToTop) {
    window.addEventListener('scroll', function () {
      if (window.scrollY > 480) {
        backToTop.classList.add('visible');
      } else {
        backToTop.classList.remove('visible');
      }
    });
    backToTop.addEventListener('click', function () {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  /* ---------- 상담 신청 폼 제출 (Formspree) ---------- */
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

      fetch(FORMSPREE_ENDPOINT, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        body: JSON.stringify({
          name: name,
          phone: phone,
          email: email,
          service_interest: serviceInterest,
          message: message
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
