import React, { useEffect, useRef, useState } from 'react'
import PropTypes from 'prop-types'
import { uniqueId } from '@src/Helpers'

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
  const [maxHeight, setMaxHeight] = useState()
  const [expanderId] = useState(`expander-${uniqueId()}`)

  const contentRef = useRef()

  useEffect(() => {
    const onResize = () => {
      setMaxHeight(contentRef.current.getBoundingClientRect().height)
    }
    onResize()
    window.addEventListener('resize', onResize)
    return () => window.removeEventListener('resize', onResize)
  }, [])

  const toggleExpand = () => {
    setExpanded(!expanded)
  }

  const toggleButton = (
    <button
      type="button"
      className={buttonClass || 'button button--tertiary'}
      onClick={toggleExpand}
      aria-controls={expanderId}
      aria-expanded={expanded}
    >
      {expanded ? expandedButtonLabel || buttonLabel : buttonLabel}
    </button>
  )

  return (
    <>
      {buttonBefore && toggleButton}
      <div
        id={expanderId}
        className="expander"
        style={{
          maxHeight: expanded ? `${maxHeight}px` : '0',
          transition: 'max-height 0.3s',
          overflow: 'hidden',
        }}
      >
        {/* vertical padding/margin to force flow-root rendering (includes children margins) */}
        <div ref={contentRef} style={{ margin: '-1px 0', padding: '1px 0' }}>
          {children}
        </div>
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
