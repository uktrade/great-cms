import React, { useState, useRef } from 'react'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'

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
    onOpen()
  }

  const closeModal = () => {
    setIsOpen(false)
  }

  const triggerButton = (
    <button
      type="button"
      className={`tag ${
        modalIsOpen ? 'tag--tertiary' : 'tag--secondary'
      } tag--icon`}
      onClick={openViewer}
      ref={buttonRef}
    >
      <span>{label}</span>
      <i
        className={`fas ${modalIsOpen ? 'fa-chevron-up' : 'fa-chevron-down'}`}
        aria-hidden="true"
      />
    </button>
  )

  return (
    <span>
      {triggerButton}
      {
        <ReactModal
          isOpen={modalIsOpen}
          onRequestClose={closeModal}
          style={customStyles}
          className="basket-view"
        >
          <div className="p-s">{children}</div>
        </ReactModal>
      }
    </span>
  )
}

BasketViewer.propTypes = {
  label: PropTypes.string.isRequired,
  onOpen: PropTypes.func,
  children: PropTypes.instanceOf(Array).isRequired,
}
BasketViewer.defaultProps = {
  onOpen: () => 0,
}
