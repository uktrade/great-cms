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
      linkText: 'International Telecommunications Union',
      linkTarget:
        'https://www.itu-ilibrary.org/science-and-technology/data/world-telecommunication-ict-indicators-database_pub_series/database/2a8478f7-en',
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
          <p>All countries start at 100. A higher number indicates prices are growing quickly, while a lower number indicates they are rising slowly.</p>
          <p>Knowing the CPI of your target country gives you a better idea of what prices consumers expect for your product and how much they expect those prices to change.</p>
         `,
      },
    },
  },
  dataFunction: Services.getPopulationByCountryData,
}
