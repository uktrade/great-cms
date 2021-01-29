import React, { useState } from 'react'
import PropTypes from 'prop-types'

export default function ExpandCollapse(props) {
  const {
    buttonLabel,
    buttonClass,
    expandedButtonLabel,
    defaultExpanded,
    children,
    buttonBefore,
  } = props
  const [expanded, setExpanded] = useState(defaultExpanded)
  const [sectionHeight, setSectionHeight] = useState()

  const toggleExpand = () => {
    setExpanded(!expanded)
  }

  const setSection = (_section) => {
    setSectionHeight((_section && _section.scrollHeight) || sectionHeight)
  }

  const toggleButton = (
    <button
      type="button"
      className={buttonClass || 'button button--tertiary'}
      onClick={toggleExpand}
    >
      {expanded ? expandedButtonLabel || buttonLabel : buttonLabel}
    </button>
  )

  return (
    <>
      {buttonBefore && toggleButton}
      <div
        className={`f-l expander ${
          expanded ? 'expander-expanded' : 'expander-collapsed'
        }`}
        style={{
          maxHeight: expanded ? `${sectionHeight}px` : '0px',
          transition: 'max-height 0.3s',
          overflow: 'hidden',
        }}
        ref={setSection}
      >
        {children}
      </div>
      {!buttonBefore && toggleButton}
    </>
  )
}

ExpandCollapse.propTypes = {
  buttonLabel: PropTypes.string,
  buttonClass: PropTypes.string,
  buttonBefore: PropTypes.bool,
  expandedButtonLabel: PropTypes.string,
  defaultExpanded: PropTypes.bool,
  children: PropTypes.oneOfType([
    PropTypes.arrayOf(PropTypes.node),
    PropTypes.node,
  ]).isRequired,
}

ExpandCollapse.defaultProps = {
  defaultExpanded: false,
  expandedButtonLabel: '',
  buttonLabel: '',
  buttonClass: '',
  buttonBefore: false,
}
