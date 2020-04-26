import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { connect, Provider } from 'react-redux'

import ProductsModal from '@src/views/ProductsModal/Component'
import SignupModal from '@src/views/SignupModal/Component'
import CountriesModal from '@src/views/CountriesModal/Component'
import Services from '@src/Services'
import actions from '@src/actions'
import { getModalIsOpen, getProductsExpertise } from '@src/reducers'


export function Container(props){

  props.productElement.onclick = () => {
    // user is explicitly sking to see the modal, so don't prevent it opening via cookie check
    props.setIsProductModalOpen(true)
    props.skipFeatureCookieCheck()
  }
  props.countryElement.onclick = () => {
    // user is explicitly sking to see the modal, so don't prevent it opening via cookie check
    props.setIsCountriesModalOpen(true)
    props.skipFeatureCookieCheck()
  }

  return null
}

const mapStateToProps = state => {
  return {
    isProductModalOpen: getModalIsOpen(state, 'products'),
    isSignupModalOpen: getModalIsOpen(state, 'signup'),
    isCountriesModalOpen: getModalIsOpen(state, 'countries'),
    productsExpertise: getProductsExpertise(state),
  }
}

const mapDispatchToProps = dispatch => {
  return {
    setIsProductModalOpen: isOpen => { dispatch(actions.toggleModalIsOpen('products', isOpen)) },
    setIsSignupModalOpen: isOpen => { dispatch(actions.toggleModalIsOpen('signup', isOpen)) },
    setIsCountriesModalOpen: isOpen => { dispatch(actions.toggleModalIsOpen('countries', isOpen)) },
    setProductsExpertise: products => { dispatch(actions.setProductsExpertise(products)) },
    skipFeatureCookieCheck: () => { dispatch(actions.skipFeatureCookieCheck()) },
  }
}

const ConnectedContainer = connect(mapStateToProps, mapDispatchToProps)(Container)

export default function({ element, ...params }) {
  const mainElement = document.createElement('span');
  element.appendChild(mainElement)

  ReactModal.setAppElement(element)
  ReactDOM.render(
    <Provider store={Services.store}>
      <ConnectedContainer {...params} />
    </Provider>,
    mainElement
  )
}