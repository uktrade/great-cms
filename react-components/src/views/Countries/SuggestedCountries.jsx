/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import AutoCompleteField, { OptionWithFlag } from '@src/components/AutoCompleteField'


export default function SuggestedCountries(props){

  function handleClick(event) {
    const value = event.target.value
    const label = event.target.innerHTML
    props.handleClick([{value, label}])
  }

  const industries = props.industries.map((item, i) => <b key={i}>{item.label}</b>)
  const countries = props.suggestedCountries.map((item, i) => (
    <button
      key={i}
      type='submit'
      className='great-mvp-pill-button'
      onClick={handleClick}
      value={item.value}
      disabled={props.disabled}
    >{item.label}
    </button>
  ))
  return (
    <div className='m-b-m great-mvp-suggested-countries'>
      <p>Based on your sector {industries} we think you might be interested in the following markets:</p>
      {countries}
    </div>
  )
}

SuggestedCountries.propTypes = {
  industries: PropTypes.array.isRequired,
  suggestedCountries: PropTypes.array.isRequired,
}
