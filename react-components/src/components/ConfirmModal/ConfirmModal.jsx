import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

export const ConfirmModal = memo(({ deleteItem, hasData }) => {
  const [modal, setModal] = useState(false)

  return (
    <>
      <button
        type="button"
        className="secondary-button delete-button"
        onClick={() => {
          if (hasData) {
            setModal(true)
          } else {
            deleteItem()
          }
        }}
      >
        <span role='img' className="fas fa-trash-alt govuk-!-margin-right-2" title="delete Objective" />
        <span>Delete</span>
      </button>
      <ReactModal
        isOpen={modal}
        className="ReactModal__Content ReactModalCentreScreen"
        overlayClassName="ReactModal__Overlay ReactModalCentreScreen"
        contentLabel="Modal"
      >
        <div className="modal w-auto">
          <div className="modal-header" />
          <div className="p-t-s p-h-s modal-inner bg-white">
            <div className="text-center">
              <h4 className="h-s p-t-0">Are you sure?</h4>
              <p className="body-l"> All data you entered will be deleted</p>
            </div>
            <div className="text-center">
              <button
                type="button"
                className="button delete-button primary-button inline m-r-xs m-b-s"
                onClick={() => {
                  deleteItem()
                  setModal(false)
                }}
              >
                <span className="fas fa-trash-alt great-red-text" />
                <span>Yes</span>
              </button>
              <button
                type="button"
                className="button secondary-button inline m-b-s"
                onClick={() => setModal(false)}
              >
                No
              </button>
            </div>
          </div>
        </div>
      </ReactModal>
    </>
  )
})

ConfirmModal.propTypes = {
  hasData: PropTypes.bool.isRequired,
  deleteItem: PropTypes.func.isRequired,
}
