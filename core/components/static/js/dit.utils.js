
// Utility Functions.
// ---------------------

// REQUIRES
// jQuery
// dit.js

dit.utils = dit.utils || (new function () {

  /* Attempt to generate a unique string
  * e.g. For HTML ID attribute.
  * @str = (String) Allow prefix string.
  **/
  this.generateUniqueStr = function (str) {
    return (str ? str : "") + ((new Date().getTime()) + "_" + Math.random().toString()).replace(/[^\w]*/mig, "");
  }
});
