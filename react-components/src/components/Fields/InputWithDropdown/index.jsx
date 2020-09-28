import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { Input } from '@src/components/Form/Input'

export const InputWithDropdown = ({
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
    <div className=''>
      <div className=''>
        <Input
          label={label}
          id={label}
          name={label}
          readOnly
          value={input}
          placeholder='Select Option'
          description={description}
          tooltip={tooltip}
          example={example}
        />
        <div className='dropdown'>
          <button aria-haspopup='listbox' onClick={() => setIsOpen(!isOpen)}>^</button>
          { isOpen &&
          <ul role='listbox'>
            {options.map((item) =>
              <li
                key={item}
                onClick={() => selectOption(item)}
                aria-selected={item.label === input}
                role='option'
              >{item.label}</li>
            )}
          </ul>
          }
        </div>
      </div>
    </div>
  )
}

InputWithDropdown.propTypes = {
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

InputWithDropdown.defaultProps = {
  selected: '',
  description: '',
  tooltip: '',
  example: ''
}
