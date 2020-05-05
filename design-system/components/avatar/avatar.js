import convertAttributesToObject from '../../utils/convertAttributesToObject'
import template from './avatar.html'
import styles from './avatar.css'

customElements.define(
  'great-avatar',
  class extends HTMLElement {
    constructor() {
      super()

      const stylesheet = document.createElement('style')
      stylesheet.innerHTML = styles

      const { class: className, style, src } = convertAttributesToObject({ self: this })

      const shadowRoot = this.attachShadow({ mode: 'open' })
      shadowRoot.innerHTML = template
      shadowRoot.appendChild(stylesheet)

      const img = shadowRoot.querySelector('.avatar')
      const emptyAvatar = shadowRoot.querySelector('.empty-avatar')
      if (src) {
          img.src = src
          emptyAvatar.style.display = 'none'
      } else {
          img.style.display = 'none'
      }
    }
  }
)
