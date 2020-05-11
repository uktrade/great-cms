import convertAttributesToObject from '../../utils/convertAttributesToObject'
import template from './link.html'
import styles from './link.css'

customElements.define(
  'great-link',
  class extends HTMLElement {
    constructor() {
      super()
        
      const stylesheet = document.createElement('style')
      stylesheet.innerHTML = styles

      const { class: className, href, size, style, theme, ...rest } = convertAttributesToObject({ self: this })

      const shadowRoot = this.attachShadow({ mode: 'open' })
      shadowRoot.innerHTML = template
      shadowRoot.appendChild(stylesheet)

      const link = shadowRoot.querySelector('a')
      if (href || href === '') link.setAttribute('href', href)
      link.innerHTML = this.innerHTML
      Object.entries(rest).forEach(([key, value]) => link.setAttribute(key, value))

      const themes = ['primary', 'secondary']
      link.classList.add(themes.includes(theme) ? theme : 'primary') 

      const sizes = ['sm', 'lg']
      if (sizes.includes(size)) link.classList.add(size)
    }
  }
)
