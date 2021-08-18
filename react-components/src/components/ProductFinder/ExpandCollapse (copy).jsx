import React, { useState } from 'react'
import PropTypes from 'prop-types'
import useUniqueId from '@src/components/hooks/useUniqueId'

export default function ExpandCollapse(props) {
  const {
    buttonLabel,
    buttonClass,
    expandedButtonLabel,
    defaultExpanded,
    children,
    buttonBefore,
    animationDuration,
    onChange,
  } = props
  const [expanded, setExpanded] = useState(defaultExpanded)
  const [sectionHeight, setSectionHeight] = useState()
  const id = useUniqueId('expander')

  const toggleExpand = () => {
    onChange(!expanded)
    setExpanded(!expanded)
  }

  const setSection = (_section) => {
    setSectionHeight((_section && _section.scrollHeight) || sectionHeight)
  }

  const toggleButton = (
    <button
      type="button"
      aria-controls={id}
      className={buttonClass || 'button button--tertiary'}
      onClick={toggleExpand}
    >
      <i className="fas fa-chevron-down m-r-xxs"
        style={{transition:`transform ${animationDuration}ms`,transform:`rotate(${ expanded ? 180 : 0}deg)`}}/>
      {expanded ? expandedButtonLabel || buttonLabel : buttonLabel}
    </button>
  )

  return (
    <>
      {buttonBefore && toggleButton}
      <div
        id={id}
        className={`f-l expander ${
          expanded ? 'expander-expanded' : 'expander-collapsed'
        }`}
        style={{
          maxHeight: expanded ? `${sectionHeight}px` : '0px',
          transition: `max-height ${animationDuration}ms`,
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
  onChange: PropTypes.func,
  animationDuration: PropTypes.string,
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
  animationDuration:'250',
  onChange: ()=>null,
}
