import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

function Tab(props) {
  const { label, onClick } = props

  return (
    <button type="button" className={`tab-list-item m-r-s ${props.activeTab === props.label ? 'tab-list-active' : ''}`} onClick={() => onClick(label)}>
      {props.label}
    </button>
  )
}

Tab.propTypes = {
  activeTab: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  onClick: PropTypes.func.isRequired,
}

export default Tab
