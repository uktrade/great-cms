import React, { useState, useRef } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import Services from '@src/Services'
import PropTypes from 'prop-types'

const customStyles = {
  overlay: {
    zIndex: '3',
    background: 'rgba(0, 0, 0, 0.6)',
    position: 'absolute',
  },
  content: {
    marginRight: '-29px',
    marginTop: '15px',
  },
}

export function Menu(props) {
  let modalContent
  const { avatar, authenticated, userName } = props
  const [modalIsOpen, setIsOpen] = useState(false)
  const firstMenuItem = useRef(null)
  const lastMenuItem = useRef(null)
  const menuItem = useRef(null)

  const openModal = (evt) => {
    const position = evt.target.getClientRects()[0] || { top: 0, height: 0 }
    const bodyWidth = evt.target.closest('body').clientWidth
    customStyles.content.top = `${
      (position.top + position.height + window.scrollY) - 15
    }px`
    customStyles.content.right = `${
      (bodyWidth - (position.left + position.right) / 2) - 27
    }px`

    setIsOpen(true)
  }

  const closeModal = () => {
    setIsOpen(false)
    document.body.style.overflow = ''
  }

  const modalAfterOpen = () => {
    modalContent.style.opacity = '1'
    document.body.style.overflow = 'auto'
  }

  const logout = () => {
    Services.logout().finally(() => {
      window.location.reload()
    })
  }

  let avatarElement = authenticated ? (
    <i className="fas fa-user text-blue-deep-80" />
  ) : (
    <i
      className="fas fa-caret-down text-blue-deep-80"
      style={{ fontSize: '30px' }}
    />
  )
  avatarElement = avatar ? (
    <img src={avatar} alt="User avatar" />
  ) : (
    avatarElement
  )

  const greeting = authenticated ? (
    <div className="h-xs p-t-xxs user-greeting">Hi {userName || 'there'}</div>
  ) : (
    ''
  )

  const focusMenuItem = (e, test, cb) => {
    if (test) {
      e.preventDefault();
      cb()
    }
  }

  const menu = {
    authenticated: (
      <ul className="menu-items">
        <li>
          <a href="/" className="link" ref={firstMenuItem} onKeyDown={(e) => {
            if (e.keyCode && e.shiftKey) {
              e.preventDefault();
              menuItem.current.focus();
            }
          }}>
            <span>Home</span>
          </a>
        </li>
        <li>
          <a href="/learn/categories/" className="link">
            <span>Learn to export</span>
            <strong className="tag tag--small">new</strong>
          </a>
        </li>
        <li>
          <a href="/where-to-export/" className="link">
            <span>Where to export</span>
            <strong className="tag tag--small">new</strong>
          </a>
        </li>
        <li>
          <a href="/export-plan/dashboard/" className="link">
            <span>Make an export plan</span>
            <strong className="tag tag--small">new</strong>
          </a>
        </li>
        <li>
          <a href="/advice" className="link">
            <span>Advice</span>
          </a>
        </li>
        <li>
          <a href="/markets" className="link">
            <span>Markets</span>
          </a>
        </li>
        <li>
          <a href="/services" className="link">
            <span>Services</span>
          </a>
        </li>
        <li>
          <a href="/account" className="link">
            <span>Account</span>
          </a>
        </li>
        <li>
          <button type="button" className="link" ref={lastMenuItem} onClick={logout} onKeyDown={(e) => {
            if (e.keyCode && !e.shiftKey) {
              e.preventDefault();
              menuItem.current.focus();
            }
          }}>
            <span>Sign out</span>
          </button>
        </li>
      </ul>
    ),
    non_authenticated: (
      <ul className="menu-items">
        <li>
          <a
            href="/contact-us/help/"
            rel="noopener noreferrer"
            className="link"
          >
            <span>Send a feedback email</span>
          </a>
        </li>
        <li>
          <a href="/login/" className="link">
            <span>Sign up / Log in</span>
          </a>
        </li>
      </ul>
    ),
  }

  return (
    <div style={{ lineHeight: 0 }}>
      <button
        type="button"
        ref={menuItem}
        className={modalIsOpen ? 'active' : ''}
        onClick={modalIsOpen ? closeModal : openModal}
        onKeyDown={(e) => {
          if (modalIsOpen && e.keyCode == 9) {
            e.preventDefault();
            e.shiftKey ? lastMenuItem.current.focus() : firstMenuItem.current.focus();
          }
        }}
      >
        Menu
        <span className="burger-icon"></span>
        <span className="visually-hidden">User menu</span>
      </button>
      <ReactModal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        style={customStyles}
        onAfterOpen={modalAfterOpen}
        contentRef={(_modalContent) => {
          modalContent = _modalContent
          return modalContent
        }}
        className="modal-menu shared-modal-menu"
      >
        {greeting}
        {menu[authenticated ? 'authenticated' : 'non_authenticated']}
      </ReactModal>
    </div>
  )
}

Menu.propTypes = {
  avatar: PropTypes.string.isRequired,
  authenticated: PropTypes.bool.isRequired,
  userName: PropTypes.string.isRequired,
}

export default function createMenu({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  ReactDOM.render(
    <Menu
      avatar={params.avatar}
      userName={params.user_name}
      authenticated={params.authenticated === 'True'}
    />,
    params.element
  )
}
