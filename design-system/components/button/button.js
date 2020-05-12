import '../spinner/spinner.js'
import '../icon/icon.js'
import convertAttributesToObject from '../../utils/convertAttributesToObject'
import template from './button.html'
import styles from './button.css'

customElements.define(
  'great-button',
  class extends HTMLElement {
    constructor() {
      super()
        
      const stylesheet = document.createElement('style')
      stylesheet.innerHTML = styles

      // Destructs attributes we need, class will be ignored in case it is passed
      // "rest" contains all attributes that we should pass down to the <button> element
      // To guard the component's appearance we deliberately exclude "class" and "style" attributes
      const { class: className, disabled, icon, loading, style, theme, ...rest } = convertAttributesToObject({ self: this })

      // Create the shadowRoot that would contain our encapsulated component like an iframe
      const shadowRoot = this.attachShadow({ mode: 'open' })
      // template is just a string of text equivalent to button.html
      shadowRoot.innerHTML = template
      shadowRoot.appendChild(stylesheet)

      // Select the button element that came from our template and manipulate its attributes
      const button = shadowRoot.querySelector('button')
      button.classList.add(theme);

      if (disabled || disabled === '') button.setAttribute('disabled', '')
      // Passes down all attributes from to the parent component like type="submit", aria-hidden="true", data-test="great-button"
      Object.entries(rest).forEach(([key, value]) => button.setAttribute(key, value))

      const content = shadowRoot.querySelector('.content')
      content.innerHTML += this.textContent

      if (icon && icon !== '') {
          const iconTheme = ['primary', 'secondary'].includes(theme) ? 'secondary' : 'primary'
          const greatIcon = `<great-icon ${disabled === '' && 'disabled'} name="${icon}" theme="${iconTheme}" size="sm" ></great-icon>`
          content.innerHTML = greatIcon + content.innerHTML
      }

      if (loading || loading === '') {
        const spinner = `<great-spinner size="sm" theme="${theme === 'tertiary' ? 'dark' : 'light'}"></great-spinner>`
        button.classList.add('loading')
        button.innerHTML += spinner
      }
    }
  }
)
