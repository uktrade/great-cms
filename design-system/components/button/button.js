import styles from './button.scss';

export class Button extends HTMLElement {
  constructor() {
    super();

    const stylesheet = document.createElement('style');
    stylesheet.innerHTML = styles;

    const theme = this.getAttribute('theme');
    const isLoading = this.hasAttribute('loading');

    const contents =
      `<button class="${theme} ${this.icon !== '' ? 'with-icon' : ''}" ${this.hasAttribute('disabled') ? 'disabled' : ''}>
          <span class="content">${isLoading ? '<span>Loading </span>' : '' }${this.textContent}</span>
        </button>`;

    const shadowRoot = this.attachShadow({ mode: 'open' })
    shadowRoot.innerHTML = contents;
    shadowRoot.appendChild(stylesheet);
  }
}

customElements.define('great-button', Button);
