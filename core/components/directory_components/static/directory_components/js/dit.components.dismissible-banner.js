var dit = dit || {};
dit.components = dit.components || {};

dit.components.dismissableBanner = (new function() {

  var BANNER_ID = 'information-banner';
  var BANNER_CLOSE_BUTTON_ID = 'dismiss-banner';

  this.hideBanner = function() {
    $('#information-banner').hide();
  }

  this.createBannerCloseButton = function() {
    var $container = $('#information-banner .banner-content');
    var $buttonContainer = $('<div></div>');
    var $closeButton = $('<a>', {
      'text': 'Close',
      'href': '#',
      'class': 'banner-close-button link',
      'aria-controls': BANNER_ID,
      id: BANNER_CLOSE_BUTTON_ID
    });
    $buttonContainer.append($closeButton);
    $container.append($buttonContainer);
    return $closeButton;
  }

  this.bannerCloseButtonEventHandler = function() {
    var $button = this.createBannerCloseButton();

    $button.on('keydown', function(e) {
      // Close on enter or space
      if(e.which === 13 || e.which === 32) {
        this.hideBanner();
      }
    });

    $button.on('click', function(e) {
      this.hideBanner();
      e.preventDefault();
    });
  }

  this.init = function() {
    this.bannerCloseButtonEventHandler();
  }

});

$(document).ready(function() {
  dit.components.dismissableBanner.init();
});
