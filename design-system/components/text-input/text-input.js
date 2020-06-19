import template from './text-input.html'
import styles from './text-input.css'

customElements.define(
    'great-text-input',
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
                'value'
            ]
        }

        constructor() {
            super()

            this.shadow = this.attachShadow({ mode: 'open' })

            const { content } = new DOMParser().parseFromString(template, 'text/html').querySelector('template')
            this.shadow.appendChild(content.cloneNode(true))

            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles
            this.shadow.appendChild(stylesheet)

            this.input = this.shadow.querySelector('input')

            this.inputTypes = [
                'color',
                'date',
                'datetime-local',
                'email',
                'file',
                'month',
                'number',
                'password',
                'search',
                'tel',
                'text',
                'time',
                'url',
                'week'
            ]
        }

        attributeChangedCallback(name, oldValue, newValue) {
            if (oldValue === newValue) return

            switch (name) {
                case 'type':
                    if (this.inputTypes.includes(newValue)) {
                        this.input.setAttribute('type', newValue)
                    }
                    break
                default:
                    this.input.setAttribute(name, newValue)
            }
        }

        focus(event) {
            this.input.focus(event)
        }
    }
)
