import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'


export default function SearchInput(props) {
  const { onChange, onKeyReturn, autoFocus } = props;
  const [value, setValue] = useState('')

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
    <div className="flex-centre search-input">
      <input
        className="form-control"
        type="text"
        ref={(_searchInput) => {searchInput = _searchInput}}
        onKeyPress={inputKeypress}
        onChange={inputChange}
        value={value}
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
          <i className="fas fa-search text-blue-deep-60"/> 
        )}
      </div>
      <span className="visually-hidden">Search markets </span>   
    </div>
  )
}

SearchInput.propTypes = {
  onChange: PropTypes.func.isRequired,
  onKeyReturn: PropTypes.func,
  autoFocus: PropTypes.bool,
}
SearchInput.defaultProps = {
  onKeyReturn: () => {},
  autoFocus: false
}


