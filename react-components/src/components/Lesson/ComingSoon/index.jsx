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
          header="Some lessons aren’t available yet"
          content="This Beta version is limited"
          onClick={() => setModal(false)}
          buttonText="Ok"
          type={'3'}
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
        <button className="button secondary-button button--small">Coming soon</button>
      </a>
    </>
  )
}

function createComingSoonModal({ element, title, backUrl }) {
  ReactDOM.render(<ComingSoon title={title} backUrl={backUrl} />, element)
}

export { createComingSoonModal }
