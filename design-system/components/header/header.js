import '../avatar/avatar'
import '../link/link'
import '../logo/logo'
import template from './header.html'
import styles from './header.css'

customElements.define(
    'great-header',
    class extends HTMLElement {
        constructor() {
            super()

            this.isMobileMenuOpen = false

            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles

            const shadowRoot = this.attachShadow({ mode: 'open' })
            const header = document.createElement('div')
            header.innerHTML = template
            const templateContent = header.querySelector('template').content
            shadowRoot.appendChild(templateContent.cloneNode(true))
            shadowRoot.appendChild(stylesheet)

            const slottedNavigation = shadowRoot.querySelector('slot[name="navigation"]').assignedNodes()
            const [slottedAvatar] = shadowRoot.querySelector('slot[name="avatar"]').assignedNodes()
            const [name] = shadowRoot.querySelector('slot[name="name"]').assignedNodes()
            const mobileMenu = shadowRoot.querySelector('.mobile-menu')
            const mobileMenuIcon = shadowRoot.querySelector('great-icon[name="menu"')
            const mobileMenuWrapper = shadowRoot.querySelector('.mobile-menu-wrapper')
            const menuDetails = shadowRoot.querySelector('.details')
            const mobileCloseIcon = shadowRoot.querySelector('great-icon[name="close"')
            const greeting = document.createElement('p')
            greeting.textContent = 'Hello '
            greeting.appendChild(name.cloneNode(true))
            menuDetails.prepend(greeting)
            menuDetails.prepend(slottedAvatar.cloneNode(true))
            const dashboardLink = shadowRoot.querySelector('.mobile-menu li')
            slottedNavigation.forEach((li) => mobileMenu.insertBefore(li.cloneNode(true), dashboardLink))

            const { width } = mobileMenuWrapper.getBoundingClientRect()
            mobileMenuIcon.addEventListener('click', () => {
                mobileMenuWrapper.style.transform = `translate3d(-${width}px, 0, 0)`
                mobileMenuWrapper.focus()
                this.isMobileMenuOpen = !this.isMobileMenuOpen
            })
            const closeMenu = () => {
                mobileMenuWrapper.style.transform = `translate3d(${width}px, 0, 0)`
                this.isMobileMenuOpen = !this.isMobileMenuOpen
            }
            mobileCloseIcon.addEventListener('click', closeMenu)
            mobileMenuWrapper.addEventListener('blur', closeMenu, true)
            shadowRoot.addEventListener('keydown', (event) => {
                if (event.code === 'Escape') closeMenu()
            })
        }
    }
)
