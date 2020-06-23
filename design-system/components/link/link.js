import convertAttributesToObject from '../../utils/convertAttributesToObject'
import template from './link.html'
import styles from './link.css'

customElements.define(
    'great-link',
    class extends HTMLElement {
        static get observedAttributes() {
            return ['href', 'size', 'theme']
        }

        constructor() {
            super()

            this.shadow = this.attachShadow({ mode: 'open' })
            this.shadow.innerHTML = template

            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles
            this.shadow.appendChild(stylesheet)

            this.link = this.shadow.querySelector('a')
        }

        connectedCallback() {
            const { class: className, href, size, style, theme, ...rest } = convertAttributesToObject({ self: this })

            Object.entries(rest).forEach(([key, value]) => this.link.setAttribute(key, value))
            this.link.innerHTML = this.innerHTML
        }

        attributeChangedCallback(name, oldValue, newValue) {
            if (oldValue === newValue) return

            const sizes = ['sm', 'lg']
            const themes = ['primary', 'secondary']

            switch (name) {
                case 'size':
                    this.link.classList.remove(oldValue)
                    // Adds the new class to change the size
                    this.link.classList.add(sizes.includes(newValue) ? newValue : 'sm')
                    break
                case 'theme':
                    this.link.classList.remove(oldValue)
                    this.link.classList.add(themes.includes(newValue) ? newValue : 'primary')
                    break
                case 'href':
                    this.link.setAttribute('href', newValue)
                    break
                default:
                    this.tag.setAttribute(name, newValue)
            }
        }
    }
)
