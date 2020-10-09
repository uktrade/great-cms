import React, { useState } from 'react'
import PropTypes from 'prop-types'

export default function ExpandCollapse(props) {
  const { buttonLabel, defaultExpanded, children } = props
  const [expanded, setExpanded] = useState(defaultExpanded)
  const [sectionHeight, setSectionHeight] = useState()

  const toggleExpand = () => {
    setExpanded(!expanded)
  }

  const setSection = (_section) => {
    setSectionHeight((_section && _section.scrollHeight) || sectionHeight)
  }

  return (
    <div>
    <div 
      className={`expander ${expanded ? 'expander-expanded' : 'expander-collapsed'}`} 
      style={{maxHeight:expanded ? `${sectionHeight}px`: '0px',transition:'max-height 0.3s', overflow:'hidden'}}
      ref={setSection}
    >
      {children}
    </div>
   <button type="button" className="button button--tertiary" onClick={toggleExpand} >{expanded ? 'Hide' : 'View'} {buttonLabel}</button>
   </div>
  )
}

ExpandCollapse.propTypes = {
  buttonLabel: PropTypes.string.isRequired,
  defaultExpanded: PropTypes.bool,
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]).isRequired
}

ExpandCollapse.defaultProps = {
  defaultExpanded: false
}
