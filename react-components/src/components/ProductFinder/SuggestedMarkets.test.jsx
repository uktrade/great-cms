/* eslint-disable */
import React from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import { Provider } from 'react-redux'
import { render, fireEvent, waitFor, cleanup } from '@testing-library/react'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'
import ReactModal from 'react-modal'

import CountryFinderModal from './CountryFinderModal'

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

const product1 = { commodity_code: '123456', commodity_name: 'product1' }
const product2 = { commodity_code: '123457', commodity_name: 'product2' }
const product3 = { commodity_code: '666666', commodity_name: 'product3' }

const userProducts = [product3, product1, product2]
const userProductsSame = [product1, product2]

const setIsOpen = jest.fn()
const selectCountry = jest.fn()

const setup = ({ activeProducts }) => {
  return render(
    <div>
    <Provider store={Services.store}>
      <CountryFinderModal
        modalIsOpen={true}
        setIsOpen={setIsOpen}
        selectCountry={selectCountry}
        activeProducts={activeProducts}
      />
    </Provider>
    </div>
  )
}

describe('Test suggested markets', () => {
  beforeEach(() => {
    ReactModal.setAppElement(document.body)
    Services.setConfig({
      apiCountriesUrl: '/api/countries/',
      apiSuggestedCountriesUrl: '/api/suggested-markets/',
    })
    Services.setInitialState({
      userSettings: {
        UserMarkets: [],
        UserProducts: userProducts,
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
    jest.clearAllMocks()
    fetchMock.reset()
  })

  it('Specific active product1', async () => {
    let rtl
    act(() => {
      rtl = setup({ activeProducts: [product1] })
    })
    await waitFor(() => {
      expect(rtl.queryAllByText('Suggested places')).toBeTruthy()
      expect(rtl.getByText(/product1/)).toBeTruthy()
    })
    expect(suggestedCountriesMock.calls())
    expect(suggestedCountriesMock.calls(/\/api\/suggested-markets\//)[0][0]).toMatch(/\?hs_code=12/)
  })

  it('Specific active product3', async () => {
    let rtl
    act(() => {
      rtl = setup({ activeProducts: [product3] })
    })
    await waitFor(() => {
      expect(rtl.queryAllByText('Suggested places')).toBeTruthy()
      expect(rtl.getByText(/product3/)).toBeTruthy()
    })
    expect(suggestedCountriesMock.calls())
    expect(suggestedCountriesMock.calls(/\/api\/suggested-markets\//)[0][0]).toMatch(/\?hs_code=66/)
  })

  it('Basket active product', async () => {
    let rtl
    act(() => {
      rtl = setup({ activeProducts: null })
    })
    await waitFor(() => {
      expect(rtl.queryAllByText('Suggested places')).toBeTruthy()
      expect(rtl.getByText(/product2/)).toBeTruthy()
    })
    expect(suggestedCountriesMock.calls(/\/api\/suggested-markets\//)[0][0]).toMatch(/\?hs_code=12/)
  })

  it('Basket active product all same hs2', async () => {
    let rtl
    Services.setInitialState({
      userSettings: {
        UserMarkets: [],
        UserProducts: userProductsSame,
        ActiveProduct: {},
      },
    })
    act(() => {
      rtl = setup({ activeProducts: null })
    })
    await waitFor(() => {
      expect(rtl.queryAllByText('Suggested places')).toBeTruthy()
      expect(rtl.getByText(/product2/)).toBeTruthy()
      expect(rtl.getByText(/\(same countries for all products\)/)).toBeTruthy()
    })
    expect(suggestedCountriesMock.calls(/\/api\/suggested-markets\//)[0][0]).toMatch(/\?hs_code=12/)
  })
})
