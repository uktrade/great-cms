import React from 'react';
import PropTypes from 'prop-types';
import ReactDOM from 'react-dom';
import Modal from 'react-modal';


export const MESSAGE_INCORRECT_CREDENTIALS = 'Incorrect username or password';
export const MESSAGE_UNEXPEXCTED_ERROR = 'Unexpected Error';
const customStyles = {
  content : {
    top: '50%',
    left: '50%',
    right: 'auto',
    bottom: 'auto',
    marginRight: '-50%',
    transform: 'translate(-50%, -50%)'
  }
};


export function checkCredentials({url, csrfToken, username, password}) {
  return fetch(url, {
    method: 'post',
    headers: {
      'Accept': 'application/json',
      'Content-Type': 'application/json',
      'X-CSRFToken': csrfToken,
      'X-Requested-With': 'XMLHttpRequest',
    },
    body: JSON.stringify({username, password}),
  }).then(response => {
    if (response.status == 400) {
      throw MESSAGE_INCORRECT_CREDENTIALS;
    } else if (response.status != 200) {
      throw MESSAGE_UNEXPEXCTED_ERROR;
    };
  });
}


export function LoginModal(props){
  const [isOpen, setIsOpen] = React.useState(props.isOpen);
  const [errorMessage, setErrorMessage] = React.useState(props.errorMessage);
  const [isInProgress, setIsInProgress] = React.useState(props.isInProgress);

  const usernameRef = React.createRef();
  const passwordRef = React.createRef();

  function openModal(event) {
    event.preventDefault();
    setIsOpen(true);
  }

  function closeModal(){
    setIsOpen(false);
  }

  function handleSubmit(event){
    event.preventDefault();
    setErrorMessage('');
    setIsInProgress(true);
    const promise = checkCredentials({
      url: props.action,
      username: usernameRef.current.value,
      password: passwordRef.current.value,
      csrfToken: props.csrfToken,
    });
    promise
      .then(response => {
         location.reload();
      })
      .catch(error => {
        setErrorMessage(error);
        setIsInProgress(false);
      })
  }

  return (
    <div>
      <a id="header-sign-in-link" onClick={openModal} className="account-link signin" href="#">Sign in</a>
      <Modal
        isOpen={isOpen}
        onRequestClose={closeModal}
        style={customStyles}
        contentLabel="Login Modal"
      >
        <button onClick={closeModal}>close</button>
        <form onSubmit={handleSubmit}>
            {errorMessage ? <div>{errorMessage}</div> : ''}
            <label>Username</label><input type="text" name="username" ref={usernameRef} disabled={isInProgress} />
            <label>Username</label><input type="password" name="password" ref={passwordRef} disabled={isInProgress} />
            <input type="submit" value="Login" disabled={isInProgress} />
        </form>
      </Modal>
    </div>
  );
};

LoginModal.propTypes = {
  isOpen: PropTypes.bool,
  errorMessage: PropTypes.string,
  isInProgress: PropTypes.bool,
  action: PropTypes.string.isRequired,
  csrfToken: PropTypes.string.isRequired,
};

LoginModal.defaultProps = {
  isOpen: false,
  errorMessage: '',
  isInProgress: false,
};

export default function createLoginModal(options) {
    Modal.setAppElement(options.element);
    ReactDOM.render(
      <LoginModal
        action={options.action}
        csrfToken={options.csrfToken}
        isOpen={options.isOpen}
        isInProgress={options.isInProgress}
        rrrorMessage={options.errorMessage}
      />, options.element
    );
};
