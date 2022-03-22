/**
 * Reveal functionality
 *
 * Used to toggle the visibility of a given component using a given trigger.
 * Trigger and target component can be separate in the markup, and are linked
 * using their respective `aria-controls` and `id` attributes.
 *
 * Usage:
 *    <button aria-controls="target" data-reveal-button>Toggle</button>
 *    <div id="target">Content to reveal</div>
 */

// eslint-disable-next-line func-names
;(function() {
  function toggleReveal(buttonEl, state) {
    const openState =
      typeof state !== 'undefined'
        ? state
        : buttonEl.getAttribute('aria-expanded') !== 'true'
    const expandedAttr = openState ? 'true' : 'false'
    const targetEl = document.querySelector(
      `#${buttonEl.getAttribute('aria-controls')}`
    )
    buttonEl.setAttribute('aria-expanded', expandedAttr)
    targetEl.setAttribute('aria-expanded', expandedAttr)
  }

  function init() {
    document.querySelectorAll('[data-reveal-button]').forEach((el) => {
      toggleReveal(el, false)
      el.addEventListener('click', (event) => {
        toggleReveal(event.target)
      })
    })
  }

  window.addEventListener('DOMContentLoaded', init)
})()
