import React, {useState} from 'react'
import ReactModal from "react-modal";

const customStyles = {
    content: {
        top: '30%',
        left: '30%',
        width: '30%',
        border: 'none',
        height: '30%',
        padding: '40px 60px',
        overflow: 'none',
    },
    overlay: {
        background: 'rgb(45 45 45 / 45%)',
        zIndex: '3',
    },
}

export function MessageConfirmation(props) {
    const [modalIsOpen, setIsOpen] = React.useState(props.productConfirmation)
    const closeModal = () => {
        setIsOpen(false)
    }
    return (
        <span>
            <ReactModal isOpen={props.productConfirmation} onRequestClose={closeModal} style={customStyles}>
                <div><strong>{props.messsageTitle}</strong>
                    <p>{props.messageBody}</p>
                </div>
                <button className="button button--primary button--round-corner"
                        onClick={props.handleButtonClick}>{props.messageButtonText}</button>
            </ReactModal>
        </span>
    )
}

export default MessageConfirmation;
