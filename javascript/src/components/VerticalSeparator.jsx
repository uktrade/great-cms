import React from 'react'
import PropTypes from 'prop-types'

import '../stylesheets/VerticalSeparator.scss'


export default function VerticalSeparator(props){
  return (
    <p className='great-mvp-vertical-separator'>
      <hr/>
      <span>or</span>
      <hr/>
    </p>
  )
}


