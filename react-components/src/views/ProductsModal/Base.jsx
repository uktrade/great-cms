/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import Services from '@src/Services'
import Wizard from './Wizard'


export function Base(props){

  const [isOpen, setIsOpen] = React.useState(props.isOpen)

  return (
    <Wizard
      isOpen={isOpen}
      setIsOpen={setIsOpen}
      onComplete={props.onComplete}
    />
  )
}

export default function createModal({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(<Base {...params} />, element)
}

