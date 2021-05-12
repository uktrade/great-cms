dit.classes = dit.classes || {};
dit.utils = dit.utils || {};

/* Class: Modal
 * -------------------------
 * Create an area to use as popup/modal/lightbox effect.
 *
 * REQUIRES:
 * jquery
 * dit.js
 * dit.responsive.js
 *
 **/
(function($, utils, classes) {

  var ARIA_EXPANDED = "aria-expanded";
  var CSS_CLASS_CLOSE_BUTTON = "close";
  var CSS_CLASS_CONTAINER = "Modal-Container";
  var CSS_CLASS_CONTENT = "content";
  var CSS_CLASS_OPEN = "open";
  var CSS_CLASS_OVERLAY = "Modal-Overlay";

  /* Constructor
   * @options (Object) Allow some configurations
   **/
  classes.Modal = Modal;
  function Modal($container, options) {
    var modal = this;
    var config = $.extend({
      $activators: $(), // (optional) Element(s) to control the Modal
      closeOnBuild: true, // Whether intial Modal view is open or closed
      overlay: true,  // Whether it has an overlay or not
      closeButtonId: '', // Option to add custom close button id
      onClose: function() {} // (optional) Callback called on modal close
    }, options || {});

    // If no arguments, likely just being inherited
    if (arguments.length) {
      // Create the required elements
      if(config.overlay) {
        this.$overlay = Modal.createOverlay();
      }

      this.$closeButton = Modal.createCloseButton(config.closeButtonId);
      this.$content = Modal.createContent();
      this.$container = Modal.enhanceModalContainer($container);
      this.onClose = config.onClose;

      // Add elements to DOM
      Modal.appendElements.call(this, config.overlay);

      // Add events
      Modal.bindCloseEvents.call(this);
      Modal.bindActivators.call(this, config.$activators);

      // Initial state
      if (config.closeOnBuild) {
        this.close();
      }
      else {
        this.open();
      }
    }
  }

  Modal.createOverlay = function() {
    var $overlay = $(document.createElement("div"));
    $overlay.addClass(CSS_CLASS_OVERLAY);
    return $overlay;
  }

  Modal.createCloseButton = function(closeButtonId) {
    var $button = $(document.createElement("button"));
    $button.text("Close");
    $button.addClass(CSS_CLASS_CLOSE_BUTTON);
    if (closeButtonId) $button.attr('id', closeButtonId);
    return $button;
  }

  Modal.createContent = function() {
    var $content = $(document.createElement("div"));
    $content.addClass(CSS_CLASS_CONTENT);
    return $content;
  }

  Modal.findFirstFocusElement = function($container) {
    return $container.find("video, a, button, input, select").eq(0);
  }

  Modal.findLastFocusElement = function($container) {
    return $container.find("video, a, button, input, select").last();
  }

  Modal.enhanceModalContainer = function($container) {
    $container.addClass(CSS_CLASS_CONTAINER);
    return $container;
  }

  Modal.appendElements = function(overlay) {
    this.$container.append(this.$content);
    this.$container.append(this.$closeButton);

    if (overlay) {
      $(document.body).append(this.$overlay);
    }
    $(document.body).append(this.$container);
  }

  // Handles open actions including whether additioal
  // ability to focus and remember activator if using
  // the keyboard for navigation.
  Modal.activate = function(activator, event) {
    this.activator = activator;
    this.open();
    switch(event.which) {
      case 1: // mouse
        this.shouldReturnFocusToActivator = false;
        break;
      case 13: // Enter
        this.shouldReturnFocusToActivator = true;
        this.focus();
        break;
    }
  }

  // Handles close including whether additional
  // ability to refocus on original activator
  // (e.g. if using keyboard for navigaiton).
  Modal.deactivate = function() {
    if(this.shouldReturnFocusToActivator) {
      this.activator.focus();
    }

    this.close();
    this.activator = null;
  }

  Modal.bindCloseEvents = function() {
    var self = this;

    self.$container.on("keydown", function(e) {
      // Close on Esc
      if(e.which === 27) {
        Modal.deactivate.call(self);
      }
    });

    self.$closeButton.on("click", function(e) {
      // Close on click
      Modal.deactivate.call(self);
      e.preventDefault();
    });

    if (self.$overlay && self.$overlay.length) {
      self.$overlay.on("click", function(e) {
        Modal.deactivate.call(self);
      });
    }
  }

  Modal.bindKeyboardFocusEvents = function() {
    var self = this;
    // Loop around to last element when pressing
    // shift+tab on first focusable element
    self.$firstFocusElement.off("keydown.modalfocus");
    self.$firstFocusElement.on("keydown.modalfocus", function(e) {
      if (e.shiftKey && e.which === 9) {
        e.preventDefault();
        self.$lastFocusElement.focus();
      }
    });
    // Loop around to first element when
    // pressing tab on last element
    self.$lastFocusElement.off("keydown.modalfocus");
    self.$lastFocusElement.on("keydown.modalfocus", function(e) {
      if (!e.shiftKey && e.which === 9) {
        e.preventDefault();
        self.$firstFocusElement.focus();
      }
    });
  }

  Modal.bindActivators = function($activators) {
    var self = this;
    $activators.on("click keydown", function(e) {
      // Click or Enter
      if(e.which === 1 || e.which === 13) {
        Modal.activate.call(self, this, e);
        e.preventDefault();
      }
    });
  }

  Modal.prototype = {};
  Modal.prototype.close = function() {
    var self = this;
    self.$container.fadeOut(50, function () {
      self.$container.attr(ARIA_EXPANDED, false);
      self.$container.removeClass(CSS_CLASS_OPEN);
      $('body').removeClass('modal-open');
      self.onClose();
    });

    if (self.$overlay && self.$overlay.length) {
      self.$overlay.fadeOut(150);
    }

  }

  Modal.prototype.open = function() {
    var self = this;
    var top;
    if (window.pageYOffset) {
      top = window.pageYOffset;
    }
    else {
      top = document.documentElement.scrollTop;
    }

    self.$container.addClass(CSS_CLASS_OPEN);
    $('body').addClass('modal-open');
    self.$container.fadeIn(250, function () {
      self.$container.attr(ARIA_EXPANDED, true);
    });

    if (self.$overlay && self.$overlay.length) {
      self.$overlay.fadeIn(0);
    }
  }

  Modal.prototype.setContent = function(content) {
    var self = this;
    self.$content.empty();
    self.$content.append(content);
    self.$content.append(this.$closeButton);
    self.$firstFocusElement = Modal.findFirstFocusElement(self.$container);
    self.$lastFocusElement = Modal.findLastFocusElement(self.$container);
    Modal.bindKeyboardFocusEvents.call(self);
    //rebind the close button
    Modal.bindCloseEvents.call(self)
  }

  // Tries to add focus to the first found element allowed with natural focus ability.
  Modal.prototype.focus = function() {
    var self = this;
    self.$firstFocusElement.focus();
  }


})(jQuery, dit.utils, dit.classes);
