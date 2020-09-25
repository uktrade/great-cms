import React, { useState } from 'react'
import ReactModal from "react-modal";

export function MessageConfirmation(props) {
  const [modalIsOpen, setIsOpen] = React.useState(props.productConfirmation)
  const closeModal = () => {
    setIsOpen(false)
  }
  return (
    <span>
      <ReactModal 
        isOpen={props.productConfirmation}
        onRequestClose={closeModal} 
        className="modal confirmation-modal"
        overlayClassName="modal-overlay center"
        >
          <div><h2 class="h-s p-t-xxs">{props.messsageTitle}</h2>
            <p>{props.messageBody}</p>
          </div>
          <button className="button button--primary" onClick={props.handleButtonClick}>{props.messageButtonText}</button>
      </ReactModal>
    </span>
  )
}

export default MessageConfirmation;
