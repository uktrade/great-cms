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
}) => {
  const [selectedOption, setSelectedOption] = useState(selected || null)

  const handleOnChange = (id) => {
    setSelectedOption(id)
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
        {options.map(({ value }) => {
          return (
            <RadiogroupItem
              key={value}
              id={value}
              group={groupName}
              value={value}
              label={value.charAt(0).toUpperCase() + value.slice(1)}
              selected={selectedOption}
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
  label: null,
}
