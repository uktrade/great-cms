import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import { Modal } from '@src/components/Modal/index'

export const ComingSoon = ({ title }) => {
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
          backUrl="/learn/categories/market-research/"
          header="This Lesson is coming soon"
          content="This lesson is not available in Beta version of the new great.gov.uk platform."
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
      >
        <span>{title}</span>
        <button className="button button--secondary button--small">Coming soon</button>
      </a>
    </>
  )
}

function createComingSoonModal({ element, title }) {
  ReactDOM.render(<ComingSoon title={title} />, element)
}

export { createComingSoonModal }
