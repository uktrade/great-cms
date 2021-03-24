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


const ageGroupDataApiResponse = (offset) => {
  return [buildRow('male', offset), buildRow('female', offset + 500)]
}

const countryDataApiResponse = {
  NL: {
    InternetUsage: [{ value: '94.712', year: 2018 }],
    ConsumerPriceIndex: [
      { value: '117.383', year: 2020 },
      { value: '115.908', year: 2019 },
    ],
    PopulationUrbanRural: [
      { urban_rural: 'urban', value: 15847, year: 2020 },
      { urban_rural: 'rural', value: 1334, year: 2020 },
    ],
  },
  DE: {
    InternetUsage: [{ value: '74.4', year: 2018 }],
    ConsumerPriceIndex: [
      { value: '113.427', year: 2020 },
      { value: '112.855', year: 2019 },
    ],
    PopulationUrbanRural: [
      { urban_rural: 'urban', value: 63930, year: 2020 },
      { urban_rural: 'rural', value: 18610, year: 2020 },
    ],
  },
}

const getText = (el, selector) => {
  const target = el && el.querySelector(selector)
  return (target && target.textContent) || ''
}

describe('Compare markets - population tab', () => {
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
      populationByCountryUrl: '/export-plan/api/country-data/',
      apiCountryDataUrl: '/api/data-service/countrydata/',
      user: { id: '6' },
    })
    fetchMock.get(/\/api\/data-service\/countrydata\//, countryDataApiResponse)
  })

  afterEach(() => {
    document.body.removeChild(container)
    container = null
    jest.clearAllMocks()
  })

  it('Opens population tab', async () => {
    // set up existing product in store
    let selectedProduct = {
      commodity_code: '123456',
      commodity_name: 'my product',
    }

    const localContainer = container

    Object.defineProperty(window.document, 'cookie', {
      writable: true,
      value: encodeURI(
        `comparisonMarkets_6=${JSON.stringify({
          NL: { country_name: 'Netherlands', country_iso2_code: 'NL' },
          DE: { country_name: 'Germany', country_iso2_code: 'DE' },
        })}`
      ),
    })

    Services.store.dispatch(
      actions.setInitialState({ exportPlan: { products: [selectedProduct] } })
    )

    localContainer.innerHTML =
      '<span id="cta-container"></span><span id="compare-market-container" ></span>'
    const dataTabs = '{ "population": true }'
    localContainer
      .querySelector('#compare-market-container')
      .setAttribute('data-tabs', dataTabs)
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
    const rowGermany = localContainer.querySelector('#market-Germany')
    expect(getText(rowGermany, '.total_population')).toMatch('82.5 million')
    expect(getText(rowGermany, '.internet_usage')).toMatch('74%')
    expect(getText(rowGermany, '.urban_population .primary')).toMatch('77%')
    expect(getText(rowGermany, '.urban_population .secondary')).toMatch(
      '63.9 million'
    )
    expect(getText(rowGermany, '.rural_population .primary')).toMatch('23%')
    expect(getText(rowGermany, '.rural_population .secondary')).toMatch(
      '18.6 million'
    )
  })

  it('Compare markets - Mobile layout', async () => {
    // set a little window
    Object.assign(window, { innerWidth: 600 });
    // set up existing product in store

    let selectedProduct = {
      commodity_code: '123456',
      commodity_name: 'my product',
    }

    const localContainer = container

    Object.defineProperty(window.document, 'cookie', {
      writable: true,
      value: encodeURI(
        `comparisonMarkets_6=${JSON.stringify({
          NL: { country_name: 'Netherlands', country_iso2_code: 'NL' },
          DE: { country_name: 'Germany', country_iso2_code: 'DE' },
        })}`
      ),
    })

    Services.store.dispatch(
      actions.setInitialState({ exportPlan: { products: [selectedProduct] } })
    )

    localContainer.innerHTML =
      '<span id="cta-container"></span><span id="compare-market-container" ></span>'
    const dataTabs = '{ "population": true }'
    localContainer
      .querySelector('#compare-market-container')
      .setAttribute('data-tabs', dataTabs)
    act(() => {
      CompareMarkets({
        element: localContainer.querySelector('#compare-market-container'),
        cta_container: localContainer.querySelector('#cta-container'),
      })
    })
    // check mock directory api data...
    await waitFor(() => {
      expect(getText(localContainer, '.market-details .selected-places')).toBeTruthy()
    })
    const selectedPlaces = localContainer.querySelector('.market-details .selected-places')
    expect(getText(selectedPlaces, 'div')).toMatch('NetherlandsGermany')
    expect(getText(selectedPlaces, 'button.add-market')).toMatch('Add place 3 of 10')
    const rows = localContainer.querySelectorAll('.market-details .total_population tr')
    expect(rows.length).toEqual(2)
    expect(getText(rows[0], ' .country-name')).toMatch('Netherlands')
    expect(getText(rows[0], 'td')).toMatch('17.2 million')
    expect(getText(rows[1], ' .country-name')).toMatch('Germany')
    expect(getText(rows[1], 'td')).toMatch('82.5 million')
  })
})
