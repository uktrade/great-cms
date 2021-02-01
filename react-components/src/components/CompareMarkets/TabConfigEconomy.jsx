import React from 'react'
import Services from '@src/Services'
import { normaliseValues, get, millify } from '../../Helpers'

const rankOutOf = (data, key) => {
  return (
    <>
      {data[key]} of {data.total}
    </>
  )
}

const sign = (value) => {
  return ['-', '', '+'][Math.sign(value) + 1]
}

const importValueAndChange = (importValue) => {
  if (!importValue.trade_value_raw) {
    throw new Error();
  }
  return (
    <>
      <div className="body-l primary">
        {millify(importValue.trade_value_raw)}
      </div>
      {importValue.year_on_year_change && (
        <div className="body-m secondary text-black-60">
          {sign(importValue.year_on_year_change)}
          {normaliseValues(importValue.year_on_year_change)}% vs{' '}
          {importValue.year - 1}
        </div>
      )}
    </>
  )
}

export default {
  sourceAttributions: [
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
  ],
  columns: {
    'world-import-value': {
      name: 'Worldwide import value (USD)',
      className: 'text-align-right',
      render: (data) => importValueAndChange(data.import_from_world),
      year: (data) => get(data, 'import_from_world.year'),
      group: 'import',
    },
    'uk-import-value': {
      name: 'Import value from the UK (USD)',
      className: 'text-align-right',
      render: (data) => importValueAndChange(data.import_data_from_uk),
      year: (data) => get(data, 'import_data_from_uk.year'),
      group: 'import',
    },
    'avg-income': {
      name: 'Adjusted net national income per capita (USD)',
      className: 'text-align-right',
      render: (data) => millify(get(data, 'country_data.income.value')),
      year: (data) => get(data, 'country_data.income.year'),
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>Adjusted net national income per capita (ANNIPC) measures the average income of consumers in a country.</p>
          <p>Each year, the World Bank publishes figures for all countries by taking the gross national income, minus fixed income and natural resource consumption, and dividing it by the total population.</p>
          <p>ANNIPC gives you an idea of how much consumers in your country earn, whether they can comfortably afford your products and at what price.</p>
         `,
      },
    },
    'eod-business': {
      name: 'Ease of doing business rank ',
      className: 'text-align-right',
      render: (data) =>
        rankOutOf(data.country_data.ease_of_doing_bussiness, 'rank'),
      year: (data) => get(data, 'country_data.ease_of_doing_bussiness.year'),
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>The Ease of Doing Business rank indicates whether doing business in a country is easy or difficult.</p>
          <p>Every year, the World Bank ranks all countries from 1 (easy to do business) to 190 (hard to do business).</p>
          <p>Knowing the rank of your target country can help you decide whether to enter a market and whether you need professional help to do so.</p>
         `,
      },
    },
    cpi: {
      name: 'Corruption Perceptions Index',
      className: 'text-align-right',
      render: (data) =>
        rankOutOf(data.country_data.corruption_perceptions_index, 'rank'),
      year: (data) =>
        get(data, 'country_data.corruption_perceptions_index.year'),
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>The Corruption Perceptions Index is published every year by Transparency International.</p>
          <p>The index ranks countries and territories by the corruption of their public sector, according to experts and business people. Here we use a rank from 1 (clean) to 180 (highly corrupt).</p>
          <p>This gives you an idea of how easy or difficult it is to deal with local officials and businesses, and to get paid.</p>
         `,
      },
    },
  },
  groups: {
    import: {
      dataFunction: Services.getComTradeData,
      splitCountriesSequential: true,
    },
  },
  dataFunction: Services.getCountryData,
}
