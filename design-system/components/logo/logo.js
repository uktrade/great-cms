import template from './logo.html'
import styles from './logo.css'

customElements.define(
    'great-logo',
    class extends HTMLElement {
        static get observedAttributes() {
            return ['size']
        }

        constructor() {
            super()

            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles

            const shadowRoot = this.attachShadow({ mode: 'open' })
            shadowRoot.innerHTML = template
            shadowRoot.appendChild(stylesheet)

            this.wrapper = shadowRoot.querySelector('span')
        }

        attributeChangedCallback(name, oldValue, newValue) {
            if (oldValue === newValue) return

            if (name === 'size' && ['sm', 'lg'].includes(newValue)) {
                if (oldValue) this.wrapper.classList.remove(oldValue)
                this.wrapper.classList.add(newValue)
            }
        }
    }
)
