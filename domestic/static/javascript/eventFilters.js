var eventFilters = function() {

    var form, filters, checks, radios, stickyFooter, body,
        mobileFiltersSelected = [];

    function init() {
      setVars();
      bindEvents();
    }

    function setVars() {
      form = document.querySelector('#events-form');
      filters = document.querySelectorAll('#events-form .filters')[0];
      checks = document.querySelectorAll('.filters li.multiple-choice input[type=checkbox]');
      radios = document.querySelectorAll('.filters li.multiple-choice input[type=radio]')
      stickyFooter = document.querySelectorAll('.filters-sticky-footer')[0];
      body = document.querySelector('body');
    }

    function bindEvents() {
      if (checks) {
        checks.forEach(check => check.addEventListener('change', submitForm))
      }

      if (radios) {
        radios.forEach(radio => radio.addEventListener('change', submitForm))
      }

      if (stickyFooter) {
        stickyFooter.querySelector('a.update').addEventListener('click', submitForm);
      }

      var mobileFilterToggle = document.querySelector('#mobile-filter-toggle');
      if (mobileFilterToggle) {
        mobileFilterToggle.addEventListener('click', setMobileFilters);
      }

      window.addEventListener("resize", resizeHandler);
      window.addEventListener("orientationchange", resizeHandler);
    }

    function resizeHandler() {
      if(window.innerWidth >= 641) {
        if(body.classList.contains('fixed')) {
          clearMobileFilters();
        }
      }
      if(window.innerWidth <= 640) {
        if(filters.classList.contains('mobile-filters')) {
          filters.style.height = window.innerHeight + 'px';
        }
      }
    }

    function submitForm() {
      form.submit();
    }

    function setMobileFilters() {
      body.classList.add('fixed');
      filters.classList.add('mobile-filters');
      filters.style.height = window.innerHeight + 'px';
      filters.setAttribute('role', 'dialog');
      filters.setAttribute('aria-labelledby', 'filters-heading');
    }

    function clearMobileFilters() {
      for(var i = 0; i < mobileFiltersSelected.length; i = i + 1) {
        document.getElementById(mobileFiltersSelected[i]).checked = false;
      }
      body.classList.remove('fixed');
      filters.classList.remove('mobile-filters');
      filters.style.height = '';
      filters.removeAttribute('role');
      filters.removeAttribute('aria-labelledby');
      mobileFiltersSelected = [];
    }

    return {
    init: init
  };

  }();
