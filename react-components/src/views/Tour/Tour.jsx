/* eslint-disable */
import React from 'react'
import ReactTour from 'reactour'

import './stylesheets/Tour.scss'
import { slugify } from '../../Helpers'

export default function Tour(props) {
  const steps = props.steps.map((step) => {
    return {
      ...step,
      content: (
        <>
          <h2 className="h-s p-v-0 great-mvp-tour-heading" id={'page-tour-step-' + slugify(step.title)}>
            {step.title}
          </h2>
          <p className="great-mvp-tour-text">{step.body}</p>
        </>
      )
    }
  })

  return (
    <ReactTour
      onAfterOpen={() => {
        document.body.style.overflowY = 'hidden'
      }}
      onBeforeOpen={() => {
        document.body.style.overflowY = 'auto'
      }}
      steps={steps}
      isOpen={props.isOpen}
      onRequestClose={props.handleClose}
      showNumber={false}
      lastStepNextButton={
        <button className="button button--primary p-v-xxs p-h-xs" id="page-tour-start-now">
          Start now
        </button>
      }
      nextButton={
        <button className="button button--primary p-v-xxs p-h-xs" id="page-tour-next-step">
          next
        </button>
      }
      prevButton={<></>}
      showCloseButton={false}
      rounded={4}
    />
  )
}
