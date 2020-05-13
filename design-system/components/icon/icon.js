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
      this.icon = this.root.querySelector('span')

      if (disabled || disabled === '') {
        console.log('before this.icon', this.icon)
        this.icon.classList.add('disabled')
        console.log('after this.icon', this.icon)
      }
    }

    attributeChangedCallback(name, oldValue, newValue) {
      if (name === 'size') {
        const sizes = ['sm', 'lg', 'xl', 'xxl']
        sizes.filter((size) => size === newValue).forEach((size) => this.icon.classList.remove(size))
        this.icon.classList.add(sizes.includes(newValue) ? newValue : 'sm')
      }

      if (name === 'theme') {
        const themes = ['primary', 'secondary']
        themes.filter((theme) => theme === newValue).forEach((theme) => this.icon.classList.remove(theme))
        this.icon.classList.add(themes.includes(newValue) ? newValue : 'primary')
      }

      if (name === 'name' && newValue && newValue !== '') {
        this.icon.innerHTML = icons[newValue]
      }

    //   if (name === 'disabled' && newValue === '') {
    //     this.icon.classList.add('disable')
    //   } else {
    //     this.icon.classList.remove('disable')
    //   }
    }
  }
)
