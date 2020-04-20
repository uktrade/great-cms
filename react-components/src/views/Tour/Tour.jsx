/* eslint-disable */
import React from 'react'
import ReactTour from 'reactour'

import './stylesheets/Tour.scss'
import { slugify } from '../../Helpers'


export default function Tour(props){
  const steps = props.steps.map(step => {
    return {
      ...step,
      content: (
        <>
          <h2 className="h-s p-v-0" id={"page-tour-step-" + slugify(step.title)}>{step.title}</h2>
          <p>{step.body}</p>
        </>
      )
    }
  })

  return (
      <ReactTour
        steps={steps}
        isOpen={props.isOpen}
        onRequestClose={props.handleClose}
        showNumber={false}
        lastStepNextButton={<button className="great-mvp-tour-button p-v-xxs p-h-xs" id="page-tour-start-now">Start now</button>}
        nextButton={<button className="great-mvp-tour-button p-v-xxs p-h-xs" id="page-tour-next-step">next</button>}
        prevButton={<></>}
        showCloseButton={false}
        rounded={4}
      />
  )
}
