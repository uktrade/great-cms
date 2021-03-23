import React, { useState } from 'react'
import PropTypes from 'prop-types'
import ReactDOM from 'react-dom'

export function PageModalManager(props) {
  const { modals } = props
  const [currentModal, setCurrentModal] = useState(modals[0])

  const nextModal = () => {
    const currentIndex = modals.indexOf(currentModal)
    setCurrentModal(modals[currentIndex + 1] || modals[currentIndex])
  }

  let Component = currentModal.factory
  return (
    currentModal && (
      <Component
      {...currentModal.params}
      handleModalClose={nextModal}
    />
    )
  )
}

PageModalManager.propTypes = {
  modals: PropTypes.arrayOf(
    PropTypes.shape({
      factory: PropTypes.elementType.isRequired,
      params: PropTypes.object.isRequired,
    })
  ).isRequired,
}

export default function LoadPageModals({ ...params }) {
  const element = document.createElement('div')
  document.body.appendChild(element)
  ReactDOM.render(
    <PageModalManager {...params} />,
    element
  )
}
