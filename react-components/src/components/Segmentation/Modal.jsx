import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

export default function Modal(props) {
  const { format,
    title,
    body,
    primaryButtonLabel,
    primaryButtonClick ,
    primaryButtonDisable,
    secondaryButtonLabel,
    secondaryButtonClick,
    closeClick,
    progressPercentage
  } = props

  return (
    <ReactModal
      isOpen={true}
      onRequestClose={closeClick}
      className="segmentation-modal modal p-v-xs p-h-s"
      overlayClassName="modal-overlay center"
      shouldCloseOnOverlayClick={false}
    >
      { closeClick &&
        <button
          id="dialog-close"
          type="button"
          aria-label="Close"
          className="pull-right m-r-0 dialog-close"
          onClick={closeClick}
        />
      }
      <div className="c-fullwidth">
        <h3 className="h-s">{title}</h3>
        <div className="body-l m-b-xs text-blue-deep-60">
        {body}
        </div>
          <div
            style={{
              display: 'flex',
              flexFlow: 'row nowrap',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
          { progressPercentage != null ? (
            <div style={{ flex: '4 0' }}>
              <div className="progress-bar m-r-m">
                <span style={{ width: `${progressPercentage}%` }}></span>
              </div>
            </div>
            ) : '' }
          { secondaryButtonClick ? (
              <button
                type="button"
                className="button button--tertiary m-v-xs m-f-xxs"
                onClick={secondaryButtonClick }
              >
                {secondaryButtonLabel || 'Exit'}
              </button>
            ) : (
              ''
            )}
            { primaryButtonClick ? (
            <button
              type="button"
              className="button button--primary m-v-xs m-f-xxs"
              disabled={primaryButtonDisable}
              onClick={primaryButtonClick}
            >
              {primaryButtonLabel || 'Continue'}
            </button>
            ) : ''}
          </div>
      </div>
    </ReactModal>
  )
}

Modal.propTypes = {
  primaryButtonDisable: PropTypes.bool,
  progressPercentage: PropTypes.number,
}
Modal.defaultProps= {
  primaryButtonDisable: false,
  progressPercentage: null
}
