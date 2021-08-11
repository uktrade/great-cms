/* eslint-disable */
import React from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import { waitFor } from '@testing-library/react'
import createCountryFinder from '@src/components/ProductFinder/CountryFinderButton'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'

let container
let countriesMock
let suggestedCountriesMock

const mockResponse = [
  { id: 'DZ', name: 'Algeria', region: 'Africa', type: 'Country' },
  { id: 'AL', name: 'Albania', region: 'Europe', type: 'Country' },
  { id: 'AT', name: 'Austria', region: 'Europe', type: 'Country' },
]

const suggestedCountries = [
  { country_iso2: 'DZ', country_name: 'Algeria' },
  { country_iso2: 'AL', country_name: 'Albania' },
  { country_iso2: 'AT', country_name: 'Austria' },
]

const selectedProduct = {
  commodity_code: '123456',
  commodity_name: 'my product',
}

describe('Test country finder button', () => {
  beforeEach(() => {
    container = document.createElement('div')
    document.body.appendChild(container)
    container.innerHTML =
      '<span id="set-country-button" data-text="my country"></span>'
    Services.setConfig({
      apiCountriesUrl: '/api/countries/',
      apiSuggestedCountriesUrl: '/api/suggested-markets/',
    })
    Services.setInitialState({
      userSettings: {
        UserMarkets: [],
        UserProducts: [selectedProduct],
        ActiveProduct: {},
      },
    })
    countriesMock = fetchMock.get(/\/api\/countries\//, mockResponse)
    suggestedCountriesMock = fetchMock.get(
      /\/api\/suggested-markets\//,
      suggestedCountries
    )
  })

  afterEach(() => {
    document.body.removeChild(container)
    container = null
    jest.clearAllMocks()
  })

  it('Opens and closes country finder', async () => {
    act(() => {
      createCountryFinder({ element: container })
    })
    expect(document.body.querySelector('.country-finder')).toBeFalsy()
    // Open up the p-bar dropdown
    act(() => {
      Simulate.click(container.querySelector('button'))
    })
    await waitFor(() => {
      const addNewButton = document.body.querySelector(
        '.ReactModal__Content button'
      )
      expect(addNewButton).toBeTruthy()
    })
    // Click on the open country finder button
    act(() => {
      Simulate.click(document.body.querySelector('.ReactModal__Content button'))
    })
    const finder = document.body.querySelector('.country-finder')
    const closeButton = finder.querySelector('button.dialog-close')
    expect(finder).toBeTruthy()
    await waitFor(() => {
      const region = finder.querySelector('.country-list h2')
      expect(region.textContent).toEqual('Africa')
    })
    act(() => {
      Simulate.click(finder.querySelector('button.dialog-close'))
    })
    expect(document.body.querySelector('.country-finder')).toBeFalsy()
  })

  it('Open country finder and type-ahead filter', async () => {
    act(() => {
      createCountryFinder({ element: container })
    })
    expect(document.body.querySelector('.country-finder')).toBeFalsy()
    // Open up the p-bar dropdown
    act(() => {
      Simulate.click(container.querySelector('button'))
    })
    await waitFor(() => {
      const addNewButton = document.body.querySelector(
        '.ReactModal__Content button'
      )
      expect(addNewButton).toBeTruthy()
    })
    // Click on the open country finder button
    act(() => {
      Simulate.click(document.body.querySelector('.ReactModal__Content button'))
    })
    const finder = document.body.querySelector('.country-finder')
    const closeButton = finder.querySelector('button.dialog-close')
    expect(finder).toBeTruthy()
    await waitFor(() => {
      const region = finder.querySelector('.country-list h2')
      expect(region.textContent).toEqual('Africa')
    })
    const searchInput = finder.querySelector('.search-input input')
    expect(
      finder.querySelector('.country-list .expand-section').textContent
    ).toEqual('Algeria')
    act(() => {
      searchInput.value = 'au'
      Simulate.change(searchInput)
    })
    expect(finder.querySelector('div.country-list .open').textContent).toEqual(
      'Austria'
    )
    act(() => {
      searchInput.value = ''
      Simulate.change(searchInput)
    })
    expect(
      finder.querySelector('div.country-list .expand-section.open')
    ).toBeFalsy()
    act(() => {
      searchInput.value = 'aub'
      Simulate.change(searchInput)
    })
    expect(finder.querySelector('.country-list').textContent).toEqual(
      'No results found'
    )
  })
})
