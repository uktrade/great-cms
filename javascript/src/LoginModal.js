import React from 'react';
import ReactDOM from 'react-dom';
import Modal from 'react-modal';


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


export function LoginModal(props){
  const [modalIsOpen,setIsOpen] = React.useState(false);
  const [isError,setIsError] = React.useState(false);
  const [isInProgress,setIsInProgress] = React.useState(false);

  const usernameRef = React.createRef();
  const passwordRef = React.createRef();

  function openModal() {
    setIsOpen(true);
  }

  function closeModal(){
    setIsOpen(false);
  }

  function handleSubmit(event) {
    event.preventDefault();
    const data = {
      'username': usernameRef.current.value,
      'password': passwordRef.current.value,
    };
    setIsError(false);
    setIsInProgress(true);

    fetch(props.action, {
      method: 'post',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'X-CSRFToken': props.csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify(data),
    }).then(response => {
      setIsInProgress(false);
      if (response.status == 400) {
        setIsError(true);
      } else if (response.status == 200) {
        location.reload();
      }
    });
  }

  return (
    <div>
      <a href="#" onClick={openModal}>Sign in</a>
      <Modal
        isOpen={modalIsOpen}
        onRequestClose={closeModal}
        style={customStyles}
        contentLabel="Login Modal"
      >
        <button onClick={closeModal}>close</button>
        <form onSubmit={handleSubmit}>
            <div>{isError?'Incorrect username or password':''}</div>
            <label>Username</label><input type="text" name="login" ref={usernameRef} disabled={isInProgress} />
            <label>Username</label><input type="password" name="password" ref={passwordRef} disabled={isInProgress} />
            <input type="submit" value="Login" disabled={isInProgress} />
        </form>
      </Modal>
    </div>
  );
}

export default function createLoginModal(options) {
    Modal.setAppElement(options.element);
    ReactDOM.render(<LoginModal action={options.action} csrfToken={options.csrfToken} />, options.element);
}
