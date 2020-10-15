import React from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import { Modal } from '@src/components/Modal/index'

export const ComingSoon = ({ isOpen, setIsOpen }) => {
  return (
    <ReactModal
      isOpen={isOpen}
      className="ReactModal__Content ReactModalCentreScreen"
      overlayClassName="ReactModal__Overlay ReactModalCentreScreen"
      contentLabel="Modal"
    >
      <Modal
        backUrl="/export-plan/dashboard/"
        header="This Lesson is coming soon"
        content="This feature is not available in Beta version of the new great.gov.uk platform."
        onClick={setIsOpen}
        buttonText="Ok"
      />
    </ReactModal>
  )
}

function renderComingSoon(element, isOpen, toggle) {
  ReactDOM.render(<ComingSoon isOpen={isOpen} setIsOpen={toggle} />, element)
}

function createComingSoonModal(element) {
  let isOpen = false

  const toggle = () => (isOpen = !isOpen)

  return {
    render: () => {
      toggle()
      renderComingSoon(element, isOpen, () => {
        toggle()
        renderComingSoon(element, isOpen, toggle)
      })
    }
  }
}

export { createComingSoonModal }
