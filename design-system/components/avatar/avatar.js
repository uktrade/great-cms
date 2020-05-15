import template from './avatar.html'
import styles from './avatar.css'

customElements.define(
    'great-avatar',
    class extends HTMLElement {
        static get observedAttributes() {
            return ['src']
        }

        constructor() {
            super()

            this.shadow = this.attachShadow({ mode: 'open' })
            const { content } = new DOMParser().parseFromString(template, 'text/html').querySelector('template')
            this.shadow.appendChild(content.cloneNode(true))

            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles
            this.shadow.appendChild(stylesheet)

            this.img = this.shadow.querySelector('.avatar')
            this.emptyAvatar = this.shadow.querySelector('.empty-avatar')
        }

        attributeChangedCallback(name, _oldValue, newValue) {
            if (name === 'src' && newValue) {
                this.img.src = newValue
                this.emptyAvatar.style.display = 'none'
            }
        }

        connectedCallback() {
            const src = this.getAttribute('src')

            if (!src) {
                this.img.style.display = 'none'
            }
        }
    }
)
