import React, {useState} from 'react'
import ReactModal from "react-modal";

const customStyles = {
    content: {
        top: '10%',
        left: '10%',
        width: '80%',
        border: 'none',
        height: '80%',
        padding: '40px 60px',
        overflow: 'none',
    },
    overlay: {
        background: 'rgb(45 45 45 / 45%)',
        zIndex: '3',
    },
}

export function MessageConfirmation(props) {
    const [modalIsOpen, setIsOpen] = React.useState(true)

    const closeModal = () => {
        setIsOpen(false)
    }

    return (
        <span>
      <button className={props.buttonClass}>
          {props.selectedProduct || 'add product'}
      </button>

      <ReactModal isOpen={modalIsOpen} onRequestClose={closeModal} style={customStyles}>
          <button className="pull-right m-r-0 dialog-close" onClick={closeModal}></button>
           <div>Confirmation message</div>
      </ReactModal>
    </span>
    )
}

export default MessageConfirmation;