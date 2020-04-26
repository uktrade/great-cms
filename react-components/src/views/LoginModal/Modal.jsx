/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import Wizard from './Wizard'
import Services from '@src/Services'

import './stylesheets/Modal.scss'


const modalStyles = {
  content : {
    background: '#f5f2ed',
    bottom: 'auto',
    left: '50%',
    marginRight: '-50%',
    padding: 30,
    right: 'auto',
    top: '50%',
    transform: 'translate(20%, 0)',
    top: 75,
    width: 430,
    overflow: 'visible',
    height: '100%',
  },
  overlay: {
    zIndex: 1000,
    backgroundColor: 'transparent',
    width: 430,
    height: '100%',
  },
}

export function Modal(props){
  const [isOpen, setIsOpen] = React.useState(props.isOpen)

  function handleOpen(event) {
    event.preventDefault()
    setIsOpen(true)
  }

  function handleRequestSkipFeature() {
    setCookie(props.skipFeatureCookieName, 'true');
    setIsOpen(false)
  }

  return (
    <div className='great-mvp-signup-modal'>
      <ReactModal
        isOpen={isOpen}
        style={modalStyles}
        contentLabel="Modal"
      >
        <Wizard nextUrl={props.nextUrl} />
      </ReactModal>
    </div>
  )
}

Modal.propTypes = {
  isOpen: PropTypes.bool,
  nextUrl: PropTypes.string.isRequired,
}

Modal.defaultProps = {
  isOpen: false,
}

export default function createModal({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(<Modal {...params} />, element)
}
