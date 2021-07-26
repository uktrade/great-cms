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

const ageGroupCategories = [
  '0-4',
  '5-9',
  '10-14',
  '15-19',
  '20-24',
  '25-29',
  '30-34',
  '35-39',
  '40-44',
  '45-49',
  '50-54',
  '55-59',
  '60-64',
  '65-69',
  '70-74',
  '75-79',
  '80-84',
  '85-89',
  '90-94',
  '95-99',
  '100+',
]

const buildRow = (gender, running) => {
  return ageGroupCategories.reduce(
    (acc, agc) => {
      running += 10
      const tmp = { ...acc }
      tmp[agc] = running
      return tmp
    },
    { gender, year: '2019' }
  )
}

const ageGroupDataApiResponse = (offset) => {
  return [buildRow('male', offset), buildRow('female', offset + 500)]
}

const countryDataApiResponse = {
  DE: {
    PopulationData: ageGroupDataApiResponse(2000),
  },
  NL: {
    PopulationData: ageGroupDataApiResponse(1000),
  },
}

// set up the mock of user data with two countries
const comparisonMarketResponse = {
  data: {
      NL: { country_name: 'Netherlands', country_iso2_code: 'NL' },
      DE: { country_name: 'Germany', country_iso2_code: 'DE' },
  },
}

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
      populationByCountryUrl: '/export-plan/api/country-data/',
      apiCountryDataUrl: '/api/data-service/countrydata/',
      apiUserDataUrl: '/sso/api/user-data/',
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

  it('Opens age group tab', async () => {
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
    const dataTabs = '{ "agegroups": true }'
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
      const rowGermany = localContainer.querySelector('#market-Germany')
      expect(rowGermany.querySelector('.loading')).toBeFalsy()
    })
    const rowGermany = localContainer.querySelector('#market-Germany')
    expect(getText(rowGermany, '.total_population')).toEqual('99.1 million100%')
    expect(getText(rowGermany, '.male_population')).toEqual('44.3 million45%')
    expect(getText(rowGermany, '.female_population')).toEqual('54.8 million55%')

    act(() => {
      const firstButton = localContainer.querySelector('.filter #cb-sector0_14')
      Simulate.click(firstButton)
    })
    expect(getText(rowGermany, '.total_population')).toEqual('13.6 million14%')
    expect(getText(rowGermany, '.male_population')).toEqual('6.1 million6%')
    expect(getText(rowGermany, '.female_population')).toEqual('7.6 million8%')
    act(() => {
      const secondButton = localContainer.querySelector(
        '.filter #cb-sector15_19'
      )
      Simulate.click(secondButton)
    })
    expect(getText(rowGermany, '.total_population')).toEqual('18.2 million18%')
    act(() => {
      const secondButton = localContainer.querySelector(
        '.filter #cb-sector15_19'
      )
      Simulate.click(secondButton)
    })
    expect(getText(rowGermany, '.total_population')).toEqual('13.6 million14%')
    act(() => {
      const firstButton = localContainer.querySelector('.filter #cb-sector0_14')
      Simulate.click(firstButton)
    })
    expect(getText(rowGermany, '.total_population')).toEqual('99.1 million100%')
  })
})
