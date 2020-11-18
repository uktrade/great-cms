import React, {useState, useEffect} from "react";
import Services from '@src/Services'


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
      const countries = Object.values(comparisonMarkets).map(function (key) {
        return key.name
      })
      Services.getPopulationByCountryData(countries).then((result) => {
        setPopulationData(Object.entries(result))
      }).finally(() => {
      })
    }
  }, [props]);

  const comparisonMarkets = props.comparisonMarkets

  let dataTable
  if (comparisonMarkets && Object.keys(comparisonMarkets).length) {

    const tableBody = Object.values(comparisonMarkets).map(market => {
      let populationCountryData = getCountryData(market.name)
      return (<tr key={`market-${market.id}`}>
        <td className="p-b-xs p-v-xs"><span className="body-l-b" id={`market-${market.name}`}>{market.name}</span>
          <button type="button" className="iconic" onClick={props.removeMarket} data-id={market.id}
                  aria-label={`Remove ${market.name}`}><i className="fa fa-times-circle"/></button>
        </td>
        <td
          id={`market-total-population-${market.name}`}>{populationCountryData ? populationCountryData.total_population : ''}</td>
        <td
          id={`market-internet-usage-${market.name}`}>{populationCountryData && populationCountryData.internet_usage ? populationCountryData.internet_usage.value + '%' : 'Data not available'}</td>
        <td
          id={`market-urban-population-${market.name}`}>{populationCountryData ? populationCountryData.urban_population_percentage_formatted : ''}</td>
        <td
          id={`market-rural-population-${market.name}`}>{populationCountryData ? populationCountryData.rural_population_percentage_formatted : ''}</td>
        <td>{populationCountryData && populationCountryData.cpi ? populationCountryData.cpi.value : 'Data not available'}</td>
      </tr>)
    })
    dataTable = (
      <span>
        <table>
          <thead>
          <tr>
            <th></th>
            <th>Total population</th>
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


