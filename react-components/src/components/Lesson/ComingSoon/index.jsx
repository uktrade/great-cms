import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import { Modal } from '@src/components/Modal/index'

export const ComingSoon = ({ title, backUrl }) => {
  const [modal, setModal] = useState(false)
  return (
    <>
      <ReactModal
        isOpen={modal}
        className="ReactModal__Content ReactModalCentreScreen"
        overlayClassName="ReactModal__Overlay ReactModalCentreScreen"
        contentLabel="Modal"
      >
        <Modal
          backUrl={backUrl}
          header="This lesson is coming soon"
          content="This lesson is not available in the Beta version of the new great.gov.uk platform."
          onClick={() => setModal(false)}
          buttonText="Ok"
          type={3}
        />
      </ReactModal>
      <a
        href=""
        className="learn__lesson-item-link h-xs"
        onClick={(e) => {
          e.preventDefault()
          setModal(true)
        }}
        role="button"
      >
        <span className="learn__lesson-item-link-text">{title}</span>
        <button className="button button--secondary button--small">Coming soon</button>
      </a>
    </>
  )
}

function createComingSoonModal({ element, title, backUrl }) {
  ReactDOM.render(<ComingSoon title={title} backUrl={backUrl} />, element)
}

export { createComingSoonModal }
