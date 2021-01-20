import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { Tooltip } from '@components/tooltip/Tooltip'
import { isArray, isObject, mapArray } from '../../Helpers'

let cache = {}

export default function DataTable(props) {
  const {
    datasetName,
    config,
    comparisonMarkets,
    commodityCode,
    removeMarket,
  } = props
  const [, setLoading] = useState(true)

  useEffect(() => {
    // Wipe cache if commodity code changes
    if (cache.commodityCode !== commodityCode) {
      cache = { commodityCode }
    }
    cache[datasetName] = cache[datasetName] || {}
    const countries = Object.values(comparisonMarkets).map(
      (country) => country.country_name
    )
    const missingCountries = countries.filter(
      (country) => !cache[datasetName][country]
    )
    if (missingCountries.length) {
      setLoading(true)
      config.dataFunction(missingCountries, commodityCode)
        .then((result) => {
          let newData = result
          // If the result is an array, make an object keyed by country
          if (isArray(result)) {
            newData = mapArray(result, 'country')
          } else if (isObject(result) && !result[missingCountries[0]]) {
            newData = mapArray(Object.values(result), 'country')
          }
          // or it could be an object already keyed by country
          cache[datasetName] = Object.assign(cache[datasetName], newData)
          setLoading(false)
        })
        .catch(() => {
          missingCountries.forEach((country) => {
            cache[datasetName][country] = {}
          })
          setLoading(false)
        })
    } else {
      setLoading(false)
    }
  }, [commodityCode, comparisonMarkets])

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

  const tableBody = Object.values(comparisonMarkets).map((market) => {
    const countryData =
      cache[datasetName] && cache[datasetName][market.country_name]
    const countryRow = Object.keys(config.columns).map((columnKey) => {
      const cellConfig = config.columns[columnKey]
      return (
        <td key={columnKey} className={`${columnKey} ${cellConfig.className || ''}`}>
          {countryData ? (
            config.columns[columnKey].render(countryData)
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
        <td className="p-v-xs name nowrap">
            <button
              type="button"
              onClick={removeMarket}
              className="button button--only-icon button--tertiary button--small m-r-xxs"
              data-id={market.country_iso2_code}
              aria-label={`Remove ${market.country_name}`}
            >
              <i className="fa fa-trash-alt icon--border" />
            </button>
            <span className="body-l-b" id={`market-${market.country_name}`}>
              {market.country_name}
            </span>
        </td>
        {countryRow}
      </tr>
    )
  })

  return (
    <span>
      <table className="m-v-0 border-blue-deep-20 valign-middle">
        <thead>
          <tr>
            <th className="body-l-b">&nbsp;</th>
            {Object.keys(config.columns).map((columnKey) => {
              const cellConfig = config.columns[columnKey]
              return (
                <th className={`body-l-b ${columnKey} ${cellConfig.className || ''}`} key={columnKey}>
                  {config.columns[columnKey].name}
                  {config.columns[columnKey].tooltip && (
                    <div>
                      <Tooltip title={cellConfig.tooltip.title} 
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
  }).isRequired,
  commodityCode: PropTypes.string.isRequired,
  removeMarket: PropTypes.func.isRequired,
}
