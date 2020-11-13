import React, { useState } from 'react'

import { ComingSoon } from '@src/components/Sidebar/ComingSoon'
import {analytics} from "../../../Helpers";

export const Buttons = () => {
  const [modal, setModal] = useState(false)

  const openComingSoonModal = (e) => {
    setModal(true)
    // record click on disable section
    analytics({
      'event':'ctaFeature',
      'featureTitle':e.target.dataset.sectiontitle
    })
  }

  return (
    <>
      <ComingSoon
        onClick={() => setModal(false)}
        isOpen={modal}
      />
      <button type='button' className="button button--secondary button--full-width button--icon m-b-xs button--disabled" onClick={openComingSoonModal} data-sectiontitle="Save your plan as a PDF">
        <i className="fas fa-download" data-sectiontitle="Save your plan as a PDF" />
        <span className="body-m text-white" data-sectiontitle="Save your plan as a PDF">Save your plan as a PDF</span>
      </button>
      <button type='button' className="button button--secondary button--full-width button--icon m-b-xs button--disabled" onClick={openComingSoonModal} data-sectiontitle="Share your plan">
        <i className="fas fa-share" data-sectiontitle="Share your plan" />
        <span className="body-m text-white" data-sectiontitle="Share your plan">Share your plan</span>
      </button>
      <button type='button' className="button button--secondary button--full-width button--icon m-b-xs button--disabled" onClick={openComingSoonModal} data-sectiontitle="Find your target market">
        <i className="fas fa-globe" data-sectiontitle="Find your target market" />
        <span className="body-m text-white" data-sectiontitle="Find your target market">Find your target market</span>
      </button>
    </>
  )
}
