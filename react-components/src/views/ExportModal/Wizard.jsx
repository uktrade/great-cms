import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import Services from '@src/Services'
import StepCategory from './StepCategory'
import StepProducts from './StepProducts'
import StepSuccess from './StepSuccess'


export const STEP_CATEGORY = 'category'
export const STEP_PRODUCTS = 'products'
export const STEP_SUCCESS = 'success'


export default function Wizard(props){
  const [errors, setErrors] = React.useState(props.errors)
  const [category, setCategory] = React.useState(props.category)
  const [products, setProducts] = React.useState(props.products)
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress)

  function handleCategorySubmit(value) {
    setIsInProgress(false)
    setErrors({})
    props.setCurrentStep(STEP_PRODUCTS)
  }

  function handleProductsSubmit() {
    setIsInProgress(false)
    setErrors({})
    setCategory('')  // so if the user goes back to step 1 they have to click again
    props.setCurrentStep(STEP_SUCCESS)
  }

  function handleComplete() {
    props.onComplete(products)
  }

  if (props.currentStep == STEP_CATEGORY) {
    return (
      <StepCategory
        errors={errors}
        disabled={isInProgress}
        handleChange={setCategory}
        handleSubmit={handleCategorySubmit}
        value={category}
      />
    )
  } else if (props.currentStep == STEP_PRODUCTS) {
    return (
      <StepProducts
        errors={errors}
        disabled={isInProgress}
        handleChange={setProducts}
        handleSubmit={handleProductsSubmit}
        value={products}
      />
    )
  } else if (props.currentStep == STEP_SUCCESS) {
    return (
      <StepSuccess
        handleSubmit={handleComplete}
        products={products}
      />
    )
  }
}

Wizard.propTypes = {
  currentStep: PropTypes.string.isRequired,
  setCurrentStep: PropTypes.func.isRequired,
  onComplete: PropTypes.func,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  category: PropTypes.string,
}

Wizard.defaultProps = {
  errors: {},
  isInProgress: false,
  category: '',
  onComplete: () => {}
}
