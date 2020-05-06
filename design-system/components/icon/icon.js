import convertAttributesToObject from '../../utils/convertAttributesToObject'
import * as icons from './icons'
import template from './icon.html'
import styles from './icon.css'


customElements.define(
  'great-icon',
  class extends HTMLElement {
    constructor() {
      super()
      
      const stylesheet = document.createElement('style')
      stylesheet.innerHTML = styles

      const { disabled, name, size, theme } = convertAttributesToObject({ self: this })

      const shadowRoot = this.attachShadow({ mode: 'open' })
      shadowRoot.innerHTML = template
      shadowRoot.appendChild(stylesheet)

      const icon = shadowRoot.querySelector('span')
      const sizes = ['sm', 'lg', 'xl', 'xxl']
      if (name && name !== '') icon.innerHTML = icons[name]
      if (sizes.includes(size)) icon.classList.add(size)
      if (theme && theme !== '') icon.classList.add(theme)
      if (disabled || disabled === '') icon.classList.add('disabled')
    }
  }
)
