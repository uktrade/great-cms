/* eslint-disable */
import { act, Simulate } from 'react-dom/test-utils'
import CompareMarkets from '@src/components/CompareMarkets'
import SelectMarket from '@src/components/CompareMarkets/SelectMarket'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'
import { waitFor } from '@testing-library/react'
import ReactModal from 'react-modal'

let container
let countriesMock

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

const economyTabTests = [
  { selector: '#market-Germany .name', expect: 'Germany' },
  { selector: '#market-Germany .avg-income', expect: '7,895' },
  { selector: '#market-Germany .avg-income .display-year', expect: '2018' },
  { selector: '#market-Netherlands .name', expect: 'Netherlands' },
  { selector: '.base-year', expect: /\s+2019\s+/ },
]

// Simulate use data response
let comparisonMarketResponse = { data: {} }

const getText = (el, selector) => {
  const target = el && el.querySelector(selector)
  return (target && target.textContent) || ''
}

describe('Compare markets', () => {
  beforeAll(() => {
    const mainElement = document.createElement('span')
    document.body.appendChild(mainElement)
    ReactModal.setAppElement(mainElement)
  })

  beforeEach(() => {
    container = document.createElement('div')
    container.innerHTML =
      '<span id="compare-market-container" data-productname="my product" data-productcode="080450" ></span>'
    document.body.appendChild(container)
    Services.setConfig({
      csrfToken: '12345',
      apiCountriesUrl: '/api/countries/',
      apiSuggestedCountriesUrl: '/api/suggestedcountries/',
      apiCountryDataUrl: '/api/data-service/countrydata/',
      apiComTradeDataUrl: '/api/data-service/comtrade/',
      apiUserDataUrl: '/sso/api/user-data/',
      user: { id: '6' },
    })
    comparisonMarketResponse = { data: {} }
    countriesMock = fetchMock.get(/\/api\/countries\//, mockResponse)
    fetchMock.get(/\/api\/suggestedcountries\//, suggestedResponse)
    fetchMock.get(/\/api\/data-service\/comtrade\//, productApiResponse)
    fetchMock.get(/\/api\/data-service\/countrydata\//, countryDataApiResponse)
    fetchMock.get(/\/sso\/api\/user-data\//, () => comparisonMarketResponse)
    fetchMock.post(/\/sso\/api\/user-data\//, (p1, p2, p3) => {
      comparisonMarketResponse = JSON.parse(p2.body).data
      return comparisonMarketResponse
    })
  })

  afterEach(() => {
    document.body.removeChild(container)
    container = null
    jest.clearAllMocks()
  })

  it('Forces product chooser when no product', async () => {
    container.innerHTML =
      '<span id="cta-container"></span><span id="compare-market-container" ></span>'
    const dataTabs = '{ "population": true, "economy": true, "society": true }'
    const cm_container = container.querySelector('#compare-market-container')
    cm_container.setAttribute('data-tabs', dataTabs)
    cm_container.setAttribute('data-max-places-allowed', 3)

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
    let selectedProduct = {
      commodity_code: '123456',
      commodity_name: 'my product',
    }

    const localContainer = container

    // set up the mock of user data with two countries
    comparisonMarketResponse = {
      data: {
        NL: { country_name: 'Netherlands', country_iso2_code: 'NL' },
        DE: { country_name: 'Germany', country_iso2_code: 'DE' },
      },
    }

    Services.store.dispatch(
      actions.setInitialState({ userBasket: { products: [selectedProduct] } })
    )

    localContainer.innerHTML =
      '<span id="cta-container"></span><span id="compare-market-container" ></span>'
    const dataTabs = '{ "product": true, "economy": true, "society": true }'
    const cm_container = container.querySelector('#compare-market-container')
    cm_container.setAttribute('data-tabs', dataTabs)
    cm_container.setAttribute('data-max-places-allowed', 3)
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
    const economy_tab = localContainer.querySelector(
      '.tab-list-item:nth-of-type(2)'
    )
    expect(economy_tab.textContent).toMatch('ECONOMY')
    act(() => {
      Simulate.click(economy_tab)
    })

    await waitFor(() => {
      expect(localContainer.querySelector('#market-Germany .name')).toBeTruthy()
      expect(
        localContainer.querySelector('#market-Germany .avg-income')
      ).toBeTruthy()
    })
    economyTabTests.forEach((test) => {
      let element = localContainer.querySelector(test.selector)
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
    expect(localContainer.querySelectorAll('.tooltip button').length).toEqual(3)
  })

  it('Select market from selection area', async () => {
    container.innerHTML =
      '<span id="cta-container"></span><span id="compare-market-container" data-productname="my product" data-productcode="123456"></span><span id="comparison-market-selector"></span>'
    const dataTabs = '{"population":true, "economy":true, "society": true}'
    const cm_container = container.querySelector('#compare-market-container')
    cm_container.setAttribute('data-tabs', dataTabs)
    cm_container.setAttribute('data-max-places-allowed', 3)

    // set up existing product in store
    let selectedProduct = {
      commodity_code: '123456',
      commodity_name: 'my product',
    }
    Object.defineProperty(window.document, 'cookie', {
      writable: true,
      value: 'comparisonMarkets_6=',
    })
    Services.store.dispatch(
      actions.setInitialState({ userBasket: { products: [selectedProduct] } })
    )

    act(() => {
      CompareMarkets({
        element: container.querySelector('#compare-market-container'),
        cta_container: container.querySelector('#cta-container'),
      })
      SelectMarket({
        element: container.querySelector('#comparison-market-selector'),
      })
    })
    await waitFor(() => {
      expect(container.querySelector('button.add-market')).toBeTruthy()
    })
    expect(container.querySelector('button.add-market').textContent).toMatch(
      'Add a place'
    )

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
      expect(container.querySelector('button.add-market').textContent).toMatch(
        'Add place 2 of 3'
      )
    })
    // check that the country appears in the selection section at the page base
    const marketSelectionBar = container.querySelector(
      '#comparison-market-selector'
    )
    expect(marketSelectionBar.querySelector('button').textContent).toMatch(
      'Germany'
    )

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
      expect(
        container.querySelector('button.add-market') &&
          container.querySelector('button.add-market').textContent
      ).toMatch('Add place 3 of 3')
    })

    let buttonSweden = marketSelectionBar.querySelector('button.market-SE')
    // check that the country appears in the selection section at the page base
    expect(buttonSweden.textContent).toMatch('Sweden')
    // remove sweden and watch it vanish from selection bar
    act(() => {
      Simulate.click(
        container.querySelector('.market-details button[data-id=SE]')
      )
    })
    await waitFor(() => {
      expect(marketSelectionBar.querySelector('button.market-SE')).toBeFalsy()
    })
  })
})
