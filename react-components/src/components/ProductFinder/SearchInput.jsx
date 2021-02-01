import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

export default function SearchInput(props) {
  const {
    id,
    onChange,
    onKeyReturn,
    autoFocus,
    defaultValue,
    placeholder,
    label,
    iconClass,
    maxWidth,
    validator,
  } = props
  const [value, setValue] = useState(defaultValue || '')
  const [isFocussed, setFocussed] = useState(false)

  let searchInput
  let inputWrapper

  const checkFocussed = (_inputWrapper) => {
    const activeEl = document.activeElement
    setFocussed(activeEl && activeEl.closest('.search-input') === _inputWrapper)
  }

  useEffect(() => {
    if (autoFocus && searchInput) {
      searchInput.focus()
    }
  }, [searchInput])

  useEffect(() => {
    checkFocussed(inputWrapper)
    const cf = () => {
      checkFocussed(inputWrapper)
    }
    window.addEventListener('focusin', cf)
    return () => {
      window.removeEventListener('focusin', cf)
    }
  })

  const setInputValue = (newValue) => {
    setValue(newValue)
    onChange(newValue)
  }

  const inputChange = () => {
    if (validator(searchInput.value)) {
      setInputValue(searchInput.value)
    }
  }

  const inputKeypress = (evt) => {
    if (evt.key === 'Enter') {
      evt.preventDefault()
      onKeyReturn()
    }
  }

  const clearSearchInput = () => {
    if (isFocussed) {
      setInputValue('')
      searchInput.focus()
    }
  }

  return (
    <label className="width-full" htmlFor={id}>
      {label && <div className="m-b-xxs">{label}</div>}
      <div
        className="flex-centre search-input"
        ref={(el) => {
          inputWrapper = el
        }}
      >
        <input
          className="form-control"
          type="text"
          id={id}
          ref={(_searchInput) => {
            searchInput = _searchInput
          }}
          onKeyPress={inputKeypress}
          onChange={inputChange}
          value={value}
          placeholder={placeholder}
          maxLength={50}
          style={{ maxWidth }}
        />
        <div className="input-icon">
          {isFocussed && value.length ? (
            <button
              type="button"
              aria-label="Clear"
              className="fa fa-times clear"
              onClick={clearSearchInput}
            />
          ) : (
            iconClass && <i className={`fas ${iconClass} text-blue-deep-60`} />
          )}
        </div>
        <span className="visually-hidden">Search markets</span>
      </div>
    </label>
  )
}

SearchInput.propTypes = {
  id: PropTypes.string,
  onChange: PropTypes.func.isRequired,
  onKeyReturn: PropTypes.func,
  autoFocus: PropTypes.bool,
  defaultValue: PropTypes.string,
  placeholder: PropTypes.string,
  label: PropTypes.string,
  iconClass: PropTypes.string,
  maxWidth: PropTypes.string,
  validator: PropTypes.func,
}
SearchInput.defaultProps = {
  id: 'search-input',
  onKeyReturn: () => {},
  autoFocus: false,
  defaultValue: '',
  placeholder: null,
  label: '',
  iconClass: '',
  maxWidth: '200em',
  validator: () => true,
}
