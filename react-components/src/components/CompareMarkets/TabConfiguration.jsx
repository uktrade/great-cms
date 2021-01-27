import React from 'react'
import Services from '@src/Services'
import { normaliseValues, get, millify, capitalize, stripPercentage } from '../../Helpers'

const DATA_NA = 'Data not available'

const populationPercentActual = (group, population) => {
  if (group && population) {
    const percentage = Math.round((group * 100) / population)
    return (
      <>
        <div className="body-l primary">{percentage}%</div>
        <div className="body-m secondary">{millify(group)} </div>
      </>
    )
  }
  return DATA_NA
}

const rankOutOf = (data, key) => {
  return (
    (data && data[key] && (
      <>
        {data[key]} of {data.total}
      </>
    )) ||
    DATA_NA
  )
}

const formatEntry = (data) => {
  const name = stripPercentage(data.name)
  const percent = data.percent ? normaliseValues(data.percent, 0) : ''

  return percent ? (name + ' - ' + percent + '%') : name
}

const getEntries = (list = {}) => {
  const maxEntries = 5
  const entries = Object.keys(list || {})
    .filter(key => list[key].name)
    .slice(0, maxEntries)
    .map((key) => {
      return (
        <div className="entry body-l" key={key}>
          {formatEntry(list[key])}
        </div>
      )
    })
  return entries
}

const language = (data) => {
  const entries = getEntries(get(data, 'language'))

  if (data && entries) {
    const year = get(data, 'date')
    const note = get(data, 'note')

    return (
      <>
        {entries}
        <div className="body-m text-black-60 display-note">
          {year}{year && note && ". "}{note && capitalize(note)}
        </div>
      </>
    )
  }
  return DATA_NA
}

const religion = (data) => {
  const entries = getEntries(get(data, 'religion'))

  if (data && entries) {
    const year = get(data, 'date')

    return (
      <>
        {entries}
        {year && (
          <div className="body-m text-black-60 display-year">{year}</div>
        )}
      </>
    )
  }
  return DATA_NA
}

const ruleOfLawRanking = (data) => {
  // TODO: get these 'total' and 'year' values from API
  const rankingTotal = 131
  const year = 2020
  if (data) {
    data.total = rankingTotal
    data.year = year
    return (
      <>
        {rankOutOf(data, 'rank')}
        {data.year && (
          <div className="body-m text-black-60 display-year">{data.year}</div>
        )}
      </>
    )
  }
  return DATA_NA
}

const sign = (value) => {
  return ['-', '', '+'][Math.sign(value) + 1]
}

const importValueAndChange = (importValue) => {
  return (
    (importValue && importValue.trade_value_raw && (
      <>
        <div className="body-l primary">
          {millify(importValue.trade_value_raw) || DATA_NA}
        </div>
        {importValue.year_on_year_change && (
          <div className="body-m secondary text-black-60">
            {sign(importValue.year_on_year_change)}
            {normaliseValues(importValue.year_on_year_change)}% vs{' '}
            {importValue.year - 1}
          </div>
        )}
      </>
    )) ||
    DATA_NA
  )
}

export default () => {
  const populationTabConfig = {
    sourceAttributions: [
      {
        title: 'Population data',
        linkText: 'United Nations',
        linkTarget: 'https://population.un.org/wup/Download/',
        text: 'CC BY 3.0 IGO.',
      },
      {
        title: 'Urban and Rural Populations',
        linkText: 'United Nations',
        linkTarget: 'https://population.un.org/wup/Download/',
        text: 'CC BY 3.0 IGO.',
      },
      {
        title: 'Access to internet',
        linkText: 'International Telecommunications Union',
        linkTarget:
          'https://www.itu-ilibrary.org/science-and-technology/data/world-telecommunication-ict-indicators-database_pub_series/database/2a8478f7-en',
      },
    ],

    columns: {
      total_population: {
        name: 'Total Population',
        className: 'text-align-right',
        render: (data) => millify(data.total_population_raw) || DATA_NA,
      },
      urban_population: {
        name: 'Living in urban areas',
        className: 'text-align-right',
        render: (data) =>
          populationPercentActual(
            get(data, 'urban_population_total', 0) * 1000,
            get(data, 'total_population_raw')
          ),
      },
      rural_population: {
        name: 'Living in rural areas',
        className: 'text-align-right',
        render: (data) =>
          populationPercentActual(
            get(data, 'rural_population_total', 0) * 1000,
            get(data, 'total_population_raw')
          ),
      },
      internet_usage: {
        name: 'Access to internet',
        className: 'text-align-right',
        render: (data) =>
          data.internet_usage
            ? normaliseValues(`${data.internet_usage.value}%`)
            : 'Data not available',
        year: (data) => get(data, 'internet_usage.year'),
      },
      cpi: {
        name: 'Consumer Price Index',
        className: 'text-align-right',
        render: (data) => get(data, 'cpi.value') || 'Data not available',
        year: (data) => get(data, 'cpi.year'),
        tooltip: {
          position: 'right',
          title: '',
          content: `
          <p>Consumer Price Index (or CPI) measures changes in the price of goods and services.</p>
          <p>All countries start at 100. A higher number indicates prices are growing quickly, while a lower number indicates they are rising slowly.</p>
          <p>Knowing the CPI of your target country gives you a better idea of what prices consumers expect for your product and how much they expect those prices to change.</p>
         `,
        },
      },
    },
    dataFunction: Services.getPopulationByCountryData,
  }

  const economyTabConfig = {
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
        linkTarget:
          'https://www.doingbusiness.org/en/data/doing-business-score',
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
      },
      'uk-import-value': {
        name: 'Import value from the UK (USD)',
        className: 'text-align-right',
        render: (data) => importValueAndChange(data.import_data_from_uk),
        year: (data) => get(data, 'import_data_from_uk.year'),
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
          rankOutOf(get(data, 'country_data.ease_of_doing_bussiness'), 'rank'),
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
          rankOutOf(
            get(data, 'country_data.corruption_perceptions_index'),
            'rank'
          ),
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
    dataFunction: Services.getComTradeData,
  }
  const societyTabConfig = {
    sourceAttributions: [
      {
        title: 'Religion',
        linkText: 'Central Intelligence Agency',
        linkTarget: 'https://www.cia.gov/the-world-factbook',
      },
      {
        title: 'Languages',
        linkText: 'Central Intelligence Agency',
        linkTarget: 'https://www.cia.gov/the-world-factbook',
      },
      {
        title: 'Rule of law',
        linkText: 'The Global Innovation Index 2020',
        linkTarget: 'https://www.globalinnovationindex.org/gii-2020-report',
      },
    ],

    columns: {
      religion: {
        name: 'Religion',
        className: 'align-top',
        render: (data) => religion(get(data, 'religions')),
      },
      language: {
        name: 'Language',
        className: 'align-top',
        render: (data) => language(get(data, 'languages')),
      },
      'rule-of-law': {
        name: 'Rule of Law ranking',
        className: 'align-top',
        render: (data) => ruleOfLawRanking(get(data, 'rule_of_law')),
        tooltip: {
          position: 'right',
          title: '',
          content: `
          <p>The strength of the law varies from country to country.</p>
          <p>Each year, the Global Innovation Index ranks countries from low (law abiding) to high (not law abiding), using factors like contract enforcement, property rights, the police, and the courts.</p>
          <p>This gives you an idea of how easy may be to follow regulations and take legal action if something goes wrong.</p>
         `,
        },
      },
    },
    dataFunction: Services.getSocietyByCountryData,
  }

  return {
    population: populationTabConfig,
    economy: economyTabConfig,
    society: societyTabConfig,
  }
}
