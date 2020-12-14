import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'

function Tab(props) {
  const [cssClassName, setCssClassName] = useState('tab-list-item')
  const onClick = () => {
    const { label, onClick } = props
    onClick(label)
  }

  useEffect(() => {
    if (props.activeTab === props.label) {
      setCssClassName('tab-list-item tab-list-active')
    } else {
      setCssClassName('tab-list-item')
    }
  }, [props])

  Tab.propTypes = {
    activeTab: PropTypes.string.isRequired,
    label: PropTypes.string.isRequired,
    onClick: PropTypes.func.isRequired,
  }

  return (
    <li className={cssClassName} onClick={onClick}>
      {props.label}
    </li>
  )
}

export default Tab
