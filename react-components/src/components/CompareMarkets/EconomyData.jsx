import React, { useState, useEffect } from 'react'
import Services from '@src/Services'
import { normaliseValues } from '../../Helpers'

export default function EconomyData(props) {
  const [economyData, setEconomyData] = useState([])

  const getCountryData = (country) => {
    if (economyData && economyData.length) {
      const country_data = Object.values(economyData).find(
        (x) => x[0] === country
      )
      return country_data ? country_data[1] : []
    }
  }

  useEffect(() => {
    if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
      const countries = Object.values(comparisonMarkets).map(function (
        country
      ) {
        return country.country_name
      })

      Services.getComTradeData(countries, props.selectedProduct.commodity_code)
        .then((result) => {
          setEconomyData(Object.entries(result))
        })
        .finally(() => {})
    }
  }, [props])

  const comparisonMarkets = props.comparisonMarkets

  const sourceAttribution = (
    <p className="source-attribution body-s">
      <strong className="body-s-b">
        Trade data
      </strong>
      :&nbsp;
      <a
        href="https://comtrade.un.org/data"
        target="_blank"
      >
        UN Comtrade
      </a>
      &nbsp;Copyright United Nations 2020.&nbsp;
      <strong className="body-s-b">
        GDP per capita
      </strong>
      &nbsp;(current US$):&nbsp;
      <a
        href="https://data.worldbank.org/indicator/NY.GDP.PCAP.CD"
        target="_blank"
      >
        World Bank, OECD
      </a>
      &nbsp;CC BY 4.0.&nbsp;
      <strong className="body-s-b">
        Ease of Doing Business Scores
      </strong>
      :&nbsp;
      <a
        href="https://www.doingbusiness.org/en/data/doing-business-score"
        target="_blank"
      >
        World Bank
      </a>
      &nbsp;CC BY 4.0.&nbsp;
      <strong className="body-s-b">
        Corruption Perceptions Index
      </strong>
      :&nbsp;
      <a
        href="https://www.transparency.org/en/cpi/2019/results/table"
        target="_blank"
      >
        Transparency International
      </a>
      &nbsp;CC BY-ND 4.0
    </p>
  )

  let DATA_NA = 'Data not available'
  let dataTable
  if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
    const tableBody = Object.values(comparisonMarkets).map((market) => {
      let data = getCountryData(market.country_name)
      let dataRow
      if (data) {
        dataRow = (
          <React.Fragment>
            <td className="world-import-value">
              {data && data.import_from_world
                ? normaliseValues(data.import_from_world.trade_value)
                : DATA_NA}
            </td>
            <td className="year-on-year-change">
              {data &&
              data.import_from_world &&
              data.import_from_world.year_on_year_change
                ? normaliseValues(data.import_from_world.year_on_year_change) +
                  '%'
                : DATA_NA}
            </td>
            <td className="uk-import-value">
              {data && data.import_data_from_uk
                ? normaliseValues(data.import_data_from_uk.trade_value)
                : DATA_NA}
            </td>
            <td className="gdp">
              {data && data.country_data && data.country_data.gdp_per_capita
                ? normaliseValues(data.country_data.gdp_per_capita.year_2019)
                : DATA_NA}
            </td>
            <td className="avg-income">{DATA_NA}</td>
            <td className="eod-business">
              {data &&
              data.country_data &&
              data.country_data.ease_of_doing_bussiness
                ? data.country_data.ease_of_doing_bussiness.year_2019
                : DATA_NA}
            </td>
            <td className="cpi">
              {data &&
              data.country_data &&
              data.country_data.corruption_perceptions_index
                ? data.country_data.corruption_perceptions_index.rank
                : DATA_NA}
            </td>
          </React.Fragment>
        )
      } else {
        dataRow = (
          <td colSpan="7" className="no-data">
            No data currently available for this country
          </td>
        )
      }
      return (
        <tr
          key={`market-${market.country_name}`}
          id={`market-${market.country_name}`}
        >
          <td className="p-v-xs name">
            <div style={{ whiteSpace: 'nowrap' }}>
              <button
                type="button"
                onClick={props.removeMarket}
                className="iconic"
                data-id={market.country_iso2_code}
                aria-label={`Remove ${market.country_name}`}
              >
                <i className="fa fa-trash-alt icon--border" />
              </button>
              <span
                className={`market-${market.country_name}` + ' ' + 'body-l-b'}
              >
                {market.country_name}
              </span>
            </div>
          </td>
          {dataRow}
        </tr>
      )
    })
    dataTable = (
      <span>
        <table className="m-v-0">
          <thead>
            <tr>
              <th className="body-s-b"></th>
              <th className="body-s-b">
                Total {props.selectedProduct.commodity_name.toLowerCase()} import value
                (USD)
              </th>
              <th className="body-s-b">
                Year-to-year {props.selectedProduct.commodity_name.toLowerCase()} import
                value change
              </th>
              <th className="body-s-b">
                {props.selectedProduct.commodity_name} import value from the UK (USD)
              </th>
              <th className="body-s-b">GDP per capita(USD)</th>
              <th className="body-s-b">Avg income(USD)</th>
              <th className="body-s-b">Ease of doing business rank</th>
              <th className="body-s-b">Corruption Perceptions Index</th>
            </tr>
          </thead>
          <tbody>{tableBody}</tbody>
        </table>
        {sourceAttribution}
      </span>
    )
  }

  return <div>{dataTable}</div>
}
