import React from 'react'
import PropTypes from 'prop-types'
import Tab from './Tab'

function Tabs(props) {
  const { setActiveTab, activeTab, showTabs, children } = props

  const onClickTabItem = (tab) => {
    setActiveTab(tab)
  }

  return (
    <div className="tabs">
      <ol className="tab-list body-m m-f-m">
        {children.map((child) => {
          const { label, tabId } = child.props
          return (
            showTabs && (
              <Tab
                activeTab={activeTab}
                key={label}
                tabId={tabId}
                label={label}
                onClick={onClickTabItem}
              />
            )
          )
        })}
      </ol>
    </div>
  )
}

Tabs.propTypes = {
  children: PropTypes.instanceOf(Array).isRequired,
  setActiveTab: PropTypes.func.isRequired,
  activeTab: PropTypes.string,
  showTabs: PropTypes.bool
}

Tabs.defaultProps = {
  showTabs: true,
  activeTab: null
}

export default Tabs
