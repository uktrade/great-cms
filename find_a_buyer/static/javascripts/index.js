var GOVUK = {};

/*
  General utility methods
  ======================= */
GOVUK.utils = (new function() {

  /* Parse the URL to retrieve a value.
   * @name (String) Name of URL param
   * e.g.
   * GOVUK.utils.getParameterByName('a_param');
   **/
  this.getParameterByName = function(name) {
    var param = name.replace(/[\\\[]/g, "\\[").replace(/[\]]/g, "\\]");
    var qs = document.location.search.replace("&amp;", "&");
    var regex = new RegExp("[\\?&]" + param + "=([^&#]*)");
    var results = regex.exec(qs);
    return results === null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
  }

  /* Try to dynamically generate a unique String value.
   **/
  this.uniqueString = function() {
    return "_" + ((new Date().getTime()) + "_" + Math.random().toString()).replace(/[^\w]*/mig, "");
  }

});


/*
  Cookie methods
  ==============
  Setting a cookie:
  GOVUK.cookie.set('hobnob', 'tasty', { days: 30 });

  Reading a cookie:
  GOVUK.cookie.get('hobnob');

  Deleting a cookie:
  GOVUK.cookie.set('hobnob', null);
*/
GOVUK.cookie = (new function() {

  /* Set a cookie.
   * @name (String) Name of cookie
   * @value (String) Value to store
   * @options (Object) Optional configurations
   **/
  this.set = function(name, value, options) {
    var opts = options || {};
    var str = name + "=" + value + "; path=/";
    var domain, domainSplit;
    if (opts.days) {
      var date = new Date();
      date.setTime(date.getTime() + (opts.days * 24 * 60 * 60 * 1000));
      str += "; expires=" + date.toGMTString();
    }

    if(opts.domain) {
      str += "; domain=" + opts.domain;
    }

    if (document.location.protocol == 'https:'){
      str += "; Secure";
    }

    document.cookie = str;
  }

 /* Read a cookie
  * @name (String) Name of cookie to read.
  **/
  this.get = function(name) {
    var nameEQ = name + "=";
    var cookies = document.cookie.split(';');
    var value;

    for(var i = 0, len = cookies.length; i < len; i++) {
      var cookie = cookies[i];
      while (cookie.charAt(0) == ' ') {
        cookie = cookie.substring(1, cookie.length);
      }
      if (cookie.indexOf(nameEQ) === 0) {
        value = decodeURIComponent(cookie.substring(nameEQ.length));
      }
    }
    return value;
  }

  /* Delete a cookie.
   * @name (String) Name of cookie
   **/
  this.remove = function(name) {
    this.set(name, null);
  }

});


/*
  UTM value storage
  =================
  Store values from URL param:
  GOVUK.utm.set();

  Reading stored values:
  GOVUK.utm.get();
*/
GOVUK.utm = (new function() {
  var utils = GOVUK.utils;

  this.set = function() {
    // params = [utm_campaign|utm_content|utm_medium|utm_source\utm_term]
    var params = document.location.search.match(/utm_[a-z]+/g) || [];
    var domain = document.getElementById("utmCookieDomain");
    var config = { days: 7 };
    var data = {};
    var json, value;

    if(domain) {
      config.domain = domain.getAttribute("value");
    }

    // 1. Does not add empty values.
    for(var i=0; i<params.length; ++i) {
      value = utils.getParameterByName(params[i]);
      if(value) {
        data[params[i]] = value;
      }
    }

    json = JSON.stringify(data);
    if(json.length > 2) { // ie. not empty
      GOVUK.cookie.set("ed_utm", json, config);
    }
  }

  this.get = function() {
    var cookie = GOVUK.cookie.get("ed_utm");
    return cookie ? JSON.parse(cookie) : null;
  }

});


/*
  General data storage and services
  =================================== */
GOVUK.data = (new function() {

  function Service(url, configuration) {
    var service = this;
    var config = $.extend({
      url: url,
      method: "GET",
      success: function(response) {
        service.response = response;
      }
    }, configuration || {});

    var listeners = [];
    var request; // Reference to active update request

    service.response = {}; // What we get back from an update

    /* Gets a fresh response
     * @params (String) Specify params for GET or data for POST
     **/
    service.update = function(params) {
      if(request) request.abort(); // Cancels a currently active request
      config.data = params || "";
      request = $.ajax(config);
      request.done(function() {
        // Activate each listener task
        for(var i=0; i<listeners.length; ++i) {
          listeners[i]();
        }
      })
    }

    /* Specify data processing task after response
     * @task (Function) Do something after service.response has been updated
     **/
    service.listener = function(task) {
      listeners.push(task);
    }
  }


  // Create service to fetch Company from name lookup on Companies House API
  this.getCompanyByName = new Service("/api/internal/companies-house-search/");

});


/*
  General reusable component classes
  ==================================== */
GOVUK.components = (new function() {

  /* Performs a data lookup and displays multiple choice results
   * to populate the input value with user choice.
   *
   * @$input (jQuery node) Target input element
   * @request (Function) Returns reference to the jqXHR requesting data
   * @content (Function) Returns content to populate the dropdown
   * @options (Object) Allow some configurations
   **/
  this.SelectiveLookup = SelectiveLookup;
  function SelectiveLookup($input, service, options) {
    var instance = this;
    var popupId = GOVUK.utils.uniqueString();

    // Configure options.
    var opts = $.extend({
      lookupOnCharacter: 4, // (Integer) At what character input to trigger the request for data
    }, options || {});

    // Some inner variable requirement.
    instance._private = {
      active: false, // State management to isolate the listener.
      service: service, // Service that retrieves and stores the data
      $list: $("<ul class=\"SelectiveLookupDisplay\" style=\"display:none;\" id=\"" + popupId + "\" role=\"listbox\"></ul>"),
      $input: $input,
      timer: null
    }

    // Will not have arguments if being inherited for prototype
    if(arguments.length >= 2) {
      
      // Bind lookup event.
      $input.attr("autocomplete", "off"); // Because it interferes with results display.
      $input.on("focus.SelectiveLookup", function() { instance._private.active = true; });
      $input.on("blur.SelectiveLookup", function() { instance._private.active = false; });
      $input.on("input.SelectiveLookup", function() {
        if(instance._private.timer) {
          clearTimeout(instance._private.timer);
        }
        
        if(this.value.length >= opts.lookupOnCharacter) {
          instance._private.timer = setTimeout(function() {
            instance.search()
          }, 500);
        }
      });

      /* Bind events to allow keyboard navigation of component.
       * Using keydown event because works better with Tab capture.
       * Supports following keys:
       * 9 = Tab
       * 13 = Enter
       * 27 = Esc
       * 38 = Up
       * 40 = Down
       */
      $input.on("keydown.SelectiveLookup", function(e) {
        switch(e.which) {

          // Esc to close when on input
          case 27:
            instance.close();
            break;

          // Tab or arrow from input to list
          case  9:
          case 40:
            if(!e.shiftKey && instance._private.$input.attr("aria-expanded") === "true") {
              e.preventDefault();
              instance._private.$list.find("li:first-child").focus();
            }
        }
      });

      instance._private.$list.on("keydown.SelectiveLookup", "li", function(e) {
        var $current = $(e.target);
        switch(e.which) {
          // Prevent tabbing beyond list
          case 9:
            if($current.is(":last-child") && !e.shiftKey) {
              e.preventDefault();
            }
            break;

          // Arrow movement between list items
          case 38:
            e.preventDefault();
            $current.prev("li").focus();
            break;
          case 40:
            e.preventDefault();
            $current.next("li").focus();
            break;

          // Esc to close when on list item (re-focus on input)
          case 27:
            instance.close();
            $input.focus();
            break;

          // Enter key item selection
          case 13:
            e.preventDefault();
            $current.click();
        }
      });

      // Tab or arrow movement from list to input
      instance._private.$list.on("keydown.SelectiveLookup", "li:first-child", function(e) {
        if(e.shiftKey && e.which === 9 || e.which === 38) {
          e.preventDefault();
          $input.focus();
        }
      });

      // Bind service update listener
      instance._private.service.listener(function() {
        if(instance._private.active) {
          instance.setContent();
          instance.bindContentEvents();
          instance.open();
        }
      });

      // Add some accessibility support
      $input.attr("aria-autocomplete", "list");
      $input.attr("role", "combobox");
      $input.attr("aria-expanded", "false");
      $input.attr("aria-owns", popupId);

      // Add display element
      $(document.body).append(instance._private.$list);

      // Register the instance
      SelectiveLookup.instances.push(this);

      // A little necessary visual calculating.
      $(window).on("resize", function() {
        instance.setSizeAndPosition();
      });
    }
  }

  SelectiveLookup.prototype = {};
  SelectiveLookup.prototype.bindContentEvents = function() {
    var instance = this;
    instance._private.$list.off("click.SelectiveLookupContent");
    instance._private.$list.on("click.SelectiveLookupContent", function(event) {
      var $eventTarget = $(event.target);
      if($eventTarget.attr("data-value")) {
        instance._private.$input.val($eventTarget.attr("data-value"));
      }
    });
  }
  SelectiveLookup.prototype.close = function() {
    var $input = this._private.$input;
    if($input.attr("aria-expanded") === "true") {
      this._private.$list.css({ display: "none" });
      $input.attr("aria-expanded", "false");
      $input.focus();
    }
  }
  SelectiveLookup.prototype.search = function() {
   this._private.$errors.empty();
   this._private.service.update(this.param());
  }
  SelectiveLookup.prototype.param = function() {
    // Set param in separate function to allow easy override.
    return this._private.$input.attr("name") + "=" + this._private.$input.value;
  }
  /* Uses the data set on associated service to build HTML
   * result output. Since data keys are quite likely to vary
   * across services, you can pass through a mappingn object
   * to avoid the default/expected key names.
   * @datamapping (Object) Allow change of required key name
   **/
  SelectiveLookup.prototype.setContent = function(datamapping) {
    var data = this._private.service.response;
    var $list = this._private.$list;
    var map = datamapping || { text: "text", value: "value" };
    $list.empty();
    if(data && data.length) {
      for(var i=0; i<data.length; ++i) {
        // Note:
        // Only need to set a tabindex attribute to allow focus.
        // The value is not important here.
        $list.append("<li role=\"option\" tabindex=\"1000\" data-value=\"" + data[i][map.value] + "\">" + data[i][map.text] + "</li>");
      }
    }
    else {
      $list.append("<li role=\"option\">No results found</li>");
    }
  }
  SelectiveLookup.prototype.setSizeAndPosition = function() {
    var position = this._private.$input.offset();
    this._private.$list.css({
      left: parseInt(position.left) + "px",
      position: "absolute",
      top: (parseInt(position.top) + this._private.$input.outerHeight()) + "px",
      width: this._private.$input.outerWidth() + "px"
    });
  }
  SelectiveLookup.prototype.open = function() {
    this.setSizeAndPosition();
    this._private.$list.css({ display: "block" });
    this._private.$input.attr("aria-expanded", "true");
  }


  SelectiveLookup.instances = [];
  SelectiveLookup.closeAll = function() {
    for(var i=0; i<SelectiveLookup.instances.length; ++i) {
      SelectiveLookup.instances[i].close();
    }
  }

  /* Extends SelectiveLookup to perform specific requirements
   * for Companies House company search by name, and resulting
   * form field population.
   * @$input (jQuery node) Target input element
   * @$field (jQuery node) Alternative element to populate with selection value
   **/
  this.CompaniesHouseNameLookup = CompaniesHouseNameLookup;
  function CompaniesHouseNameLookup($input, $field) {
    var instance = this;
    SelectiveLookup.call(this,
      $input,
      GOVUK.data.getCompanyByName
    );

    // Some inner variable requirement.
    this._private.$field = $field || $input; // Allows a different form field to receive value.
    this._private.$form = $input.parents("form");
    this._private.$errors = $(".errors", this._private.$form);
    
    // Custom error handling.
    this._private.$form.on("submit.CompaniesHouseNameLookup", function(e) {
      // If no input or no company selected
      if(instance._private.$field.val() === "") {
        e.preventDefault();
        instance._private.$errors.empty();
        instance._private.$errors.append("<p>Check that you entered the company name correctly and select the matching company name from the list.</p>");
      }
    });
  }
  CompaniesHouseNameLookup.prototype = new SelectiveLookup;
  CompaniesHouseNameLookup.prototype.bindContentEvents = function() {
    var instance = this;
    instance._private.$list.off("click.SelectiveLookupContent");
    instance._private.$list.on("click.CompaniesHouseNameLookup", function(event) {
      var $eventTarget = $(event.target);
      
      // Try to set company number value.
      if($eventTarget.attr("data-value")) {
        instance._private.$input.val($eventTarget.text());
        instance._private.$field.val($eventTarget.attr("data-value"));
      }
    });
  }
  CompaniesHouseNameLookup.prototype.param = function() {
    return "term=" + escape(this._private.$input.val());
  }
  CompaniesHouseNameLookup.prototype.setContent = function() {
    SelectiveLookup.prototype.setContent.call(this, {
      text: "title",
      value: "company_number"
    });
  }
});


/* In test mode we don't want the code to
 * run immediately because we have to compensate
 * for not having a browser environment first.
 **/
GOVUK.page = (new function() {

  // What to run on every page (called from <body>).
  this.init = function() {
    captureUtmValue();
    setupCompaniesHouseLookup();
  }

  /* Attempt to capture UTM information if we haven't already
   * got something and querystring is not empty.
   **/
  function captureUtmValue() {
    var captured = GOVUK.utm.get();
    if(!captured && document.location.search.substring(1)) {
      GOVUK.utm.set();
    }
  }

  /* Add Companies House name lookup AJAX functionality.
   **/
  function setupCompaniesHouseLookup() {
    $(".register-company-number-form.js-enabled-only").each(function() {
      var $companyNumber = $("input[name='company_number']", this);
      var $companyName = $("input[name='company_name']", this);
      
      // Apply JS lookup functionality.
      new GOVUK.components.CompaniesHouseNameLookup($companyName, $companyNumber);
    });
    $(document.body).on(
      "click.SelectiveLookupCloseAll",
      GOVUK.components.SelectiveLookup.closeAll
    );
  }

});
