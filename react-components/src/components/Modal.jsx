import React from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

import { withCookies, useCookies } from 'react-cookie';
import '../../../core/sass/components/Modal.scss'


export function Modal(props){
  const [cookies, setCookie] = useCookies([props.skipFeatureCookieName])

  function isOpen() {
    // some modals are opened on user click. Those should be able to skip the
    // "do not open if user previosuly asked not to see the modal again"
    if (props.performSkipFeatureCookieCheck) {
      const skipFeature = cookies[props.skipFeatureCookieName] == 'true'
      return !skipFeature && props.isOpen
    }
    return props.isOpen
  }


  function handleClose(event){
    event.preventDefault()
    props.setIsOpen(false)
  }

  function handleRequestSkipFeature() {
    setCookie(props.skipFeatureCookieName, 'true', {path: '/'})
    props.setIsOpen(false)
  }

  function onRequestClose(event) {
    event.preventDefault()
    if (!props.preventClose) {
      props.setIsOpen(false)
    }
  }

  function getSkipFeature() {
    const SkipFeature = props.skipFeatureComponent
    if (SkipFeature && !props.preventClose) {
      return <SkipFeature onClick={handleRequestSkipFeature} />
    }
  }

  return (
    <ReactModal
      isOpen={isOpen()}
      onRequestClose={onRequestClose}
      className={'ReactModal__Content ReactModalCentreScreen ' + props.className}
      overlayClassName='ReactModal__Overlay ReactModalCentreScreen'
      contentLabel='Modal'
      id={props.id}
    >
     <div>
        {props.children}
        {getSkipFeature()}
      </div>
    </ReactModal>
  )
}

Modal.propTypes = {
  isOpen: PropTypes.bool,
  skipFeatureCookieName: PropTypes.string,
  id: PropTypes.string,
  performSkipFeatureCookieCheck: PropTypes.bool,
  preventClose: PropTypes.bool,
}

Modal.defaultProps = {
  isOpen: false,
  performSkipFeatureCookieCheck: true,
  preventClose: false,
}

export default withCookies(Modal)
