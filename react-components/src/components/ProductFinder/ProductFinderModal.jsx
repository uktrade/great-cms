import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import { connect, Provider } from 'react-redux'

import Services from '@src/Services'
import actions from '@src/actions'
import { getModalIsOpen, getProductsExpertise } from '@src/reducers'


export function Container(props){

  return (
    <Component
      {...props}
    />
  )
}


const mapStateToProps = state => {
  debugger
  return {
    isOpen: getModalIsOpen(state, 'products'),
    products: getProductsExpertise(state),
  }
}

const mapDispatchToProps = dispatch => {
  return {
    setIsOpen: isOpen => { dispatch(actions.toggleModalIsOpen('products', isOpen))},
  }
}

const ConnectedContainer = connect(mapStateToProps, mapDispatchToProps)(Container)

export default function({ element, ...params }) {
  debugger;
  ReactModal.setAppElement(element)
  ReactDOM.render(
    <Provider store={Services.store}>
      <ConnectedContainer {...params} />
    </Provider>,
    element
  )
}