import React, {useState, useEffect} from "react";
import Services from '@src/Services'
import {normaliseValues} from '../../Helpers'

export default function EconomyData(props) {
  const [economyData, setEconomyData] = useState([])

    const getCountryData = (country) => {
      if (economyData && economyData.length) {
        const country_data = Object.values(economyData).find(x => x[0] === country)
        return country_data ? country_data[1] : []
    }
  }

  useEffect(() => {
    if (comparisonMarkets && Object.keys(comparisonMarkets).length) {
      const countries = Object.values(comparisonMarkets).map(function (country) {
        return country.country_name
      })

      Services.getComTradeData(countries, props.selectedProduct.code).then((result) => {
        setEconomyData(Object.entries(result))
      }).finally(() => {
      })
    }
  }, [props]);

  const comparisonMarkets = props.comparisonMarkets
  let DATA_NA = 'Data not available'
  let dataTable
  if (comparisonMarkets && Object.keys(comparisonMarkets).length) {

    const tableBody = Object.values(comparisonMarkets).map(market => {
      let data = getCountryData(market.country_name)
      let  dataRow
       if (data) {
        dataRow = (
          <React.Fragment>
            <td id={`market-total-population-${market.country_name}`}>{data && data.import_from_world ? data.import_from_world.trade_value : DATA_NA}</td>
            <td id={`market-total-population-${market.country_name}`}>{data && data.import_from_world &&  data.import_from_world.year_on_year_change ? data.import_from_world.year_on_year_change + '%' : DATA_NA}</td>
            <td id={`market-total-population-${market.country_name}`}>{data && data.import_data_from_uk ? data.import_data_from_uk.trade_value : DATA_NA}</td>
            <td id={`market-total-population-${market.country_name}`}>{data && data.country_data && data.country_data.gdp_per_capita ? normaliseValues(data.country_data.gdp_per_capita.year_2019) : DATA_NA}</td>
            <td id={`market-total-population-${market.country_name}`}>{DATA_NA}</td>
            <td id={`market-total-population-${market.country_name}`}>{data && data.country_data && data.country_data.ease_of_doing_bussiness ? data.country_data.ease_of_doing_bussiness.year_2019 : DATA_NA}</td>
            <td id={`market-total-population-${market.country_name}`}>{data && data.country_data && data.country_data.corruption_perceptions_index ? data.country_data.corruption_perceptions_index.rank : DATA_NA}</td>

          </React.Fragment>
        )} else {
           dataRow = (
          <td colSpan="5" className="no-data">Data is not currently available for this country</td>
        )
       }
       return (<tr key={`market-${market.country_name}`}>
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
        {dataRow}
      </tr>)
    })
    dataTable = (
      <span>
        <table>
          <thead>
          <tr className="body-l-b">
            <th></th>
            <th>Total {props.selectedProduct.name.toLowerCase()} import value (USD)</th>
            <th>Year-to-year {props.selectedProduct.name.toLowerCase()} import value change</th>
            <th>{props.selectedProduct.name} import value from the UK (USD)</th>
            <th>GDP per capita(USD)</th>
            <th>Avg income(USD)</th>
            <th>Ease of doing business rank</th>
            <th>Corruption Perceptions Index</th>
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

