import React, { memo, useState } from 'react'
import PropTypes from 'prop-types'
import { RadiogroupItem } from './RadiogroupItem'

export const Radiogroup = memo(
  ({
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
      // Remove `id_` from groupname
      const key = groupName.slice(String(id).length + 1)

      setSelectedOption(value)
      update({ value, key })
    }

    return (
      <>
        {!hideLabel && <p className="form-label m-v-0">{label}</p>}
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
)

Radiogroup.propsTypes = {
  options: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string,
      value: PropTypes.string,
    })
  ).isRequired,
  selected: PropTypes.string.isRequired,
  label: PropTypes.string,
  hideLabel: PropTypes.bool,
  groupName: PropTypes.string.isRequired,
  className: PropTypes.string,
  type: PropTypes.string,
  buttonType: PropTypes.string,
  update: PropTypes.func.isRequired,
  id: PropTypes.number.isRequired,
}

Radiogroup.defaultProps = {
  className: 'm-b-xs',
  type: 'button',
  buttonType: '',
  hideLabel: false,
  label: '',
}
