import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'

export const RadiogroupItem = ({
  id,
  group,
  value,
  label,
  update,
  selected,
}) => {
  return (
    <div className="great-radiogroup__item">
      <input
        className="great-radiogroup__input"
        type="radio"
        name={group}
        id={id}
        value={value}
        onChange={() => update(value, group)}
        checked={selected === id}
      />
      <label htmlFor={id} className="great-radiogroup__label">
        {label}
      </label>
    </div>
  )
}

RadiogroupItem.defaultProps = {}
