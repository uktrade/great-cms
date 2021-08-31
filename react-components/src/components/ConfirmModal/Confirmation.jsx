import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

export const Confirmation = memo(({ title, body, onYes, onNo }) => {
  return (
    <ReactModal
      isOpen={true}
      className="ReactModal__Content ReactModalCentreScreen"
      overlayClassName="ReactModal__Overlay ReactModalCentreScreen"
      contentLabel="Modal"
    >
      <div className="modal" style={{maxWidth:'400px'}}>
        <div className="modal-header" />
        <div className="p-t-s p-h-s modal-inner text-blue-deep-80 bg-white radius">
          <div className="text-center">
            <h4 className="h-xs p-t-0">{title}</h4>
            <p className="body-l"> {body}</p>
          </div>
          <div className="text-center">
            <button
              type="button"
              className="button button--icon inline m-r-xs m-b-s"
              onClick={onYes}
            >
              <i className="fas fa-check" />
              <span>Yes</span>
            </button>
            <button
              type="button"
              className="button button--icon button--tertiary inline m-b-s"
              onClick={onNo}
            >
              <i className="fas fa-times" />
              <span>No</span>
            </button>
          </div>
        </div>
      </div>
    </ReactModal>
  )
})

Confirmation.propTypes = {
  title: PropTypes.string.isRequired,
  body: PropTypes.string,
  onYes: PropTypes.func,
  onNo: PropTypes.func,
}
