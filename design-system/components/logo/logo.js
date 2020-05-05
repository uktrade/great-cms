import convertAttributesToObject from '../../utils/convertAttributesToObject'
import template from './logo.html'
import styles from './logo.css'

customElements.define(
  'great-logo',
  class extends HTMLElement {
    constructor() {
      super()

      const stylesheet = document.createElement('style')
      stylesheet.innerHTML = styles

      const shadowRoot = this.attachShadow({ mode: 'open' })
      shadowRoot.innerHTML = template
      shadowRoot.appendChild(stylesheet)

      const wrapper = shadowRoot.querySelector('span')
      const size = this.getAttribute('size')
      const sizes = ['sm']
      if (sizes.includes(size)) wrapper.classList.add(size)
    }
  }
)
