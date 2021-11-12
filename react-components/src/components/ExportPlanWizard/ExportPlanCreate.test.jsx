import React from 'react'
import { render, fireEvent } from '@testing-library/react'
import { Provider } from 'react-redux'
import Services from '@src/Services'
import ReactModal from 'react-modal'
import fetchMock from 'fetch-mock'

import { ExportPlanWizard } from './ExportPlanCreate'

const country1 = { country_iso2: 'DZ', country_name: 'Algeria' }
const country2 = { country_iso2: 'AL', country_name: 'Albania' }
const country3 = { country_iso2: 'AT', country_name: 'Austria' }
const countryNotInBasket = {
  country_iso2: 'HH',
  country_name: 'country not in basket',
}

const userCountries = [country1, country2, country3]

const product1 = { commodity_code: '123456', commodity_name: 'product1' }
const product2 = { commodity_code: '123457', commodity_name: 'product2' }
const product3 = { commodity_code: '666666', commodity_name: 'product3' }
const productNotInBasket = {
  commodity_code: '999999',
  commodity_name: 'product not in basket',
}

const userProducts = [product3, product1, product2]

const exportPlan1 = {
  export_commodity_codes: [product2],
  export_countries: [country2],
}

const exportPlan2 = {
  export_commodity_codes: [productNotInBasket],
  export_countries: [countryNotInBasket],
}

const setup = (ep) => {
  Services.setConfig({
    apiUserDataUrl: '/sso/api/user-data/-name-/',
    apiSuggestedCountriesUrl: '/api/suggested-markets/',
    apiCountriesUrl: '/api/countries/',
    apiCreateExportPlanUrl: 'api/create-export-plan',
    apiUpdateExportPlanUrl: 'api/update-export-plan',
    exportPlanBaseUrl: '/export-plan/',
  })
  Services.setInitialState({
    userSettings: {
      UserMarkets: userCountries,
      UserProducts: userProducts,
      ActiveProduct: {},
    },
  })

  ReactModal.setAppElement(document.body)
  window.location.assign('#')

  return render(
    <Provider store={Services.store}>
      {ep ? <ExportPlanWizard exportPlan={ep} /> : <ExportPlanWizard />}
    </Provider>
  )
}

describe('Wizard market selector', () => {
  afterEach(fetchMock.restore)

  it('Renders wizard', () => {
    const createEpMock = fetchMock.post(/\/api\/create-export-plan/, {
      hashid: 1234,
    })
    const { getByText, queryByText } = setup()
    expect(getByText('What are you exporting?')).toBeTruthy()
    const product1Radio = getByText('product1')
    expect(queryByText('Continue')).toBeFalsy()
    // Select a product
    fireEvent.click(product1Radio)
    // Click contine
    fireEvent.click(getByText('Continue'))
    // Select a market
    expect(getByText("Where's your target market?")).toBeTruthy()
    expect(queryByText('Create export plan')).toBeFalsy()
    fireEvent.click(getByText('Albania'))
    // Click create and check the parameters
    expect(queryByText('Create export plan')).toBeTruthy()
    fireEvent.click(getByText('Create export plan'))
    expect(createEpMock.calls()).toHaveLength(1)
    const [url, details] = createEpMock.calls()[0]
    expect(url).toMatch('/api/create-export-plan')
    const body = JSON.parse(details.body)
    expect(body.export_commodity_codes[0].commodity_name).toEqual('product1')
    expect(body.export_countries[0].country_name).toEqual('Albania')

    // Check analytics event...
    expect(window.dataLayer[window.dataLayer.length - 1]).toEqual({
      event: 'createExportPlan',
      exportPlanMarketSelected: body.export_countries[0],
      exportPlanProductSelected: body.export_commodity_codes[0]
    })
  })
  it('Renders wizard in update mode', () => {
    const updateEpMock = fetchMock.post(/\/api\/update-export-plan/, {})
    const { getByText, queryByText } = setup(exportPlan1)
    expect(getByText('What are you exporting?')).toBeTruthy()
    expect(getByText('product1')).toBeTruthy()
    expect(queryByText('Continue')).toBeTruthy()
    fireEvent.click(getByText('Continue'))
    // Select a market
    expect(getByText("Where's your target market?")).toBeTruthy()
    expect(queryByText('Update export plan')).toBeTruthy()
    expect(updateEpMock.calls()).toHaveLength(0)
    fireEvent.click(getByText('Update export plan'))
    expect(updateEpMock.calls()).toHaveLength(1)
    const [url, details] = updateEpMock.calls()[0]

    expect(url).toMatch('/api/update-export-plan')
    const body = JSON.parse(details.body)
    expect(body.export_commodity_codes[0]).toEqual(product2)
    expect(body.export_countries[0]).toEqual(country2)
  })
  it('Renders wizard in update mode not in basket', () => {
    const updateEpMock = fetchMock.post(/\/api\/update-export-plan/, {})
    const { getByText, queryByText } = setup(exportPlan2)
    expect(getByText('What are you exporting?')).toBeTruthy()
    expect(queryByText('Continue')).toBeTruthy()
    fireEvent.click(getByText('Continue'))
    // Select a market
    expect(getByText("Where's your target market?")).toBeTruthy()
    expect(queryByText('Update export plan')).toBeTruthy()
    expect(updateEpMock.calls()).toHaveLength(0)
    fireEvent.click(getByText('Update export plan'))
    expect(updateEpMock.calls()).toHaveLength(1)
    const [url, details] = updateEpMock.calls()[0]

    expect(url).toMatch('/api/update-export-plan')
    const body = JSON.parse(details.body)
    expect(body.export_commodity_codes[0]).toEqual(productNotInBasket)
    expect(body.export_countries[0]).toEqual(countryNotInBasket)
  })
})
