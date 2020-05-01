export class GreatAvatar extends HTMLElement {
    constructor() {
        super()

        const template = document.getElementById('great-avatar-template')

        const shadowRoot = this.attachShadow({ mode: 'open' })
        shadowRoot.appendChild(template.content.cloneNode(true))

        const imgSrc = this.getAttribute('src')
        const name = this.getAttribute('name')
        const imgElement = shadowRoot.querySelector('img')
        if (imgSrc) imgElement.setAttribute('src', imgSrc)
        if (name) imgElement.setAttribute('alt', `${name}'s avatar`)
    }
}

if(!customElements.get('great-avatar')) customElements.define('great-avatar', GreatAvatar)
