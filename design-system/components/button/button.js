import template from './button.html'
import styles from './button.scss'
import '../spinner/spinner.js'

customElements.define(
  'great-button',
  class extends HTMLElement {
    constructor() {
      super()
        
      const stylesheet = document.createElement('style')
      stylesheet.innerHTML = styles

      // Get all attributes passed to the component and convert them to an object
      const attributes = this.getAttributeNames().reduce((accumulator, attribute) => {
        accumulator[attribute] = this.getAttribute(attribute)
        return accumulator
      }, {})

      // Destructs attributes we need, class will be ignored in case it is passed
      // "rest" contains all attributes that we should pass down to the <button> element
      // To guard the component's appearance we deliberately exclude "class" and "style" attributes
      const { class: className, disabled, icon, loading, style, theme, ...rest } = attributes

      // Create the shadowRoot that would contain our encapsulated component like an iframe
      const shadowRoot = this.attachShadow({ mode: 'open' })
      // template is just a string of text equivalent to button.html
      shadowRoot.innerHTML = template
      shadowRoot.appendChild(stylesheet)

      // Select the button element that came from our template and manipulate its attributes
      const button = shadowRoot.querySelector('button')
      button.classList.add(theme);
      if (icon) button.classList.add('with-icon')

      if (disabled || disabled === '') button.setAttribute('disabled', '')
      // Passes down all attributes from to the parent component like type="submit", aria-hidden="true", data-test="great-button"
      Object.entries(rest).forEach(([key, value]) => button.setAttribute(key, value))

      const content = shadowRoot.querySelector('.content')
      content.innerHTML = this.textContent

      if (loading || loading === '') {
        const spinner = `<great-spinner size="sm" theme="${theme === 'tertiary' ? 'dark' : 'light'}"></great-spinner>`
        content.classList.add('loading')
        button.innerHTML += spinner
      }
    }
  }
)
