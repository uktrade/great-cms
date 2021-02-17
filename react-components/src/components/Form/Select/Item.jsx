import React, { memo } from 'react'
import PropTypes from 'prop-types'

export const Item = memo(
  ({ onClick, onKeyDown, selected, label, forwardedRef, isDisabled }) => (
    <li
      tabIndex="0"
      role="option"
      className={`select__list--item ${isDisabled ? 'text-black-50' : ''}`}
      onClick={onClick}
      onKeyDown={onKeyDown}
      aria-selected={selected}
      ref={forwardedRef}
    >
      {label}
    </li>
  )
)

Item.propTypes = {
  onClick: PropTypes.func.isRequired,
  onKeyDown: PropTypes.func.isRequired,
  selected: PropTypes.bool.isRequired,
  label: PropTypes.string.isRequired,
  forwardedRef: PropTypes.elementType.isRequired,
  isDisabled: PropTypes.bool,
}

Item.defaultProps = {
  isDisabled: false,
}
