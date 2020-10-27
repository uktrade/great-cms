import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import Services from '@src/Services'
import PropTypes from 'prop-types'

const customStyles = {
  overlay: {
    zIndex: '3',
    background: 'transparent',
    position: 'absolute',
  },
  content: {
    marginRight: '-29px',
    marginTop: '15px'
  }
}

export function Menu(props) {
  let modalContent
  const {avatar, authenticated, userName} = props
  const [modalIsOpen, setIsOpen] = useState(false)

  const openModal = (evt) => {
    const position = evt.target.getClientRects()[0] || { top: 0, height: 0 }
    const bodyWidth = evt.target.closest('body').clientWidth
    customStyles.content.top = `${position.top + position.height + window.scrollY}px`
    customStyles.content.right = `${bodyWidth - (position.left + position.right) / 2}px`

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
    Services.logout().then(() => {
      window.location.reload()
    }).catch(
      window.location.reload()
    )
  }
  let avatarElement = (authenticated ? <i className="fas fa-user text-blue-deep-80"/> : <i className="fas fa-caret-down text-blue-deep-80" style={{fontSize:'30px'}}/>)
  avatarElement = avatar ? <img src={avatar} alt="User avatar" /> : avatarElement

  const greeting = authenticated ? (<div className="h-xs p-t-xxs">Hi {userName || 'there'}</div>) : ''

  const menu = {
    authenticated: (
      <ul className="menu-items">
          <li>
            <a href="/dashboard/" className="link">
              <i className="fa fa-tachometer-alt" />
              <span>Dashboard</span>
            </a>
          </li>
          <li>
            <a href="/learn/categories/" className="link">
              <i className="fa fa-book" />
              <span>Learn to export</span>
            </a>
          </li>
          <li>
            <a href="/find-your-target-market/" className="link">
              <i className="fa fa-map-marker-alt" />
              <span>Target a market</span>
            </a>
          </li>
          <li>
            <a href="/export-plan/dashboard/" className="link">
              <i className="fa fa-folder" />
              <span>Build an export plan</span>
            </a>
          </li>
          <hr className="m-v-xxs" />
          <li>
            <a href="https://www.great.gov.uk/contact/feedback/" target="_blank" rel="noopener noreferrer" className="link">
              <i className="fa fa-comment" />
              <span>Send a feedback email</span>
            </a>
          </li>
          <li>
            <button type="button" className="link" onClick={logout}>
              <i className="fa fa-arrow-right" />
              <span>Sign out</span>
            </button>
          </li>
        </ul>),
    non_authenticated: (
      <ul className="menu-items">
          <li>
            <a href="https://www.great.gov.uk/contact/feedback/" target="_blank" rel="noopener noreferrer" className="link">
              <i className="fa fa-comment" />
              <span>Send a feedback email</span>
            </a>
          </li>
          <li>
            <a href="/login/" className="link">
              <i className="fa fa-pencil-alt" />
              <span>Sign up / Log in</span>
            </a>
          </li>
        </ul>
    )
  }

  return (
    <div style={{ lineHeight: 0 }}>
      <button type="button" className={`avatar${  modalIsOpen ? ' active' : ''}`} onClick={openModal}>
        {avatarElement}
      </button>
      <ReactModal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        style={customStyles}
        onAfterOpen={modalAfterOpen}
        contentRef={(_modalContent) => {modalContent = _modalContent; return modalContent}}
        className="modal-menu"
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
  ReactDOM.render(<Menu avatar={params.avatar} userName={params.user_name} authenticated={params.authenticated === 'True'} />, params.element)
}
