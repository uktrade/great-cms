/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import AutoCompleteField from '@src/components/AutoCompleteField'

import { components } from 'react-select'


function FormattedOption(props) {
  return (
    <components.Option {...props}>
      <div>{props.data.label}</div>
      <div>{props.data.value}</div>
    </components.Option>
  )
}

const loadOptions = (inputValue, callback) => Services.lookupProduct({q: inputValue}).then(callback)

export default function ProductLookup(props){
  return (
    <div className='m-b-m'>
      <h2 className='h-m'>What is your product?</h2>
      <p>(We call them commodities)</p>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <AutoCompleteField
          autoFocus={true}
          loadOptions={loadOptions}
          disabled={props.disabled}
          errors={props.errors.products || []}
          handleChange={props.handleChange}
          name='products'
          value={props.value}
          components={{Option: FormattedOption}}
          placeholder='Start typing and select a product'
        />
        <input
          type='submit'
          value='Save and continue'
          className='great-mvp-wizard-step-button m-t-l'
          disabled={props.disabled}
          style={{'visibility': props.value.length > 0 ? 'visible' : 'hidden'}}
        />
      </form>
    </div>
  )
}

ProductLookup.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.array,
}

ProductLookup.defaultProps = {
  disabled: false,
  errors: {},
  value: [],
}
