import React from 'react'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'

export function MessageConfirmation(props) {

  const { messageTitle, messageBody, handleButtonClick, productConfirmation, messageButtonText } = props
  return (
    <span>
      <ReactModal 
        isOpen={productConfirmation}
        className="modal confirmation-modal"
        overlayClassName="modal-overlay center"
        >
          <div><h2 className="h-s p-t-xxs">{messageTitle}</h2>
            <p>{messageBody}</p>
          </div>
          <button type="button" className="button button--primary" onClick={handleButtonClick}>{messageButtonText}</button>
      </ReactModal>
    </span>
  )
}

MessageConfirmation.propTypes = {
  messageTitle: PropTypes.string.isRequired,
  messageBody: PropTypes.string.isRequired,
  messageButtonText: PropTypes.string.isRequired,
  handleButtonClick: PropTypes.func.isRequired,
  productConfirmation: PropTypes.bool.isRequired, 
}

export default MessageConfirmation;
