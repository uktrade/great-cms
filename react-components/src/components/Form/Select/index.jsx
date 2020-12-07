import React, { useState, useRef } from 'react'
import PropTypes from 'prop-types'
import { Input } from '@src/components/Form/Input'
import { useOnOutsideClick } from '@src/components/hooks/useOnOutsideClick'
import { useNoScroll } from '@src/components/hooks/useNoScroll'

const ENTER_KEY_CODE = 13
const DOWN_ARROW_KEY_CODE = 40
const UP_ARROW_KEY_CODE = 38
const ESCAPE_KEY_CODE = 27

export const Select = ({
  label,
  update,
  name,
  selected,
  options,
  description,
  tooltip,
  example,
  hideLabel,
  placeholder
}) => {

  const [input, setInput] = useState(selected)
  const [isOpen, setIsOpen] = useState(false)
  const liRef = useRef([]);
  const [element] = useOnOutsideClick(() => setIsOpen(false))
  useNoScroll(isOpen)

  const selectOption = (item) => {
    setInput(item.label)
    setIsOpen(false)
    update({ [name]: item.value })
  }

  const focusNext = (e, i, item) => {
    const next = i+1
    const prev = i-1

    switch (e.keyCode) {
      case ENTER_KEY_CODE:
        selectOption(item)
        break
      case DOWN_ARROW_KEY_CODE:
        if (next < liRef.current.length) liRef.current[next].focus()
        break
      case UP_ARROW_KEY_CODE:
        if (prev >= 0) liRef.current[prev].focus()
        break
      case ESCAPE_KEY_CODE:
        setIsOpen(false)
        break
      default:
        break
    }
  }

  const toggle = (e) => {
    switch (e.keyCode) {
      case DOWN_ARROW_KEY_CODE:
        setIsOpen(true)
        liRef.current[0].focus()
        break
      case ESCAPE_KEY_CODE:
        setIsOpen(false)
        break
      default:
        break
    }
  }

  return (
    <div className='select m-b-l'>
      <Input
        label={label}
        id={label}
        name={label}
        readOnly
        value={input}
        placeholder={placeholder}
        description={description}
        tooltip={tooltip}
        example={example}
        tabIndex='-1'
        hideLabel={hideLabel}
        onChange={() => {}}
      />
      <button
        className={`select__button text-blue-deep-20 button--toggle ${isOpen ? 'select__button--close' : ''}`}
        type='button'
        role='button'
        aria-haspopup='listbox'
        onClick={() => setIsOpen(!isOpen)}
        tabIndex='0'
        onKeyDown={toggle}
      >
        <i className={`fas button--toggle ${isOpen ? 'fa-times-circle text-blue-deep-60' : 'fa-sort'}`} />
      </button>
      <ul role='listbox' className={`select__list body-l bg-white radius ${isOpen ? '' : 'hidden'}`} aria-expanded={isOpen} ref={element}>
        <li>{placeholder}</li>
        {options.map((item, i) =>
          <li
            tabIndex='0'
            className='select__list--item'
            key={item.label}
            onClick={() => selectOption(item)}
            onKeyDown={(e) => focusNext(e, i, item)}
            aria-selected={item.label === input}
            role='option'
            ref={el => liRef.current[i] = el}
          >{item.label}</li>
        )}
      </ul>
    </div>
  )
}

Select.propTypes = {
  label: PropTypes.string.isRequired,
  update: PropTypes.func.isRequired,
  name: PropTypes.string.isRequired,
  selected: PropTypes.string,
  options: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string,
      label: PropTypes.string,
    })
  ).isRequired,
  description: PropTypes.string,
  tooltip: PropTypes.string,
  example: PropTypes.string,
  hideLabel: PropTypes.bool,
  placeholder: PropTypes.string,
}

Select.defaultProps = {
  selected: '',
  description: '',
  tooltip: '',
  example: '',
  hideLabel: false,
  placeholder: 'Select one'
}
