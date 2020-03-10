import React from 'react'
import PropTypes from 'prop-types'


export default function Sector(props){
  return (
    <li className="border-thin border-mid-grey text-mid-grey text-hover-grey bg-hover-white border-hover-grey pill">{props.name}</li>
  )
}

Sector.propTypes = {
  name: PropTypes.string.isRequired
}
