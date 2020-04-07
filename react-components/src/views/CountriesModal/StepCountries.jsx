/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import AutoCompleteField from '@src/components/AutoCompleteField'
import './stylesheets/Step.scss'
import FlagIcon from '@src/components/FlagIcon'


function OptionWithFlag(props) {
  return (
    <components.Option {...props}>
      <FlagIcon code={props.data.value.toLowerCase()} />
      <span style={{paddingLeft: 10}}>{props.data.label} ({props.data.value})</span>
    </components.Option>
  )
}


export default function StepCountries(props){
  return (
    <div className='m-b-m'>
      <h2 className='h-m'>Where do you want to export?</h2>
      <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
        <AutoCompleteField
          autoFocus={true}
          options={Services.config.countryOptions}
          disabled={props.disabled}
          errors={props.errors.expertise_countries || []}
          handleChange={props.handleChange}
          name='expertise_countries'
          value={props.value}
          components={{Option: OptionWithFlag}}
          placeholder='Start typing and select a country'
        />
        <input
          type='submit'
          value='Continue'
          className='great-mvp-wizard-step-button m-t-l'
          disabled={props.disabled}
          style={{'visibility': props.value.length > 0 ? 'visible' : 'hidden'}}
        />
      </form>
    </div>
  )
}

StepCountries.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.array,
}

StepCountries.defaultProps = {
  disabled: false,
  errors: {},
  value: [],
}
