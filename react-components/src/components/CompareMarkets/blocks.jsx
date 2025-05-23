import React from 'react'
import { Tooltip } from '@components/tooltip/Tooltip'
import { isFunction } from '@src/Helpers'

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

const renderColumnHeader = (columnConfig, context, mobile) => {
  const columnName = isFunction(columnConfig.name)
    ? columnConfig.name(context)
    : columnConfig.name
  return (
    <>
      {!mobile ? columnName : ''}
      {columnConfig.tooltip && (
        <div className={mobile ? 'f-r' : ''}>
          <Tooltip
            title={columnConfig.tooltip.title || `What is '${columnName}'?`}
            content={columnConfig.tooltip.content}
            position={mobile ? 'right' : columnConfig.tooltip.position}
            showTitle={columnConfig.tooltip.showTitle || false}
            className="text-align-left body-m"
          />
        </div>
      )}
      {mobile ? columnName : ''}
    </>
  )
}
const renderRemoveButton = ({ market, removeMarket }) => (
  <button
    type="button"
    onClick={removeMarket || (() => null)}
    className="button button--tiny-toggle remove-market"
    data-id={market.country_iso2_code}
    aria-label={`Remove ${market.country_name} from table`}
  >
    <span className="great-icon fa fa-trash-alt great-red-text" />
  </button>
)

const renderAddRemoveShortlist = ({
  market,
  selectedMarkets,
  addRemoveShortlist,
}) => {
  const iso = market.country_iso2_code
  return (
    <>
      <input
        onChange={() => addRemoveShortlist(market, !selectedMarkets[iso])}
        type="checkbox"
        className="checkbox-favourite"
        id={`cb-${iso}`}
        checked={!!selectedMarkets[iso]}
      />
      <label
        htmlFor={`cb-${iso}`}
        className="far"
        aria-label={`${market.country_name} shortlisted`}
      />
    </>
  )
}

const renderCountryName = ({ market }) => (
  <div
    className="body-l-b country-name"
    id={`marketheader-${market.country_name}`}
  >
    {market.country_name}
  </div>
)

const renderCountryRowHeader = ({
  market,
  removeMarket,
  config,
  selectedMarkets,
  addRemoveShortlist,
}) => {
  // A row header in normal mode.
  const iso = market.country_iso2_code
  const headingClass = `
    ${(config && config.headingClass) || ''} ${'table-highlight'}
  `
  return (
    <>
      <td className={`p-h-s ${headingClass}`} >
        {renderRemoveButton({ market, removeMarket })}
      </td>
      <th className={`p-v-xs name ${headingClass} table--width`} scope="row">
        {renderCountryName({ market })}
      </th>
      <td key={iso} className={`p-v-xs ${headingClass}`}>
        {renderAddRemoveShortlist({
          market,
          selectedMarkets,
          addRemoveShortlist,
        })}
      </td>
    </>
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
        <th className="p-v-xs name" scope="row">
          {renderCountryName({ market })}
        </th>
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
  renderAddRemoveShortlist,
  renderRemoveButton,
  renderCountryName,
  sourceAttribution,
  renderCell,
  setBaseYear,
}
