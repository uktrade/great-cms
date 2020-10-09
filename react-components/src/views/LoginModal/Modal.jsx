import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

import Wizard from './Wizard'

const Modal = ({ nextUrl, email, errors }) => {
  return (
    <Wizard nextUrl={nextUrl} email={email} errors={errors} />
  )
}

Modal.propTypes = {
  nextUrl: PropTypes.string.isRequired
}

export default function createModal({ element, ...params }) {
  ReactDOM.render(<Modal {...params} />, element)
}
