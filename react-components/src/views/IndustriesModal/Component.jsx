/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import AutoCompleteField from '@src/components/AutoCompleteField'
import Modal from '@src/components/Modal'
import ErrorList from '@src/components/ErrorList'

import '@src/stylesheets/_WizardStep.scss'

export function SkipShowGenericContent(props) {
  return (
    <div className='grid'>
      <div className='c-1-3'>&nbsp;</div>
      <div className='c-2-3'>
        <a
          href='#'
          className='great-mvp-wizard-step-link'
          onClick={event => { event.preventDefault(); props.onClick() }}
        >No thanks, I would like generic content</a>
      </div>
    </div>
  )
}

export default function Component(props){
  return (
    <Modal
      isOpen={props.isOpen}
      skipFeatureCookieName='skip-industries-of-interest'
      skipFeatureComponent={SkipShowGenericContent}
      id='dashboard-question-modal-lets-get-to-know-you'
      className='p-s'
    >
      <ErrorList errors={props.errors.__all__ || []} className='m-t-s' />
      <div className='grid-flex'>
        <div className='c-1-3'>
          <img src='/static/images/book-chap.png' width='150' />
        </div>
        <div className='c-2-3'>
          <h2 className='h-m'>What sectors are you interested in?</h2>
          <form onSubmit={event => {event.preventDefault(); props.handleSubmit() }}>
            <AutoCompleteField
              placeholder='Start typing and select an industry'
              options={props.industryOptions}
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
    </Modal>
  )
}

Component.propTypes = {
  disabled: PropTypes.bool,
  errors: PropTypes.object,
  handleChange: PropTypes.func.isRequired,
  handleSubmit: PropTypes.func.isRequired,
  value: PropTypes.array,
}

Component.defaultProps = {
  disabled: false,
  errors: {},
  password: '',
  value: [],
}
