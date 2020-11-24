/* eslint-disable */
import { act, Simulate } from 'react-dom/test-utils'
import CompareMarkets from '@src/components/CompareMarkets'
import SelectMarket from '@src/components/CompareMarkets/SelectMarket'
import Services from '@src/Services'
import fetchMock from 'fetch-mock'
import { waitFor } from '@testing-library/react'
import ReactModal from 'react-modal'

let container
let countriesMock

const mockResponse = [
  { id: "DZ", name: "Algeria", region: "Africa", type: "Country" },
  { id: "AL", name: "Albania", region: "Europe", type: "Country" },
  { id: "AT", name: "Austria", region: "Europe", type: "Country" },
]

const suggestedResponse = [
  { "hs_code": 4, "country_name": "Germany", "country_iso2": "DE", "region": "Europe" },
  { "hs_code": 4, "country_name": "Italy", "country_iso2": "IT", "region": "Europe" },
  { "hs_code": 4, "country_name": "Russia", "country_iso2": "RU", "region": "Eastern Europe and Central Asia" },
  { "hs_code": 4, "country_name": "Spain", "country_iso2": "ES", "region": "Europe" },
  { "hs_code": 4, "country_name": "Sweden", "country_iso2": "SE", "region": "Europe" }
]

const populationByCountryApiResponse = [
  { "country": "Germany", "internet_usage": { "value": "74.39", "year": 2018 }, "rural_population_total": 17125, "rural_population_percentage_formatted": "28.32% (17.12 million)", "urban_population_total": 42007, "urban_population_percentage_formatted": "69.48% (42.01 million)", "total_population": "60.46 million", "cpi": { "value": "110.62", "year": 2019 } }
]

beforeAll(() => {
  const mainElement = document.createElement('span')
  document.body.appendChild(mainElement)
  ReactModal.setAppElement(mainElement)
})

beforeEach(() => {
  container = document.createElement('div')
  container.innerHTML = '<span id="compare-market-container" data-productname="my product" data-productcode="123456"></span>'
  document.body.appendChild(container)
  Services.setConfig({
    csrfToken: '12345',
    apiCountriesUrl: '/api/countries/',
    apiSuggestedCountriesUrl: '/api/suggestedcountries/',
    populationByCountryUrl: '/export-plan/api/country-data/'
  })
  countriesMock = fetchMock.get(/\/api\/countries\//, mockResponse)
  fetchMock.get(/\/api\/suggestedcountries\//, suggestedResponse)
  fetchMock.get(/\/export-plan\/api\/country-data\//, populationByCountryApiResponse)
})

afterEach(() => {
  document.body.removeChild(container)
  container = null
  jest.clearAllMocks()
})


it('Forces product chooser when no product', () => {
  container.innerHTML = '<span id="compare-market-container" data-productname="" data-productcode=""></span>'
  act(() => {
    CompareMarkets({ element: container.querySelector('span') })
  })
  expect(document.body.querySelector('.product-finder')).toBeFalsy()
  // Click the button and check it opens product finder
  const button = container.querySelector('button')
  expect(button.textContent).toMatch('Select product')
  act(() => {
    Simulate.click(button)
  })
  const finder = document.body.querySelector('.product-finder');
  expect(document.body.querySelector('.product-finder')).toBeTruthy()
  const closeButton = finder.querySelector('button.dialog-close');
  act(() => {
    Simulate.click(closeButton)
  })
  expect(document.body.querySelector('.product-finder')).toBeFalsy()
})

it('Allows selection of markets and fetch data when product selected', async () => {
  container.innerHTML = '<span id="compare-market-container" data-productname="my product" data-productcode="123456"></span>'
  act(() => {
    CompareMarkets({ element: container.querySelector('#compare-market-container') })
  })

  const button = container.querySelector('button')
  expect(button.textContent).toMatch('Select market 1 of 3')
  act(() => {
    Simulate.click(button)
  })
  const finder = document.body.querySelector('.country-finder');
  expect(finder).toBeTruthy();
  await waitFor(() => {
    const region = finder.querySelector('.country-list h2');
    expect(region.textContent).toEqual('Africa')
    const suggested = finder.querySelector('.suggested-markets button')
    expect(suggested.textContent).toEqual('Germany')
  })
  const firstCountry = finder.querySelector('.suggested-markets button')
  // Select first suggested country
  act(() => {
    Simulate.click(firstCountry)
  })
  await waitFor(() => {
    expect(container.querySelector('button.add-market').textContent).toMatch('Select market 2 of 3')
  })

  // check mock directory api data...
  const rowGermany = container.querySelector('#market-Germany')
  expect(rowGermany.querySelector('.name').textContent).toMatch('Germany')
  expect(rowGermany.querySelector('.total-population').textContent).toMatch('60.46 million')
  expect(rowGermany.querySelector('.internet-usage').textContent).toMatch('74.39%')
  expect(rowGermany.querySelector('.urban-population').textContent).toMatch('69.48% (42.01 million)')
  expect(rowGermany.querySelector('.rural-population').textContent).toMatch('28.32% (17.12 million)')


  // remove the country
  act(() => {
    Simulate.click(container.querySelector('.market-details button'))
  })
  await waitFor(() => {
    expect(container.querySelector('button.add-market').textContent).toMatch('Select market 1 of 3')
  })
})


it('Select market from selection area', async () => {
  container.innerHTML = '<span id="compare-market-container" data-productname="my product" data-productcode="123456"></span><span id="comparison-market-selector"></span>'
  act(() => {
    CompareMarkets({ element: container.querySelector('#compare-market-container') })
    SelectMarket({ element: container.querySelector('#comparison-market-selector') })
  })
  await waitFor(() => {
    expect(container.querySelector('button.add-market').textContent).toMatch('Select market 1 of 3')
  })

  // Select a country
  act(() => {
    Simulate.click(container.querySelector('button.add-market'))
  })
  let finder = document.body.querySelector('.country-finder')
  let suggested
  await waitFor(() => {
    suggested = finder.querySelector(`.suggested-markets button[data-id=DE]`)
    expect(suggested).toBeTruthy()
  })
  act(() => {
    Simulate.click(suggested)
  })
  await waitFor(() => {
    expect(container.querySelector('button.add-market').textContent).toMatch('Select market 2 of 3')
  })

  // check that the country appears in the selection section at the page base
  const marketSelectionBar = container.querySelector('#comparison-market-selector');
  expect(marketSelectionBar.querySelector('button').textContent).toMatch('Germany')

  // Select a country
  act(() => {
    Simulate.click(container.querySelector('button.add-market'))
  })
  finder = document.body.querySelector('.country-finder')
  await waitFor(() => {
    suggested = finder.querySelector(`.suggested-markets button[data-id=SE]`)
    expect(suggested).toBeTruthy()
  })
  act(() => {
    Simulate.click(suggested)
  })
  await waitFor(() => {
    expect(container.querySelector('button.add-market').textContent).toMatch('Select market 3 of 3')
  })

  let buttonSweden = marketSelectionBar.querySelector('button.market-SE')
  // check that the country appears in the selection section at the page base
  expect(buttonSweden.textContent).toMatch('Sweden')
  // remove sweden and watch it vanish from selection bar
  act(() => {
    Simulate.click(container.querySelector('.market-details button[data-id=SE]'))
  })
  await waitFor(() => {
    expect(marketSelectionBar.querySelector('button.market-SE')).toBeFalsy()
  })

})
