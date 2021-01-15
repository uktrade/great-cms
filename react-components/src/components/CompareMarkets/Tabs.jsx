import React, { useState } from 'react'
import PropTypes from 'prop-types'
import Tab from './Tab'

function Tabs(props) {
  const { setActiveTab, showTabs, children } = props

  const [activeTab, setLocalActiveTab] = useState(children[0].props.label)

  const onClickTabItem = (tab) => {
    setLocalActiveTab(tab)
    setActiveTab(tab)
  }

  return (
    <div className="tabs">
      <ol className="tab-list body-m m-f-m">
        {children.map((child) => {
          const { label } = child.props
          return (
            showTabs && (
              <Tab
                activeTab={activeTab}
                key={label}
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
  showTabs: PropTypes.bool
}

Tabs.defaultProps = {
  showTabs: true
}

export default Tabs
