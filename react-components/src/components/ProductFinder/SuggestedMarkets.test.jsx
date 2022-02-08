import React from 'react'
import { Provider } from 'react-redux'
import { render, waitFor } from '@testing-library/react'
import Services from '@src/Services'
import fetchMock from 'fetch-mock'
import ReactModal from 'react-modal'

import CountryFinderModal from './CountryFinderModal'

let suggestedCountriesMock
let scheduleResponseMock

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

const product1 = { commodity_code: '123456', commodity_name: 'product1' }
const product2 = { commodity_code: '123457', commodity_name: 'product2' }
const product3 = { commodity_code: '666666', commodity_name: 'product3' }

const userProducts = [product3, product1, product2]
const userProductsSame = [product1, product2]

const setIsOpen = jest.fn()
const selectCountry = jest.fn()

const setup = ({ activeProducts }) => render(
  <Provider store={Services.store}>
    <CountryFinderModal
      modalIsOpen
      setIsOpen={setIsOpen}
      selectCountry={selectCountry}
      activeProducts={activeProducts}
    />
  </Provider>,
)

ReactModal.setAppElement(document.body)

describe('Test suggested markets', () => {
  beforeEach(() => {
    Services.setConfig({
      apiCountriesUrl: '/api/countries/',
      apiSuggestedCountriesUrl: '/api/suggested-markets/',
      apiLookupProductScheduleUrl: '/api/lookup-product-schedule/',
    })
    Services.setInitialState({
      userSettings: {
        UserMarkets: [],
        UserProducts: userProducts,
        ActiveProduct: {},
      },
    })
    fetchMock.get(/\/api\/countries\//, mockResponse)
    suggestedCountriesMock = fetchMock.get(
      /\/api\/suggested-markets\//,
      suggestedCountries,
    )
    scheduleResponseMock = fetchMock.get(/\/api\/lookup-product-schedule\//, scheduleResponse)
  })

  afterEach(() => {
    jest.clearAllMocks()
    fetchMock.reset()
  })

  it('Specific active product1', async () => {
    const { getAllByText, getByText } = setup({ activeProducts: [product1] })

    await waitFor(() => {
      expect(getAllByText('Possible export markets')).toBeTruthy()
    })
    expect(getByText(/dairy produce/)).toBeTruthy()
    expect(suggestedCountriesMock.calls(/\/api\/suggested-markets\//)[0][0]).toMatch(/\?hs_code=12/)
    expect(scheduleResponseMock.calls(/\/api\/lookup-product-schedule\//)[0][0]).toMatch(/\?hs_code=123456/)
  })

  it('Specific active product3', async () => {
    const { getAllByText, getByText } = setup({ activeProducts: [product3] })

    await waitFor(() => {
      expect(getAllByText('Possible export markets')).toBeTruthy()
    })

    expect(getByText(/dairy produce/)).toBeTruthy()
    expect(suggestedCountriesMock.calls(/\/api\/suggested-markets\//)[0][0]).toMatch(/\?hs_code=66/)
  })

  it('Basket active product', async () => {
    const { getByText } = setup({ activeProducts: null })

    let explanation

    await waitFor(() => {
      explanation = getByText(/These markets are based on consumer demand/)
      expect(explanation).toBeTruthy()
    })

    expect(explanation.textContent).toMatch('dairy produce')
    expect(explanation.textContent).toMatch('product2')
    expect(suggestedCountriesMock.calls(/\/api\/suggested-markets\//)[0][0]).toMatch(/\?hs_code=12/)
  })

  it('Basket active product all same hs2', async () => {
    Services.setInitialState({
      userSettings: {
        UserMarkets: [],
        UserProducts: userProductsSame,
        ActiveProduct: {},
      },
    })

    const { getAllByText, getByText } = setup({ activeProducts: null })

    await waitFor(() => {
      expect(getAllByText('Possible export markets')).toBeTruthy()
    })

    expect(getByText(/dairy produce/)).toBeTruthy()
  })
})
