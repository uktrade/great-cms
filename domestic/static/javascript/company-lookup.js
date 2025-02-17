var GOVUK = {};

/*
  General utility methods
  ======================= */
GOVUK.utils = (new function() {
  /* Try to dynamically generate a unique String value. */
  this.uniqueString = function() {
    return "_" + ((new Date().getTime()) + "_" + Math.random().toString()).replace(/[^\w]*/mig, "");
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
        service.response = response && response.items;
      },
      error: function(jqXHR) {
        if (jqXHR.status >= 400) {
          service.response = { error: "An error occurred while fetching data." };
          for (var i = 0; i < listeners.length; ++i) {
            listeners[i]();
          }
        }
      }
    }, configuration || {});

    var listeners = [];
    var request; // Reference to active update request

    service.response = {}; // What we get back from an update

    /* Gets a fresh response
     * @params (String) Specify params for GET or data for POST
     **/
    service.update = function(params, skipListeners = false) {
      if (request) request.abort(); // Cancels a currently active request
      config.data = params || "";
      request = $.ajax(config);
      request.done(function() {
        // Activate each listener task
        if (!skipListeners) {
          for (var i = 0; i < listeners.length; ++i) {
            listeners[i]();
          }
        }
      });
    }

    /* Specify data processing task after response
     * @task (Function) Do something after service.response has been updated
     **/
    service.listener = function(task) {
      listeners.push(task);
    }
  }

  // Create service to fetch Company from name lookup on Companies House API
  this.getCompanyByName = new Service("/api/companies-house/");
});

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
      lookupOnCharacter: 4,   // (Integer) At what character input to trigger the request for data.
      showNoneOfThese: false, // (Boolean) Show "none of these results" at the end.
    }, options || {});

    instance.options = opts;
    // Some inner variable requirement.
    instance._private = {
      active: false, // State management to isolate the listener.
      service: service, // Service that retrieves and stores the data
      $list: $("<ul class=\"SelectiveLookupDisplay\" style=\"display:none;\" id=\"" + popupId + "\" role=\"listbox\"></ul>"),
      $input: $input,
      timer: null,
      apiError: false,
    }

    // Will not have arguments if being inherited for prototype
    if (arguments.length >= 2) {
      // Bind lookup event.
      $input.attr("autocomplete", "off"); // Because it interferes with results display.
      $input.on("focus.SelectiveLookup", function() { instance._private.active = true; });
      $input.on("blur.SelectiveLookup", function() { instance._private.active = false; });
      $input.on("input.SelectiveLookup", function() {
        if (instance._private.timer) {
          clearTimeout(instance._private.timer);
        }

        if (this.value.length >= opts.lookupOnCharacter) {
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
        switch (e.which) {
          // Esc to close when on input
          case 27:
            instance.close();
            break;

          // Tab or arrow from input to list
          case 9:
          case 40:
            if (!e.shiftKey && instance._private.$input.attr("aria-expanded") === "true") {
              e.preventDefault();
              instance._private.$list.find("li:first-child").focus();
            }
        }
      });

      instance._private.$list.on("keydown.SelectiveLookup", "li", function(e) {
        var $current = $(e.target);
        switch (e.which) {
          // Prevent tabbing beyond list
          case 9:
            if ($current.is(":last-child") && !e.shiftKey) {
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
        if (e.shiftKey && e.which === 9 || e.which === 38) {
          e.preventDefault();
          $input.focus();
        }
      });

      // Bind service update listener
      instance._private.service.listener(function() {
        instance.setContent();
        instance.bindContentEvents();
        instance.open();
      });

      // Add some accessibility support
      $input.attr("aria-autocomplete", "list");
      $input.attr("role", "combobox");
      $input.attr("aria-expanded", "false");
      $input.attr("aria-owns", popupId);

      // Add display element if not already present
      if (!instance._private.$list.parent().length) {
        $(document.body).append(instance._private.$list);
      }

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
      if ($eventTarget.attr("data-value")) {
        instance._private.$input.val($eventTarget.attr("data-value"));
      }
    });
  }
  SelectiveLookup.prototype.close = function() {
    var $input = this._private.$input;
    if ($input.attr("aria-expanded") === "true") {
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
    return this._private.$input.attr("name") + "=" + this._private.$input.val();
  }
  /* Uses the data set on associated service to build HTML
   * result output. Since data keys are quite likely to vary
   * across services, you can pass through a mapping object
   * to avoid the default/expected key names.
   * @datamapping (Object) Allow change of required key name
   **/
  SelectiveLookup.prototype.setContent = function(datamapping) {
    var data = this._private.service.response;
    var $list = this._private.$list;
    var map = datamapping || { text: "text", value: "value" };
    $list.empty();
    if (data && data.error) {
      this._private.$errors.empty();
      $list.append('<li id="company-lookup-api-error" role="status" class="SelectiveLookupDisplay__list-item--inactive"><div class="govuk-warning-text govuk-!-padding-0 govuk-!-margin-0"><span class="great-warning-text__icon govuk-!-margin-top-1" aria-hidden="true">!</span><div class="great-padding-left-35"><span class="govuk-warning-text__assistive">Warning</span>Sorry, there is a problem. We expect the service to resume shortly. Try again later.</div></div></li>');
      window.companyNameLookup._private.$input.get(0).classList.add("company-search-input--disabled");
      this._private.$input.attr("disabled", "disabled");
      this._private.apiError = true;
      this.open();
    } else if (data && data.length) {
      this._private.apiError = false;
      for (var i = 0; i < data.length; ++i) {
        // Note:
        // Only need to set a tabindex attribute to allow focus.
        // The value is not important here.
        $list.append("<li role=\"option\" tabindex=\"1000\" data-value=\"" + data[i][map.value] + "\">" + data[i][map.text] + "</li>");
      }
      if (this.options.showNoneOfThese) {
        $list.append('<li id="company-lookup-name-not-in-companies-house" role="option">None of these companies. I\'m not in Companies House</li>');
      }
      this.open();
    } else {
      this._private.apiError = false;
      $list.append('<li id="company-lookup-name-no-results-found" role="option">No results found</li>');
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
    for (var i = 0; i < SelectiveLookup.instances.length; ++i) {
      if (!SelectiveLookup.instances[i]._private.apiError) {
        SelectiveLookup.instances[i].close();
      }
    }
  }

  // So that we close any open when another is activated
  $(document).ready(function() {
    $(document.body).on("click.SelectiveLookupCloseAll", SelectiveLookup.closeAll);
  });

  /* Extends SelectiveLookup to perform specific requirements
   * for Companies House company search by name, and resulting
   * form field population.
   * @$input (jQuery node) Target input element
   * @$field (jQuery node) Alternative element to populate with selection value
   **/
  this.CompaniesHouseNameLookup = CompaniesHouseNameLookup;
  function CompaniesHouseNameLookup($input, $field, options) {
    var instance = this;
    SelectiveLookup.call(this,
      $input,
      GOVUK.data.getCompanyByName,
      options,
    );

    // Some inner variable requirement.
    this._private.$field = $field || $input; // Allows a different form field to receive value.
    this._private.$form = $input.parents("form");
    this._private.$errors = $(".errors", this._private.$form);

    // Custom error handling.
    this._private.$form.on("submit.CompaniesHouseNameLookup", function(e) {
      // If no input or no company selected
      if (instance._private.$field.val() === "") {
        instance._private.$errors.empty();
        instance._private.$errors.append("<p>Check that you entered the company name correctly and select the matching company name from the list.</p>");
        instance._private.$errors.show();
      }
    });
  }
  CompaniesHouseNameLookup.prototype = new SelectiveLookup;
  CompaniesHouseNameLookup.prototype.bindContentEvents = function() {
    var instance = this;
    instance._private.$list.off("click.CompaniesHouseNameLookup");
    instance._private.$list.on("click.CompaniesHouseNameLookup", function(event) {
      var $eventTarget = $(event.target);

      // Try to set company number value.
      if ($eventTarget.attr("data-value")) {
        instance._private.$input.val($eventTarget.text());
        instance._private.$field.val($eventTarget.attr("data-value"));
      }
    });
  }
  CompaniesHouseNameLookup.prototype.param = function() {
    var encodedValue = encodeURIComponent(this._private.$input.val());
    return "term=" + encodedValue;
  }
  CompaniesHouseNameLookup.prototype.setContent = function() {
    SelectiveLookup.prototype.setContent.call(this, {
      text: "title",
      value: "company_number"
    });
  }
});


