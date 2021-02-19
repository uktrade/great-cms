import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import { RadiogroupItem } from './RadiogroupItem'

export const Radiogroup = ({
  options,
  selected,
  label,
  hideLabel,
  groupName,
  className,
  type,
  buttonType,
  update,
  id,
}) => {
  const [selectedOption, setSelectedOption] = useState(selected || null)

  const handleUpdate = (value, groupName) => {
    setSelectedOption(value)
    update({ value, groupName })
  }

  return (
    <>
      {!hideLabel && <h3 className="form-label">{label}</h3>}
      <div
        className={`
          great-radiogroup 
          ${type === 'button' ? 'great-radiogroup--button' : ''}
          ${buttonType === 'temperature' ? 'great-radiogroup--temperature' : ''}
          ${className}
        `}
      >
        {options.map(({ value, label }) => {
          return (
            <RadiogroupItem
              key={value}
              id={`${id}_${groupName}_${value}`}
              group={`${id}_${groupName}`}
              value={value}
              label={label}
              selected={selectedOption}
              update={(value, groupName) => handleUpdate(value, groupName)}
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
  buttonType: '',
  label: null,
}
