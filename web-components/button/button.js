import styles from './button.scss';

export class Button extends HTMLElement {
  constructor() {
    super();

    const stylsheet = document.createElement('style');
    stylsheet.innerHTML = styles.toString();

    const contents =
      `<button class="great-button ${this.icon !== '' ? 'great-button--with-icon' : ''}" ${this.hasAttribute('disabled') ? 'disabled' : ''}>
          <div class="great-button__content">${this.textContent}</div>
        </button>`;

    const shadowRoot = this.attachShadow({ mode: 'open' })
    shadowRoot.innerHTML = contents;
    shadowRoot.appendChild(stylsheet);
  }
}