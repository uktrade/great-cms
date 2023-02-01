dit = window.dit || {}

dit.reveal = new function () {
    this.init = function () {
        document.querySelectorAll('[data-reveal-button]').forEach(function (el) {
            toggleReveal(el, false);
            el.addEventListener('click', function (event) {
                toggleReveal(event.target);
            });
        });
    }

    function toggleReveal(buttonEl, state) {
        const openState = typeof state !== 'undefined'
            ? state
            : buttonEl.getAttribute('aria-expanded') !== 'true';
        const expandedAttr = openState ? 'true' : 'false';
        const targetEl = document.querySelector('#' + buttonEl.getAttribute('aria-controls'));
        buttonEl.setAttribute('aria-expanded', expandedAttr);
        targetEl.setAttribute('aria-expanded', expandedAttr);
    }
}

window.addEventListener('DOMContentLoaded', dit.reveal.init);
