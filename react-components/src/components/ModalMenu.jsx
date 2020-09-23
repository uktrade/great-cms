import React, { useState, useEffect } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import Services from '@src/Services'

const customStyles = {
  overlay: {
    zIndex: '3',
    background: 'transparent',
    position: 'absolute'
  },
}

export function Menu(props) {
  let modalContent
  const [modalIsOpen, setIsOpen] = React.useState(false)

  const openModal = () => {
    setIsOpen(true)
  }

  const closeModal = () => {
    setIsOpen(false)
  }

  const modalAfterOpen = () => {
    modalContent.style.maxHeight = '700px'
  }

  let avatar = props.avatar ? (<img src={props.avatar} />) : ''

  return (
    <span>
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
      <div className="h-xs p-t-xxs">Hi {props.user_name || ''}</div>
        <ul className="menu-items">
          <li><a href="/dashboard/" className="link"><i className="fa fa-tachometer-alt"></i><span>Dashboard</span></a></li>
          <li><a href="/learn/categories/" className="link"><i className="fa fa-book"></i><span>Learn to export</span></a></li>
          <li><a href="/export-plan/dashboard/" className="link"><i className="fa fa-map-marker-alt"></i><span>Target a market</span></a></li>
          <li><a className="link"><i className="fa fa-folder"></i><span>Make an export plan</span></a></li>
          <hr className="m-v-xxs"></hr>
          <li><a href="#" className="link"><i className="fa fa-comment"></i><span>Send a feedback email</span></a></li>
          <li><a href="#" className="link"><i className="fa fa-arrow-right"></i><span>Sign out</span></a></li>
        </ul>
      </ReactModal>
    </span>
  )
}

export default function({ ...params }) {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
  ReactDOM.render(<Menu avatar={params.avatar} user_name={params.user_name}></Menu>, params.element)
}
