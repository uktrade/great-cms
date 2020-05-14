/* eslint-disable */
import React from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'
import { connect, Provider } from 'react-redux'

import Component from './Component'
import Services from '@src/Services'
import actions from '@src/actions'
import {
  getModalIsOpen,
  getPerformFeatureSKipCookieCheck,
  getProductsExpertise,
  getCountriesExpertise,
} from '@src/reducers'


export function Container(props){
  return (
    <Component {...props} />
  )
}


const mapStateToProps = state => {
  return {
    isOpen: getModalIsOpen(state, 'signup'),
    performSkipFeatureCookieCheck: getPerformFeatureSKipCookieCheck(state),
    products: getProductsExpertise(state),
    countries: getCountriesExpertise(state),
  }
}

const mapDispatchToProps = dispatch => {
  return {
    setIsOpen: isOpen => { dispatch(actions.toggleModalIsOpen('signup', isOpen))},
  }
}

const ConnectedContainer = connect(mapStateToProps, mapDispatchToProps)(Container)

export default function({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(
    <Provider store={Services.store}>
      <ConnectedContainer {...params} />
    </Provider>,
    element
  )
}