import React from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'
import Modal from 'react-modal'

import SignupModal from './SignupModal'
import LoginModal from './LoginModal'


export function UserStateModal(props){
  const [isLoginModalOpen, setIsLoginModalOpen] = React.useState(false)
  const [isSignupModalOpen, setIsSignupModalOpen] = React.useState(false)

  function openLoginModal(event) {
    event.preventDefault()
    setIsSignupModalOpen(false)
    setIsLoginModalOpen(true)
  }

  function closeLoginModal(){
    setIsLoginModalOpen(false)
  }

  function openSignupModal() {
    setIsLoginModalOpen(false)
    setIsSignupModalOpen(true)
  }

  function closeSignupModal(){
    setIsSignupModalOpen(false)
  }

  return (
    <div>
      <a
        id='header-sign-in-link'
        onClick={openLoginModal}
        className='account-link signin'
        href='#'
      >Sign in</a>
      <LoginModal
        loginUrl={props.loginUrl}
        csrfToken={props.csrfToken}
        isOpen={isLoginModalOpen}
        handleClose={closeLoginModal}
        handleSignupClick={openSignupModal}
      />
      <SignupModal
        signupUrl={props.signupUrl}
        csrfToken={props.csrfToken}
        linkedInUrl={props.linkedInUrl}
        googleUrl={props.googleUrl}
        termsUrl={props.termsUrl}
        isOpen={isSignupModalOpen}
        handleClose={closeSignupModal}
        handleLoginOpen={openLoginModal}
      />
    </div>
  )
}

SignupModal.propTypes = {
  ...UserStateModal.propTypes,
  ...SignupModal.propTypes,
}

export default function createUserStateModal({ element, ...params }) {
  Modal.setAppElement(element)
  ReactDOM.render(<UserStateModal {...params} />, element)
}
