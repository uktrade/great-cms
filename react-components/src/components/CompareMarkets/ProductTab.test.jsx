/* eslint-disable */
import { act, Simulate } from 'react-dom/test-utils'
import CompareMarkets from '@src/components/CompareMarkets'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'
import { waitFor } from '@testing-library/react'
import ReactModal from 'react-modal'

let container

const productApiResponse = {
  DE: {
    import_from_world: {
      year: '2017',
      trade_value_raw: 21670,
      country_name: 'Germany',
      year_on_year_change: '2.751',
      last_year: '2016',
    },
    import_from_uk: {
      year: '2019',
      trade_value_raw: 135150,
      country_name: 'Germany',
      year_on_year_change: '0.736',
      last_year: '2018',
    },
  },
  NE: {
    import_from_world: {
      year: '2019',
      trade_value_raw: 21670,
      country_name: 'Netherlands',
      year_on_year_change: '2.751',
    },
    import_from_uk: {
      year: '2019',
      trade_value_raw: 135150,
      country_name: 'Netherlands',
      year_on_year_change: '0.736',
    },
  },
}

// set up the mock of user daa with two countries
const comparisonMarketResponse = {
  ComparisonMarkets: {
    NL: { country_name: 'Netherlands', country_iso2_code: 'NL' },
    DE: { country_name: 'Germany', country_iso2_code: 'DE' },
  },
}

// set up existing product in store
const product1 = {
  commodity_code: '123456',
  commodity_name: 'my product1',
}
const product2 = {
  commodity_code: '123456',
  commodity_name: 'my product2',
}

const getText = (el, selector) => {
  const target = el && el.querySelector(selector)
  return (target && target.textContent) || ''
}

describe('Compare markets - Product tab', () => {
  beforeAll(() => {
    const mainElement = document.createElement('span')
    document.body.appendChild(mainElement)
    ReactModal.setAppElement(mainElement)
  })

  beforeEach(() => {
    container = document.createElement('div')
    container.innerHTML = '<span id="compare-market-container"></span>'
    document.body.appendChild(container)
    Services.setConfig({
      csrfToken: '12345',
      apiComTradeDataUrl: '/api/data-service/comtrade/',
      apiUserDataUrl: '/sso/api/user-data/',
      user: { id: '6' },
    })

    fetchMock.get(/\/api\/data-service\/comtrade\//, productApiResponse)
    fetchMock.get(/\/sso\/api\/user-data\//, () => comparisonMarketResponse)
    fetchMock.post(/\/sso\/api\/user-data\//, () => comparisonMarketResponse)

    Services.store.dispatch(
      actions.setInitialState({
        userSettings: {
          UserProducts: [product1, product2],
          ActiveProduct: product1,
          ComparisonMarkets: comparisonMarketResponse.ComparisonMarkets,
        },
      })
    )

    container.innerHTML =
      '<span id="cta-container"></span><span id="compare-market-container" ></span>'
    const dataTabs = '{ "product": true }'
    container
      .querySelector('#compare-market-container')
      .setAttribute('data-tabs', dataTabs)
  })

  afterEach(() => {
    document.body.removeChild(container)
    container = null
    jest.clearAllMocks()
  })

  it('Opens product tab', async () => {
    act(() => {
      CompareMarkets({
        element: container.querySelector('#compare-market-container'),
        cta_container: container.querySelector('#cta-container'),
      })
    })
    // check mock directory api data...
    await waitFor(() => {
      expect(container.querySelector('#market-Germany .name')).toBeTruthy()
    })
    const rowGermany = container.querySelector('#market-Germany')
    expect(getText(rowGermany, '.world-import-value .primary')).toMatch(
      '21,670'
    )
    expect(getText(rowGermany, '.world-import-value .secondary')).toMatch(
      '+2.8% vs 2016'
    )
    expect(getText(rowGermany, '.uk-import-value .primary')).toMatch('135,150')
    expect(getText(rowGermany, '.uk-import-value .secondary')).toMatch(
      '+0.7% vs 2018'
    )
    expect(getText(container, '.select .select__placeholder--value')).toMatch(
      product1.commodity_name
    )
    act(() => {
      Simulate.click(container.querySelector('.select__placeholder'))
    })
    await waitFor(() => {
      expect(
        container.querySelector('div.select li[aria-selected=false')
      ).toBeTruthy()
    })
    act(() => {
      Simulate.click(
        container.querySelector('div.select li[aria-selected=false')
      )
    })
    // Check analytics event...
    expect(window.dataLayer[window.dataLayer.length - 1]).toEqual({
      event: 'selectGridProduct',
      gridProductSelected: product2.commodity_name,
      gridProductSelectedCode: product2.commodity_code,
    })

    await waitFor(() => {
      expect(getText(container, '.select .select__placeholder--value')).toMatch(
        product2.commodity_name
      )
    })
  })

  it('Opens product finder', async () => {
    act(() => {
      CompareMarkets({
        element: container.querySelector('#compare-market-container'),
        cta_container: container.querySelector('#cta-container'),
      })
    })
    const addProductButton = container.querySelector(
      '#product-tab .button--tertiary'
    )
    expect(document.body.querySelector('.product-finder')).toBeFalsy()
    expect(addProductButton.textContent).toMatch('Add another product')
    act(() => {
      Simulate.click(addProductButton)
    })
    await waitFor(() => {
      expect(document.body.querySelector('.product-finder')).toBeTruthy()
    })
  })
})
