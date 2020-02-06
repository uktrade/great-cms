import React from 'react'
import PropTypes from 'prop-types'


const styles = {
  input: {
    width: 371,
    padding: 10,
    borderColor: '#333333',
    height: 51,
    backgroundColor: '#FFFFFF',
  },
}

export default function Field(props){

  function handleChange(event) {
    props.handleChange(event.target.value)
  }

  return (
    <div className="form-group">
      <input
        type={props.type}
        placeholder={props.placeholder}
        name={props.name}
        className="form-control"
        style={styles.input}
        value={props.value}
        onChange={handleChange}
        disabled={props.disabled}
        autoFocus={props.autofocus}
      />
    </div>
  )
}
  

Field.propTypes = {
  type: PropTypes.string.isRequired,
  placeholder: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  handleChange: PropTypes.func.isRequired,
  value: PropTypes.string.isRequired,
  disabled: PropTypes.bool,
  autofocus: PropTypes.bool
}

Field.defaultProps = {
  autofocus: false,
  disabled: false
}
