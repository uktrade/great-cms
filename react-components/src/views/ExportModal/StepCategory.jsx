/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import Field from '@src/components/Field'
import SocialLoginButtons from '@src/components/SocialLoginButtons'


export default function StepCategory(props){

  function handleChange(value) {
    props.handleChange(value)
    props.handleSubmit()
  }

  return (
    <div className='great-mvp-export-wizard-step-category'>
      <h2 className="h-m">What are you looking to export?</h2>
      <Field
        type="radio"
        name="category"
        disabled={props.disabled}
        value={props.value}
        handleChange={handleChange}
        autofocus={true}
        errors={props.errors.category || []}
        options={[
          {value: 'products', label: 'products', disabled: false},  
          {value: 'services', label: 'services', disabled: true},
          {value: 'products-and-services', label: 'products and services', disabled: true},
        ]}
      />
    </div>
  )
}

StepCategory.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.string,
}

StepCategory.defaultProps = {
  disabled: false,
  errors: {},
  value: [],
}
