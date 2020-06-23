import convertAttributesToObject from '../../utils/convertAttributesToObject'
import template from './tag.html'
import styles from './tag.css'

customElements.define(
    'great-tag',
    class extends HTMLElement {
        static get observedAttributes() {
            return [
                'autofocus',
                'disabled',
                'onblur',
                'onclick',
                'onfocus',
                'onmouseover',
                'name',
                'theme',
                'type',
                'value',
            ]
        }

        constructor() {
            super()

            this.shadow = this.attachShadow({ mode: 'open' })
            this.shadow.innerHTML = template

            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles
            this.shadow.appendChild(stylesheet)

            this.tag = this.shadow.querySelector('button')
        }

        connectedCallback() {
            this.tag.textContent = this.textContent

            const { class: className, style, theme, ...rest } = convertAttributesToObject({ self: this })
            Object.entries(rest).forEach(([key, value]) => this.button.setAttribute(key, value))
        }

        attributeChangedCallback(name, oldValue, newValue) {
            if (oldValue === newValue) return

            switch (name) {
                case 'theme':
                    if (['primary', 'secondary'].includes(newValue)) {
                        if (oldValue) this.tag.classList.remove(oldValue)
                        this.tag.classList.add(newValue)
                    }
                    break
                default:
                    this.tag.setAttribute(name, newValue)
            }
        }

        click(event) {
            this.tag.click(event)
        }

        focus(event) {
            this.tag.focus(event)
        }
    }
)
