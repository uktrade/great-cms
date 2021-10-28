/* eslint-disable */
import { act, Simulate } from 'react-dom/test-utils'
import CompareMarkets from '@src/components/CompareMarkets'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'
import { waitFor } from '@testing-library/react'
import ReactModal from 'react-modal'

let container

const countryDataApiResponse = {
  DE: {
    CorruptionPerceptionsIndex: [
      {
        total: 180,
        cpi_score_2019: 80,
        rank: 9,
        year: 2017,
      },
    ],
    EaseOfDoingBusiness: [
      {
        max_rank: 264,
        year_2019: 22,
        rank: 22,
        year: 2019,
      },
    ],
    RuleOfLaw: [
      {
        rank: 16,
        score: '89.200',
      },
    ],
  },
}

// set up the mock of user daa with two countries
const comparisonMarketResponse = {
  ComparisonMarkets: {
    DE: { country_name: 'Germany', country_iso2_code: 'DE' },
  },
}

const getText = (el, selector) => {
  const target = el && el.querySelector(selector)
  return (target && target.textContent) || ''
}

describe('Compare markets - Business tab', () => {
  beforeAll(() => {
    const mainElement = document.createElement('span')
    document.body.appendChild(mainElement)
    ReactModal.setAppElement(mainElement)
  })

  beforeEach(() => {
    container = document.createElement('div')
    container.innerHTML =
      '<span id="compare-market-container"></span>'
    document.body.appendChild(container)
    Services.setConfig({
      csrfToken: '12345',
      apiUserDataUrl: '/sso/api/user-data/',
      apiCountryDataUrl: '/api/data-service/countrydata/',
      user: { id: '6' },
    })

    fetchMock.get(/\/api\/data-service\/countrydata\//, countryDataApiResponse)
    fetchMock.get(/\/sso\/api\/user-data\//, () => comparisonMarketResponse)
  })

  afterEach(() => {
    document.body.removeChild(container)
    container = null
    jest.clearAllMocks()
  })

  it('Opens product tab', async () => {
    // set up existing product in store
    let selectedProduct = {
      commodity_code: '123456',
      commodity_name: 'my product',
    }

    const localContainer = container

    Services.store.dispatch(
      actions.setInitialState({
        userSettings: { UserProducts: [selectedProduct] },
      })
    )

    localContainer.innerHTML =
      '<span id="cta-container"></span><span id="compare-market-container" ></span>'
    const dataTabs = '{ "business": true }'
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
    expect(getText(rowGermany, '.eod-business')).toMatch('22 of 264')
    expect(getText(rowGermany, '.cpi')).toMatch('9 of 180')
    expect(getText(rowGermany, '.cpi .display-year')).toMatch('2017')
    expect(getText(rowGermany, '.rule-of-law')).toMatch('16 of 131')
  })
})
