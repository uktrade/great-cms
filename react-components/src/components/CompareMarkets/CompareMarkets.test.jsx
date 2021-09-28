import { act, Simulate } from 'react-dom/test-utils'
import CompareMarkets from '@src/components/CompareMarkets'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'
import { waitFor } from '@testing-library/react'
import ReactModal from 'react-modal'

let container
let userDataPostMock

const mockResponse = [
  { id: 'DZ', name: 'Algeria', region: 'Africa', type: 'Country' },
  { id: 'AL', name: 'Albania', region: 'Europe', type: 'Country' },
  { id: 'AT', name: 'Austria', region: 'Europe', type: 'Country' },
]

const suggestedResponse = [
  { hs_code: 4, country_name: 'Germany', country_iso2: 'DE', region: 'Europe' },
  { hs_code: 4, country_name: 'Italy', country_iso2: 'IT', region: 'Europe' },
  {
    hs_code: 4,
    country_name: 'Russia',
    country_iso2: 'RU',
    region: 'Eastern Europe and Central Asia',
  },
  { hs_code: 4, country_name: 'Spain', country_iso2: 'ES', region: 'Europe' },
  { hs_code: 4, country_name: 'Sweden', country_iso2: 'SE', region: 'Europe' },
]

const productApiResponse = {
  DE: {
    import_from_world: {
      year: '2017',
      trade_value_raw: 21670,
      country_name: 'Germany',
      year_on_year_change: '2.751',
      last_year: '2016',
    },
  },
}

const countryDataApiResponse = {
  DE: {
    ConsumerPriceIndex: [
      {
        country_name: 'Germany',
        country_code: 'DEU',
        value: '112.855',
        year: 2019,
      },
    ],
    GdpPerCapita: [
      {
        country_name: 'Germany',
        country_code: 'DEU',
        year_2019: '46258.878',
      },
    ],
    Income: [
      {
        country_name: 'Germany',
        country_code: 'DEU',
        year: 2018,
        value: '7895',
      },
    ],
  },
  NL: {
    ConsumerPriceIndex: [
      {
        country_name: 'Netherlands',
        value: '112.855',
        year: 2019,
      },
    ],
    Income: [
      {
        country_name: 'Netherlands',
        year: 2019,
        value: '7895',
      },
    ],
  },
}

const selectedProduct = {
  commodity_code: '123456',
  commodity_name: 'my product',
}

const economyTabTests = [
  { selector: '#market-Germany .name', expect: 'Germany' },
  { selector: '#market-Germany .avg-income', expect: '7,895' },
  { selector: '#market-Germany .avg-income .display-year', expect: '2018' },
  { selector: '#market-Netherlands .name', expect: 'Netherlands' },
  { selector: '.base-year', expect: /\s+2019\s+/ },
]

// Simulate use data response
let comparisonMarketResponse = { data: {} }

describe('Compare markets', () => {
  beforeAll(() => {
    const mainElement = document.createElement('span')
    document.body.appendChild(mainElement)
    ReactModal.setAppElement(mainElement)
  })

  beforeEach(() => {
    container = document.createElement('div')
    container.innerHTML =
      '<div id="next-steps">Next Steps</div><span id="cta-container"></span><span id="compare-market-container" ></span>'
    document.body.appendChild(container)
    Services.setConfig({
      csrfToken: '12345',
      apiCountriesUrl: '/api/countries/',
      apiSuggestedCountriesUrl: '/api/suggestedcountries/',
      apiCountryDataUrl: '/api/data-service/countrydata/',
      apiComTradeDataUrl: '/api/data-service/comtrade/',
      apiUserDataUrl: '/sso/api/user-data/-name-/',
      user: { id: '6' },
    })
    comparisonMarketResponse = { data: {} }
    fetchMock.get(/\/api\/countries\//, mockResponse)
    fetchMock.get(/\/api\/suggestedcountries\//, suggestedResponse)
    fetchMock.get(/\/api\/data-service\/comtrade\//, productApiResponse)
    fetchMock.get(/\/api\/data-service\/countrydata\//, countryDataApiResponse)
    fetchMock.get(
      /\/sso\/api\/user-data\/ComparisonMarkets\//,
      () => comparisonMarketResponse
    )
    userDataPostMock = fetchMock.post(
      /\/sso\/api\/user-data\//,
      (p1, p2) => JSON.parse(p2.body).data
    )
  })

  afterEach(() => {
    document.body.removeChild(container)
    container = null
    jest.clearAllMocks()
  })

  it('Forces product chooser when no product', async () => {
    Services.store.dispatch(
      actions.setInitialState({
        userSettings: {
          UserProducts: [],
          ActiveProduct: {},
          UserMarkets: [],
        },
      })
    )
    container.innerHTML =
      '<span id="cta-container"></span><span id="compare-market-container" ></span>'
    const dataTabs = '{ "population": true, "economy": true, "society": true }'
    const cmContainer = container.querySelector('#compare-market-container')
    cmContainer.setAttribute('data-tabs', dataTabs)
    cmContainer.setAttribute('data-max-places-allowed', 3)

    act(() => {
      CompareMarkets({
        element: container.querySelector('span'),
        cta_container: container.querySelector('#cta-container'),
      })
    })
    expect(document.body.querySelector('.product-finder')).toBeFalsy()

    await waitFor(() => {
      const button = container.querySelector('button')
      expect(button.textContent).toMatch('Select product')
    })
    // Click the button and check it opens product finder
    act(() => {
      Simulate.click(container.querySelector('button'))
    })
    const finder = document.body.querySelector('.product-finder')
    expect(document.body.querySelector('.product-finder')).toBeTruthy()
    const closeButton = finder.querySelector('button.dialog-close')
    act(() => {
      Simulate.click(closeButton)
    })
    expect(document.body.querySelector('.product-finder')).toBeFalsy()
  })

  it('Allows selection of markets and fetch data when product selected', async () => {
    // set up existing product in store

    const localContainer = container

    // set up the mock of user data with two countries
    const comparisonMarkets = {
      NL: { country_name: 'Netherlands', country_iso2_code: 'NL' },
      DE: { country_name: 'Germany', country_iso2_code: 'DE' },
    }

    Services.store.dispatch(
      actions.setInitialState({
        userSettings: {
          UserProducts: [selectedProduct],
          ActiveProduct: selectedProduct,
          ComparisonMarkets: comparisonMarkets,
          UserMarkets: [],
        },
      })
    )

    localContainer.innerHTML =
      '<span id="cta-container"></span><span id="compare-market-container" ></span>'
    const dataTabs = '{ "product": true, "economy": true, "society": true }'
    const cmContainer = container.querySelector('#compare-market-container')
    cmContainer.setAttribute('data-tabs', dataTabs)
    cmContainer.setAttribute('data-max-places-allowed', 3)

    act(() => {
      CompareMarkets({
        element: localContainer.querySelector('#compare-market-container'),
        cta_container: localContainer.querySelector('#cta-container'),
      })
    })
    // check mock directory api data...
    await waitFor(() => {
      expect(localContainer.querySelector('#market-Germany .name')).toBeTruthy()
    })

    // check economy data
    const economyTab = localContainer.querySelector(
      '.tab-list-item:nth-of-type(2)'
    )
    expect(economyTab.textContent).toMatch('ECONOMY')
    act(() => {
      Simulate.click(economyTab)
    })

    await waitFor(() => {
      expect(localContainer.querySelector('#market-Germany .name')).toBeTruthy()
      expect(
        localContainer.querySelector('#market-Germany .avg-income')
      ).toBeTruthy()
    })
    economyTabTests.forEach((test) => {
      const element = localContainer.querySelector(test.selector)
      if (!element) {
        if (!test.fail) {
          expect(test.selector).toEqual(
            'Following selector failed to return an element'
          )
        }
      } else {
        if (test.fail) {
          expect(test.selector).toEqual(
            'Following selector returned an element'
          )
        }
        expect(element.textContent).toMatch(test.expect)
      }
    })
    expect(localContainer.querySelectorAll('.tooltip button')).toHaveLength(3)
  })

  it('Allows markets to be added and removed from shortlist', async () => {
    const localContainer = container

    // set up the mock of user data with two countries
    const NL = { country_name: 'Netherlands', country_iso2_code: 'NL' }
    const DE = { country_name: 'Germany', country_iso2_code: 'DE' }
    const comparisonMarkets = { NL, DE }

    Services.store.dispatch(
      actions.setInitialState({
        userSettings: {
          UserProducts: [selectedProduct],
          ActiveProduct: selectedProduct,
          ComparisonMarkets: comparisonMarkets,
          UserMarkets: [NL],
        },
      })
    )

    localContainer.innerHTML =
      '<div id="next-steps">Next Steps</div><span id="cta-container"></span><span id="compare-market-container" ></span>'
    const dataTabs = '{ "product": true }'
    const cmContainer = container.querySelector('#compare-market-container')
    cmContainer.setAttribute('data-tabs', dataTabs)
    cmContainer.setAttribute('data-max-places-allowed', 3)
    act(() => {
      CompareMarkets({
        element: cmContainer,
        cta_container: localContainer.querySelector('#cta-container'),
      })
    })
    await waitFor(() => {
      expect(localContainer.querySelector('#market-Germany .name')).toBeTruthy()
    })
    const germanyCb = localContainer.querySelector(
      '#market-Germany .checkbox-favourite'
    )
    const netherlandsCb = localContainer.querySelector(
      '#market-Netherlands .checkbox-favourite'
    )
    expect(germanyCb.checked).toBeFalsy()
    expect(netherlandsCb.checked).toBeTruthy()
    act(() => {
      Simulate.change(germanyCb)
    })
    await waitFor(() => {
      const calls = userDataPostMock.calls()
      const lastcall = calls[calls.length - 1]
      const { data } = JSON.parse(lastcall[1].body)
      expect(data).toEqual([NL, DE])
    })
    act(() => {
      Simulate.change(netherlandsCb)
    })
    await waitFor(() => {
      const calls = userDataPostMock.calls()
      const lastcall = calls[calls.length - 1]
      const { data } = JSON.parse(lastcall[1].body)
      expect(data).toEqual([DE])
    })
  })
})
