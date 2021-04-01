/* eslint-disable */
import { act, Simulate } from 'react-dom/test-utils'
import Services from '@src/Services'
import actions from '@src/actions'
import fetchMock from 'fetch-mock'
import { waitFor } from '@testing-library/react'
import { createDataSnapShot } from '@src/views/sections/TargetMarketResearch'

let container

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
    CorruptionPerceptionsIndex: [
      {
        total: 180,
        country_name: 'Germany',
        country_code: 'DEU',
        cpi_score_2019: 80,
        rank: 9,
        year: 2017,
      },
    ],
    EaseOfDoingBusiness: [
      {
        max_rank: 264,
        country_name: 'Germany',
        country_code: 'DEU',
        year_2019: 22,
        rank: 22,
        year: 2019,
      },
    ],
    GDPPerCapita: [
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
    ComtradeReport: [
      {
        year: 2019,
        uk_or_world: 'WLD',
        trade_value: 1234,
      },
      {
        year: 2018,
        uk_or_world: 'WLD',
        trade_value: 1000,
      },
      {
        year: 2019,
        uk_or_world: 'GBR',
        trade_value: 12,
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
        year: 2018,
        value: '7895',
      },
    ],
  },
}

const selectedProduct = {
  commodity_code: '123456',
  commodity_name: 'my product',
}
const knownMarket = {
  country_name: 'Germany',
  country_iso2_code: 'DE',
}
const unknownMarket = {
  country_name: 'Spain',
  country_iso2_code: 'ES',
}

const getText = (el, selector) => {
  const target = el && el.querySelector(selector)
  return (target && target.textContent) || ''
}

describe('Target Market research', () => {
  beforeEach(() => {
    container = document.createElement('div')
    document.body.appendChild(container)
    Services.setConfig({
      csrfToken: '12345',
      apiUpdateExportPlanUrl: '/api/export-plan/api/update/',
      apiCountryDataUrl: '/api/data-service/countrydata/',
      user: { id: '6' },
    })
    fetchMock.get(/\/api\/data-service\/countrydata\//, countryDataApiResponse)
    fetchMock.post(/\/api\/export-plan\/api\/update\//, 200)

    Services.store.dispatch(
      actions.setInitialState({
        exportPlan: { products: [selectedProduct], markets: [unknownMarket] },
      })
    )
  })

  afterEach(() => {
    document.body.removeChild(container)
    container = null
    jest.clearAllMocks()
  })

  it('Renders market research data snapshot', async () => {
    act(() => {
      createDataSnapShot({
        element: container,
        groups: [],
        selected: [],
        currentSection: { url: 'Some url' },
      })
    })
    const expander = container.querySelector('button')
    expect(expander.textContent).toMatch('Open Data Snapshot')
    act(() => {
      Simulate.click(expander)
    })
    // We're starting with a country with no data - check the not available text
    await waitFor(() => {
      const caption = container.querySelector('.world-trade-value')
      expect(caption).toBeTruthy()
    })
    expect(
      getText(container, '.world-trade-value .statistic__caption')
    ).toMatch('my product import value (USD)')
    expect(getText(container, '.world-trade-value .statistic__figure')).toMatch(
      'Data not available'
    )
    expect(getText(container, '.uk-trade-value .statistic__caption')).toMatch(
      'my product import value from the UK (USD)'
    )
    expect(getText(container, '.uk-trade-value .statistic__figure')).toMatch(
      'Data not available'
    )
    // Change to a known market on the fly - React should re-render, so wait for correct content
    Services.store.dispatch(actions.setMarket(knownMarket))
    await waitFor(() => {
      expect(
        getText(container, '.world-trade-value .statistic__caption')
      ).toMatch('my product import value in 2019 (USD)')
    })
    expect(
      getText(container, '.world-trade-value .statistic__caption')
    ).toMatch('my product import value in 2019 (USD)')
    expect(getText(container, '.world-trade-value .statistic__figure')).toMatch(
      '1,234'
    )
    expect(getText(container, '.uk-trade-value .statistic__caption')).toMatch(
      'my product import value from the UK in 2019 (USD)'
    )
    expect(getText(container, '.uk-trade-value .statistic__figure')).toMatch(
      '12'
    )
    expect(
      getText(container, '.year-on-year-change .statistic__figure')
    ).toMatch('+23.4% vs 2018')
    expect(getText(container, '.gdp-per-capita .statistic__figure')).toMatch(
      '46,259'
    )
    expect(getText(container, '.income-per-capita .statistic__figure')).toMatch(
      '7,895'
    )
  })
})
