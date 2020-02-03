import React from 'react'
import PropTypes from 'prop-types'


const styles = {
  errors: {
    textAlign: 'left',
    marginBottom: 30,
  }
}

export default function ErrorList(props){
  return (
    <div className="form-group-error">
      <ul className="errorlist">
        <li style={styles.errors}>{props.message}</li>
      </ul>
    </div>
  )
}
  

ErrorList.propTypes = {
  message: PropTypes.string.isRequired,
}
