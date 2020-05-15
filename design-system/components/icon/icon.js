import convertAttributesToObject from '../../utils/convertAttributesToObject'
import * as icons from './icons'
import template from './icon.html'
import styles from './icon.css'

customElements.define(
    'great-icon',
    class extends HTMLElement {
        static get observedAttributes() {
            return ['disabled', 'name', 'theme', 'size']
        }

        constructor() {
            super()

            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles

            this.root = this.attachShadow({ mode: 'open' })
            this.root.innerHTML = template
            this.root.appendChild(stylesheet)
            this.icon = this.root.querySelector('span')
        }

        attributeChangedCallback(name, oldValue, newValue) {
            switch (name) {
                case 'size':
                    if (oldValue) this.icon.classList.remove(oldValue)
                    if (['sm', 'lg', 'xl', 'xxl'].includes(newValue)) this.icon.classList.add(newValue)
                    break
                case 'theme':
                    if (oldValue) this.icon.classList.remove(oldValue)
                    if (['primary', 'secondary'].includes(newValue)) this.icon.classList.add(newValue)
                    break
                case 'name':
                    if (newValue !== '') this.icon.innerHTML = icons[newValue]
                    break
                case 'disabled':
                    if (newValue !== undefined) {
                        this.icon.classList.add('disabled')
                    } else {
                        this.icon.classList.remove('disabled')
                    }
                    break
                default:
            }
        }

        connectedCallback() {
            const { size, theme } = convertAttributesToObject({ self: this })

            // Sets default attributes
            if (!size) this.setAttribute('size', 'lg')
            if (!theme) this.setAttribute('theme', 'primary')
        }
    }
)
