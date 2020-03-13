import React from 'react'
import ReactDOM from 'react-dom'

import ReactTour from 'reactour'

import './stylesheets/Tour.scss'


export default function Tour(props){
  const steps = props.steps.map(step => {
    return {
      ...step,
      content: (
        <>
          <h2 className="h-s p-v-0">{step.title}</h2>
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
        lastStepNextButton={<button className="great-mvp-tour-button p-v-xxs p-h-xs">Start now</button>}
        nextButton={<button className="great-mvp-tour-button p-v-xxs p-h-xs">next</button>}
        prevButton={<></>}
        showCloseButton={false}
        rounded={4}
      />
  )
}
