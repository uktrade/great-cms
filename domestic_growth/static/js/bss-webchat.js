;(function () {
  const bss_webchat_text = document.querySelector('[data-bss-webchat]')

  const load_bss_webchat = () => {
    ;(function (n, u) {
      ;(window.CXoneDfo = n),
        (window[n] =
          window[n] ||
          function () {
            ;(window[n].q = window[n].q || []).push(arguments)
          }),
        (window[n].u = u),
        (e = document.createElement('script')),
        (e.type = 'module'),
        (e.src = u + '?' + Math.round(Date.now() / 1e3 / 3600)),
        document.head.appendChild(e)
    })(
      'cxone',
      'https://web-modules-de-uk1.niceincontact.com/loader/1/loader.js'
    )

    cxone('init', '1342')
    cxone('guide', 'init', '8b9d74c6-3467-4cc0-b7fe-44ff5331f9ec')
  }

  const show_bss_webchat = () => {
    const now = new Date()
    const day = now.getDay()
    const hour = now.getHours()

    const is_weekday = day >= 1 && day <= 5
    const is_within_service_hours = hour >= 9 && hour < 18

    if (is_weekday && is_within_service_hours) {
      return true
    }

    return false
  }

  if (bss_webchat_text && show_bss_webchat()) {
    bss_webchat_text.innerText = 'Use the Business Support Service chat button'
    load_bss_webchat()

    setTimeout(() => {
      const bss_webchat_container = document.querySelector(
        '[data-bss-webchat-container]'
      )
      const bss_webchat = document.getElementById('cxone-guide-container')

      if (bss_webchat_container && bss_webchat) {
        bss_webchat_container.append(bss_webchat)
      }
    }, 5000)
  }

  if (bss_webchat_text && !show_bss_webchat()) {
    bss_webchat_text.innerText = 'Unavailable - out of hours'
  }
})()
