import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const AddButton = memo(
  ({ numberOfItems, add, limit, cta, isDisabled, btnClass }) => (
    <>
      {numberOfItems !== limit && (
        <button
          disabled={isDisabled}
          type="button"
          className={`button primary-button button--icon ${btnClass}`}
          onClick={add}
        >
          <span role="img" className="fas fa-plus govuk-!-margin-right-2" />
          {cta}
        </button>
      )}
    </>
  )
)

AddButton.propTypes = {
  numberOfItems: PropTypes.number,
  isDisabled: PropTypes.bool,
  add: PropTypes.func.isRequired,
  limit: PropTypes.number,
  cta: PropTypes.string,
  btnClass: PropTypes.string,
}

AddButton.defaultProps = {
  numberOfItems: 0,
  isDisabled: false,
  limit: 5,
  cta: 'Add',
  btnClass: 'button--add button--large',
}
