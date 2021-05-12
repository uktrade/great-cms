var dit = dit || {};

// Responsive Functionality.
// -------------------------
// Adds functionality to help control JS responsive code.
// Needs corresponding CSS (using media queries) to control
// the values. See getResponsiveValue();
// E.g.

dit.responsive = dit.responsive || (new function () {

  // Constants
  var RESET_EVENT = "dit:responsive:reset";
  var RESPONSIVE_ELEMENT_ID = "dit-responsive-size";

  // Sizing difference must be greater than this to trigger the events.
  // This is and attempt to restrict the number of changes when, for
  // example, resizing the screen by dragging.
  var ARBITRARY_DIFFERENCE_MEASUREMENT = 10;

  // Private
  var _self = this;
  var _rotating = false;
  var _responsiveValues = [];
  var _height = 0;
  var _width = 0;


  /* Detect responsive size in play.
  * Use CSS media queries to control z-index values of the
  * #RESPONSIVE_ELEMENT_ID hidden element. Detected value
  * should match up with index number of _responsiveValues
  * array. dit.responsive.mode() will return a string that
  * should give the current responsive mode.
  * E.g. For _responsiveValues array ["desktop", "table", "mobile"],
  * the expected z-index values would be:
  * desktop = 0
  * tablet = 1
  * mobile = 2
  **/
  function getResponsiveValue() {
    return Number($("#" + RESPONSIVE_ELEMENT_ID).css("z-index"));
  };

  /* Create and append a hidden element to track the responsive
  * size. Note: You need to add CSS to set the z-index property
  * of the element. Do this using media queries so that it fits
  * in with other media query controlled responsive sizing.
  * See _responsiveValues variable for expected values (the
  * array index should match the set z-index value).
  **/
  function addResponsiveTrackingElement() {
    var $responsiveElement = $("<span></span>");
    $responsiveElement.attr("id", RESPONSIVE_ELEMENT_ID);
    $responsiveElement.css({
      "height": "1px",
      "position": "absolute",
      "top": "-1px",
      "visibility": "hidden",
      "width": "1px"
    })

    $(document.body).append($responsiveElement);
  }

  /* Create in-page <style> tag containing set media query
  * breakpoints passed to dit.responsive.init()
  * @queries (Object) Media queries and label - e.g. { desktop: "min-width: 1200px" }
  **/
  function addResponsiveSizes(queries) {
    var $style = $("<style id=\"dit-responsive-css\" type=\"text/css\"></style>");
    var css = "";
    var index = 0;
    for(var query in queries) {
      if(queries.hasOwnProperty(query)) {
        _responsiveValues.push(query);
        css += "@media (" + queries[query] + ") {\n";
        css += " #"  + RESPONSIVE_ELEMENT_ID + "{\n";
        css += "   z-index: " + index + ";\n";
        css += "  }\n";
        css += "}\n\n";
        index++;
      }
    }

    $style.text(css);
    $(document.head).append($style);
  }

  /* Triggers jQuery custom event on body for JS elements
  * listening to resize changes (e.g. screen rotate).
  **/
  function bindResizeEvent() {
    $(window).on("resize", function () {
      if (!_rotating) {
        _rotating = true;
        setTimeout(function () {
          if (_rotating) {
            _rotating = false;
            if(dimensionChangeWasBigEnough()) {
              $(document.body).trigger(RESET_EVENT, [_self.mode()]);
            }
          }
        }, "500");
      }
    });
  }

  /* Calculate if window dimensions have changed enough
  * to trigger a reset event. Note: This was added
  * because some mobile browsers hide the address bar
  * on scroll, which otherwise gives false positive
  * when trying to detect a resize.
  **/
  function dimensionChangeWasBigEnough() {
    var height = $(window).height();
    var width = $(window).width();
    var result = false;

    if (Math.abs(height - _height) >= ARBITRARY_DIFFERENCE_MEASUREMENT) {
      result = true;
    }

    if (Math.abs(width - _width) >= ARBITRARY_DIFFERENCE_MEASUREMENT) {
      result = true;
    }

    // Update internals with latest values
    _height = height;
    _width = width;
    return result;
  }

  /* Return the detected current responsive mode */
  this.mode = function() {
    return _responsiveValues[getResponsiveValue()];
  };

  this.reset = RESET_EVENT;

  this.init = function(breakpoints) {
    addResponsiveSizes(breakpoints);
    addResponsiveTrackingElement();
    bindResizeEvent();
  }
});
