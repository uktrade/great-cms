import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import Services from '@src/Services'
import SuggestedCountries from './SuggestedCountries'
import ErrorList from '@src/components/ErrorList'
import Form from './Form'

import './stylesheets/Base.scss'


export default function Components(props){
  return (
    <div className="great-mvp-countries container p-v-m">
      <div className="grid">
      <div className="c-1-5">&nbsp;</div>
        <div className="c-2-3 p-f-0">
          <ErrorList errors={props.errors.__all__ || []} className='m-t-s' />
          <Form
            options={Services.config.countryOptions}
            handleSubmit={props.handleSubmit}
            handleChange={props.setCountries}
            value={props.countries}
            isInProgress={props.isInProgress}
            errors={props.errors}
          />
          {
            props.suggestedCountries.length > 0 && <SuggestedCountries
              suggestedCountries={props.suggestedCountries}
              countries={props.countries}
              industries={Services.config.userIndustries}
              handleClick={props.setCountries}
              disabled={props.isInProgress}
            />
          }
        </div>
      </div>
    </div>
  )
}

Components.propTypes = {
  suggestedCountries: PropTypes.array.isRequired,
  errors: PropTypes.object,
}

Components.defaultProps = {
  errors: {}
}

