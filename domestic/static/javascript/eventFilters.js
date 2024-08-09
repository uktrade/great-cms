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
    scrollToTopOfResults()
  }

  function setVars() {
    form = document.querySelector('#events-form')
    filters = document.querySelectorAll('#events-form .filters')[0]
    checks = document.querySelectorAll(
      '.filters li.multiple-choice input[type=button]'
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
    const filterSectionHeadings = document.querySelectorAll('.filter-section-headings');
    const hasFilterSectionHeadings = filterSectionHeadings.length >= 1;

    if (hasFilterSectionHeadings){
      filterSectionHeadings.forEach(function(el) {
      // This code was added as part of GREATUK-2 and is technical debt in it's purest form. It addresses an accessibility
      // audit, changing the accordian menu on the filters to a type=button rather than type=checkbox. The JS below has
      // been added compliance failure by to replace previous CSS styling which handled the accordian visibility toggle.

        // Graceful degradation for browsers without JS enabled and also persist opened filter sections across reloads.
        if (window.localStorage.getItem(el.id) != 'true') {
          el.classList.remove("arrows-left-active");
          el.nextElementSibling.classList.remove('filter-section-active');
          el.previousElementSibling.ariaExpanded = false;
        }

        // Set accordian toggles
        el.addEventListener('click', function(e) {
          // UI
          el.classList.toggle('arrows-left-active');
          el.nextElementSibling.classList.toggle('filter-section-active');
          // Persistence across sessions
          let state = el.previousElementSibling.ariaExpanded !== 'true';
          el.previousElementSibling.ariaExpanded = state;
          window.localStorage.setItem(el.id, state);
        })
      });
    }

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

  function scrollToTopOfResults() {
    // Scroll so that results are at the top of the screen
    // when filters are changed
    const url = new URL(window.location.href)
    const filtersChanged = document.referrer.includes('/events/')
    if (url.search.length && filtersChanged) {
      const breadcrumbs = document.getElementById('breadcrumbs')
      breadcrumbs.scrollIntoView(true)
    }
  }

  return {
    init: init,
  }
})()
