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

      const { class: className, style, href, ...rest } = convertAttributesToObject({ self: this })

      const shadowRoot = this.attachShadow({ mode: 'open' })
      shadowRoot.innerHTML = template
      shadowRoot.appendChild(stylesheet)

      const link = shadowRoot.querySelector('a')
      if (href || href === '') link.setAttribute('href', href)
      link.innerHTML = this.textContent
      Object.entries(rest).forEach(([key, value]) => link.setAttribute(key, value))
    }
  }
)
