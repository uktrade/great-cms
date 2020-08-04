import React, { useState } from 'react'
import PropTypes from 'prop-types'

export const InputWithDropdown = ({
  label,
  update,
  name,
  selected,
  options
}) => {

  const [input, setInput] = useState(selected)
  const [isOpen, setIsOpen] = useState(false)

  const selectOption = (item) => {
    setInput(item)
    setIsOpen(false)
    update({ [name]: item })
  }

  return (
    <div className='route-to-market__table-cell'>
      <label htmlFor={label}>{label}</label>
      <div className='route-to-market__input'>
        <input
          id={label}
          name={label}
          readOnly
          value={input}
          placeholder='Select Option'
        />
        <div className='dropdown'>
          <button aria-haspopup='listbox' onClick={() => setIsOpen(!isOpen)}>^</button>
          { isOpen &&
          <ul role='listbox'>
            {options.map((item) =>
              <li
                key={item}
                onClick={() => selectOption(item)}
                aria-selected={item === input}
                role='option'
              >{item}</li>
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
  options: PropTypes.arrayOf(PropTypes.string).isRequired
}

InputWithDropdown.defaultProps = {
  selected: ''
}
