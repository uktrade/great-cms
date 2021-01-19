// Main dit.js file
// Expected to hold global variables, messages, and provide base to namespaces

var dit = {
  // Namespace to be populated by external files
  classes: {},
  components: {},
  data: {},
  pages: {},
  tagging: {},

  constants: {
    COMPANIES_HOUSE_SEARCH: "/static/temp/companies-house-data.json"
  }
};


// Utility Functions.
// ---------------------

// REQUIRES
// jQuery
// dit.js

dit.utils = (new function () {

  /* Attempt to generate a unique string
  * e.g. For HTML ID attribute.
  * @str = (String) Allow prefix string.
  **/
  this.generateUniqueStr = function (str) {
    return (str ? str : "") + ((new Date().getTime()) + "_" + Math.random().toString()).replace(/[^\w]*/mig, "");
  };

  /* Return max height measurement of passed elements
  * @$items (jQuery collection) elements to compare.
  **/
  this.maxHeight = function ($items, outer) {
    var max = 0;
    $items.each(function () {
      var $this = $(this);
      var height = outer ? $this.outerHeight(true) : $this.height();
      max = height > max ? height : max;
    });
    return max;
  }

  /* Align heights of elements in row where
  * CSS fails or using this is easier.
  * $items = (String) jQuery selector to target elements.
  **/
  this.alignHeights = function ($items) {
    var collection = $();
    var max = 0;
    var lasttop;

    function align(items) {
      var max = dit.utils.maxHeight(items);
      items.height(max + "px");
    }

    $items.each(function () {
      var $this = $(this);
      var newtop = $this.position().top;
      if (newtop !== lasttop) {
        // Find max height
        align(collection);
        collection = $();
      }

      lasttop = newtop;
      collection = collection.add($this);
    });

    // Catch the last collection
    // (or first/only if they're all the same)
    align(collection);
  }


  /* Basically the reset to alignHeights because
  * it clears the inline height setting.
  * $items = (String) jQuery selector to target elements.
  **/
  this.clearHeights = function ($items) {
    $items.each(function () {
      this.style.height = "";
    });
  }

});


// Scroll Related Functions.
// Requires main dit.js file

dit.scroll = (new function () {
  this.scrollPosition = 0;

  this.disable = function () {
    this.scrollPosition = window.scrollY,
    $(document.body).css({
      overflow: "hidden"
    });

    $(document).trigger("scrollingdisabled");
  }

  this.enable = function () {
    $(document.body).css({
      overflow: "auto"
    });

    window.scrollTo(0, this.scrollPosition);
    $(document).trigger("scrollingenabled");
  }
});
/* Class: Expander
* ----------------
* Expand and collapse a target element by another specified, controlling element,
* or through an automatically added default controller.
*
* Note: The COLLAPSED class is added when the Expander element is closed, so
* you can control CSS the open/close state, or other desired styling.
*
* REQUIRES:
* jquery
* dit.js
* dit.utils.js
*
**/
(function($, utils, classes) {
  var TYPE = "Expander";
  var COLLAPSED = "collapsed";
  var ACTIVE = "active";
  var OPEN = "open";
  var CLOSE = "close";
  var CLICK = "click." + TYPE;
  var BLUR = "blur." + TYPE;
  var FOCUS = "focus." + TYPE;
  var KEY = "keydown." + TYPE;
  var ONMOUSEOUT = "mouseout." + TYPE;
  var ONMOUSEOVER = "mouseover." + TYPE;

  /* Main Class
  * @$target (jQuery node) Target element that should open/close
  * @options (Object) Configuration switches.
  **/
  classes.Expander = Expander;
  function Expander($target, options) {
    var EXPANDER = this;
    var id = utils.generateUniqueStr(TYPE + "_");
    var $wrapper, $control;

    this.config = $.extend({
      blur: true, // If enabled closes on blur.
      cleanup: function() {
        // Additional tasks that may be performed on destroy.
      },
      closed: true, // Whether the item has initial closed state.
      cls: "", // config.wrap ? put on wrapper : put on target.
      complete: function() {
        // You can pass a function to run on open+close
      },
      focus: false, // If enabled puts focus back on activating element target is closed.
      hover: false, // If enabled opens/closes on hover as well.
      text: "Expand", // Control button text.
      wrap: false,
      $control: null // Pass a node if you want to specify something.
    }, options);

    if (arguments.length && $target.length) {

      $control = this.config.$control || $(document.createElement("a"));
      if ($control.get(0).tagName.toLowerCase() === "a") {
        $control.attr("href", "#" + id);
      }

      // Figure out and setup the expanding element
      if(this.config.wrap) {
        $wrapper = $(document.createElement("div"));
        $control.after($wrapper);
        $wrapper.append($target);
        this.$node = $wrapper;
      }
      else {
        id = $target.attr("id") || id; // In case the existing element has its own
        this.$node = $target;
      }

      this.links = {
        $found: $("a", this.$node) || $(),
        counter: -1
      }

      // If we detected any links, enable arrow movement through them.
      this.links.$found.on(KEY, function(e) {
        if (e.which !== 9 && e.which !== 13) {
          e.preventDefault();
        }
        Expander.move.call(EXPANDER, e);
      }).on(BLUR, function(){
        Expander.blur.call(EXPANDER);
      }).on(FOCUS, function() {
        Expander.focus.call(EXPANDER);
      });

      this.$node.before($control);
      this.$node.addClass(TYPE);
      this.$node.addClass(this.config.cls);
      this.$node.attr("id", id);

      // Finish setting up control
      this.$control = $control;
      $control.addClass(TYPE + "Control");
      $control.attr("aria-controls", id);
      $control.attr("aria-expanded", "false");
      $control.attr("aria-haspopup", "true");
      $control.attr("tabindex", 0);
      if($control.text() === "") {
        $control.html(this.config.text)
      }

      // Set initial state
      if (this.config.closed) {
        this.state = OPEN;
        this.close();
      }
      else {
        this.state = CLOSE;
        this.open();
      }

      // Bind events for user interaction
      Expander.bindEvents.call(this);
    }
  }

  /* Class utility function to bind required
  * events upon instantiation. Needs to be run
  * with context of the instantiated object.
  **/
  Expander.bindEvents = function() {
    var EXPANDER = this;

    Expander.AddKeyboardSupport.call(EXPANDER);

    if (EXPANDER.config.hover) {
      Expander.AddHoverSupport.call(EXPANDER);
    }
    else {
      Expander.AddClickSupport.call(EXPANDER);
    }
  }

  /* Add ability to control by keyboard
  **/
  Expander.AddKeyboardSupport = function() {
    var EXPANDER = this;

    EXPANDER.$control.on(KEY, function(e) {
      // keypress charCode=0, keyCode=13 = enter
      if (e.which !== 9 && e.which !== 13) {
        e.preventDefault();
      }
      Expander.focus.call(EXPANDER);

      switch(e.which) {
        case 37: // Fall through.
        case 27:
        EXPANDER.close();
        break;
        case 39:
          if(EXPANDER.state === OPEN) {
            // Move though any detected links.
            Expander.move.call(EXPANDER, e);
          }
        else {
          EXPANDER.open();
        }
        break;
        case 32:
          EXPANDER.toggle();
        default: ; // Nothing yet.
      }
    });
  }

  /* Add Hover events (for desktop only)
  **/
  Expander.AddHoverSupport = function() {
    var EXPANDER = this;
    var $node = EXPANDER.$node;

    EXPANDER.$control.add($node).on(ONMOUSEOVER, function(event) {
      event.preventDefault();
      Expander.on.call(EXPANDER);
      EXPANDER.open();
    });

    EXPANDER.$control.add($node).on(ONMOUSEOUT, function() {
      Expander.off.call(EXPANDER);
    });

    EXPANDER.$control.on(CLICK, function(event) {
      event.preventDefault();
    });
  }

  /* Using click for desktop and mobile.
  **/
  Expander.AddClickSupport = function() {
    var EXPANDER = this;

    EXPANDER.$control.on(CLICK, function(event) {
      event.preventDefault();
      Expander.on.call(EXPANDER);
      EXPANDER.toggle();
    });

    // And now what happens on blur.
    if(EXPANDER.config.blur) {
      EXPANDER.$control.on(BLUR, function() {
        Expander.blur.call(EXPANDER);
      });
    }
  }

  Expander.on = function() {
    clearTimeout(this.closerequest);
  }

  Expander.off = function() {
    var self = this;
    this.closerequest = setTimeout(function() {
      self.close(true);
    }, 0.5);
  }

  Expander.focus = function() {
    Expander.on.call(this);
  }

  Expander.blur = function() {
    if(this.config.blur && this.state != CLOSE) {
      Expander.off.call(this);
    }
  }

  Expander.move = function(e) {
    var counter = this.links.counter;
    var $links = this.links.$found;
    if($links) {
      switch(e.which) {
        case 37: // Fallthrough
        case 27: this.close();
        break;
        case 40:
        // Down.
        if(counter < ($links.length - 1)) {
          $links.eq(++counter).focus();
        }
        break;
        case 39:
        $links.eq(0).focus();
        break;
        case 38:
        // Up.
        if(counter > 0) {
          $links.eq(--counter).focus();
        }
        else {
          counter--;
          this.close();
        }
        break;
        default: ; // Nothing yet.
      }
    }
    this.links.counter = counter;
  }

  Expander.prototype = new Object;
  Expander.prototype.toggle = function() {
    if(this.state != OPEN) {
      this.open();
    }
    else {
      this.close();
    }
  }

  Expander.prototype.open = function() {
    if(!this._locked && this.state != OPEN) {
      this._locked = true;
      this.state = OPEN;
      this.$control.addClass(ACTIVE);
      this.$node["removeClass"](COLLAPSED);
      this.$control.attr("aria-expanded", "true");
      this.links.$found.attr("tabindex", 0);
      this.config.complete.call(this);
      this._locked = false;
    }
  }

  Expander.prototype.close = function() {
    var focus = this.config.focus;
    if(!this._locked && this.state != CLOSE) {
      this._locked = true;
      this.state = CLOSE;
      this.$control.removeClass(ACTIVE);
      this.$node["addClass"](COLLAPSED);
      this.config.complete.call(this);
      this.$control.attr("aria-expanded", "false");
      this.links.$found.attr("tabindex", -1);
      if(focus) {
        this.$control.focus();
      }
      this.links.counter = -1; // Reset.
      this._locked = false;
    }
  }

  Expander.prototype.destroy = function() {
    var events = CLICK + " " + BLUR + " " + FOCUS + " " + KEY + " " + ONMOUSEOUT + " " + ONMOUSEOVER;
    if(this.config.wrap) {
      this.$node.replaceWith(this.$node.contents());
    }
    else {
      this.$node.removeClass(this.config.cls);
      this.$node.removeClass(COLLAPSED);
      this.$node.removeClass(TYPE);
    }

    if(this.config.$control) {
      this.$control.off(events);
      this.$control.removeClass(this.config.cls + "Control");
      this.$control.removeAttr("tabindex");
      this.$control.removeAttr("aria-controls");
      this.$control.removeAttr("aria-expanded");
      this.$control.removeAttr("aria-haspopup");
    }
    else {
      this.$control.remove();
    }

    this.links.$found.off(events);
    this.links.$found.removeAttr("tabindex");
    this.config.cleanup();
  }

})(jQuery, dit.utils, dit.classes);

/* Class will add a controller before the $target element.
* The triggered event will toggle a class on the target element and controller.
* the target element with collapse, or expand.
*
* Note: The COLLAPSED class is added when the Expander element is closed, so
* you can add additional CSS for this state. Inline style, display:none is
* added by the code (mainly only because IE8 doesn't support CSS transitions).
*
* REQUIRES:
* jquery
* dit.js
* dit.utils.js
* dit.classes.expander.js
*
**/

(function($, utils, classes) {

  function Accordion(items, open, close) {
    if (arguments.length) {
      this.items = items;

      for (var i=0; i<items.length; ++i) {
        Accordion.enhance.call(this, items[i], open, close);
      }
    }
  }
  Accordion.enhance = function(target, open, close) {
    var items = this.items;
    var originalOpen = target[open];
    target[open] = function() {
      for(var i=0; i<items.length; ++i) {
        if(items[i] !== target) {
          items[i][close]();
        }
      }
      originalOpen.call(target);
    }
  }

  classes.Accordion = Accordion;
})(jQuery, dit.utils, dit.classes);


/* Class: Select Tracker
 * ---------------------
 * Adds a label element to mirror the matched selected option
 * text of a <select> input, for enhanced display purpose.
 *
 * REQUIRES:
 * jquery
 * dit.js
 * dit.classes.js
 *
 **/
(function($, classes) {

  /* Constructor
   * @$select (jQuery node) Target input element
   **/
  classes.SelectTracker = SelectTracker;
  function SelectTracker($select) {
    var SELECT_TRACKER = this;
    var button, code, lang;

    if(arguments.length && $select.length) {
      this.$node = $(document.createElement("p"));
      this.$node.attr("aria-hidden", "true");
      this.$node.addClass("SelectTracker");
      this.$select = $select;
      this.$select.addClass("SelectTracker-Select");
      this.$select.after(this.$node);
      this.$select.on("change.SelectTracker", function() {
        SELECT_TRACKER.update();
      });

      // Initial value
      this.update();
    }
  }
  SelectTracker.prototype = {};
  SelectTracker.prototype.update = function() {
    this.$node.text(this.$select.find(":selected").text());
  }

})(jQuery, dit.classes);
