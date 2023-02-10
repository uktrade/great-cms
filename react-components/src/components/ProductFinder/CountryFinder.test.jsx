import React from 'react'
import { act, Simulate } from 'react-dom/test-utils'
import { waitFor, render } from '@testing-library/react'
import createCountryFinder, {
  CountryFinderButton,
} from '@src/components/ProductFinder/CountryFinderButton'
import Services from '@src/Services'
import fetchMock from 'fetch-mock'
import { Provider } from 'react-redux'
import ReactModal from 'react-modal'

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

const scheduleResponse = {
  children: [
    {
      children: [
        {
          desc: 'CHAPTER 4 - DAIRY PRODUCE',
        },
      ],
    },
  ],
}

const selectedProduct = {
  commodity_code: '123456',
  commodity_name: 'my product',
}

ReactModal.setAppElement('body')

describe('Test country finder button', () => {
  beforeEach(() => {
    document.body.innerHTML =
      '<span id="set-country-button" data-text="my country"></span>'

    Services.setConfig({
      apiCountriesUrl: '/api/countries/',
      apiSuggestedCountriesUrl: '/api/suggested-markets/',
      apiLookupProductScheduleUrl: '/api/lookup-product-schedule/',
    })
    Services.setInitialState({
      userSettings: {
        UserMarkets: [],
        UserProducts: [selectedProduct],
        ActiveProduct: {},
      },
    })

    fetchMock.get(/\/api\/countries\//, mockResponse)
    fetchMock.get(/\/api\/suggested-markets\//, suggestedCountries)
    fetchMock.get(/\/api\/lookup-product-schedule\//, scheduleResponse)
  })

  afterEach(() => {
    document.body.innerHTML = ''
    jest.clearAllMocks()
  })

  it('Opens and closes country finder', async () => {
    const { container } = render(
      <Provider store={Services.store}>
        <CountryFinderButton />
      </Provider>
    )

    expect(container.querySelector('.country-finder')).toBeFalsy()

    // Open up the p-bar dropdown
    container.querySelector('button').click()

    await waitFor(() => {
      expect(container.querySelector('.personalization-menu button')).toBeTruthy()
    })

    // Click on the open country finder button
    container.querySelector('.personalization-menu button').click()

    expect(document.querySelector('.country-finder')).toBeTruthy()

    await waitFor(() => {
      const region = document.querySelector('.country-list h2')
      expect(region.textContent).toEqual('Africa')
    })

    document.querySelector('button.dialog-close').click()

    expect(document.querySelector('.country-finder')).toBeFalsy()
  })

  /* Skipping this test as the country search is disabled ATM */
  it.skip('Open country finder and type-ahead filter', async () => {
    act(() => {
      createCountryFinder({ element: container })
    })
    expect(document.body.querySelector('.country-finder')).toBeFalsy()
    // Open up the p-bar dropdown
    act(() => {
      Simulate.click(container.querySelector('button'))
    })
    let addNewButton
    await waitFor(() => {
      addNewButton = container.querySelector('.personalization-menu button')
      expect(addNewButton).toBeTruthy()
    })
    // Click on the open country finder button
    act(() => {
      Simulate.click(addNewButton)
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
