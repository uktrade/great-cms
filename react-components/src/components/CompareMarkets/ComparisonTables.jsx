import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useWindowSize } from '@src/components/hooks/useWindowSize'
import DataTable from './DataTable'
import Tabs from './Tabs'
import { isObject, get } from '../../Helpers'

import economyTabConfig from './TabConfigEconomy'
import populationTabConfig from './TabConfigPopulation'
import societyTabConfig from './TabConfigSociety'
import ageGroupsTabConfig from './TabConfigAgeGroups'


const mobileBreakpoint = 980

export default function ComparisonTables(props) {
  const {
    tabsJson,
    comparisonMarkets,
    selectedProduct,
    removeMarket,
    triggerButton,
    cacheVersion,
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
      setActiveTab(listOfTabs[0])
    }
  }

  const tabConfig = {
    economy: economyTabConfig,
    population: populationTabConfig,
    society: societyTabConfig,
    agegroups: ageGroupsTabConfig,
  }
  const mobile = useWindowSize().width < mobileBreakpoint

  const tabStrip = (
    <Tabs
      setActiveTab={setActiveTab}
      activeTab={activeTab}
      showTabs={!!listOfTabs.length}
    >
      {listOfTabs.map((item) => {
        return (
          <div
            key={item}
            label={tabConfig[item].tabName || item.toUpperCase()}
            className="button button--small button--tertiary"
            tabId={item}
          />
        )
      })}
    </Tabs>
  )

  return (
    <>
      {!mobile && (<div className="p-h-m p-t-l">{tabStrip}</div>)}
      <div
        className={`table market-details ${
          (mobile && 'm-h-0') || 'm-h-m bg-white p-v-s p-b-s p-h-s radius'
        }`}
      >
        {listOfTabs.map(
          (item) =>
            activeTab === item &&
            tabConfig[item] && (
              <React.Fragment key={item}>
                {!mobile && tabConfig[item].filter}
                <DataTable
                  datasetName={item}
                  config={tabConfig[item]}
                  comparisonMarkets={comparisonMarkets}
                  commodityCode={get(selectedProduct, 'commodity_code')}
                  removeMarket={removeMarket}
                  cacheVersion={cacheVersion}
                  mobile={mobile}
                  triggerButton={triggerButton}
                  tabStrip={tabStrip}
                />
              </React.Fragment>
            )
        )}
        {!mobile && triggerButton}
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
  cacheVersion: PropTypes.number,
}

ComparisonTables.defaultProps = {
  cacheVersion: null,
}
