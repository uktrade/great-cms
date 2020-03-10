import React from 'react'
import PropTypes from 'prop-types'


export default function Sector(props){
  return (
    <li className="bg-white border-thin border-grey pill">{props.name}</li>
  )
}

Sector.propTypes = {
  name: PropTypes.string.isRequired
}
