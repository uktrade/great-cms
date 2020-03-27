import React from 'react'
import PropTypes from 'prop-types'
import ReactModal from 'react-modal'

import { withCookies, useCookies } from 'react-cookie';


export function Modal(props){
  const [cookies, setCookie] = useCookies([props.skipFeatureCookieName])
  const SkipFeature = cookies[props.skipFeatureCookieName] == 'true'
  const [isOpen, setIsOpen] = React.useState(!SkipFeature && props.isOpen)

  function handleClose(event){
    event.preventDefault()
    setIsOpen(false)
  }

  function handleRequestSkipFeature() {
    setCookie(props.skipFeatureCookieName, 'true');
    setIsOpen(false)
  }

  function getSkipFeature() {
    const SkipFeature= props.skipFeatureComponent
    if (SkipFeature) {
      return <SkipFeature onClick={handleRequestSkipFeature} />
    }
  }

  return (
    <ReactModal
      isOpen={isOpen}
      onRequestClose={handleClose}
      className='ReactModal__Content'
      overlayClassName='ReactModal__Overlay'
      contentLabel='Modal'
      id={props.id}
    >
     <div className='m-s'>
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

