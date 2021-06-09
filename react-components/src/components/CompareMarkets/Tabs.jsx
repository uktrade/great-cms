import React, { useRef } from 'react'
import PropTypes from 'prop-types'
import Tab from './Tab'

function Tabs(props) {
  const { label, setActiveTab, activeTab, showTabs, children } = props

  const tabRefs = useRef([])

  const onClickTabItem = (tab) => {
    setActiveTab(tab)
  }

  const onKeyDown = (e, tabId) => {
    // this table maps keycode to displacement from current position
    const displacement = {35: 1000, 36: -1000, 37:-1, 39: 1}[e.keyCode]
    if(displacement) {
        e.preventDefault()
        const tabList = children.map((child) => child.props.tabId)
        const newPosition = Math.max(0, Math.min(tabList.indexOf(tabId) + displacement, tabList.length - 1))
        setActiveTab(tabList[newPosition])
        tabRefs.current[newPosition].focus()
    }
  }

  return (
    <div className="tabs body-m m-b-s"
    role="tablist"
      aria-label={label}
    >
      {children.map((child, index) => {
        const { label:childLabel, tabId } = child.props
        return (
          showTabs && (
            <Tab
              activeTab={activeTab}
              key={childLabel}
              tabId={tabId}
              label={childLabel}
              onClick={onClickTabItem}
              onKeyDown={(e) => onKeyDown(e, tabId)}
              setRef={(el) => {(tabRefs.current[index] = el)}}
            />
          )
        )
      })}
    </div>
  )
}

Tabs.propTypes = {
  label: PropTypes.string.isRequired,
  children: PropTypes.instanceOf(Array).isRequired,
  setActiveTab: PropTypes.func.isRequired,
  activeTab: PropTypes.string,
  showTabs: PropTypes.bool,
}

Tabs.defaultProps = {
  showTabs: true,
  activeTab: null,
}

export default Tabs
