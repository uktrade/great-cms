import React, { useState, memo } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

export const ConfirmModal = memo(({ action, hasData }) => {
  const [modal, setModal] = useState(false)

  return (
    <>
      <button
        type="button"
        className="button--only-icon button button--small button--delete bg-white m-v-xs"
        onClick={() => {
          if (hasData) {
            setModal(true)
          } else {
            action()
          }
        }}
      >
        <i className="fas fa-trash-alt" />
      </button>
      <ReactModal
        isOpen={modal}
        className="ReactModal__Content ReactModalCentreScreen"
        overlayClassName="ReactModal__Overlay ReactModalCentreScreen"
        contentLabel="Modal"
      >
        <div className="modal modal--auto">
          <div className="modal-header" />
          <div className="p-s modal-inner text-blue-deep-80 bg-white radius">
            <div className="text-center">
              <h4 className="h-s p-t-0">Are you sure?</h4>
              <p className="body-l"> All data you entered will be deleted</p>
            </div>
            <div className="text-center">
              <button
                type="button"
                className="button button--icon inline m-r-xs"
                onClick={() => {
                  action()
                  setModal(false)
                }}
              >
                <i className="fas fa-trash-alt" />
                <span>Yes</span>
              </button>
              <button
                type="button"
                className="button button--secondary button--icon inline"
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
  action: PropTypes.func.isRequired,
}
