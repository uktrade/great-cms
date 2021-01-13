import React, { useState } from 'react'
import PropTypes from 'prop-types'
import Tab from './Tab'

function Tabs(props) {
  Tabs.propTypes = {
    children: PropTypes.instanceOf(Array).isRequired,
  }

  const [activeTab, setActiveTab] = useState(props.children[0].props.label)

  const onClickTabItem = (tab) => {
    setActiveTab(tab)
  }

  return (
    <div className="tabs">
      <ol className="tab-list body-m m-f-m">
        {props.children.map((child) => {
          const { label } = child.props
          return props.showTabs && (
            <Tab
              activeTab={activeTab}
              key={label}
              label={label}
              onClick={onClickTabItem}
            />
          )
        })}
      </ol>
      <div className="tab-content">
        {props.children.map((child) => {
          if (child.props.label !== activeTab) return undefined
          return child.props.children
        })}
      </div>
    </div>
  )
}

export default Tabs
