import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import { RadiogroupItem } from './RadiogroupItem'

export const Radiogroup = ({ radiogroup, className, type, buttonType }) => {
  const [selected, setSelected] = useState(radiogroup.selected || null)
  const [radioState, setRadioState] = useState(radiogroup)

  const handleOnChange = (id) => {
    setSelected(id)
    setRadioState({ ...radioState, selected })
  }

  return (
    <>
      <h3 className="form-label">{radiogroup.label}</h3>
      <div
        className={`
          great-radiogroup 
          ${type === 'button' ? 'great-radiogroup--button' : ''}
          ${buttonType === 'temperature' ? 'great-radiogroup--temperature' : ''}
          ${className}
        `}
      >
        {radioState.options.map(({ value }) => {
          return (
            <RadiogroupItem
              key={value}
              id={value}
              group={radiogroup.field}
              value={value}
              label={value.charAt(0).toUpperCase() + value.slice(1)}
              selected={selected}
              onChange={handleOnChange}
            />
          )
        })}
      </div>
    </>
  )
}

Radiogroup.defaultProps = {
  className: 'm-b-xs',
  type: 'button',
  buttonType: 'temperature',
}
