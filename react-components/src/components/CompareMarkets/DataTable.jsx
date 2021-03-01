import React, { useEffect } from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import actions from '@src/actions'
import { Tooltip } from '@components/tooltip/Tooltip'
import { isArray, mapArray, deepAssign } from '../../Helpers'

let cache = {}
const DATA_NA = 'Data not available'

export default function DataTable(props) {
  const {
    datasetName,
    config,
    comparisonMarkets,
    commodityCode,
    removeMarket,
    cacheVersion,
  } = props

  const dataIn = (data) => {
    cache[datasetName] = deepAssign(cache[datasetName], data)
    Services.store.dispatch(
      actions.setLoaded()
    )
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
            outData[iso2] = outData[iso2] || 
                inData[iso2] ||
                inData[country.country_name] ||
                {}
            outData[iso2].loading = flagArray(
              columnList,
              0
            )
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
    if (cache.commodityCode !== commodityCode) {
      cache = { commodityCode }
      cache[datasetName] = {}
    }
    cache[datasetName] = cache[datasetName] || {}

    const missingCountries = Object.values(comparisonMarkets).filter(
      (country) => !cache[datasetName][country.country_iso2_code]
    )

    if (missingCountries.length) {
      getTableData(missingCountries)
    }

  }, [commodityCode, comparisonMarkets])

  const yearDiv = (year, baseYear) => {
    return (
      year &&
      String(year) !== baseYear && (
        <div className="body-m text-black-60 display-year">{year}</div>
      )
    )
  }

  const sourceAttribution = (attributions) => {
    return (
      <p className="source-attribution body-s m-r-s m-v-xs">
        {attributions.map((attribution) => {
          return (
            <React.Fragment key={`attr-${attribution.title}`}>
              <strong className="body-s-b">{attribution.title}</strong>
              {attribution.preLinkText && (
                <>&nbsp;{attribution.preLinkText}&nbsp;</>
              )}
              :&nbsp;
              {attribution.linkTarget && (
                <a
                  href={attribution.linkTarget}
                  rel="noreferrer"
                  target="_blank"
                >
                  {attribution.linkText}
                </a>
              )}
              {attribution.text && <>&nbsp;{attribution.text}</>}
              &nbsp;
            </React.Fragment>
          )
        })}
      </p>
    )
  }

  const years = {}
  Object.values(comparisonMarkets).forEach((market) => {
    const countryData =
      cache[datasetName] && cache[datasetName][market.country_iso2_code]
    if (countryData) {
      Object.values(config.columns).forEach((columnConfig) => {
        if (columnConfig.year) {
          const year = columnConfig.year(countryData)
          if (year) {
            years[year] = (years[year] || 0) + 1
          }
        }
      })
    }
  })
  const baseYear = Object.keys(years).sort((a, b) => {
    return years[a] < years[b] ? 1 : -1
  })[0]

  const renderCell = (cellConfig, countryData) => {
    try {
      const value = cellConfig.render(countryData)
      if (!value) {
        throw new Error()
      }
      return (
        <>
          {value}
          {yearDiv((cellConfig.year || (() => null))(countryData), baseYear)}
        </>
      )
    } catch {
      return DATA_NA
    }
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
            <>{renderCell(cellConfig, countryData)}</>
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
        <th className="p-v-xs  p-f-l name relative">
          <button
            type="button"
            onClick={removeMarket}
            className="button button--only-icon button--tertiary button--small f-l"
            data-id={market.country_iso2_code}
            aria-label={`Remove ${market.country_name}`}
          >
            <i className="fa fa-trash-alt icon--border" />
          </button>
          <div className="body-l-b" id={`market-${market.country_name}`}>
            {market.country_name}
          </div>
        </th>
        {countryRow}
      </tr>
    )
  })

  return (
    <span>
      <table className={`m-v-0 border-blue-deep-20 valign-middle cache-version-${cacheVersion}`}>
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
                >
                  {config.columns[columnKey].name}
                  {config.columns[columnKey].tooltip && (
                    <div>
                      <Tooltip
                        title={cellConfig.tooltip.title}
                        content={cellConfig.tooltip.content}
                        position={cellConfig.tooltip.position}
                        className="text-align-left body-m"
                      />
                    </div>
                  )}
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody>{tableBody}</tbody>
      </table>
      {baseYear && (
        <div className="base-year body-m m-t-xs">
          Displaying data from {baseYear} unless otherwise indicated.
        </div>
      )}
      {config.sourceAttributions &&
        sourceAttribution(config.sourceAttributions)}
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
  }).isRequired,
  commodityCode: PropTypes.string.isRequired,
  removeMarket: PropTypes.func.isRequired,
  cacheVersion: PropTypes.number,
}
DataTable.defaultProps = {
  cacheVersion: null
}
