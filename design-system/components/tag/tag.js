import convertAttributesToObject from '../../utils/convertAttributesToObject'
import template from './tag.html'
import styles from './tag.css'

customElements.define(
  'great-tag',
  class extends HTMLElement {
    constructor() {
      super()
        
      const stylesheet = document.createElement('style')
      stylesheet.innerHTML = styles

      const { class: className, disabled, icon, loading, style, theme, ...rest } = convertAttributesToObject({ self: this })

      const shadowRoot = this.attachShadow({ mode: 'open' })
      shadowRoot.innerHTML = template
      shadowRoot.appendChild(stylesheet)

      const tag = shadowRoot.querySelector('button')
      tag.classList.add(theme);

      if (disabled || disabled === '') tag.setAttribute('disabled', '')
      Object.entries(rest).forEach(([key, value]) => tag.setAttribute(key, value))

      tag.textContent = this.textContent
    }
  }
)
