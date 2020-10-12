import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import Services from '@src/Services'

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
  const [modalIsOpen, setIsOpen] = React.useState(false)

  const openModal = (evt) => {
    const position = evt.target.getClientRects()[0] || { top: 0, height: 0 }
    const bodyWidth = evt.target.closest('body').clientWidth
    customStyles.content.top = position.top + position.height + window.scrollY + 'px'
    customStyles.content.right = bodyWidth - (position.left + position.right) / 2 + 'px'

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
    Services.logout().then((response) => {
      window.location.reload()
    }).catch(
      window.location.reload()
    )
  }

  let avatar = props.avatar ? <img src={props.avatar} /> : (props.authenticated ? <i className="fas fa-user text-blue-deep-80"></i> : <i className="fas fa-caret-down text-blue-deep-80" style={{fontSize:'30px'}}></i>)

  let greeting = props.authenticated ? (<div className="h-xs p-t-xxs">Hi {props.user_name || 'there'}</div>) : ''

  let menu = {
    authenticated: (
      <ul className="menu-items">
          <li>
            <a href="/dashboard/" className="link">
              <i className="fa fa-tachometer-alt"></i>
              <span>Dashboard</span>
            </a>
          </li>
          <li>
            <a href="/learn/categories/" className="link">
              <i className="fa fa-book"></i>
              <span>Learn to export</span>
            </a>
          </li>
          <li>
            <a href="/find-your-target-market/" className="link">
              <i className="fa fa-map-marker-alt"></i>
              <span>Target a market</span>
            </a>
          </li>
          <li>
            <a href="/export-plan/dashboard/" className="link">
              <i className="fa fa-folder"></i>
              <span>Make an export plan</span>
            </a>
          </li>
          <hr className="m-v-xxs"></hr>
          <li>
            <a href="https://www.great.gov.uk/contact/feedback/" target="_blank" className="link">
              <i className="fa fa-comment"></i>
              <span>Send a feedback email</span>
            </a>
          </li>
          <li>
            <a href="#" className="link" onClick={logout}>
              <i className="fa fa-arrow-right"></i>
              <span>Sign out</span>
            </a>
          </li>
        </ul>),
    non_authenticated: (
      <ul className="menu-items">
          <li>
            <a href="https://www.great.gov.uk/contact/feedback/" target="_blank" className="link">
              <i className="fa fa-comment"></i>
              <span>Send a feedback email</span>
            </a>
          </li>
          <li>
            <a href="/login/" className="link">
              <i className="fa fa-pencil-alt"></i>
              <span>Sign up / Log in</span>
            </a>
          </li>
        </ul>
    )
  }

  return (
    <div style={{ lineHeight: 0 }}>
      <button className={'avatar' + (modalIsOpen ? ' active' : '')} onClick={openModal}>
        {avatar}
      </button>
      <ReactModal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        style={customStyles}
        onAfterOpen={modalAfterOpen}
        contentRef={(_modalContent) => (modalContent = _modalContent)}
        className="modal-menu"
      > 
        {greeting}
        {menu[props.authenticated ? 'authenticated' : 'non_authenticated']}
      </ReactModal>
    </div>
  )
}

export default function({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  ReactDOM.render(<Menu avatar={params.avatar} user_name={params.user_name} authenticated={params.authenticated == 'True'}></Menu>, params.element)
}
