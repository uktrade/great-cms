import React from 'react'
import { render, fireEvent } from '@testing-library/react'
import { Provider } from 'react-redux'
import Services from '@src/Services'
import ReactModal from 'react-modal'
import fetchMock from 'fetch-mock'

import { ExportPlanWizard } from './ExportPlanCreate'

const valueChange = jest.fn()

const country1 = { country_iso2: 'DZ', country_name: 'Algeria' }
const country2 = { country_iso2: 'AL', country_name: 'Albania' }
const country3 = { country_iso2: 'AT', country_name: 'Austria' }

const userCountries = [country1, country2, country3]

const product1 = { commodity_code: '123456', commodity_name: 'product1' }
const product2 = { commodity_code: '123457', commodity_name: 'product2' }
const product3 = { commodity_code: '666666', commodity_name: 'product3' }

const userProducts = [product3, product1, product2]


const setup = () => {
  Services.setConfig({
    apiUserDataUrl: '/sso/api/user-data/-name-/',
    apiSuggestedCountriesUrl: '/api/suggested-markets/',
    apiCountriesUrl: '/api/countries/',
    apiCreateExportPlanUrl: 'api/create-export-plan',
  })
  Services.setInitialState({
    userSettings: {
      UserMarkets: userCountries,
      UserProducts: userProducts,
      ActiveProduct: {},
    },
  })

  ReactModal.setAppElement(document.body)

  const component = render(
    <Provider store={Services.store}>
      <ExportPlanWizard valueChange={valueChange}/>
    </Provider>
  )
  return {
    ...component,
  }
}

describe('Wizard market selector', () => {
  it('Renders wizard', () => {
    const createEpMock = fetchMock.post(/\/api\/create-export-plan/, {})
    const { getByText, queryByText } = setup()
    expect(getByText('What are you exporting?')).toBeTruthy()
    const product1Radio = getByText('product1')
    expect(queryByText('Continue')).toBeFalsy()
    // Select a product
    fireEvent.click(product1Radio)
    // Click contine
    fireEvent.click(getByText('Continue'))
    // Select a market
    expect(getByText('Where\'s your target market?')).toBeTruthy()
    expect(queryByText('Continue')).toBeFalsy()
    fireEvent.click(getByText('Albania'))
    // Click create and check the parameters

    fireEvent.click(getByText('Create export plan'))
    expect(createEpMock.calls()).toHaveLength(1)
    const [url,details] = createEpMock.calls()[0]
    const body = JSON.parse(details.body)
    expect(body.export_commodity_codes[0].commodity_name).toEqual('product1')
    expect(body.export_countries[0].country_name).toEqual('Albania')
  })
})
