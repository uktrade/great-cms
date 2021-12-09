var dit = dit || {};
dit.components = dit.components || {};

dit.components.cookieNotice = function() {
  var COOKIE_NOTICE_ID = 'header-cookie-notice';
  var COOKIE_CLOSE_BUTTON_ID = 'dismiss-cookie-notice';
  var COOKIE_DOMAIN = $('#privacyCookieDomain').attr('value');
  var cookiePreferencesName = 'cookie_preferences_set';
  var cookiePreferencesDurationDays = 365;
  var cookiesPolicyName = 'cookies_policy';
  var cookiesPolicyDurationDays = 365;
  var bannerClassName = '.cookie-notice';
  var acceptButtonClassName = '.button-accept';

  function setCookie (name, value, options) {
    if (typeof options === 'undefined') {
      options = {};
    }
    var cookieString = name + '=' + value + '; domain=' + COOKIE_DOMAIN + ';path=/;';
    if (options.days) {
      var date = new Date();
      date.setTime(date.getTime() + options.days * 24 * 60 * 60 * 1000);
      cookieString = cookieString + '; expires=' + date.toGMTString();
    }
    if (document.location.protocol === 'https:') {
      cookieString = cookieString + '; Secure';
    }
    document.cookie = cookieString;
  }

  function getCookie (name) {
    var nameEQ = name + '=';
    var cookies = document.cookie.split(';');
    for (var i = 0, len = cookies.length; i < len; i++) {
      var cookie = cookies[i];
      while (cookie.charAt(0) === ' ') {
        cookie = cookie.substring(1, cookie.length);
      }
      if (cookie.indexOf(nameEQ) === 0) {
        return decodeURIComponent(cookie.substring(nameEQ.length));
      }
    }
    return null;
  }

  function getDefaultPolicy () {
    return {
      essential: true,
      settings: false,
      usage: false,
      campaigns: false
    };
  }

  function getPolicyOrDefault () {
    var cookie = getCookie(cookiesPolicyName);
    var policy = getDefaultPolicy();
    if (!cookie) return policy;

    try {
      var parsed = JSON.parse(cookie);

      policy.campaigns = parsed.campaigns || false;
      policy.usage = parsed.usage || false;
      policy.settings = parsed.settings || false;

    } catch (e) {
      return policy;
    }

    return policy;

  }

  function createPoliciesCookie (settings, usage, campaigns) {
    var policy = getDefaultPolicy();
    policy.settings = settings || false;
    policy.usage = usage || false;
    policy.campaigns = campaigns || false;
    var json = JSON.stringify(policy);
    setCookie(cookiesPolicyName, json, { days: cookiesPolicyDurationDays });
    return policy;
  }

  function hideCookieBanner (className) {
    var banner = document.querySelectorAll(className)[0];
    banner.classList.remove('block', 'confirmation-message');
  }

  function displayCookieBannerAcceptAll () {
    var banner = document.querySelectorAll(bannerClassName)[0];
    banner.classList.add('confirmation-message');

    var hideButton = document.querySelectorAll('.cookie-close')[0];

    hideButton.addEventListener('click', function (e) {
      e.preventDefault();
      hideCookieBanner(bannerClassName);
      }, false);

    hideButton.addEventListener('keydown', function(e) {
      if(e.which === 13 || e.which === 32) {
        hideCookieBanner(bannerClassName);
      }
    });
  }

  function displayCookieBanner () {
    var banner = document.querySelectorAll(bannerClassName)[0];
    banner.classList.add('block');
  }

  function bindAcceptAllCookiesButton (callBack) {
    var button = document.querySelectorAll(acceptButtonClassName)[0];
    button.addEventListener('click', callBack, false);
  }

  function setPreferencesCookie () {
    setCookie(cookiePreferencesName, 'true', { days: cookiePreferencesDurationDays });
  }

  function getPreferencesCookie () {
    return getCookie(cookiePreferencesName);
  }

  function enableCookieBanner () {
    displayCookieBanner();
    bindAcceptAllCookiesButton(function(event) {
      acceptAllCookie(event);
      displayCookieBannerAcceptAll();
    })
  }

  function createCloseButton () {
    var $container = $('.cookie-notice-container');
    var $closeButton = $('<button>', {
      'class': 'cookie-close',
      'aria-controls': COOKIE_NOTICE_ID,
      'aria-label': 'Close this message',
      id: COOKIE_CLOSE_BUTTON_ID
    });
    $container.prepend($closeButton);
    return $closeButton;
  }

  function acceptAllCookies(event) {
    event.preventDefault();
    createPoliciesCookie(true, true, true);
    setPreferencesCookie();
    return false;
  }

  function acceptAllCookiesAndShowSuccess(event) {
    acceptAllCookies(event)
    createCloseButton()
    displayCookieBannerAcceptAll()
    displayCookieBanner()
  }

  function init (cookiesPolicyUrl) {
    var preferenceCookie = getPreferencesCookie();
    var isCookiesPage = document.URL.indexOf(cookiesPolicyUrl) !== -1;

    if ((!preferenceCookie) && !isCookiesPage) {
      enableCookieBanner();
      createCloseButton();
    }
  }

  return {
    init: init,
    getPolicyOrDefault: getPolicyOrDefault,
    createPoliciesCookie: createPoliciesCookie,
    setPreferencesCookie: setPreferencesCookie,
    acceptAllCookiesAndShowSuccess: acceptAllCookiesAndShowSuccess,
    getPreferencesCookie: getPreferencesCookie
  };
}();

if (typeof exports !== 'undefined') {
  if (typeof module !== 'undefined' && module.exports) {
    exports = module.exports = dit.components.cookieNotice
  }
}
