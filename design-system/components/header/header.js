import '../avatar/avatar.js'
import '../link/link.js'
import '../logo/logo.js'
import convertAttributesToObject from '../../utils/convertAttributesToObject'
import template from './header.html'
import styles from './header.css'

customElements.define(
  'great-header',
  class extends HTMLElement {
    constructor() {
      super()
        
      const stylesheet = document.createElement('style')
      stylesheet.innerHTML = styles

      const { class: className, style, ...rest } = convertAttributesToObject({ self: this })

      const shadowRoot = this.attachShadow({ mode: 'open' })
      const header = document.createElement('div')
      header.innerHTML = template
      const templateContent = header.querySelector('template').content
      shadowRoot.appendChild(templateContent.cloneNode(true))
      shadowRoot.appendChild(stylesheet)
    }
  }
)
