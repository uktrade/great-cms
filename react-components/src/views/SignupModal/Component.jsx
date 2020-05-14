/* eslint-disable */
import React from 'react'
import PropTypes from 'prop-types'

import Modal from '@src/components/Modal'
import { ConnectedContainer as Signup } from '@src/views/Signup/Container'
import './stylesheets/Modal.scss'


export function SkipShowGenericContent(props) {
  return (
    <div className="grid">
      <div className="c-1-2">
        &nbsp;
        <img src='/static/images/tourists.png' className="great-mvp-image-tourists" />
      </div>
      <div className="c-1-2">
        <a
          href='#'
          className='great-mvp-wizard-step-link m-t-l'
          onClick={event => { event.preventDefault(); props.onClick() }}
        >I don't want to sign up</a>
      </div>
    </div>
  )
}

export default function Component(props){
  const { isOpen, setIsOpen, preventClose, performSkipFeatureCookieCheck, ...otherProps } = props
  
  function getClassName() {
    const className = 'ReactModal__Content--Signup p-l'
    if (props.products.length > 0 || props.countries.length) {
      className += ' ReactModal__Content--two-columns '
    }
    return className
  }

  return (
    <Modal
      isOpen={isOpen}
      setIsOpen={setIsOpen}
      id='signup-modal'
      skipFeatureCookieName='skip-signup'
      skipFeatureComponent={SkipShowGenericContent}
      performSkipFeatureCookieCheck={performSkipFeatureCookieCheck}
      className={getClassName()}
      preventClose={preventClose}
    >
      <Signup {...otherProps} />
    </Modal>
  )
}

Component.propTypes = {
  isOpen: PropTypes.bool,
  setIsOpen: PropTypes.func.isRequired,
  performSkipFeatureCookieCheck: PropTypes.bool,
  preventClose: PropTypes.bool,
}

Component.defaultProps = {
  isOpen: false,
  performSkipFeatureCookieCheck: true,
  preventClose: false,
}
