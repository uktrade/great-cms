import React, { useState } from 'react'
import PropTypes from 'prop-types'
import { useWindowSize } from '@src/components/hooks/useWindowSize'
import DataTable from './DataTable'
import Tabs from './Tabs'
import { isObject, analytics } from '../../Helpers'

import productTabConfig from './TabConfigProduct'
import economyTabConfig from './TabConfigEconomy'
import businessTabConfig from './TabConfigBusiness'
import societyTabConfig from './TabConfigSociety'
import ageGroupsTabConfig from './TabConfigAgeGroups'

const mobileBreakpoint = 980

export default function ComparisonTables(props) {
  const {
    tabsJson,
    comparisonMarkets,
    activeProduct,
    removeMarket,
    triggerButton,
    cacheVersion,
  } = props
  const [activeTab, setActiveTab] = useState()


  // Note This object dictates the order of tabs displayed
  const tabConfig = {
    product: productTabConfig,
    economy: economyTabConfig,
    agegroups: ageGroupsTabConfig,
    society: societyTabConfig,
    business: businessTabConfig,
  }

  let tabs = JSON.parse(tabsJson)
  if (!isObject(tabs)) {
    tabs = JSON.parse(tabs)
  }
  let listOfTabs = []
  if (tabs && Object.keys(tabs).length > 0) {
    listOfTabs = Object.keys(tabConfig).filter((key) => tabs[key])
    if (!activeTab && listOfTabs.length) {
      setActiveTab(listOfTabs[0])
    }
  }

  const setActiveTabWithEvent = (tab) => {
    const tabName = tabConfig[tab].tabName || tab.toUpperCase();
    analytics({
      event: 'addWhereToExportPageview',
      virtualPageUrl:`/where-to-export/${tabName.toLowerCase().replace(' ','-')}`,
      virtualPageTitle:`Where To Export - ${tabName}`
    })
    setActiveTab(tab)
  }

  const mobile = useWindowSize().width < mobileBreakpoint

  const tabStrip = (
    <Tabs
      label="Country comparison data"
      setActiveTab={setActiveTabWithEvent}
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
      {mobile ? '' : <div>{tabStrip}</div>}

      {Object.keys(tabConfig).map(
        (item) =>
          activeTab === item &&
          tabConfig[item] && (
            <React.Fragment key={item}>
              <div
                className={`table market-details ${
                  mobile ? 'm-h-0' : 'bg-white p-v-s p-b-s p-h-s'
                }`}
                id={`${item}-tab`}
                role="tabpanel"
                aria-labelledby={item}
                tabIndex="0"
              >
                {!mobile && tabConfig[item].filter}
                <DataTable
                  datasetName={item}
                  config={tabConfig[item]}
                  comparisonMarkets={comparisonMarkets}
                  product={activeProduct || {}}
                  removeMarket={removeMarket}
                  cacheVersion={cacheVersion}
                  mobile={mobile}
                  triggerButton={triggerButton}
                  tabStrip={tabStrip}
                />
                {!mobile && triggerButton}
              </div>
            </React.Fragment>
          )
      )}
    </>
  )
}

ComparisonTables.propTypes = {
  tabsJson: PropTypes.string.isRequired,
  comparisonMarkets: PropTypes.instanceOf(Object).isRequired,
  activeProduct: PropTypes.shape({
    commodity_name: PropTypes.string,
    commodity_code: PropTypes.string,
  }),
  removeMarket: PropTypes.func.isRequired,
  triggerButton: PropTypes.instanceOf(Object).isRequired,
  cacheVersion: PropTypes.number,
}

ComparisonTables.defaultProps = {
  cacheVersion: null,
  activeProduct: null,
}
