import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import Modal from '@src/components/Modal'
import Services from '@src/Services'
import Wizard from './Wizard'

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


export default function ModalCentreScreen(props){
  const products = props.companySettings.expertise_products_services.other;
  const {isOpen, ...otherProps} = props;
  return (
    <Modal
      isOpen={isOpen}
      id='dashboard-question-modal-signup'
      skipFeatureCookieName='skip-signup'
      skipFeatureComponent={SkipShowGenericContent}
      className='ReactModal__Content--Signup p-l'
    >
      <div className="grid">
        <aside className="c-1-2">
          <h2 className="h-l">Sign up so we can save your settings</h2>
          { products && <p className="p-xxs m-r-m">{products.map((item, i) => <span key={i}>{item.label}</span>)}</p> }
        </aside>
        <div className="c-1-2">
          <Wizard showCredentialsLede={false} {...otherProps} />
        </div>
      </div>
    </Modal>
  )
}

ModalCentreScreen.propTypes = {
  isOpen: PropTypes.bool,
  isInProgress: PropTypes.bool,
  errors: PropTypes.object,
  currentStep: PropTypes.string,
}

ModalCentreScreen.defaultProps = {
  isOpen: false,
  isInProgress: false,
  errors: {},
  companySettings: {}
}
