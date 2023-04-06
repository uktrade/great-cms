var eventFilters = (function () {
  var form,
    filters,
    checks,
    radios,
    stickyFooter,
    body,
    cancel,
    mobileFiltersSelected = []

  function init() {
    setVars()
    bindEvents()
    setFilters()
  }

  function setVars() {
    form = document.querySelector('#events-form')
    filters = document.querySelectorAll('#events-form .filters')[0]
    checks = document.querySelectorAll(
      '.filters li.multiple-choice input[type=checkbox]'
    )
    filterSectionToggles = document.querySelectorAll('.filter-section-toggle')
    radios = document.querySelectorAll(
      '.filters li.multiple-choice input[type=radio]'
    )
    stickyFooter = document.querySelectorAll('.filters-sticky-footer')[0]
    body = document.querySelector('body')
    cancel = document.querySelector('.cancel.link')
  }

  function bindEvents() {
    if (checks) {
      checks.forEach((check) =>
        check.addEventListener('change', () => {
          if (window.innerWidth >= 641) {
            submitForm()
          }
        })
      )
    }

    if (radios) {
      radios.forEach((radio) =>
        radio.addEventListener('change', () => {
          if (window.innerWidth >= 641) {
            submitForm()
          }
        })
      )
    }

    filterSectionToggles.forEach((toggle) =>
      toggle.addEventListener('change', () =>
        window.localStorage.setItem(toggle.id, toggle.checked)
      )
    )

    if (stickyFooter) {
      stickyFooter
        .querySelector('a.update')
        .addEventListener('click', submitForm)
    }

    var mobileFilterToggle = document.querySelector('#mobile-filter-toggle')
    if (mobileFilterToggle) {
      mobileFilterToggle.addEventListener('click', setMobileFilters)
    }

    if (cancel) {
      cancel.addEventListener('click', clearMobileFilters)
    }

    window.addEventListener('resize', resizeHandler)
    window.addEventListener('orientationchange', resizeHandler)
  }

  function setFilters() {
    filterSectionToggles.forEach((filterSectionToggle) => {
      const isOpened = window.localStorage.getItem(filterSectionToggle.id)
      if (isOpened) {
        filterSectionToggle.checked = isOpened.toLowerCase() === 'true'
      }
    })
  }

  function resizeHandler() {
    if (window.innerWidth >= 641) {
      if (body.classList.contains('fixed')) {
        clearMobileFilters()
      }
    }
    if (window.innerWidth <= 640) {
      if (filters.classList.contains('mobile-filters')) {
        filters.style.height = window.innerHeight + 'px'
      }
    }
  }

  function submitForm() {
    form.submit()
  }

  function setMobileFilters() {
    body.classList.add('fixed')
    filters.classList.add('mobile-filters')
    filters.style.height = window.innerHeight + 'px'
    filters.setAttribute('role', 'dialog')
    filters.setAttribute('aria-labelledby', 'filters-heading')
  }

  function clearMobileFilters() {
    for (var i = 0; i < mobileFiltersSelected.length; i = i + 1) {
      document.getElementById(mobileFiltersSelected[i]).checked = false
    }
    body.classList.remove('fixed')
    filters.classList.remove('mobile-filters')
    filters.style.height = ''
    filters.removeAttribute('role')
    filters.removeAttribute('aria-labelledby')
    mobileFiltersSelected = []
  }

  return {
    init: init,
  }
})()
