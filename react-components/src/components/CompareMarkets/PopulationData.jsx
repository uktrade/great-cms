import React, {useState, useEffect} from "react";
import Services from '@src/Services'
import {useCookies} from 'react-cookie';
import {normaliseValues} from '../../Helpers'


export default function PopulationData(props) {
  const [populationData, setPopulationData] = useState([])

  const getCountryData = (country) => {
    if (populationData && populationData.length) {
      const country_data = Object.values(populationData).find(x => x[1].country === country)
      return country_data ? country_data[1] : []
    }
  }

  useEffect(() => {
    if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
      const countries = Object.values(comparisonMarkets).map((country) => {
        return country.country_name
      })
      Services.getPopulationByCountryData(countries).then((result) => {
        setPopulationData(Object.entries(result))
      }).finally(() => {})
    }
  }, [props]);



  const comparisonMarkets = props.comparisonMarkets

  let dataTable
  if (comparisonMarkets && Object.keys(comparisonMarkets).length) {

    const tableBody = Object.values(comparisonMarkets).map(market => {
      const populationCountryData = getCountryData(market.country_name)
      let populationCountryRow

      if (populationCountryData) {
        populationCountryRow = (
          <React.Fragment>
            <td className="total-population">{normaliseValues(populationCountryData.total_population)}</td>
            <td
              className="internet-usage">{populationCountryData.internet_usage ? normaliseValues(`${populationCountryData.internet_usage.value}%`) : 'Data not available'}</td>
            <td className="urban-population">
              <h1>{normaliseValues(populationCountryData.urban_population_percentage_formatted)[0]}</h1>
              <span
                className="body-m">{normaliseValues(populationCountryData.urban_population_percentage_formatted)[1]}</span>
            </td>
            <td className="rural-population">
              <h1>{normaliseValues(populationCountryData.rural_population_percentage_formatted)[0]}</h1>
              <span
                className="body-m">{normaliseValues(populationCountryData.rural_population_percentage_formatted)[1]}</span>
            </td>
            <td>{populationCountryData.cpi ? populationCountryData.cpi.value : 'Data not available'}</td>
          </React.Fragment>
        )
      } else {
        populationCountryRow = (
          <td colSpan="5" className="no-data">Data is not currently available for this country</td>
        )
      }

      return (
        <tr key={`market-${market.country_iso2_code}`} id={`market-${market.country_name}`}>
          <td className="p-v-xs name">
            <div style={{whiteSpace: 'nowrap'}}>
              <button type="button"
                      onClick={props.removeMarket}
                      className="iconic"
                      data-id={market.country_iso2_code}
                      aria-label={`Remove ${market.country_name}`}>
                <i className="fa fa-trash-alt icon--border"/>
              </button>
              <span className="body-l-b" id={`market-${market.country_name}`}>{market.country_name}</span>
            </div>
          </td>
          {populationCountryRow}
        </tr>
      )
    })
    dataTable = (
      <span>
        <table>
          <thead>
          <tr className="body-l-b">
            <th>&nbsp;</th>
            <th>Total Population </th>
            <th>Access to internet</th>
            <th>Living in urban areas</th>
            <th>Living in rural areas</th>
            <th>Consumer Price Index</th>
          </tr>
          </thead>
          <tbody>
          {tableBody}
          </tbody>
        </table>

      </span>
    )
  }

  return (
    <div>
      {dataTable}
    </div>
  )
}

