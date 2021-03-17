import React from 'react'
import Services from '@src/Services'
import { normaliseValues, get, millify } from '../../Helpers'


const populationPercentActual = (data, urbanRural) => {
  const population = 1000 * data.reduce((total, row) => total + row.value, 0)
  const group = 1000 * data.reduce((total, row) => total + (urbanRural === row.urban_rural ? row.value : 0), 0)
  const percentage = Math.round((group * 100) / population)
  return (
    <>
      <div className="body-l primary">{percentage}%</div>
      <div className="body-m secondary">{millify(group)} </div>
    </>
  )
}

const totalPopulation = (data) => {
  return millify(1000 * data.reduce((total, row) => total + row.value, 0))
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
      render: (data) => totalPopulation(data.PopulationUrbanRural),
    },
    urban_population: {
      name: 'Living in urban areas',
      className: 'text-align-right',
      render: (data) =>
        populationPercentActual(data.PopulationUrbanRural, 'urban'),
    },
    rural_population: {
      name: 'Living in rural areas',
      className: 'text-align-right',
      render: (data) =>
        populationPercentActual(data.PopulationUrbanRural, 'rural'),
    },
    internet_usage: {
      name: 'Access to internet',
      className: 'text-align-right',
      render: (data) => {
        const thing = normaliseValues(`${data.InternetUsage[0].value}%`)
        return thing
      },
      year: (data) => get(data, 'internet_usage.year'),
    },
    cpi: {
      name: 'Consumer Price Index',
      className: 'text-align-right',
      render: (data) => data.ConsumerPriceIndex[0].value,
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
  dataFunction: (countries) => Services.getCountryData(countries, JSON.stringify([
    {model:'InternetUsage'},
    {model:'ConsumerPriceIndex'},
    {model:'PopulationUrbanRural',filter:{year:2020}}])),
}
