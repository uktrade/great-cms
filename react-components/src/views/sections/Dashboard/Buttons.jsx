import React, { useState } from 'react'

import { ComingSoon } from '@src/components/Sidebar/ComingSoon'

export const Buttons = () => {
  const [modal, setModal] = useState(false)

  return (
    <>
      <ComingSoon
        onClick={() => setModal(false)}
        isOpen={modal}
      />
      <button type='button' className="button button--secondary button--full-width button--icon m-b-xs button--disabled" onClick={() => setModal(true)}>
        <i className="fas fa-download" />
        <span className="body-m text-white">Save your plan as a PDF</span>
      </button>
      <button type='button' className="button button--secondary button--full-width button--icon m-b-xs button--disabled" onClick={() => setModal(true)}>
        <i className="fas fa-share" />
        <span className="body-m text-white">Share your plan</span>
      </button>
      <button type='button' className="button button--secondary button--full-width button--icon m-b-xs button--disabled" onClick={() => setModal(true)}>
        <i className="fas fa-globe" />
        <span className="body-m text-white">Find your target market</span>
      </button>
    </>
  )
}
