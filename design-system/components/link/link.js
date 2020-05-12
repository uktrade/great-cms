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

      const stylesheet = document.createElement('style')
      stylesheet.innerHTML = styles

      const { class: className, href, size, style, theme, ...rest } = convertAttributesToObject({ self: this })

      this.root = this.attachShadow({ mode: 'open' })
      this.root.innerHTML = template
      this.root.appendChild(stylesheet)

      this.link = this.root.querySelector('a')
      this.link.innerHTML = this.innerHTML
      Object.entries(rest).forEach(([key, value]) => link.setAttribute(key, value))
    }

    attributeChangedCallback(name, oldValue, newValue) {
      if (name === 'size') {
        const sizes = ['sm', 'lg']
        // Removes all previously set classes
        sizes.filter((size) => size === newValue).forEach((size) => this.link.classList.remove(size))
        // Adds the new class to change the size
        this.link.classList.add(sizes.includes(newValue) ? newValue : 'sm')
      }

      if (name === 'theme') {
        const themes = ['primary', 'secondary']
        themes.filter((theme) => theme === newValue).forEach((theme) => this.link.classList.remove(theme))
        this.link.classList.add(themes.includes(newValue) ? newValue : 'primary')
      }

      if (name === 'href') {
        this.link.setAttribute('href', newValue)
      }
    }
  }
)
