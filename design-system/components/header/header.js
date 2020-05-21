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

            this.shadow = this.attachShadow({ mode: 'open' })

            const header = document.createElement('div')
            header.innerHTML = template
            const templateContent = header.querySelector('template').content
            this.shadow.appendChild(templateContent.cloneNode(true))

            const stylesheet = document.createElement('style')
            stylesheet.innerHTML = styles
            this.shadow.appendChild(stylesheet)
        }

        connectedCallback() {
            // Get slotted elements passed as <element slot="name" />
            const slottedNavigation = this.shadow.querySelector('slot[name="navigation"]').assignedNodes()
            const [slottedAvatar] = this.shadow.querySelector('slot[name="avatar"]').assignedNodes()
            const [name] = this.shadow.querySelector('slot[name="name"]').assignedNodes()

            // Mobile menu
            const mobileMenu = this.shadow.querySelector('.mobile-menu')
            this.mobileMenuIcon = this.shadow.querySelector('great-icon[name="menu"')
            this.mobileMenuWrapper = this.shadow.querySelector('.mobile-menu-wrapper')
            const menuDetails = this.shadow.querySelector('.details')
            this.mobileCloseIcon = this.shadow.querySelector('great-icon[name="close"')
            const greeting = document.createElement('p')
            greeting.textContent = 'Hello '
            greeting.appendChild(name.cloneNode(true))
            menuDetails.prepend(greeting)
            menuDetails.prepend(slottedAvatar.cloneNode(true))
            const dashboardLink = this.shadow.querySelector('.mobile-menu li')
            slottedNavigation.forEach((li) => mobileMenu.insertBefore(li.cloneNode(true), dashboardLink))

            // Event listeners
            const { width } = this.mobileMenuWrapper.getBoundingClientRect()

            this.handleClick = () => {
                this.mobileMenuWrapper.style.transform = `translate3d(-${width}px, 0, 0)`
                this.mobileMenuWrapper.focus()
                this.isMobileMenuOpen = !this.isMobileMenuOpen
            }

            this.handleCloseMenu = () => {
                this.mobileMenuWrapper.style.transform = `translate3d(${width}px, 0, 0)`
                this.isMobileMenuOpen = !this.isMobileMenuOpen
            }

            this.handleKeydown = (event) => {
                if (event.code === 'Escape') this.handleCloseMenu()
            }

            this.mobileMenuIcon.addEventListener('click', this.handleClick)
            this.mobileCloseIcon.addEventListener('click', this.handleCloseMenu)
            this.mobileMenuWrapper.addEventListener('blur', this.handleCloseMenu, true)
            this.shadow.addEventListener('keydown', this.handleKeydown)
        }

        disconnectedCallback() {
            // Always remove event listeners as these are not garbage collected
            this.mobileMenuIcon.removeEventListener('click', this.handleClick)
            this.mobileCloseIcon.removeEventListener('click', this.handleCloseMenu)
            this.mobileMenuWrapper.removeEventListener('blur', this.handleCloseMenu, true)
            this.shadow.removeEventListener('keydown', this.handleKeydown)
        }
    }
)
