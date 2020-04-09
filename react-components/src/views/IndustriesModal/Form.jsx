/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import Services from '@src/Services'
import AutoCompleteField from '@src/components/AutoCompleteField'

import '@src/stylesheets/_WizardStep.scss'


export default function Form(props){
  return (
    <div className='grid-flex'>
      <div className='c-1-3'>
        <img src='/static/images/book-chap.png' width='150' />
      </div>
      <div className='c-2-3'>
        <h2 className='h-m'>What sectors are you interested in?</h2>
        <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
          <AutoCompleteField
            placeholder='Start typing and select an industry'
            options={Services.config.industryOptions}
            name='expertise_industries'
            disabled={props.disabled}
            value={props.value}
            handleChange={props.handleChange}
            autoFocus={true}
            errors={props.errors.expertise_industries || []}
          />
          <input
            type='submit'
            value='Save'
            id='dashboard-question-modal-submit'
            className='great-mvp-wizard-step-button m-v-s'
            disabled={props.disabled}
          />
        </form>
      </div>
    </div>
  )
}

Form.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.array,
}

Form.defaultProps = {
  disabled: false,
  errors: {},
  password: '',
  value: [],
}
