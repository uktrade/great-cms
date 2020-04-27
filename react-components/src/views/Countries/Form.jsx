/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import AutoCompleteField, { OptionWithFlag } from '@src/components/AutoCompleteField'

import ErrorList from '@src/components/ErrorList'


export default function Form(props){
  return (
    <>
      <h2 className='h-m p-t-0'>Which markets do you have in mind?</h2>
      <form className='grid' onSubmit={event => {event.preventDefault(); props.handleSubmit()}}>
        <div className='c-2-3'>
          <AutoCompleteField
            autoFocus={true}
            errors={props.errors.expertise_countries || []}
            options={props.options}
            handleChange={props.handleChange}
            name='expertise_countries'
            value={props.value}
            components={{Option: OptionWithFlag}}
            placeholder={props.suggestedCountries ? 'Start typing or select recommented markets' : 'Start typing and select a market'}
            isDisabled={props.isInProgress}
            isLoading={props.isInProgress}
          />
        </div>
        <div className='c-1-3'>
          <input
            type='submit'
            value='Save'
            className='great-mvp-wizard-step-button'
            disabled={props.disabled}
            style={{'visibility': props.isInProgress || (props.value.length === 0) ? 'hidden' : 'visible'}}
          />
        </div>
      </form>
    </>
  )
}

Form.propTypes = {
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.array,
}

Form.defaultProps = {
  isInProgress: false,
  errors: {},
  value: [],
}
