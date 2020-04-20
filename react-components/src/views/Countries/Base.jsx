import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import Services from '@src/Services'
import SuggestedCountries from './SuggestedCountries'
import ErrorList from '@src/components/ErrorList'
import Form from './Form'

import './stylesheets/Base.scss'


export function Base(props){

  const [countries, setCountries] = React.useState(Services.config.userCountries || [])
  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)

  function handleSubmit() {
    setIsInProgress(true)
    setErrors({})
    Services.updateCompany({expertise_countries: countries.map(item => item.value)})
      .then(handleSubmitSuccess)
      .catch(handleSubmitError)
  }
  function handleSubmitSuccess(nextStep) {
    location.reload()
  }

  function handleSubmitError(errors) {
    setErrors(errors.message || errors)
    setIsInProgress(false)
  }


  return (
    <div className="great-mvp-countries container p-v-m">
      <div className="grid">
      <div className="c-1-5">&nbsp;</div>
        <div className="c-2-3 p-f-0">
          <ErrorList errors={errors.__all__ || []} className='m-t-s' />
          <Form
            options={Services.config.countryOptions}
            handleSubmit={handleSubmit}
            handleChange={setCountries}
            value={countries}
            isInProgress={isInProgress}
            errors={errors}
          />
          {
            props.suggestedCountries.length > 0 && <SuggestedCountries
              suggestedCountries={props.suggestedCountries}
              countries={countries}
              industries={Services.config.userIndustries}
              handleClick={setCountries}
              disabled={isInProgress}
            />
          }
        </div>
      </div>
    </div>
  )
}

Base.propTypes = {
  suggestedCountries: PropTypes.array.isRequired,
  errors: PropTypes.object,
}

Base.defaultProps = {
  errors: {}
}


export default function({ element, ...params }) {
  ReactDOM.render(<Base {...params} />, element)
}

