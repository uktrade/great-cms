var common;
/******/ (() => { // webpackBootstrap
/******/ 	var __webpack_modules__ = ({

/***/ "./node_modules/great-styles/src/js/Reveal.js":
/*!****************************************************!*\
  !*** ./node_modules/great-styles/src/js/Reveal.js ***!
  \****************************************************/
/***/ (() => {

/**
 * Reveal functionality
 *
 * Used to toggle the visibility of a given component using a given trigger.
 * Trigger and target component can be separate in the markup, and are linked
 * using their respective `aria-controls` and `id` attributes.
 *
 * Usage:
 *    <button
 *      aria-controls="target"
 *      data-reveal-button
 *      [data-reveal-modal]
 *      [data-reveal-tabs="tab-group"]
 *    >
 *      Toggle
 *    </button>
 *    <div id="target">Content to reveal</div>
 *
 * CSS should be used to show/hide the content based on the `aria-expanded` and `aria-hidden` attributes.
 *
 * Optional attribute: `data-reveal-modal`
 * When added to the trigger, will treat the content as a modal:
 * - Pressing 'Escape' will close
 * - Clicking anywhere outside the content will close (provide your own overlay with CSS)
 * - Focus will be trapped within content and trigger
 *
 * Optional attribute: `data-reveal-tabs="tab-group-id"
 * When added to the trigger, will handle all related reveals as linked and function like tabs, i.e. only
 * one of the linked reveals will be open at once, with the first one open by default at the start.
 */

const tabbable = 'a[href], button, input, select, textarea, [tabindex]:not([tabindex="-1"])'

class Reveal {
  constructor(buttonElement) {
    if (!buttonElement) return

    this.button = buttonElement
    this.content = document.querySelector(`#${buttonElement.getAttribute('aria-controls')}`)
    this.asModal = buttonElement.getAttribute('data-reveal-modal') !== null
    this.tabGroup = buttonElement.getAttribute('data-reveal-tabs')

    if (this.asModal) {
      const contentTabbable = Array.from(this.content.querySelectorAll(tabbable))
      this.firstTabbableElement = contentTabbable[0]
      this.lastTabbableElement = contentTabbable[contentTabbable.length - 1]
    }

    this.toggle = this.toggle.bind(this)
    this.close = this.close.bind(this)
    this.handleKeydown = this.handleKeydown.bind(this)
    this.handleOutsideClick = this.handleOutsideClick.bind(this)

    if (this.tabGroup && document.querySelector(`[data-reveal-tabs="${this.tabGroup}"]`) === this.button) {
      this.open()
    } else {
      this.close()
    }

    buttonElement.addEventListener('click', this.toggle)
  }

  handleKeydown(event) {
    if (this.isOpen()) {
      if (event.key === 'Escape') {
        this.close()
      }
      if (event.key === 'Tab') {
        if (event.target === this.firstTabbableElement && event.shiftKey) {
          event.preventDefault()
          this.button.focus()
        }
        if (event.target === this.lastTabbableElement && !event.shiftKey) {
          event.preventDefault()
          this.button.focus()
        }
        if (event.target === this.button && !event.shiftKey) {
          event.preventDefault()
          this.firstTabbableElement.focus()
        }
        if (event.target === this.button && event.shiftKey) {
          event.preventDefault()
          this.lastTabbableElement.focus()
        }
      }
    }
  }

  handleOutsideClick(event) {
    if (this.isOpen() && !this.content.contains(event.target) && event.target !== this.button) {
      this.close()
    }
  }

  isOpen() {
    return this.button.getAttribute('aria-expanded') === 'true'
  }

  toggle() {
    if (this.isOpen() && !this.tabGroup) {
      this.close()
    } else {
      this.open()
    }
  }

  open() {
    this.button.setAttribute('aria-expanded', 'true')
    this.content.setAttribute('aria-hidden', 'false')

    if (this.tabGroup) {
      this.button.addEventListener('reveal:close', this.close)

      document.querySelectorAll(`[data-reveal-tabs="${this.tabGroup}"]`).forEach(el => {
        if (el !== this.button) {
          el.dispatchEvent(new Event('reveal:close'))
        }
      })
    }

    if (this.asModal) {
      document.addEventListener('keydown', this.handleKeydown)
      document.addEventListener('click', this.handleOutsideClick)
    }
  }

  close() {
    this.button.setAttribute('aria-expanded', 'false')
    this.content.setAttribute('aria-hidden', 'true')

    if (this.tabGroup) {
      this.button.removeEventListener('reveal:close', this.close)
    }

    if (this.asModal) {
      document.removeEventListener('keydown', this.handleKeydown)
      document.removeEventListener('click', this.handleOutsideClick)
    }
  }
}

(() => {
  window.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-reveal-button]').forEach((el) => new Reveal(el))
  })
})()


/***/ })

/******/ 	});
/************************************************************************/
/******/ 	// The module cache
/******/ 	var __webpack_module_cache__ = {};
/******/ 	
/******/ 	// The require function
/******/ 	function __webpack_require__(moduleId) {
/******/ 		// Check if module is in cache
/******/ 		var cachedModule = __webpack_module_cache__[moduleId];
/******/ 		if (cachedModule !== undefined) {
/******/ 			return cachedModule.exports;
/******/ 		}
/******/ 		// Create a new module (and put it into the cache)
/******/ 		var module = __webpack_module_cache__[moduleId] = {
/******/ 			// no module.id needed
/******/ 			// no module.loaded needed
/******/ 			exports: {}
/******/ 		};
/******/ 	
/******/ 		// Execute the module function
/******/ 		__webpack_modules__[moduleId](module, module.exports, __webpack_require__);
/******/ 	
/******/ 		// Return the exports of the module
/******/ 		return module.exports;
/******/ 	}
/******/ 	
/************************************************************************/
var __webpack_exports__ = {};
// This entry need to be wrapped in an IIFE because it need to be isolated against other modules in the chunk.
(() => {
/*!***************************!*\
  !*** ./core/js/common.js ***!
  \***************************/
__webpack_require__(/*! great-styles/src/js/Reveal */ "./node_modules/great-styles/src/js/Reveal.js");
})();

common = __webpack_exports__["default"];
/******/ })()
;
//# sourceMappingURL=common.js.map