import React, { useState, useEffect } from 'react'
import PropTypes from 'prop-types'
import { isArray } from '../../Helpers'

const cache = {}

export default function DataTable(props) {
  const {
    datasetName,
    columns,
    comparisonMarkets,
    commodityCode,
    removeMarket,
    sourceAttributions,
    dataFunction,
  } = props
  const [, setLoading] = useState(true)

  useEffect(() => {
    cache[datasetName] = cache[datasetName] || {}
    const countries = Object.values(comparisonMarkets).map(
      (country) => country.country_name
    )
    const missingCountries = countries.filter((country) => !cache[datasetName][country])
    if (missingCountries.length) {
      setLoading(true)
      dataFunction(missingCountries, commodityCode)
        .then((result) => {
          let newData = result
          // If the result is an array, make an object keyed by country
          if (isArray(result)) {
            const out = {}
            result.forEach((entry) => {
              out[entry.country] = entry
            })
            newData = out
          }
          // or it could be an object already keyed by country
          cache[datasetName] = Object.assign(cache[datasetName], newData)
          setLoading(false)
        })
        .finally(() => {})
    } else {
      setLoading(false)
    }
  }, [commodityCode, comparisonMarkets])

  const sourceAttribution = (attributions) => {
    return (
      <p className="source-attribution body-s m-r-s">
        {attributions.map((attribution) => {
          return (
            <React.Fragment key={`attr-${attribution.title}`}>
              <strong className="body-s-b">{attribution.title}</strong>
              {attribution.preLinkText && (
                <>
                  &nbsp;{attribution.preLinkText}&nbsp;
                </>
              )}
              :&nbsp;
              {attribution.linkTarget && (
                <a href={attribution.linkTarget}  
                  rel="noreferrer" 
                  target="_blank"
                >
                  {attribution.linkText}
                </a>
              )}
              {attribution.text && (
                <>&nbsp;{attribution.text}&nbsp;</>
              )}
            </React.Fragment>
          )
        })}
      </p>
    )
  }

  const tableBody = Object.values(comparisonMarkets).map((market) => {
    const countryData =
      cache[datasetName] && cache[datasetName][market.country_name]
    const countryRow = Object.keys(columns).map((columnKey) => {
      return (
        <td key={columnKey} className={`${columnKey}`}>
          {countryData ? (
            columns[columnKey].render(countryData)
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
        <td className="p-v-xs name">
          <div style={{ whiteSpace: 'nowrap' }}>
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
          </div>
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
            <th className="body-s-b">&nbsp;</th>
            {Object.keys(columns).map((columnKey) => {
              return (
                <th className="body-s-b" key={columnKey}>
                  {columns[columnKey].name}
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody>{tableBody}</tbody>
      </table>
      {sourceAttributions && sourceAttribution(sourceAttributions)}
    </span>
  )
}

DataTable.propTypes = {
  datasetName: PropTypes.string.isRequired,
  columns: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
      render: PropTypes.func,
    })
  ).isRequired,
  comparisonMarkets: PropTypes.instanceOf(Array).isRequired,
  commodityCode: PropTypes.string.isRequired,
  removeMarket: PropTypes.func.isRequired,
  sourceAttributions: PropTypes.arrayOf(
    PropTypes.shape({
      name: PropTypes.string,
    })
  ).isRequired,
  dataFunction: PropTypes.func.isRequired,
}
