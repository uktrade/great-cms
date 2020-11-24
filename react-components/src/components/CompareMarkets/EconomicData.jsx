import React, {useState, useEffect} from "react";
import Services from '@src/Services'



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
      const countries = Object.values(comparisonMarkets).map(function (key) {
        return key.name
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
      let data = getCountryData(market.name)
       return (<tr key={`market-${market.id}`}>
        <td className="p-b-xs p-v-xs"><span className="body-l-b" id={`market-${market.name}`}>{market.name}</span>
          <button type="button" className="iconic" onClick={props.removeMarket} data-id={market.id}
                  aria-label={`Remove ${market.name}`}><i className="fa fa-times-circle"/></button>
        </td>
        <td id={`market-total-population-${market.name}`}>{data && data.import_from_world ? data.import_from_world.trade_value : DATA_NA}</td>
        <td id={`market-total-population-${market.name}`}>{data && data.import_from_world &&  data.import_from_world.year_on_year_change ? data.import_from_world.year_on_year_change + '%' : DATA_NA}</td>
        <td id={`market-total-population-${market.name}`}>{data && data.import_data_from_uk ? data.import_data_from_uk.trade_value : DATA_NA}</td>
        <td id={`market-total-population-${market.name}`}>{DATA_NA}</td>
        <td id={`market-total-population-${market.name}`}>{DATA_NA}</td>
        <td id={`market-total-population-${market.name}`}>{data && data.country_data ? data.country_data.ease_of_doing_bussiness.year_2019 : DATA_NA}</td>
        <td id={`market-total-population-${market.name}`}>{data && data.corruption_perceptions_index ? data.country_data.corruption_perceptions_index.rank : DATA_NA}</td>

      </tr>)
    })
    dataTable = (
      <span>
        <table>
          <thead>
          <tr>
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


