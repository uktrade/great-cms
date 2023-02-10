import React, { useState, useRef } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import Services from '@src/Services'
import PropTypes from 'prop-types'
import { config } from '@src/config'

const customStyles = {
  overlay: {
    zIndex: '3',
    background: 'rgba(0, 0, 0, 0.6)',
    position: 'absolute',
  },
  content: {
    position: 'relative',
    height: '100%',
    overflow: 'visible',
    pointerEvents: 'none',
  },
}

export function Menu(props) {
  const { authenticated, userName } = props
  const [modalIsOpen, setIsOpen] = useState(false)
  const [topOffset, setTopOffset] = useState(0)
  const firstMenuItem = useRef(null)
  const lastMenuItem = useRef(null)
  const menuItem = useRef(null)

  const openModal = (evt) => {
    setTopOffset(evt.target.getBoundingClientRect().bottom)
    setIsOpen(true)
  }

  const closeModal = () => {
    setIsOpen(false)
  }

  const logout = () => {
    Services.logout().finally(() => {
      window.location = '/'
    })
  }

  const greeting =
    authenticated && userName ? (
      <div className="magna-header__greeting">Hi {userName}</div>
    ) : (
      ''
    )

  const menu = {
    authenticated: (
      <ul className="magna-header__menu-items">
        <li>
          <a
            href="/"
            ref={firstMenuItem}
            onKeyDown={(e) => {
              if (e.keyCode && e.shiftKey) {
                e.preventDefault()
                menuItem.current.focus()
              }
            }}
          >
            Home
          </a>
        </li>
        <li>
          <a href="/learn/categories/">
            Learn to export
          </a>
        </li>
        <li>
          <a href={config.compareCountriesUrl}>
            Where to export
          </a>
        </li>
        <li>
          <a href={config.exportPlanBaseUrl}>
            Make an export plan
          </a>
        </li>
        <li>
          <a href="/profile">Account</a>
        </li>
        <li>
          <a href="/advice">Advice</a>
        </li>
        <li>
          <a href="/markets">Markets</a>
        </li>
        <li>
          <a href="/services">Services</a>
        </li>
        <li>
          <button
            type="button"
            ref={lastMenuItem}
            onClick={logout}
            onKeyDown={(e) => {
              if (
                e.keyCode &&
                !e.shiftKey &&
                e.keyCode !== 13 &&
                e.keyCode !== 32
              ) {
                e.preventDefault()
                menuItem.current.focus()
              }
            }}
          >
            Sign out
          </button>
        </li>
      </ul>
    ),
    non_authenticated: (
      <ul className="magna-header__menu-items">
        <li>
          <a
            href="/contact-us/help/"
            rel="noopener noreferrer"
            ref={firstMenuItem}
          >
            <span>Send a feedback email</span>
          </a>
        </li>
        <li>
          <a href="/login/" ref={lastMenuItem}>
            <span>Sign up / Log in</span>
          </a>
        </li>
      </ul>
    ),
  }

  return (
    <>
      <button
        type="button"
        ref={menuItem}
        className="magna-header__dropdown-button"
        onClick={modalIsOpen ? closeModal : openModal}
        onKeyDown={(e) => {
          if (modalIsOpen && e.keyCode === 9) {
            e.preventDefault()
            ;(e.shiftKey ? lastMenuItem : firstMenuItem).current.focus()
          }
        }}
        aria-expanded={modalIsOpen}
      >
        Menu
        <span className="magna-header__dropdown-button__icon" />
      </button>
      <ReactModal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        style={customStyles}
        tabIndex="-1"
        className="container"
      >
        <div
          className={`magna-header__dropdown ${
            modalIsOpen ? 'magna-header__dropdown--open' : ''
          }`}
          style={{ top: `${topOffset}px`, pointerEvents: 'initial' }}
        >
          {greeting}
          {menu[authenticated ? 'authenticated' : 'non_authenticated']}
        </div>
      </ReactModal>
    </>
  )
}

Menu.propTypes = {
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
