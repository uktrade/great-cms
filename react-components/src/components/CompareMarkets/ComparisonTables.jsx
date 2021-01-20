import React, { useState } from 'react'
import PropTypes from 'prop-types'
import tabConfiguration from './TabConfiguration'
import DataTable from './DataTable'
import Tabs from './Tabs'
import { isObject, get } from '../../Helpers'

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
  let listOfTabs = []
  if (tabs && Object.keys(tabs).length > 0) {
    listOfTabs = Object.keys(tabs).filter((key) => tabs[key])
    if (!activeTab && listOfTabs.length) {
      setActiveTab(listOfTabs[0].toUpperCase())
    }
  }

  const tabConfig = tabConfiguration(selectedProduct)
  return (
    <>
      <Tabs setActiveTab={setActiveTab} showTabs={!!listOfTabs.length}>
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
        {listOfTabs.map(
          (item) =>
            activeTab === item.toUpperCase() &&
            tabConfig[item] && (
              <DataTable
                key={item}
                datasetName={item}
                config={tabConfig[item]}
                comparisonMarkets={comparisonMarkets}
                commodityCode={get(selectedProduct, 'commodity_code')}
                removeMarket={removeMarket}
              />
            )
        )}
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
  triggerButton: PropTypes.instanceOf(Object).isRequired,
}


