import React from 'react'
import { render, fireEvent, waitFor } from '@testing-library/react'
import { act } from 'react-dom/test-utils'
import { Provider } from 'react-redux'
import Services from '@src/Services'
import ReactModal from 'react-modal'
import fetchMock from 'fetch-mock'

import MarketSelector from './MarketSelector'

const valueChange = jest.fn()

const countriesResponse = [
  { id: 'DZ', name: 'Algeria', region: 'Africa', type: 'Country' },
  { id: 'AL', name: 'Albania', region: 'Europe', type: 'Country' },
  { id: 'AT', name: 'Austria', region: 'Europe', type: 'Country' },
]

const country1 = { country_iso2: 'DZ', country_name: 'Algeria' }
const country2 = { country_iso2: 'AL', country_name: 'Albania' }
const country3 = { country_iso2: 'AT', country_name: 'Austria' }

const userCountries = [country1, country2, country3]

const scheduleResponse = {
  children: [
    {
      children: [
        {
          desc:
            'CHAPTER 4 - DAIRY PRODUCE',
        },
      ],
    },
  ],
}
const selectedProduct = {
  commodity_code: '123456',
  commodity_name: 'my product',
}

const setup = () => {
  Services.setConfig({
    apiUserDataUrl: '/sso/api/user-data/-name-/',
    apiSuggestedCountriesUrl: '/api/suggested-markets/',
    apiCountriesUrl: '/api/countries/',
    apiLookupProductScheduleUrl: '/api/lookup-product-schedule/',
  })
  Services.setInitialState({
    userSettings: {
      UserMarkets: userCountries,
      UserProducts: [selectedProduct],
      ActiveProduct: {},
    },
  })
  ReactModal.setAppElement(document.body)

  const component = render(
    <Provider store={Services.store}>
      <MarketSelector valueChange={valueChange} />
    </Provider>
  )
  return {
    ...component,
  }
}

describe('Wizard market selector', () => {
  it('Renders market selector', () => {
    const { getByText } = setup()
    const country2Radio = getByText('Albania')
    expect(country2Radio).toBeTruthy()
    fireEvent.click(country2Radio)
    expect(valueChange).toHaveBeenCalled()
    expect(valueChange).toHaveBeenCalledWith(country2)
  })
  it('Opens market finder modal', async () => {
    fetchMock.get(/api\/suggested-markets\//, userCountries)
    fetchMock.get(/\/api\/countries\//, countriesResponse)
    fetchMock.get(/\/api\/lookup-product-schedule\//, scheduleResponse)
    const { getByText } = setup()
    const somewhereElse = getByText('Somewhere else')
    expect(somewhereElse).toBeTruthy()
    act(() => {
      fireEvent.click(somewhereElse)
    })
    const addButton = getByText('Choose Market')
    expect(addButton).toBeTruthy()
    act(() => {
      fireEvent.click(addButton)
    })
    await waitFor(() => {
      expect(
        document.body.querySelector('.ReactModalPortal .country-finder')
      ).toBeTruthy()
    })
  })
})
