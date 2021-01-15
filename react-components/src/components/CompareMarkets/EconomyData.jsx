import React from 'react'
import PropTypes from 'prop-types'
import Services from '@src/Services'
import { normaliseValues, get } from '../../Helpers'
import DataTable from './DataTable'

export default function EconomyData(props) {
  const { comparisonMarkets, selectedProduct, removeMarket, active } = props

  const sourceAttributionList = [
    {
      title: 'Trade data',
      linkText: 'UN Comtrade',
      linkTarget: 'https://comtrade.un.org/data',
      text: 'Copyright United Nations 2020.',
    },
    {
      title: 'GDP per capita',
      preLinkText: '(current US$)',
      linkText: 'World Bank, OECD',
      linkTarget: 'https://data.worldbank.org/indicator/NY.GDP.PCAP.CD',
      text: 'CC BY 4.0.',
    },
    {
      title: 'Ease of Doing Business Scores',
      linkText: 'World Bank',
      linkTarget: 'https://www.doingbusiness.org/en/data/doing-business-score',
      text: 'CC BY 4.0.',
    },
    {
      title: 'Corruption Perceptions Index',
      linkText: 'Transparency International',
      linkTarget: 'https://www.transparency.org/en/cpi/2019/results/table',
      text: 'CC BY-ND 4.0',
    },
  ]

  const DATA_NA = 'Data not available'

  const getAndFormat = (data, key, unit = '') => {
    const value = get(data, key)
    return value !== undefined ? `${normaliseValues(value)}${unit}` : DATA_NA
  }

  const columns = {
    'world-import-value': {
      name: `Total ${selectedProduct.commodity_name.toLowerCase()} import value (USD)`,
      render: (data) => getAndFormat(data, 'import_from_world.trade_value'),
    },
    'year-on-year-change': {
      name: `Year-to-year ${selectedProduct.commodity_name.toLowerCase()} import value change`,
      render: (data) =>
        getAndFormat(data, 'import_from_world.year_on_year_change', '%'),
    },
    'uk-import-value': {
      name: `${selectedProduct.commodity_name} import value from the UK (USD)`,
      render: (data) => getAndFormat(data, 'import_data_from_uk.trade_value'),
    },
    gdp: {
      name: 'GDP per capita(USD)',
      render: (data) =>
        getAndFormat(data, 'country_data.gdp_per_capita.year_2019'),
    },
    'avg-income': {
      name: 'Avg income(USD)',
      render: (data) => getAndFormat(data, 'country_data.income.value'),
    },
    'eod-business': {
      name: 'Ease of doing business rank',
      render: (data) =>
        getAndFormat(data, 'country_data.ease_of_doing_bussiness.year_2019'),
    },
    cpi: {
      name: 'Corruption Perceptions Index',
      render: (data) =>
        getAndFormat(data, 'country_data.corruption_perceptions_index.rank'),
    },
  }

  return (
    active && (
      <DataTable
        datasetName="economy"
        columns={columns}
        comparisonMarkets={comparisonMarkets}
        commodityCode={get(selectedProduct, 'commodity_code')}
        removeMarket={removeMarket}
        sourceAttributions={sourceAttributionList}
        dataFunction={Services.getComTradeData}
      />
    )
  )
}

EconomyData.propTypes = {
  comparisonMarkets: PropTypes.instanceOf(Object).isRequired,
  selectedProduct: PropTypes.shape({
    commodity_name: PropTypes.string,
    commodity_code: PropTypes.string,
  }).isRequired,
  removeMarket: PropTypes.func.isRequired,
  active: PropTypes.bool.isRequired,
}
