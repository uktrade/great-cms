import Services from '@src/Services'
import { normaliseValues, millify } from '../../Helpers'

export default {
  sourceAttributions: [
    {
      title: 'Adjusted net national income per capita',
      preLinkText: '(current US$)',
      linkText: 'World Bank',
      linkTarget: 'https://data.worldbank.org/indicator/NY.ADJ.NNTY.PC.CD',
      text: 'CC BY 4.0.',
    },
    {
      title: 'Consumer price index',
      linkText: 'International Monetary Fund',
      linkTarget:
        'https://data.imf.org/?sk=4FFB52B2-3653-409A-B471-D47B46D904B5',
    },
    {
      title: 'Access to internet',
      linkText: 'International Telecommunications Union.',
      linkTarget:
        'https://www.itu-ilibrary.org/science-and-technology/data/world-telecommunication-ict-indicators-database_pub_series/database/2a8478f7-en',
    },
  ],
  columns: {
    'avg-income': {
      name: 'Adjusted net national income per capita (USD)',
      className: 'text-align-right',
      render: (data) => millify(data.Income[0].value),
      year: (data) => data.Income[0].year,
      tooltip: {
        position: 'right',
        title: 'What is Adjusted net national income per capita?',
        content: `
          <p>Adjusted net national income per capita (ANNIPC) measures the average income of consumers.</p>
          <p>Each year, the World Bank calculates ANNIPC by taking the gross national income, minus fixed income and natural resource consumption, and dividing it by the total population.</p>
          <p>ANNIPC gives you an idea of how much consumers earn, whether they can comfortably afford your products and at what price.</p>
         `,
      },
    },
    cpi: {
      name: 'Consumer Price Index',
      className: 'text-align-right',
      render: (data) => normaliseValues(data.ConsumerPriceIndex[0].value, 2),
      year: (data) => data.ConsumerPriceIndex[0].year,
      tooltip: {
        position: 'right',
        content: `
          <p>Consumer Price Index (or CPI) measures changes in the price of goods and services.</p>
          <p>A higher number indicates prices are growing quickly and a lower number indicates they’re rising slowly.</p>
          <p>CPI gives you an idea of the cost of living and how much those costs have changed.</p>
         `,
      },
    },
    internet_usage: {
      name: 'Access to internet',
      className: 'text-align-right',
      render: (data) => normaliseValues(`${data.InternetUsage[0].value}%`),
      year: (data) => data.InternetUsage[0].year,
      tooltip: {
        position: 'right',
        content: `
          <p>The percentage of the population that has access to the internet.</p>
         `,
      },
    },
  },
  dataFunction: (countries) =>
    Services.getCountryData(
      countries,
      JSON.stringify([
        { model: 'Income', latest_only: true },
        { model: 'InternetUsage', latest_only: true },
        { model: 'ConsumerPriceIndex', latest_only: true },
      ])
    ),
}
