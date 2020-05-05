import template from './spinner.html'
import styles from './spinner.css'

customElements.define(
    'great-spinner',
    class extends HTMLElement {
        constructor() {
            super()

            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles

            const shadowRoot = this.attachShadow({ mode: 'open' })
            shadowRoot.innerHTML = template
            shadowRoot.appendChild(stylesheet)

            const wrapper = shadowRoot.querySelector('.spinner')
            if (this.hasAttribute('size')) wrapper.classList.add(this.getAttribute('size'))
            if (this.hasAttribute('theme')) wrapper.classList.add(this.getAttribute('theme'))
        }
    }
)
