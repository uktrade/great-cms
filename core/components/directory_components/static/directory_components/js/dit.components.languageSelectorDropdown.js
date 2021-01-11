var dit = dit || {};
dit.components = dit.components || {};
dit.utils = dit.utils || {};

dit.components.languageSelectorDropdown = (new function() {
  var self = this;

  var LANGUAGE_SELECT = '#great-header-language-select';
  var LANGUAGE_SUBMIT = '#great-header-language-submit';
  var LANGUAGE_DISPLAY = '#great-header-language-display';

  self.init = function() {
    var $select = $(LANGUAGE_SELECT);
    var currentLanguageCode = $select.find('option:selected').attr('value');
    var currentLanguageName = $select.find('option:selected').text();
    var $display = $(LANGUAGE_DISPLAY);

    $display.text(currentLanguageName);
    $select.css('width', $display.outerWidth());

    $select.on("change", function() {

      $select.find("option:selected").each(function() {
        currentLanguageName = $(this).text();
        currentLanguageCode = $(this).attr('value');
        $display.text(currentLanguageName);
        $select.css('width', $display.outerWidth());
      });

      this.form.submit();

    });
  }

  self.viewInhibitor = function(activate) {
    var rule = LANGUAGE_SUBMIT + ' { display: none; }';
    var style;
    if (arguments.length && activate) {
      style = document.createElement('style');
      style.setAttribute('type', 'text/css');
      style.setAttribute('id', LANGUAGE_SUBMIT);
      style.appendChild(document.createTextNode(rule));
      document.head.appendChild(style);
    }
    else {
      document.head.removeChild(document.getElementById(LANGUAGE_SUBMIT));
    }
  };

  // Hide on load
  self.viewInhibitor(true);

});
