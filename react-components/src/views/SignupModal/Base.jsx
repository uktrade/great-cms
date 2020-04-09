/* eslint-disable */
import React from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'
import PropTypes from 'prop-types'

import ModalCentreScreen from './ModalCentreScreen'
import ModalHalfScreen from './ModalHalfScreen'


export function Base(props) {
  if (props.mode === 'half') {
    return <ModalHalfScreen {...props} />
  } else if (props.mode === 'centre') {
    return <ModalCentreScreen {...props} />
  }
}

export default function createModal({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(<Base {...params} />, element)
}


Base.propTypes = {
  mode: PropTypes.string.isRequired
}
