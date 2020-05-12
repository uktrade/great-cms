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

      const { disabled, name, size, theme } = convertAttributesToObject({ self: this })

      this.root = this.attachShadow({ mode: 'open' })
      this.root.innerHTML = template
      this.root.appendChild(stylesheet)
    }

    attributeChangedCallback(name, oldValue, newValue) {
      const icon = this.root.querySelector('span')

      if (name === 'size') {
        const sizes = ['sm', 'lg', 'xl', 'xxl']
        sizes.filter((size) => size === newValue).forEach((size) => icon.classList.remove(size))
        icon.classList.add(sizes.includes(newValue) ? newValue : 'sm')
      }

      if (name === 'theme') {
        const themes = ['primary', 'secondary']
        themes.filter((theme) => theme === newValue).forEach((theme) => icon.classList.remove(theme))
        icon.classList.add(themes.includes(newValue) ? newValue : 'primary')
      }

      if (name === 'name' && newValue && newValue !== '') {
        icon.innerHTML = icons[newValue]
      }

      if (name === 'disabled' && newValue || newValue === '') {
        icon.classList.add('disabled')
      } else {
        icon.classList.remove('disabled')
      }
    }
  }
)
