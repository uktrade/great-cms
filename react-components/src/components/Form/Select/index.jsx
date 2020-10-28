import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Input } from '@src/components/Form/Input'

export const Select = ({
  label,
  update,
  name,
  selected,
  options,
  description,
  tooltip,
  example
}) => {

  const [input, setInput] = useState(selected)
  const [isOpen, setIsOpen] = useState(false)

  const selectOption = (item) => {
    setInput(item.label)
    setIsOpen(false)
    update({ [name]: item.value })
  }

  return (
    <div className='select m-b-l'>
      <Input
        label={label}
        id={label}
        name={label}
        readOnly
        value={input}
        placeholder='Select one'
        description={description}
        tooltip={tooltip}
        example={example}
      />
      <button className={`select__button text-blue-deep-20 ${isOpen ? 'select__button--close' : ''}`} type='button' role='button' aria-haspopup='listbox' onClick={() => setIsOpen(!isOpen)}>
        <i className={`fas ${isOpen ? 'fa-times-circle text-blue-deep-60' : 'fa-sort'}`} />
      </button>
      { isOpen &&
      <ul role='listbox' className='select__list body-l bg-white radius'>
        <li>Select one</li>
        {options.map((item) =>
          <li
            className='select__list--item'
            key={item}
            onClick={() => selectOption(item)}
            aria-selected={item.label === input}
            role='option'
          >{item.label}</li>
        )}
      </ul>
      }
    </div>
  )
}

Select.propTypes = {
  label: PropTypes.string.isRequired,
  update: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
  selected: PropTypes.string,
  options: PropTypes.arrayOf({
    value: PropTypes.string,
    label: PropTypes.string,
  }).isRequired,
  description: PropTypes.string,
  tooltip: PropTypes.string,
  example: PropTypes.string,
}

Select.defaultProps = {
  selected: '',
  description: '',
  tooltip: '',
  example: ''
}
