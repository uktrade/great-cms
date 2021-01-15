import React from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
<<<<<<< HEAD
import { normaliseValues } from '../../Helpers'
=======
import { normaliseValues, get } from '../../Helpers'
import DataTable from './DataTable'

>>>>>>> GP2-1318_Compare_markets_data_table_refactor

export default function PopulationData(props) {
  const { comparisonMarkets, selectedProduct, removeMarket, active } = props

  const headingAndBody = (value) => {
    return (<>
      <h1>{ normaliseValues(value)[0]}</h1>
      <span className="body-m">{normaliseValues(value)[1]}</span>
    </>)
  }

  const sourceAttributionList = [
    {
      title: 'Population data',
      linkText: 'United Nations',
      linkTarget: 'https://population.un.org/wup/Download/',
      text: 'CC BY 3.0 IGO.'
    },
    {
      title: 'Urban and Rural Populations',
      linkText: 'United Nations',
      linkTarget: 'https://population.un.org/wup/Download/',
      text: 'CC BY 3.0 IGO.'
    },
    {
      title: 'Access to internet',
      linkText: 'International Telecommunications Union',
      linkTarget: 'https://www.itu-ilibrary.org/science-and-technology/data/world-telecommunication-ict-indicators-database_pub_series/database/2a8478f7-en',
    },
  ]

  const columns= {
    'total_population': {
      name:'Total Population',
      render: (data) => normaliseValues(data.total_population),
    },
    'internet_usage': {
      name:'Access to internet',
      render: (data) => data.internet_usage ? normaliseValues(`${data.internet_usage.value}%`)
                : 'Data not available'
    },
    'urban_population': {
      name:'Living in urban areas',
      render: (data) => headingAndBody(data.urban_population_percentage_formatted),
    },
    'rural_population': {
      name:'Living in rural areas',
      render: (data) => headingAndBody(data.rural_population_percentage_formatted),      
    },
    'cpi': {
      name:'Consumer Price Index',
      render: (data) => get(data,'cpi.value') || 'Data not available'  
    },
  }
  return (active && <DataTable
    datasetName="population"
    columns={columns}
    comparisonMarkets={comparisonMarkets}
    commodityCode={get(selectedProduct,'commodity_code')}
    removeMarket={removeMarket}
    sourceAttributions={sourceAttributionList}
    dataFunction={Services.getPopulationByCountryData}
  />)
}

PopulationData.propTypes = {
  comparisonMarkets: PropTypes.instanceOf(Object).isRequired,
  selectedProduct: PropTypes.shape({
    commodity_name: PropTypes.string,
    commodity_code: PropTypes.string,
  }).isRequired,
  removeMarket: PropTypes.func.isRequired,
  active: PropTypes.bool.isRequired,
}
