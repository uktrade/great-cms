/* eslint-disable */
import { act, Simulate } from 'react-dom/test-utils'
import CompareMarkets from '@src/components/CompareMarkets'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'
import { waitFor } from '@testing-library/react'
import ReactModal from 'react-modal'

let container

const societyApiResponse = [
  {
    country: 'Germany',
    languages: {
      date: '2018',
      note:
        'Danish, Frisian, Sorbian, and Romani are official minority languages',
      language: [
        {
          name: 'German',
          note: 'official',
        },
      ],
    },
    religions: {
      date: '2018',
      religion: [
        {
          name: 'Roman Catholic',
          percent: 27.7,
        },
        {
          name: 'Protestant',
          percent: 25.5,
        },
        {
          name: 'Muslim',
          percent: 5.1,
        },
        {
          name: 'Orthodox',
          percent: 1.9,
        },
        {
          name: 'other Christian',
          percent: 1.1,
        },
        {
          name: 'other .9%',
        },
        {
          name: 'none',
          percent: 37.8,
        },
      ],
    },
  },
]

const countryDataApiResponse = {
  DE: {
    PopulationUrbanRural: [
      {
        urban_rural: 'urban',
        value:1000,
        year: 2020,
      },
      {
        urban_rural: 'rural',
        value:500,
        year: 2020,
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

describe('Compare markets - Society tab', () => {
  beforeAll(() => {
    const mainElement = document.createElement('span')
    document.body.appendChild(mainElement)
    ReactModal.setAppElement(mainElement)
  })

  beforeEach(() => {
    container = document.createElement('div')
    document.body.appendChild(container)
    Services.setConfig({
      csrfToken: '12345',
      apiUserDataUrl: '/sso/api/user-data/',
      societyByCountryUrl: '/export-plan/api/society-data/',
      apiCountryDataUrl: '/api/data-service/countrydata/',
      apiUserDataUrl: '/sso/api/user-data/-name-/',
      user: { id: '6' },
    })
    fetchMock.get(/\/export-plan\/api\/society-data\//, societyApiResponse)
    fetchMock.get(/\/api\/data-service\/countrydata\//, countryDataApiResponse)
    fetchMock.get(/\/sso\/api\/user-data\/ComparisonMarkets\//,() => {
      return comparisonMarketResponse
    })
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
      actions.setInitialState({ userBasket: { products: [selectedProduct] } })
    )
    localContainer.innerHTML =
      '<span id="cta-container"></span><span id="compare-market-container" ></span>'
    const dataTabs = '{ "society": true }'
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

    expect(getText(rowGermany, '.religion')).toMatch('Roman Catholic - 28%Protestant - 26%Muslim - 5%Orthodox - 2%other Christian - 1%2018')
    expect(getText(rowGermany, '.language')).toMatch('German2018. Danish, Frisian, Sorbian, and Romani are official minority languages')
    expect(getText(rowGermany, '.urban_population')).toMatch('Urban - 67%Rural - 33%')
  })
})
