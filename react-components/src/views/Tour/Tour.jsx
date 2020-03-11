import React from 'react'
import ReactDOM from 'react-dom'

import ReactTour from 'reactour'

// import './stylesheets/Tour.scss'


export default function Tour(props){

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

const steps = [
  {
    selector: '#exportplan-country-sector-customisation-bar p',
    content: 'Welcome to your export plan',
    position: 'bottom',
  },
  {
    selector: '#exportplan-completion-progress-indicator',
    content: 'Track your progress',
    position: 'top',
  },
  {
    selector: '#exportplan-continue-leaning-title',
    content: 'Learn as you go',
    position: 'top',
  },
  {
    selector: '#exportplan-collaboraton-menu',
    content: 'Collaborate with your team',
    position: 'bottom',
  },
  {
    selector: '.exportplan-section-item img',
    content: "let's start",
    position: 'bottom',
  },
]
