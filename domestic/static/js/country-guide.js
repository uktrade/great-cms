dit.countryGuide = new (function () {
  // Page init
  this.init = function () {
    setupAccordionExpanders()
    delete this.init // Run once
  }

  /* Add expanding functionality to target elements for desktop.
   **/
  var accordions = []
  function setupAccordionExpanders() {
    $('.accordion-content').each(function () {
      var $this = $(this)
      accordions.push(
        new dit.classes.Expander($this, {
          hover: false,
          blur: false,
          wrap: false,
          $control: $this.parent().find('a.accordion-expander'),
        })
      )
    })
  }
})()

$(document).ready(function () {
  dit.countryGuide.init()
})
