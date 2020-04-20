import React from 'react'
import ReactDOM from 'react-dom'
import ReactModal from 'react-modal'

import Wizard from './Wizard'


export function Base(props){
  const [isOpen, setIsOpen] = React.useState(props.isOpen)

  return (
    <Wizard
      isOpen={isOpen}
      setIsOpen={setIsOpen}
    />
  )
}


export default function createModal({ element, ...params }) {
  ReactModal.setAppElement(element)
  ReactDOM.render(<Wizard {...params} />, element)
}

