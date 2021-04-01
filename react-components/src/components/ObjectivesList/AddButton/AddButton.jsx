import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const AddButton = memo(
  ({ numberOfItems, add, limit, cta, isDisabled }) => (
    <>
      {numberOfItems !== limit && (
        <button
          disabled={isDisabled}
          type="button"
          className="button button--add button--large button--icon"
          onClick={add}
        >
          <i className="fas fa-plus-circle" />
          {cta}
        </button>
      )}
    </>
  )
)

AddButton.propTypes = {
  numberOfItems: PropTypes.number,
  isDisabled: PropTypes.bool.isRequired,
  add: PropTypes.func.isRequired,
  limit: PropTypes.number,
  cta: PropTypes.string,
}

AddButton.defaultProps = {
  numberOfItems: 0,
  limit: 5,
  cta: 'Add',
}
