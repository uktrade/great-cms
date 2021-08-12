import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'
import { useOnOutsideClick } from '@src/components/hooks/useOnOutsideClick'

export default function BasketViewer({ label, onOpen, children }) {
  const [modalIsOpen, setIsOpen] = useState(false)
  const buttonRef = useRef(null)
  const outerSpan = useRef()

  const toggleViewer = () => {
    setIsOpen(!modalIsOpen)
    if (!modalIsOpen) {
      onOpen()
    }
  }

  useOnOutsideClick(outerSpan, (target) => {
    // Don't close basket if user has opened product finder or country finder from inside
    if(!target.closest('.ReactModalPortal')) {
      setIsOpen(false)
    }
  })

  const triggerButton = (
    <button
      type="button"
      className={`tag ${
        modalIsOpen ? 'tag--tertiary' : 'tag--secondary'
      } tag--icon`}
      onClick={toggleViewer}
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
    <span ref={outerSpan}>
      {triggerButton}
      {modalIsOpen ? <div className="basket-view p-s">{children}</div> : ''}
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
