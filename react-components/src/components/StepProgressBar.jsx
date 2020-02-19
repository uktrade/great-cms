import React from 'react'
import PropTypes from 'prop-types'

import googleIcon from '@assets/google-icon.png'
import linkedinIcon from '@assets/linkedin-icon.png'
import Services from '../Services'

import './stylesheets/StepProgressBar.scss'


export default function StepProgressBar(props){
  const scale = 1 + (1 / props.steps.length)
  return (
    <div className="great-mvp-step-progress-bar">
      <ul style={{scale: `${scale}`}}>
        {props.steps.map((step, i) => <li key={i} className={step == props.currentStep && "active"}></li>)}
      </ul>
    </div>
  )
}
