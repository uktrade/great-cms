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
  return ['', '', '+'][Math.sign(value) + 1]
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
          {importValue.last_year}
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
      title: 'Adjusted net national income per capita',
      preLinkText: '(current US$)',
      linkText: 'World Bank',
      linkTarget: 'https://data.worldbank.org/indicator/NY.ADJ.NNTY.PC.CD',
      text: 'CC BY 4.0.',
    },
    {
      title: 'Ease of Doing Business Rank',
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
      render: (data) => millify(data.Income.value),
      year: (data) => get(data, 'Income.year'),
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>Adjusted net national income per capita (ANNIPC) measures the average income of consumers.</p>
          <p>Each year, the World Bank calculates ANNIPC by taking the gross national income, minus fixed income and natural resource consumption, and dividing it by the total population.</p>
          <p>ANNIPC gives you an idea of how much consumers earn, whether they can comfortably afford your products and at what price.</p>
         `,
      },
    },
    'eod-business': {
      name: 'Ease of doing business rank',
      className: 'text-align-right',
      render: (data) => rankOutOf(data.EaseOfDoingBusiness, 'rank'),
      year: (data) => get(data, 'EaseOfDoingBusiness.year'),
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>The Ease of Doing Business rank indicates how easy or hard it is to do business somewhere.</p>
          <p>The rank is from 1 (easy to do business) to 190 (hard to do business).</p>
          <p>This  can help you decide whether to export somewhere and whether you need professional help to do so.</p>
         `,
      },
    },
    cpi: {
      name: 'Corruption Perceptions Index',
      className: 'text-align-right',
      render: (data) => {
        return rankOutOf(data.CorruptionPerceptionsIndex, 'rank')
      },
      year: (data) =>
        get(data, 'CorruptionPerceptionsIndex.year'),
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>The Corruption Perceptions Index is published every year by Transparency International.</p>
          <p>The index ranks  public-sector corruption  according to experts and business people. Here we use a rank from 1 (clean) to 180 (highly corrupt).</p>
          <p>This gives you an idea of how easy or difficult it is to deal with local officials and businesses, and to get paid.</p>
         `,
      },
    },
  },
  groups: {
    import: {
      dataFunction: Services.getComTradeData,
    },
  },
  dataFunction: (countries) => {
    return Services.getCountryData(countries, ['ConsumerPriceIndex','Income','CorruptionPerceptionsIndex','EaseOfDoingBusiness'])
  },
}
