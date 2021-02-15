import React, { memo, useState } from 'react'
// import PropTypes from 'prop-types'
import { RadiogroupItem } from './RadiogroupItem'

export const Radiogroup = ({ radioList, className, type, buttonType }) => {
  const [selected, setSelected] = useState(radioList.selectedId || null)
  const [radioState, setRadioState] = useState(radioList)

  const handleOnChange = (id) => {
    setSelected(id)
    setRadioState({ ...radioState, selectedId: selected })
  }

  return (
    <>
      <h3 className="form-label">{radioList.label}</h3>
      <radiogroup
        className={`
          great-radiogroup 
          ${type === 'button' ? 'great-radiogroup--button' : ''}
          ${buttonType === 'temperature' ? 'great-radiogroup--temperature' : ''}
          ${className}
        `}
      >
        {radioState.options.map((item) => {
          return (
            <RadiogroupItem
              key={item.pk}
              id={item.pk}
              group={item.group}
              value={item.value}
              label={item.label}
              selected={selected}
              onChange={handleOnChange}
            />
          )
        })}
      </radiogroup>
    </>
  )
}

Radiogroup.defaultProps = {
  className: 'm-b-xs',
  type: 'button',
  buttonType: 'temperature',
}
