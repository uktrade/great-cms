/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import Modal from '@src/components/Modal'
import Services from '@src/Services'
import StepCategory from './StepCategory'
import StepProducts from '@src/components/ProductLookup'
import StepSuccess from './StepSuccess'

import './stylesheets/Modal.scss'

export const STEP_CATEGORY = 'category'
export const STEP_PRODUCTS = 'products'
export const STEP_SUCCESS = 'success'


export default function Wizard(props){
  const isLastStep = props.currentStep == STEP_SUCCESS

  function getStep() {
    if (props.currentStep == STEP_CATEGORY) {
      return (
        <StepCategory
          errors={props.errors}
          disabled={props.isInProgress}
          handleChange={props.handleCategoryChange}
          value={props.category}
        />
      )
    } else if (props.currentStep == STEP_PRODUCTS) {
      return (
        <StepProducts
          errors={props.errors}
          disabled={props.isInProgress}
          handleChange={props.setProducts}
          handleSubmit={props.handleProductsSubmit}
          value={props.products}
        />
      )
    } else if (props.currentStep == STEP_SUCCESS) {
      return (
        <StepSuccess
          handleComplete={props.handleComplete}
          handleSignup={props.handleSignup}
          products={props.products}
        />
      )
    }
  }

  function SkipShowGenericContent(innerProps) {
    const children = []
    if (isLastStep) {
      children.push(
        <a
          key='change-answers'
          href='#'
          className='great-mvp-wizard-step-link'
          onClick={event => { event.preventDefault(); props.handleChangeAnswers() }}
        >Change answers</a>
      )
    } else if (!Services.config.userIsAuthenticated) {
      children.push(
        <a
          key='show-generic-content'
          href='#'
          className='great-mvp-wizard-step-link'
          onClick={event => { event.preventDefault(); innerProps.onClick() }}
        >No thanks I would like generic content</a>
      )
    }
    if (children.length > 0) {
      return (
        <div className="grid">
          <div className="c-1-3">&nbsp;</div>
          <div className="c-2-3">
            <p className="m-t-xxs">{children}</p>
          </div>
        </div>
      )
    }
    return null
  }
  return (
    <Modal
      isOpen={props.isOpen}
      setIsOpen={props.setIsOpen}
      id='dashboard-question-modal-export'
      skipFeatureCookieName='skip-export'
      skipFeatureComponent={SkipShowGenericContent}
      performSkipFeatureCookieCheck={props.performSkipFeatureCookieCheck}
      className='ReactModal__Content--Export p-v-s p-r-s'
    >
      <div className="grid">
        <aside className="c-1-3">
          <img src='/static/images/book-chap.png' className="book-chap-image" />
        </aside>
        <div className="c-2-3">
          {getStep()}
        </div>
      </div>
    </Modal>
  )

}

Wizard.propTypes = {
  isOpen: PropTypes.string.isRequired,
  setIsOpen: PropTypes.func.isRequired,
  onComplete: PropTypes.func,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  category: PropTypes.string,
  currentStep: PropTypes.string,
  performSkipFeatureCookieCheck: PropTypes.bool,
}

Wizard.defaultProps = {
  errors: {},
  isInProgress: false,
  category: '',
  onComplete: () => {},
  currentStep: STEP_CATEGORY,
  performSkipFeatureCookieCheck: true,
}
