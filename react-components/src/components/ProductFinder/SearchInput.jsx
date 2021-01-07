import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'


export default function SearchInput(props) {
  const { id, onChange, onKeyReturn, autoFocus, defaultValue, placeholder, label, iconClass, maxWidth } = props;
  const [value, setValue] = useState(defaultValue || '')

  let searchInput

  useEffect(() => {
    if(autoFocus && searchInput) {
      searchInput.focus()
    }
  },[searchInput])

  const setInputValue = (newValue) => {
    setValue(newValue)
    onChange(newValue)
  }

  const inputChange = () => {
    setInputValue(searchInput.value)
  }

  const inputKeypress = (evt) => {
    if (evt.key === 'Enter') {
      evt.preventDefault()
      onKeyReturn()
    }
  }

  const clearSearchInput = () => {
    setInputValue('')
    searchInput.focus()
  }

  return (
    <label htmlFor={id}>
      {label && (<div className="m-b-xxs">{label}</div>)}
      <div className="flex-centre search-input">
        <input
          className="form-control"
          type="text"
          id={id}
          ref={(_searchInput) => {searchInput = _searchInput}}
          onKeyPress={inputKeypress}
          onChange={inputChange}
          value={value}
          placeholder={placeholder}
          maxLength={50}
          style={{maxWidth}}
        />
        <div className="input-icon">
          {value.length ? (
            <button 
              type="button" 
              aria-label="Clear" 
              className="fa fa-times clear" 
              onClick={clearSearchInput}
            />
          ) : (
            iconClass && <i className={`fas ${iconClass} text-blue-deep-60`}/>
          )}
        </div>
        <span className="visually-hidden">Search markets </span>
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
}


