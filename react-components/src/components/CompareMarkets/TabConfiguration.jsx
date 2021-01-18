import React from 'react'
import Services from '@src/Services'
import { normaliseValues, get } from '../../Helpers'

const headingAndBody = (value) => {
  return (
    <>
      <h1>{normaliseValues(value)[0]}</h1>{' '}
      <span className="body-m"> {normaliseValues(value)[1]} </span>{' '}
    </>
  )
}

const DATA_NA = 'Data not available'

const getAndFormat = (data, key, unit = '') => {
  const value = get(data, key)
  return value !== undefined ? `${normaliseValues(value)}${unit}` : DATA_NA
}

  const formatReligion = (religion) => {
    return `${religion.name} ${(religion.percent ? `${religion.percent}%` : '')}`
  }

  const formatLanguage = (language) => {
    return `${language.name}${language.note === 'official' ? ' (official)' : ''}`
  }

  const getEntries = (list={}, func) => {
    const entries = Object.keys(list || {}).map((key) => {
      return <p className="entry body-m" key={key}>{func(list[key])}</p>
    })
    return entries
  }

export default (selectedProduct) => {
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
        render: (data) => normaliseValues(data.total_population),
      },
      internet_usage: {
        name: 'Access to internet',
        render: (data) =>
          data.internet_usage
            ? normaliseValues(`${data.internet_usage.value}%`)
            : 'Data not available',
      },
      urban_population: {
        name: 'Living in urban areas',
        render: (data) =>
          headingAndBody(data.urban_population_percentage_formatted),
      },
      rural_population: {
        name: 'Living in rural areas',
        render: (data) =>
          headingAndBody(data.rural_population_percentage_formatted),
      },
      cpi: {
        name: 'Consumer Price Index',
        render: (data) => get(data, 'cpi.value') || 'Data not available',
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
        linkTarget:
          'https://www.globalinnovationindex.org/gii-2020-report',
      }
    ],

    columns: {
      'religion': {
        name: 'Religion',
        className: 'text-align-left align-top',
        render: (data) => {return getEntries(get(data, 'religions.religion'), formatReligion)},
      },
      'language': {
        name: 'Languages',
        className: 'text-align-left align-top',
        render: (data) => {return getEntries(get(data, 'languages.language'), formatLanguage)},
      },
      'rule-of-law': {
        name: 'Rule of law score align-top',
        render: (data) => normaliseValues(get(data,'rule_of_law.score'))
      }
    },
    dataFunction: Services.getSocietyByCountryData,
  }

  return {
    population: populationTabConfig,
    economy: economyTabConfig,
    society: societyTabConfig,
  }
}
