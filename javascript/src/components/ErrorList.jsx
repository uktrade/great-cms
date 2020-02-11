import React from 'react'
import PropTypes from 'prop-types'

import '../stylesheets/ErrorList.scss'


export default function ErrorList(props){
  if (Object.entries(props.errors).length === 0) {
    return null
  }

  let errors = []
  for (let key in props.errors){
    for (let i in props.errors[key]) {
      const error = props.errors[key][i]
      const prefix = key === '__all__' ? '' : `${key}: ` 
      errors.push(<li key={i}>{prefix}{error}</li>)
    }
  }

  return (
    <div className="form-group-error great-mvp-error-list">
      <ul className="errorlist">{errors}</ul>
    </div>
  )
}
  

ErrorList.propTypes = {
  errors: PropTypes.object.isRequired,
}
