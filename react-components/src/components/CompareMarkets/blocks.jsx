import React from 'react'
import { Tooltip } from '@components/tooltip/Tooltip'

const DATA_NA = 'Data not available'
let baseYear = null

const yearDiv = (year) => {
  return (
    year &&
    String(year) !== baseYear && (
      <div className="body-m text-black-60 display-year">{year}</div>
    )
  )
}

const renderCell = (cellConfig, countryData) => {
  try {
    const value = cellConfig.render(countryData)
    if (!value) {
      throw new Error()
    }
    return (
      <>
        {value}
        {yearDiv((cellConfig.year || (() => null))(countryData))}
      </>
    )
  } catch {
    return DATA_NA
  }
}

const setBaseYear = (year) => {
  baseYear = year
}

const sourceAttribution = (attributions) => {
  // source attribution and base year
  return (
    <>
      {baseYear && (
        <div className="base-year body-m m-t-xs">
          Displaying data from {baseYear} unless otherwise indicated.
        </div>
      )}
      {attributions && (
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
      )}
    </>
  )
}

const renderColumnHeader = (columnConfig, mobile) => (
  <>
    {columnConfig.name}
    {columnConfig.tooltip && (
      <div>
        <Tooltip
          title={columnConfig.tooltip.title}
          content={columnConfig.tooltip.content}
          position={mobile ? 'left' : columnConfig.tooltip.position}
          className="text-align-left body-m"
        />
      </div>
    )}
  </>
)

const renderCountryRowHeader = (market, removeMarket) => {
  // A row header in normal or mobile mode is the country label. In mobile mode there is no 'remove' button
  return (
    <th className={`p-v-xs name`}>
      <div className='flex-center'>
      {(removeMarket && (
        <button
          type="button"
          onClick={removeMarket || (() => null)}
          className="button button--only-icon button--tertiary button--small m-r-xxs"
          data-id={market.country_iso2_code}
          aria-label={`Remove ${market.country_name}`}
        >
          <i className="fa fa-trash-alt icon--border" />
        </button>
      )) ||
        ''}
      <div className="body-l-b country-name" id={`marketheader-${market.country_name}`}>
        {market.country_name}
      </div>
      </div>
    </th>
  )
}

const renderMobileBlock = (
  dataSet,
  comparisonMarkets,
  columnKey,
  cellConfig
) => {
  // One white block in mobile layout. Entire block is for one column/data-point in normal view.
  // The block is a table with each row being for one country
  return Object.values(comparisonMarkets).map((market) => {
    const countryData = dataSet && dataSet[market.country_iso2_code]
    return (
      <tr key={`${market.country_iso2_code}:${columnKey}`}>
        {renderCountryRowHeader(market)}
        <td
          key={columnKey}
          className={`p-v-xs body-l ${cellConfig.className || ''}`}
        >
          {countryData &&
          (!countryData.loading || !countryData.loading[columnKey]) ? (
            <>{renderCell(cellConfig, countryData)}</>
          ) : (
            <div className="loading">&nbsp;</div>
          )}
        </td>
      </tr>
    )
  })
}

export default {
  renderMobileBlock,
  renderCountryRowHeader,
  renderColumnHeader,
  sourceAttribution,
  renderCell,
  setBaseYear,
}
