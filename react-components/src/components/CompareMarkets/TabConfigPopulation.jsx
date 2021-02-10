import React from 'react'
import Services from '@src/Services'
import { normaliseValues, get, millify } from '../../Helpers'

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
  throw new Error()
}

export default {
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
      linkText: 'International Telecommunications Union.',
      linkTarget:
        'https://www.itu-ilibrary.org/science-and-technology/data/world-telecommunication-ict-indicators-database_pub_series/database/2a8478f7-en',
    },
    {
      title: 'Consumer price index',
      linkText: 'International Monetary Fund',
      linkTarget: 'https://data.imf.org/?sk=4FFB52B2-3653-409A-B471-D47B46D904B5',
    },
  ],

  columns: {
    total_population: {
      name: 'Total Population',
      className: 'text-align-right',
      render: (data) => millify(data.total_population_raw),
    },
    urban_population: {
      name: 'Living in urban areas',
      className: 'text-align-right',
      render: (data) =>
        populationPercentActual(
          data.urban_population_total * 1000,
          data.total_population_raw
        ),
    },
    rural_population: {
      name: 'Living in rural areas',
      className: 'text-align-right',
      render: (data) =>
        populationPercentActual(
          data.rural_population_total * 1000,
          data.total_population_raw
        ),
    },
    internet_usage: {
      name: 'Access to internet',
      className: 'text-align-right',
      render: (data) => normaliseValues(`${data.internet_usage.value}%`),
      year: (data) => get(data, 'internet_usage.year'),
    },
    cpi: {
      name: 'Consumer Price Index',
      className: 'text-align-right',
      render: (data) => data.cpi.value,
      year: (data) => get(data, 'cpi.year'),
      tooltip: {
        position: 'right',
        title: '',
        content: `
          <p>Consumer Price Index (or CPI) measures changes in the price of goods and services.</p>
          <p>A higher number indicates prices are growing quickly and a lower number indicates they’re rising slowly.</p>
          <p>CPI gives you an idea of the cost of living and how much those costs have changed.</p>
         `,
      },
    },
  },
  dataFunction: Services.getPopulationByCountryData,
}
