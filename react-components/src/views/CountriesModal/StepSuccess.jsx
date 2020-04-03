import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import AutoCompleteField from '@src/components/AutoCompleteField'

import './stylesheets/Step.scss'

import Select, { components } from 'react-select'
import FlagIcon from '@src/components/FlagIcon'



export default function StepSuccess(props){
  const countries = props.countries.map((item, i) => <span key={i} className='great-mvp-pill-button'>{item.label}</span>)
  const industries = props.industries.map((item, i) => <span key={i} className='great-mvp-pill-button'>{item.label}</span>)
  return (
    <div className='great-mvp-wizard-step'>
      <div className='grid-flex'>
        <div className='c-1-3'>
          <img src='/static/images/book-chap.png' width='150' />
        </div>
        <div className='c-2-3 m-b-s'>
          <h2 className='h-m p-t-0'>Complete</h2>
          <p>Your relevant opportunities and events in {industries} and {countries} are ready.</p>
          <a className='great-mvp-wizard-step-button m-t-l' href={props.successUrl}>Let's go</a>
          <div className='m-t-s'>
            <a href='#' className='great-mvp-wizard-step-link' onClick={event => {event.preventDefault(); props.handleChangeAnswers()} }>Change answers</a>
          </div>
        </div>
      </div>
    </div>
  )
}

StepSuccess.propTypes = {
  countries:  PropTypes.array,
  industries: PropTypes.array,
}
