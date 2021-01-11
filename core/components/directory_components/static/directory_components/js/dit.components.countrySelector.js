var dit = dit || {};
dit.components = dit.components || {};

dit.components.countrySelector = (new function() {
  var self = this;

  var BANNER = '#country-selector-dialog';
  var BANNER_ID = 'country-selector-dialog';
  var BANNER_CLOSE_BUTTON_ID = 'close-country-selector-dialog';
  var BANNER_ACTIVATOR = '#country-selector-activator';
  var BANNER_ACTIVATOR_ID = 'country-selector-activator';
  var COUNTRY_SELECT = '#great-header-country-select';
  var COUNTRY_SUBMIT = '#great-header-country-submit';
  var COUNTRY_SUBMIT_ID = 'great-header-country-submit';
  var COUNTRY_DISPLAY = '#great-header-country-display';
  var FLAG = '#great-header-flag-icon';

  self.createBannerCloseButton = function() {
    var $container = $(BANNER + ' .countries');
    var $button = $('<button></button>', {
      'text': 'Close',
      'class': 'close-button',
      'aria-controls': BANNER_ID,
      id: BANNER_CLOSE_BUTTON_ID
    });
    $container.append($button);
    return $button;
  }

  self.bannerCloseButtonEventHandler = function() {
    var $button = self.createBannerCloseButton();

    $button.on('keydown', function(e) {
      // Close on enter, space or esc
      if(e.which === 13 || e.which === 32 || e.which == 27) {
        e.preventDefault();
        self.closeBanner();
      }
    });

    $button.on('click', function(e) {
      e.preventDefault();
      self.closeBanner();
    });
  }

  self.createBannerOpenButton = function() {
    var $element = $('#country-text');
    var $button = $('<button></button>', {
      'text': $element.text(),
      'aria-controls': BANNER_ID,
      'class': 'country-selector-activator',
      id: BANNER_ACTIVATOR_ID
    });
    $element.replaceWith($button);
    return $button;
  }

  self.bannerOpenButtonEventHandler = function() {
    var $button = self.createBannerOpenButton();

    $button.on('keydown', function(e) {
      // Close on enter or space
      if(e.which === 13 || e.which === 32) {
        e.preventDefault();
        self.openBanner();
      }
    });

    $button.on('click', function(e) {
      e.preventDefault();
      $(BANNER).show();
    });
  }

  self.closeBanner = function() {
    $(BANNER).hide();
    $(BANNER_ACTIVATOR).focus();
  }

  self.openBanner = function() {
    $(BANNER).show();
    $(COUNTRY_SELECT).focus();
  }

  self.bannerContentsEventHandler = function() {
    var $items = $(BANNER).find('form').find('select, a, button, input');

    $items.each(function() {
      $(this).on('keydown', function(e) {
        if (e.which === 27) { // esc
          self.closeBanner();
        }
      })
    })
  }

  self.bannerSelectEventHandler = function() {
    $(COUNTRY_SELECT).on('change', function() {
      var country = '';

      $(COUNTRY_SELECT).find("option:selected").each(function() {
        country = $(this).attr('value');
      });
      $(FLAG).attr('class', 'flag-icon flag-icon-' + country.toLowerCase())
    });
  }

  self.headerSelectEventHandler = function() {
    var $select = $(COUNTRY_SELECT);
    // setup initial width
    var country = $select.find("option:selected").text();
    var $display = $(COUNTRY_DISPLAY);
    var code = $select.find("option:selected").attr('value');

    $(COUNTRY_SUBMIT).hide();

    $display.text(country);
    $select.css('width', $display.outerWidth());

    $select.on('change', function() {

      $select.find("option:selected").each(function() {
        code = $(this).attr('value');
        country = $(this).text();
        $display.text(country);
        $select.css('width', $display.outerWidth());
      });

      $(FLAG).attr('class', 'flag-icon flag-icon-' + code.toLowerCase());

      this.form.submit();

    });
  }

  self.init = function() {
    // only run this if the banner exists in the DOM
    if ($(BANNER).length) {
      self.bannerCloseButtonEventHandler();
      self.bannerOpenButtonEventHandler();
      self.bannerContentsEventHandler();
      self.bannerSelectEventHandler();
    // otherwise setup header dropdown
    } else {
      self.headerSelectEventHandler();
    }
  }

  self.viewInhibitor = function(activate) {
    var rule = '#' + COUNTRY_SUBMIT_ID + ' { display: none; }';
    var style;
    if (arguments.length && activate) {
      style = document.createElement('style');
      style.setAttribute('type', 'text/css');
      style.setAttribute('id', COUNTRY_SUBMIT_ID);
      style.appendChild(document.createTextNode(rule));
      document.head.appendChild(style);
    }
    else {
      document.head.removeChild(document.getElementById(COUNTRY_SUBMIT_ID));
    }
  };

  // Hide on load
  self.viewInhibitor(true);

});
