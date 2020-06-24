import template from './avatar.html'
import styles from './avatar.css'

customElements.define(
    'great-avatar',
    class extends HTMLElement {
        static get observedAttributes() {
            return ['onblur', 'onclick', 'onfocus', 'onmouseover', 'src']
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

        attributeChangedCallback(name, oldValue, newValue) {
            if (oldValue === newValue) return

            switch (name) {
                case 'src':
                    if (newValue) {
                        this.img.src = newValue
                        this.emptyAvatar.style.display = 'none'
                    } else {
                        this.emptyAvatar.style.display = 'block'
                        this.img.style.display = 'none'
                    }
                    break
                default:
                    this.emptyAvatar.setAttribute(name, newValue)
                    this.img.setAttribute(name, newValue)
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
