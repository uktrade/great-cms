// Language Selector Component Functionality.
//
// Requires...
// dit.js
// dit.utils.js
// dit.class.modal.js

// Usage
// --------------------------------------------------------------------
// To find all Language Selector components and enhance using
// the default settings.
//
// dit.components.languageSelector.init()
//
// For greater control, use either of the individual enhance functions
// for Language Selector Control or Language Selector Dialog components.
// This also allow passing options to customise the output.
//
// dit.components.languageSelector.enhanceControl()
// dit.components.languageSelector.enhanceDialog()
//
dit.components.languageSelector = (new function() {

  var SelectTracker = dit.classes.SelectTracker;
  var LANG_SELECT_CLOSE_BUTTON_ID = "header-language-selector-close";

  /* Extends SelectTracker to meet additional display requirement
   * @$select (jQuery node) Target input element
   * @options (Object) Configurable options
   **/
  function LanguageSelectorControl($select, options) {
    SelectTracker.call(this, $select);
    if(this.$node) {
      this.$node.addClass("SelectTraker-Tracker");
      $select.parents("form").addClass("enhancedLanguageSelector");
      $select.on("change", function() {
        this.form.submit();
      })
    }
  }
  LanguageSelectorControl.prototype = new SelectTracker;
  LanguageSelectorControl.prototype.update = function() {
    var $code = $(document.createElement("span"));
    var $lang = $(document.createElement("span"));
    SelectTracker.prototype.update.call(this);
    $lang.addClass("lang");
    $code.addClass("code");
    $lang.text(this.$node.text());
    $code.text(this.$select.val());
    this.$node.empty();
    this.$node.append($code);
    this.$node.append($lang);
  }

  /* Contructor
   * Displays control and dialog enhancement for language-selector-dialog element.
   * @$dialog (jQuery node) Element displaying list of selective links
   * @options (Object) Configurable options
   **/
  function LanguageSelectorDialog($dialog, options) {
    var LANGUAGE_SELECTOR_DISPLAY = this;
    var id = dit.utils.generateUniqueStr("LanguageSelectorDialog_");
    var $control = LanguageSelectorDialog.createControl($dialog, id);
    dit.classes.Modal.call(LANGUAGE_SELECTOR_DISPLAY, $dialog, {
      $activators: $control,
      closeButtonId: LANG_SELECT_CLOSE_BUTTON_ID
    });
    this.config = $.extend({
      $controlContainer: $dialog.parent() // Where to append the generated control
    }, options);


    if(arguments.length > 0 && $dialog.length) {
      this.$container.attr("id", id);
      this.$container.addClass("LanguageSelectorDialog-Modal");
      this.config.$controlContainer.append($control);
      this.setContent($dialog.children());
    }
  }

  LanguageSelectorDialog.createControl = function($node, id) {
    var $controlContainer = $(document.createElement("li"));
    var $control = $(document.createElement("a"));
    var $lang = $(document.createElement("span"));
    var $country = $(document.createElement("span"));
    $lang.addClass("lang");
    $lang.text($node.attr("data-lang"));
    $country.addClass("label");
    $country.text($node.attr("data-label"));
    $control.append($lang);
    $control.append($country);
    $control.addClass("LanguageSelectorDialog-Tracker bidi-ltr");
    $control.attr("href", ("#" + id));
    $control.attr("aria-controls", id);
    $controlContainer.append($control);
    return $controlContainer;
  }

  LanguageSelectorDialog.prototype = new dit.classes.Modal


  // Just finds all available Language Selector components
  // and enhances using the any default settings.
  this.init = function() {
    $("[data-component='language-selector-control'] select").each(function() {
      new LanguageSelectorControl($(this));
    });

    $("[data-component='language-selector-dialog']").each(function() {
      new LanguageSelectorDialog($(this));
    });
  }

  // Selective enhancement for individual Language Selector Control views
  // Allows passing of custom options.
  // @$control (jQuery object) Something like this: $("[data-component='language-selector-control'] select")
  // @options (Object) Configurable options for class used.
  this.enhanceControl = function($control, options) {
    if ($control.length) {
      new LanguageSelectorControl($control, options);
    }
    else {
      console.error("Language Selector Control missing or not passed")
    }
  }

  // Selective enhancement for individual Language Selector Dialog views
  // Allows passing of custom options.
  // @$control (jQuery object) Something like this: $("[data-component='language-selector-dialog']")
  // @options (Object) Configurable options for class used.
  this.enhanceDialog = function($dialog , options) {
    if ($dialog.length) {
      new LanguageSelectorDialog($dialog, options);
    }
    else {
      console.error("Language Selector Dialog missing or not passed");
    }
  }

});
