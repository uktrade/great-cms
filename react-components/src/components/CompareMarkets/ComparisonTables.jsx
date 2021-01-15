import React, { useState } from 'react'
import PropTypes from 'prop-types'
import PopulationData from './PopulationData'
import EconomyData from './EconomyData'
import Tabs from './Tabs'
import { isObject } from '../../Helpers'

export default function ComparisonTables(props) {
  const {
    tabsJson,
    comparisonMarkets,
    selectedProduct,
    removeMarket,
    triggerButton,
  } = props
  const [activeTab, setActiveTab] = useState()


  let tabs = JSON.parse(tabsJson)
  if (!isObject(tabs)) {
    tabs = JSON.parse(tabs)
  }
  let listOfTabs
  if (tabs && Object.keys(tabs).length > 0) {
    listOfTabs = Object.keys(tabs).filter((key) => tabs[key])
    if(!activeTab && listOfTabs.length){
      setActiveTab(listOfTabs[0].toUpperCase())
    }
  }
  return (
    <>
      <Tabs setActiveTab={setActiveTab} showTabs={listOfTabs.length > 1}>
        {listOfTabs.map((item) => {
          return (
            <div
              key={item}
              label={item.toUpperCase()}
              className="button button--small button--tertiary"
            />
          )
        })}
      </Tabs>
      <div className="table market-details m-h-m bg-white p-v-s p-b-s p-h-s radius">
        {listOfTabs.map((item) => {
          return (
            <React.Fragment key={`tab-${item}`}>
              {item === 'population' && (
                <PopulationData
                  key={item}
                  comparisonMarkets={comparisonMarkets}
                  selectedProduct={selectedProduct}
                  removeMarket={removeMarket}
                  active={activeTab === item.toUpperCase()}
                />
              )}
              {item === 'economy' && (
                <EconomyData
                  key={item}
                  comparisonMarkets={comparisonMarkets}
                  removeMarket={removeMarket}
                  selectedProduct={selectedProduct}
                  active={activeTab === item.toUpperCase()}
                />
              )}
            </React.Fragment>
          )
        })}
        {triggerButton}
      </div>
    </>
  )
}

ComparisonTables.propTypes = {
  tabsJson: PropTypes.string.isRequired,
  comparisonMarkets: PropTypes.instanceOf(Object).isRequired,
  selectedProduct: PropTypes.shape({
    commodity_name: PropTypes.string,
    commodity_code: PropTypes.string,
  }).isRequired,
  removeMarket: PropTypes.func.isRequired,
  triggerButton: PropTypes.elementType.isRequired,
}
