import template from './spinner.html'
import styles from './spinner.css'

customElements.define(
    'great-spinner',
    class extends HTMLElement {
        static get observedAttributes() {
            return ['size', 'theme']
        }

        constructor() {
            super()

            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles

            this.shadow = this.attachShadow({ mode: 'open' })
            this.shadow.innerHTML = template
            this.shadow.appendChild(stylesheet)
            this.span = this.shadow.querySelector('.spinner')
        }

        attributeChangedCallback(name, oldValue, newValue) {
            if (oldValue === newValue) return

            switch (name) {
                case 'size':
                    if (oldValue) this.span.classList.remove(oldValue)
                    if (['sm', 'lg'].includes(newValue)) this.span.classList.add(newValue)
                    break
                case 'theme':
                    if (oldValue) this.span.classList.remove(oldValue)
                    if (['dark', 'light'].includes(newValue)) this.span.classList.add(newValue)
                    break
                default:
            }
        }
    }
)
