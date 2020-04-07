import React from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

import { withCookies, useCookies } from 'react-cookie';


export function Modal(props){
  const [cookies, setCookie] = useCookies([props.skipFeatureCookieName])
  const SkipFeature = cookies[props.skipFeatureCookieName] == 'true'

  function handleClose(event){
    event.preventDefault()
    props.setIsOpen(false)
  }

  function handleRequestSkipFeature() {
    setCookie(props.skipFeatureCookieName, 'true', {path: '/'})
    props.setIsOpen(false)
  }

  function getSkipFeature() {
    const SkipFeature= props.skipFeatureComponent
    if (SkipFeature) {
      return <SkipFeature onClick={handleRequestSkipFeature} />
    }
  }

  return (
    <ReactModal
      isOpen={!SkipFeature && props.isOpen}
      onRequestClose={handleClose}
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
  id: PropTypes.string
}

Modal.defaultProps = {
  isOpen: false,
}

export default withCookies(Modal)

