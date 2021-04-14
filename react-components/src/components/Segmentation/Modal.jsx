import React from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

export default function Modal(props) {
  const {
    format,
    title,
    body,
    primaryButtonLabel,
    primaryButtonClick,
    primaryButtonDisable,
    secondaryButtonLabel,
    secondaryButtonClick,
    closeClick,
    progressPercentage,
  } = props

  return (
    <ReactModal
      isOpen
      onRequestClose={closeClick}
      className="segmentation-modal modal p-v-xs p-h-s"
      overlayClassName="modal-overlay center"
      shouldCloseOnOverlayClick={false}
    >
      {closeClick && (
        <button
          id="dialog-close"
          type="button"
          aria-label="Close"
          className="pull-right m-r-0 dialog-close"
          onClick={closeClick}
        />
      )}
      <div className="c-fullwidth">
        <h3 className="h-s">{title}</h3>
        <div className="modal-body body-l m-b-xs text-blue-deep-60">{body}</div>
        <div className="modal-button-bar"
        >
          {progressPercentage != null ? (
            <div className="progress-section">
              <div className="progress-bar m-r-m">
                <span style={{ width: `${progressPercentage}%` }}/>
              </div>
            </div>
          ) : (
            ''
          )}
          {secondaryButtonClick ? (
            <button
              type="button"
              className="button button--tertiary m-v-xs m-f-xxs"
              onClick={secondaryButtonClick}
            >
              {secondaryButtonLabel || 'Exit'}
            </button>
          ) : (
            ''
          )}
          {primaryButtonClick ? (
            <button
              type="button"
              className="button button--primary m-v-xs m-f-xxs"
              disabled={primaryButtonDisable}
              onClick={primaryButtonClick}
            >
              {primaryButtonLabel || 'Continue'}
            </button>
          ) : (
            ''
          )}
        </div>
      </div>
    </ReactModal>
  )
}

Modal.propTypes = {
  format: PropTypes.string,
  title: PropTypes.string.isRequired,
  body: PropTypes.string,
  primaryButtonLabel: PropTypes.string,
  primaryButtonClick: PropTypes.func,
  primaryButtonDisable: PropTypes.bool,
  secondaryButtonLabel: PropTypes.string,
  secondaryButtonClick: PropTypes.func,
  closeClick: PropTypes.func,
  progressPercentage: PropTypes.number,
}
Modal.defaultProps = {
  format: null,
  body: null,
  primaryButtonLabel: '<Primary>',
  primaryButtonClick: null,
  secondaryButtonLabel: '<Secondary>',
  secondaryButtonClick: null,
  primaryButtonDisable: false,
  closeClick: null,
  progressPercentage: null,
}
