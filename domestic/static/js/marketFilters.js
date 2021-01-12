var marketFilters = function() {

    var form, filters, checks, sortby, cards, stickyFooter, body,
        mobileFiltersSelected = [];

    function init() {
      setVars();
      bindEvents();
      getImages();
    }

    function setVars() {
      form = document.querySelector('#sectors-form');
      filters = document.querySelectorAll('#sectors-form .filters')[0];
      checks = document.querySelectorAll('.filters li.multiple-choice input[type=checkbox]');
      sortby = document.querySelector('#sortby');
      cards = document.querySelectorAll('.markets-grid .card');
      stickyFooter = document.querySelectorAll('.filters-sticky-footer')[0];
      body = document.querySelector('body');
    }

    function bindEvents() {
      for (var i=0; i< checks.length; i=i+1) {
          checks[i].addEventListener('change', submitForm);
      }

      if(sortby) {
        sortby.addEventListener("change", submitForm);
      }
      stickyFooter.querySelector('a.cancel').addEventListener('click', clearMobileFilters);
      stickyFooter.querySelector('a.update').addEventListener('click', submitForm);
      document.querySelector('#mobile-filter-toggle').addEventListener('click', setMobileFilters);
      window.addEventListener("resize", resizeHandler);
      window.addEventListener("orientationchange", resizeHandler);
    }

    function resizeHandler() {
      if(window.innerWidth >= 641) {
        getImages();
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

    function submitForm(e) {
      if((e.target.name === 'sector' || e.target.name === 'region') && window.innerWidth <= 640){
          /* triggered by checkboxes in mobile filters view -
          below creates a temporay array of filters selected, which need to be unchecked if user cancels the overlay
          */
          if(e.target.checked) {
            mobileFiltersSelected.push(e.target.id);
          } else {
            mobileFiltersSelected.splice(mobileFiltersSelected.indexOf(e.target.id), 1);
          }
      } else {
        form.submit();
      }

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

    function getImages() {
      if(window.innerWidth >= 641) {
        $(cards).each(function(int, card) {
          var $marketImg = $(card).find('img.card-image');
          if($marketImg.attr('src')) {
            return;
          } else {
            $marketImg.attr('src', $marketImg.data('src'));
          }
        });
      }
    }

    return {
    init: init
  };

  }();
