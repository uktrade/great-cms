import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

export const ConfirmModal = memo(({ deleteItem, hasData }) => {
  const [modal, setModal] = useState(false)

  return (
    <>
      <button
        type="button"
        className="button--only-icon button button--small button--delete button--tertiary m-v-xs"
        onClick={() => {
          if (hasData) {
            setModal(true)
          } else {
            deleteItem()
          }
        }}
      >
        <i className="fas fa-trash-alt" title="delete Objective" />
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
                <i className="fas fa-trash-alt" />
                <span>Yes</span>
              </button>
              <button
                type="button"
                className="button button--secondary inline m-b-s"
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
