import '../spinner/spinner'
import '../icon/icon'
import convertAttributesToObject from '../../utils/convertAttributesToObject'
import { iconNames } from '../icon/icons'
import template from './button.html'
import styles from './button.css'

customElements.define(
    'great-button',
    class extends HTMLElement {
        // Attributes that when changed will trigger 'attributeChangedCallback' method
        static get observedAttributes() {
            return [
                'autofocus',
                'disabled',
                'form',
                'formaction',
                'formenctype',
                'formmethod',
                'formnovalidate',
                'formtarget',
                'icon',
                'onblur',
                'onclick',
                'onfocus',
                'onmouseover',
                'loading',
                'name',
                'theme',
                'type',
                'value',
            ]
        }

        constructor() {
            super()

            // Create the shadowRoot that would contain our encapsulated component like an iframe
            this.shadow = this.attachShadow({ mode: 'open' })

            // template is just text equivalent to button.html, we need to create a DOM and render it first
            const { content } = new DOMParser().parseFromString(template, 'text/html').querySelector('template')
            this.shadow.appendChild(content.cloneNode(true))

            // styles that are imported from 'button.css' should also be attached to the shadowRoot
            // these will encapsulate the web component appearance, no styles on the parent document will apply
            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles
            this.shadow.appendChild(stylesheet)

            // Select the button element that came from our template and manipulate its attributes
            this.button = this.shadow.querySelector('button')

            this.buttonContent = this.shadow.querySelector('.content')
        }

        // Use 'attributeChangedCallback' lifecycle method to allow this component react on attr changes in a dynamic way
        // If we are to set these in the constructor any attr that changes past component initialisation won't trigger this code
        // attributes on the host element e.g. <great-button> are not guarantied to be present in the constructor
        attributeChangedCallback(name, oldValue, newValue) {
            if (oldValue === newValue) return

            const { disabled, theme } = convertAttributesToObject({ self: this })
            const availableThemes = ['primary', 'secondary', 'tertiary']

            switch (name) {
                case 'icon':
                    if (iconNames.includes(newValue)) {
                        const iconTheme = ['primary', 'secondary'].includes(theme) ? 'secondary' : 'primary'
                        const greatIcon = document.createElement('great-icon')
                        if (disabled !== undefined) greatIcon.setAttribute('disabled', disabled)
                        greatIcon.setAttribute('name', newValue)
                        greatIcon.setAttribute('theme', iconTheme)
                        greatIcon.setAttribute('size', 'sm')
                        this.button.prepend(greatIcon)
                    }
                    break
                case 'loading':
                    if (newValue !== undefined) {
                        const greatSpinner = document.createElement('great-spinner')
                        greatSpinner.setAttribute('size', 'sm')
                        greatSpinner.setAttribute('theme', theme === 'tertiary' ? 'dark' : 'light')
                        this.button.classList.add('loading')
                        this.button.prepend(greatSpinner)
                    }
                    break
                case 'theme':
                    if (availableThemes.includes(newValue)) {
                        if (oldValue) this.button.classList.remove(oldValue)
                        this.button.classList.add(newValue)
                    }
                    break
                default:
                    // any other attribute that is in observedAttributes will trigger the default behaviour
                    this.button.setAttribute(name, newValue)
            }
        }

        // A lifecycle method that fires when the element is attached to the DOM, we are guaranteed to have
        // access to other custom elements on the DOM and also to get host attributes
        connectedCallback() {
            // Gets all attributes passed to the root custom component
            // filters attrs that are already used or like 'class' and 'style' enforcing style encapsulation
            const { class: className, icon, loading, style, theme, ...rest } = convertAttributesToObject({ self: this })

            // Passes down all attributes from to the parent component like type="submit", aria-hidden="true", data-test="great-button"
            Object.entries(rest).forEach(([key, value]) => this.button.setAttribute(key, value))

            this.buttonContent.innerHTML = this.textContent
        }

        // Pass external clicks to the internal button
        click(event) {
            this.button.click(event)
        }

        // Pass external focuses to the internal button
        focus(event) {
            this.button.focus(event)
        }
    }
)