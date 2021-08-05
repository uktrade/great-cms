import React, { useState, useRef } from 'react'
import ReactDOM from 'react-dom'
import ReactHtmlParser from 'react-html-parser'

import ReactModal from 'react-modal'

const customStyles = {
  overlay: {
    zIndex: '3',
    background: 'rgba(0, 0, 0, 0)',
    position: 'fixed',
  },
  content: {},
}

export default function BasketViewer({ label, onOpen, children }) {
  const [modalIsOpen, setIsOpen] = useState(false)
  const buttonRef = useRef(null)

  const openViewer = () => {
    const { left, top, height } = buttonRef.current.getBoundingClientRect()
    customStyles.content = { margin: `${top + height + 8}px 0 0 ${left}px` }
    setIsOpen(true)
    onOpen && onOpen()
  }

  const closeModal = () => {
    setIsOpen(false)
  }

  const triggerButton = (
    <button
      type="button"
      className={`tag ${modalIsOpen ? 'tag--tertiary' : 'tag--secondary'}`}
      onClick={openViewer}
      ref={buttonRef}
    >
      <span>{label}</span>
      <i className={`fas ${'fa-chevron-down'} m-f-xxs`} aria-hidden="true" />
    </button>
  )

  return (
    <span>
      {triggerButton}
      <ReactModal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        style={customStyles}
        //onAfterOpen={modalAfterOpen}
        className="basket-view"
      >
        <div className="p-s">{children}</div>
      </ReactModal>
    </span>
  )
}
