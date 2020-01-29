import React from 'react';
import PropTypes from 'prop-types';
import ReactDOM from 'react-dom';
import Modal from 'react-modal';

import ErrorList from './ErrorList'
import Services from './Services'


const styles = {
  close: {
    'float': 'right',
  },
  input: {
    width: '100%',
  },
  button: {
    background: '#000000',
    color: '#ffffff',
  },
  modal: {
    content : {
      top: '50%',
      left: '50%',
      right: 'auto',
      bottom: 'auto',
      marginRight: '-50%',
      transform: 'translate(-50%, -50%)',
      textAlign: 'center',
      width: 350,
      background: '#f5f2ed',
    }
  }
}


export function SignupModal(props){
  const [isOpen, setIsOpen] = React.useState(props.isOpen);
  const [errorMessage, setErrorMessage] = React.useState(props.errorMessage);
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress);

  const usernameRef = React.createRef();
  const passwordRef = React.createRef();

  function openModal(event) {
    event.preventDefault();
    setIsOpen(true);
  }

  function closeModal(event){
    event.preventDefault();
    setIsOpen(false);
  }

  function handleSubmit(event){
    event.preventDefault();
    setErrorMessage('');
    setIsInProgress(true);
    Services.createUser({
      url: props.signupUrl,
      username: usernameRef.current.value,
      password: passwordRef.current.value,
      csrfToken: props.csrfToken,
    }).then(response => {
      location.reload();
    })
    .catch(error => {
      const message = error.message || error;
      setErrorMessage(error);
      setIsInProgress(false);
    })
  }
  return (
    <div>
      <a
        id="header-signup-link"
        onClick={openModal}
        className="account-link signup"
        href="#"
      >Sign up</a>
      <Modal
        isOpen={isOpen}
        onRequestClose={closeModal}
        style={styles.modal}
        contentLabel="Login Modal"
      >
        <a href="#" className="link" onClick={closeModal} style={styles.close}>close</a>
        <h2 className="heading-large">Sign up</h2>
        <a href={props.linkedInUrl} className="button" style={styles.button}>Continue with LinkedIn</a>
        <p>-- or --</p>
        <form onSubmit={handleSubmit}>
          { errorMessage && <ErrorList message={errorMessage} /> }
          <div className="form-group">
            <input
              type="text"
              placeholder="Email address"
              name="username"
              className="form-control"
              ref={usernameRef}
              disabled={isInProgress}
              style={styles.input}
            />
          </div>
          <div className="form-group">
            <input
              type="password"
              placeholder="Password"
              name="password"
              className="form-control"
              ref={passwordRef}
              disabled={isInProgress}
              style={styles.input}
            />
          </div>
          <p>By clicking Sign up, you accept the <a href={props.termsUrl} target="_blank">terms and conditions</a> of the great.gov.uk service.</p>
          <input
            type="submit"
            value="Sign up"
            className="button"
            disabled={isInProgress}
            style={styles.button}
          />
        </form>
      </Modal>
    </div>
  );
};

SignupModal.propTypes = {
  signupUrl: PropTypes.string.isRequired,
  csrfToken: PropTypes.string.isRequired,
  errorMessage: PropTypes.string,
  isInProgress: PropTypes.bool,
  isOpen: PropTypes.bool,
  linkedInUrl: PropTypes.string.isRequired,
  termsUrl: PropTypes.string.isRequired,
};

SignupModal.defaultProps = {
  isOpen: false,
  errorMessage: '',
  isInProgress: false,
};

export default function createSignupModal({ element, ...params }) {
  Modal.setAppElement(element);
  ReactDOM.render(<SignupModal {...params} />, element);
};
