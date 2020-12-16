import React, { useState, useEffect } from 'react'
import Services from '@src/Services'
import { useCookies } from 'react-cookie'
import { normaliseValues } from '../../Helpers'

export default function PopulationData(props) {
  const [populationData, setPopulationData] = useState([])

  const getCountryData = (country) => {
    if (populationData && populationData.length) {
      const country_data = Object.values(populationData).find(
        (x) => x[1].country === country
      )
      return country_data ? country_data[1] : []
    }
  }

  useEffect(() => {
    if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
      const countries = Object.values(comparisonMarkets).map((country) => {
        return country.country_name
      })
      Services.getPopulationByCountryData(countries)
        .then((result) => {
          setPopulationData(Object.entries(result))
        })
        .finally(() => {})
    }
  }, [props])

  const comparisonMarkets = props.comparisonMarkets

  const sourceAttribution = (
    <p className="source-attribution body-s">
      Population data: <a href="https://population.un.org/wpp/Download/Standard/Population/" target="_blank">United Nations</a>
      &nbsp;CC BY 3.0 IGO. Urban and Rural Populations:&nbsp;
      <a href="https://population.un.org/wup/Download/" target="_blank">United Nations</a>
      &nbsp;CC BY 3.0 IGO. ICT Indicators Edition 2019/2:&nbsp;
      <a href="https://www.itu-ilibrary.org/science-and-technology/data/world-telecommunication-ict-indicators-database_pub_series/database/2a8478f7-en" target="_blank">ITU (2020)</a>
    </p>
  )

  let dataTable
  if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
    const tableBody = Object.values(comparisonMarkets).map((market) => {
      const populationCountryData = getCountryData(market.country_name)
      let populationCountryRow

      if (populationCountryData) {
        populationCountryRow = (
          <React.Fragment>
            <td className="total-population">
              {normaliseValues(populationCountryData.total_population)}
            </td>
            <td className="internet-usage">
              {populationCountryData.internet_usage
                ? normaliseValues(
                    `${populationCountryData.internet_usage.value}%`
                  )
                : 'Data not available'}
            </td>
            <td className="urban-population">
              <h1>
                {
                  normaliseValues(
                    populationCountryData.urban_population_percentage_formatted
                  )[0]
                }
              </h1>
              <span className="body-m">
                {
                  normaliseValues(
                    populationCountryData.urban_population_percentage_formatted
                  )[1]
                }
              </span>
            </td>
            <td className="rural-population">
              <h1>
                {
                  normaliseValues(
                    populationCountryData.rural_population_percentage_formatted
                  )[0]
                }
              </h1>
              <span className="body-m">
                {
                  normaliseValues(
                    populationCountryData.rural_population_percentage_formatted
                  )[1]
                }
              </span>
            </td>
            <td>
              {populationCountryData.cpi
                ? populationCountryData.cpi.value
                : 'Data not available'}
            </td>
          </React.Fragment>
        )
      } else {
        populationCountryRow = (
          <td colSpan="5" className="no-data">
            No data currently available for this country
          </td>
        )
      }

      return (
        <tr
          key={`market-${market.country_iso2_code}`}
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
              <span className="body-l-b" id={`market-${market.country_name}`}>
                {market.country_name}
              </span>
            </div>
          </td>
          {populationCountryRow}
        </tr>
      )
    })
    dataTable = (
      <span>
        <table className="m-v-0">
          <thead>
            <tr>
              <th className="body-s-b">&nbsp;</th>
              <th className="body-s-b">Total Population </th>
              <th className="body-s-b">Access to internet</th>
              <th className="body-s-b">Living in urban areas</th>
              <th className="body-s-b">Living in rural areas</th>
              <th className="body-s-b">Consumer Price Index</th>
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
