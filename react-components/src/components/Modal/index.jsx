import React from 'react'
import PropTypes from 'prop-types'

export const Modal = ({
  type,
  backUrl,
  footer,
  header,
  content,
  onClick,
  buttonText,
}) => {
  return (
    <div className="modal">
      <div
        className={`modal-header ${
          type ? `modal-header-bg modal-header-bg--${type}` : ''
        } radius-top-s bg-blue-deep-80 p-s`}
      >
        <a
          href={backUrl}
          className="link text-white body-m modal-close"
          title="navigate back"
        >
          <i className="fas fa-arrow-circle-left m-r-xxs" /> back
        </a>
      </div>
      <div className="modal-inner text-blue-deep-80 bg-white radius-bottom-s">
        <div className="p-s">
          <h4 className="h-xs p-0">{header}</h4>
          <p className="m-t-xs">{content}</p>
          <button type="button" className="button" onClick={onClick}>
            {buttonText}
          </button>
        </div>
        {footer && (
          <div className="modal-footer">
            <hr className="hr hr--light m-0" />
            <div className="p-h-s p-b-s">
              <h4 className="h-xs p-b-xs">
                Select a market you’ve already researched
              </h4>
              <button
                type="button"
                className="button button--secondary button--icon inline m-r-xs"
              >
                <i className="fas fa-plus-square" />
                <span>United Kingdom</span>
              </button>
              <button
                type="button"
                className="button button--secondary button--icon inline"
              >
                <i className="fas fa-plus-square" />
                <span>United Kingdom</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

Modal.propTypes = {
  type: PropTypes.oneOf(['1', '2', '3', '']),
  backUrl: PropTypes.string.isRequired,
  footer: PropTypes.bool,
  header: PropTypes.string.isRequired,
  content: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
  buttonText: PropTypes.string.isRequired,
}

Modal.defaultProps = {
  type: '',
  footer: false,
}
