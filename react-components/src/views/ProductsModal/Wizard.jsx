/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import Modal from '@src/components/Modal'
import Services from '@src/Services'
import StepCategory from './StepCategory'
import StepProducts from './StepProducts'
import StepSuccess from './StepSuccess'

import './stylesheets/Modal.scss'

export const STEP_CATEGORY = 'category'
export const STEP_PRODUCTS = 'products'
export const STEP_SUCCESS = 'success'


export default function Wizard(props){
  const [errors, setErrors] = React.useState(props.errors)
  const [category, setCategory] = React.useState(props.category)
  const [products, setProducts] = React.useState(props.products)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)
  const [currentStep, setCurrentStep] = React.useState(props.currentStep)
  const isLastStep = currentStep == STEP_SUCCESS

  function handleCategorySubmit(value) {
    setIsInProgress(false)
    setErrors({})
    setCurrentStep(STEP_PRODUCTS)
  }

  function handleProductsSubmit() {
    setIsInProgress(false)
    setErrors({})
    setCategory('')  // so if the user goes back to step 1 they have to click again
    setCurrentStep(STEP_SUCCESS)
  }

  function handleComplete(userHasSignupIntent) {
    props.onComplete(userHasSignupIntent, products)
  }

  function getStep() {
    if (currentStep == STEP_CATEGORY) {
      return (
        <StepCategory
          errors={errors}
          disabled={isInProgress}
          handleChange={setCategory}
          handleSubmit={handleCategorySubmit}
          value={category}
        />
      )
    } else if (currentStep == STEP_PRODUCTS) {
      return (
        <StepProducts
          errors={errors}
          disabled={isInProgress}
          handleChange={setProducts}
          handleSubmit={handleProductsSubmit}
          value={products}
        />
      )
    } else if (currentStep == STEP_SUCCESS) {
      return (
        <StepSuccess
          handleComplete={handleComplete}
          products={products}
        />
      )
    }
  }

  function SkipShowGenericContent(props) {
    const children = []
    if (isLastStep) {
      children.push(
        <a
          key='change-answers'
          href='#'
          className='great-mvp-wizard-step-link'
          onClick={event => { event.preventDefault(); setCurrentStep(STEP_CATEGORY) }}
        >Change answers</a>
      )
    } else {
      children.push(
        <a
          key='show-generic-content'
          href='#'
          className='great-mvp-wizard-step-link'
          onClick={event => { event.preventDefault(); props.onClick() }}
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
