/* eslint-disable jsx-a11y/no-noninteractive-element-interactions */
import React, { memo, useState, useEffect } from 'react'
import PropTypes from 'prop-types'

export const RadiogroupItem = memo(
  ({ id, group, value, label, update, selected }) => {
    return (
      <div
        className="great-radiogroup__item"
        role="radio"
        aria-checked={selected === value}
      >
        <input
          className="great-radiogroup__input"
          type="radio"
          name={group}
          id={id}
          value={value}
          onChange={() => update(value, group)}
          checked={selected === value}
        />
        <label
          htmlFor={id}
          className="great-radiogroup__label"
          tabIndex="0"
          onKeyUp={(e) => (e.key === 'Enter' ? update(value, group) : null)}
        >
          {label}
        </label>
      </div>
    )
  }
)

RadiogroupItem.protTypes = {
  id: PropTypes.string.isRequired,
  group: PropTypes.string.isRequired,
  value: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  update: PropTypes.func.isRequired,
  selected: PropTypes.string.isRequired,
}
