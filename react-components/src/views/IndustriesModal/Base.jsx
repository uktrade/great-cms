import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { CookiesProvider, useCookies } from 'react-cookie';

import Modal from '@src/components/Modal'
import ErrorList from '@src/components/ErrorList'
import Services from '@src/Services'
import '@src/stylesheets/ModalCentreScreen.scss'

import Form from './Form'

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

export function Base(props){
  const [errors, setErrors] = React.useState(props.errors)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [industries, setIndustries] = React.useState(props.industries)

  function handleIndustriesSubmit() {
    Services.updateCompany({expertise_industries: (industries || []).map(item => item.value)})
      .then(handleIndustriesSubmitSuccess)
      .catch(handleIndustriesSubmitError)
  }

  function handleIndustriesSubmitSuccess(nextStep) {
    setIsInProgress(false)
    setErrors({})
    window.location.assign(`${window.location}?success`)
  }

  function handleIndustriesSubmitError(errors) {
    setErrors(errors.message || errors)
    setIsInProgress(false)
  }

  return (
    <Modal
      isOpen={props.isOpen}
      skipFeatureCookieName='skip-industries-of-interest'
      skipFeatureComponent={SkipShowGenericContent}
      id='dashboard-question-modal-lets-get-to-know-you'
    >
      <ErrorList errors={errors.__all__ || []} className='m-t-s' />
      <Form
        errors={errors}
        disabled={isInProgress}
        handleSubmit={handleIndustriesSubmit}
        handleChange={setIndustries}
        value={industries}
        onSkipButtonClick={props.handleRequestSkipFeature}
      />
    </Modal>
  )
}

Base.propTypes = {
  isOpen: PropTypes.bool,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  industries: PropTypes.array,
}

Base.defaultProps = {
  isOpen: false,
  errors: {},
  isInProgress: false,
  industries: [],
}


export default function createModal({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(<Base {...params} />, element)
}

