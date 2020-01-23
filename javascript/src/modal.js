import React from 'react';
import ReactDOM from 'react-dom';
import Modal from 'react-modal';


const customStyles = {
  content : {
    top                   : '50%',
    left                  : '50%',
    right                 : 'auto',
    bottom                : 'auto',
    marginRight           : '-50%',
    transform             : 'translate(-50%, -50%)'
  }
};


function Login(props){
  const [modalIsOpen,setIsOpen] = React.useState(false);

  function openModal() {
    setIsOpen(true);
  }

  function closeModal(){
    setIsOpen(false);
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
        <form action={props.action} method="post">
            <label>Username</label><input type="text" name="login" />
            <label>Username</label><input type="password" name="password" />
            <button>Login</button>
        </form>
      </Modal>
    </div>
  );
}

function createLoginModal(options) {
    Modal.setAppElement(options.element);
    ReactDOM.render(<Login action={options.action} />, options.element);
}


export default createLoginModal;