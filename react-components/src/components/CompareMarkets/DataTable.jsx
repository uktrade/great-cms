import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import actions from '@src/actions'
import { isArray, mapArray, deepAssign } from '../../Helpers'
import blocks from './blocks'

let cache = {}

export default function DataTable(props) {
  const {
    datasetName,
    config,
    comparisonMarkets,
    product,
    removeMarket,
    cacheVersion,
    mobile,
    triggerButton,
    tabStrip,
  } = props

  const dataIn = (data) => {
    cache[datasetName] = deepAssign(cache[datasetName], data)
    Services.store.dispatch(actions.setLoaded())
  }

  const flagArray = (array, value) => {
    // Generates an object from an array,
    const out = {}
    array.forEach((entry) => {
      out[entry] = value
    })
    return out
  }

  const setLoadingIndicators = (countries, columnList) => {
    // Set the columns in the countries provided - to loading
    const loadingIndicators = {}
    countries.forEach((country) => {
      loadingIndicators[country.country_iso2_code] = {
        loading: flagArray(columnList, 1),
      }
    })
    dataIn(loadingIndicators)
  }

  const getChunk = (countries, columnList, requestFunction) => {
    // Get a chunk of the table.
    // Pass in an array of countries, an array of column names and a request function
    return new Promise((resolve, reject) => {
      requestFunction(countries, cache.commodityCode)
        .then((result) => {
          const outData = {}
          let inData = result
          if (isArray(inData)) {
            inData = mapArray(inData, 'country')
          }
          countries.forEach((country) => {
            const iso2 = country.country_iso2_code
            outData[iso2] =
              outData[iso2] ||
              inData[iso2] ||
              inData[country.country_name] ||
              {}
            outData[iso2].loading = flagArray(columnList, 0)
          })
          dataIn(outData)
          resolve()
        })
        .catch(() => {
          const clear = {}
          countries.forEach((country) => {
            clear[country.country_iso2_code] = {
              loading: flagArray(columnList, 0),
            }
          })
          dataIn(clear)
          reject()
        })
    })
  }

  const getByCountrySequential = (countries, columnList, requestFunction) => {
    // gets chunk for one country at a time - but sequentially - i.e. only one request in flight
    const localCountries = [...countries]
    const country = localCountries.shift()
    getChunk([country], columnList, requestFunction).finally(() => {
      if (localCountries.length) {
        getByCountrySequential(localCountries, columnList, requestFunction)
      }
    })
  }

  const getTableData = (missingCountries) => {
    // Collect the retrieval groups.
    // Any columns without a group are collected as the default group
    const groups = {}
    Object.keys(config.columns).forEach((columnName) => {
      const groupName = config.columns[columnName].group || 'default'
      groups[groupName] = groups[groupName] || []
      groups[groupName].push(columnName)
    })
    // Make a request for each group using the group config.
    Object.keys(groups).forEach((groupName) => {
      const groupDef = (config.groups && config.groups[groupName]) || {
        dataFunction: config.dataFunction,
      }
      const columnList = groups[groupName]
      setLoadingIndicators(missingCountries, columnList)
      if (groupDef.splitCountries) {
        missingCountries.forEach((country) => {
          getChunk([country], columnList, groupDef.dataFunction)
        })
      } else if (groupDef.splitCountriesSequential) {
        getByCountrySequential(
          missingCountries,
          columnList,
          groupDef.dataFunction
        )
      } else {
        getChunk(missingCountries, columnList, groupDef.dataFunction)
      }
    })
  }

  useEffect(() => {
    // Wipe cache if commodity code changes
    if (cache.commodityCode !== product.commodityCode) {
      cache = { commodityCode: product.commodityCode }
      cache[datasetName] = {}
    }
    cache[datasetName] = cache[datasetName] || {}

    const missingCountries = Object.values(comparisonMarkets).filter(
      (country) => !cache[datasetName][country.country_iso2_code]
    )

    if (missingCountries.length) {
      getTableData(missingCountries)
    }
  }, [product, comparisonMarkets])

  const setBaseYear = (dataSet, markets, tabConfig) => {
    // Calculate base year
    const years = {}
    Object.values(markets).forEach((market) => {
      const countryData = dataSet && dataSet[market.country_iso2_code]
      if (countryData) {
        Object.values(tabConfig.columns).forEach((columnConfig) => {
          if (columnConfig.year) {
            try {
              const year = columnConfig.year(countryData)
              if (year) {
                years[year] = (years[year] || 0) + 1
              }
            } catch {
              // no data for year - it doesn't really matter.
            }
          }
        })
      }
    })
    blocks.setBaseYear(
      Object.keys(years).sort((a, b) => {
        return years[a] < years[b] ? 1 : -1
      })[0]
    )
  }

  setBaseYear(cache[datasetName], comparisonMarkets, config)

  if (mobile) {
    return (
      <>
        <div className="bg-blue-deep-80 p-h-xs p-v-xs selected-places">
          <h2 className="h-xs text-white p-v-0">Selected places</h2>
          <div className="bg-white radius overflow-hidden p-h-s">
            <table className="m-v-0 border-blue-deep-20 no-bottom-border">
              <tbody>
                {Object.values(comparisonMarkets).map((market) => {
                  return (
                    <tr key={market.country_iso2_code}>
                      {blocks.renderCountryRowHeader(market, removeMarket)}
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
          {triggerButton}
        </div>
        <div className="p-h-s">{tabStrip}</div>
        {config.filter && <div className="p-h-s">{config.filter}</div>}
        {Object.keys(config.columns).map((columnKey) => {
          const cellConfig = config.columns[columnKey]
          return (
            <div
              key={columnKey}
              className={`${columnKey} p-h-s m-t-xs ${
                cellConfig.className || ''
              }`}
            >
              <div className="text-align-left body-l-b p-v-xs">
                {blocks.renderColumnHeader(cellConfig, props, mobile)}
              </div>
              <div className="bg-white radius overflow-hidden p-h-s">
                <table className="m-v-0 border-blue-deep-20 no-bottom-border">
                  <tbody>
                    {blocks.renderMobileBlock(
                      cache[datasetName],
                      comparisonMarkets,
                      columnKey,
                      cellConfig
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )
        })}
        {config.sourceAttributions && (
          <div className="bg-white radius overflow-hidden p-h-s m-t-s m-h-s">
            {blocks.sourceAttribution(config.sourceAttributions)}
          </div>
        )}
      </>
    )
  }

  const tableBody = Object.values(comparisonMarkets).map((market) => {
    const countryData =
      cache[datasetName] && cache[datasetName][market.country_iso2_code]
    const countryRow = Object.keys(config.columns).map((columnKey) => {
      const cellConfig = config.columns[columnKey]
      return (
        <td
          key={columnKey}
          className={`${columnKey} p-v-xs body-l ${cellConfig.className || ''}`}
        >
          {countryData &&
          (!countryData.loading || !countryData.loading[columnKey]) ? (
            <>{blocks.renderCell(cellConfig, countryData)}</>
          ) : (
            <div className="loading">&nbsp;</div>
          )}
        </td>
      )
    })

    return (
      <tr
        key={`market-${market.country_iso2_code}`}
        id={`market-${market.country_name}`}
      >
        {blocks.renderCountryRowHeader(market, removeMarket, config)}
        {countryRow}
      </tr>
    )
  })

  return (
    <span>
      <table
        className={`m-v-0 border-blue-deep-20 valign-middle cache-version-${cacheVersion}`}
      >
        {config.caption && config.caption()}
        <thead>
          <tr>
            <th className="body-l-b">&nbsp;</th>
            {Object.keys(config.columns).map((columnKey) => {
              const cellConfig = config.columns[columnKey]
              return (
                <th
                  className={`body-l-b p-b-xs ${columnKey} ${
                    cellConfig.className || ''
                  }`}
                  key={columnKey}
                  scope="col"
                >
                  {blocks.renderColumnHeader(cellConfig, props)}
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody>{tableBody}</tbody>
      </table>
      {blocks.sourceAttribution(config.sourceAttributions)}
    </span>
  )
}

DataTable.propTypes = {
  datasetName: PropTypes.string.isRequired,
  comparisonMarkets: PropTypes.instanceOf(Object).isRequired,
  config: PropTypes.shape({
    columns: PropTypes.instanceOf(Object),
    sourceAttributions: PropTypes.instanceOf(Array),
    dataFunction: PropTypes.func,
    groups: PropTypes.instanceOf(Object),
    filter: PropTypes.element,
  }).isRequired,
  product: PropTypes.shape({
    commodityCode: PropTypes.string,
  }).isRequired,
  removeMarket: PropTypes.func.isRequired,
  cacheVersion: PropTypes.number,
  mobile: PropTypes.bool,
  triggerButton: PropTypes.element.isRequired,
  tabStrip: PropTypes.element.isRequired,
}
DataTable.defaultProps = {
  cacheVersion: null,
  mobile: false,
}
