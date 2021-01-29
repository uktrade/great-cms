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

const populationApiResponse = [
  {
    country: 'Germany',
    internet_usage: { value: '74.39', year: 2018 },
    rural_population_total: 17125,
    rural_population_percentage_formatted: '28.32% (17.12 million)',
    urban_population_total: 42007,
    urban_population_percentage_formatted: '69.48% (42.01 million)',
    total_population: '60.46 million',
    total_population_raw: 60463456,
    cpi: { value: '110.62', year: 2019 },
  },
]

const economyApiResponse = {
  Germany: {
    import_from_world: {
      year: '2017',
      trade_value_raw: 21670,
      country_name: 'Germany',
      year_on_year_change: '2.751',
    },
    import_data_from_uk: {
      year: '2019',
      trade_value_raw: 135150,
      country_name: 'Germany',
      year_on_year_change: '0.736',
    },
    country_data: {
      consumer_price_index: {
        country_name: 'Germany',
        country_code: 'DEU',
        value: '112.855',
        year: 2019,
      },
      corruption_perceptions_index: {
        total: 180,
        country_name: 'Germany',
        country_code: 'DEU',
        cpi_score_2019: 80,
        rank: 9,
        year: 2017
      },
      ease_of_doing_bussiness: {
        total: 264,
        country_name: 'Germany',
        country_code: 'DEU',
        year_2019: 22,
        rank: 22,
        year: 2019,
      },
      gdp_per_capita: {
        country_name: 'Germany',
        country_code: 'DEU',
        year_2019: '46258.878',
      },
      income: {
        country_name: 'Germany',
        country_code: 'DEU',
        year: 2018,
        value: '7895',
      },
    },
  },
  Netherlands: {
    import_from_world: {
      year: '2019',
      trade_value_raw: 21670,
      country_name: 'Netherlands',
      year_on_year_change: '2.751',
    },
    import_data_from_uk: {
      year: '2019',
      trade_value_raw: 135150,
      country_name: 'Netherlands',
      year_on_year_change: '0.736',
    },
    country_data: {
      consumer_price_index: {
        country_name: 'Netherlands',
        value: '112.855',
        year: 2019,
      },
      income: {
        country_name: 'Netherlands',
        year: 2018,
        value: '7895',
      },
    },
  },


}

const economyTabTests = [
  {selector: '#market-Germany .name', expect: 'Germany' },
  {selector: '#market-Germany .world-import-value .primary', expect: '21,670' },
  {selector: '#market-Germany .world-import-value .secondary', expect: '+2.8% vs 2016' },
  {selector: '#market-Germany .uk-import-value .primary', expect: '135,150' },
  {selector: '#market-Germany .uk-import-value .secondary', expect: '+0.7% vs 2018' },
  {selector: '#market-Germany .avg-income', expect: '7,895' },
  {selector: '#market-Germany .avg-income .display-year', expect: '2018'},
  {selector: '#market-Germany .cpi', expect: '9' },
  {selector: '#market-Germany .eod-business', expect: '22 of 264'},
  {selector: '#market-Germany .eod-business .display-year', fail:true},
  {selector: '#market-Germany .cpi', expect: '9 of 180'},
  {selector: '#market-Germany .cpi .display-year', expect: '2017'},
  {selector: '#market-Netherlands .name', expect: 'Netherlands'},
  {selector: '#market-Netherlands .eod-business', expect: 'Data not available'},
  {selector: '#market-Netherlands .cpi', expect: 'Data not available'},
  {selector: '.base-year', expect: /\s+2019\s+/},
]

const societyApiResponse = [
  {
    country: 'Germany',
    languages: {
      date: '2018',
      note: 'Danish, Frisian, Sorbian, and Romani are official minority languages',
      language: [
        {
          name: 'German',
          note: 'official',
        },
      ]
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
      ]
    },
    rule_of_law: {
      country_name: 'Germany',
      iso2: 'DE',
      rank: 16,
      score: '89.200',
    },
  },
]

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
    populationByCountryUrl: '/export-plan/api/country-data/',
    apiComTradeDataUrl: '/api/data-service/comtrade/',
    societyByCountryUrl: '/export-plan/api/society-data/',
  })
  countriesMock = fetchMock.get(/\/api\/countries\//, mockResponse)
  fetchMock.get(/\/api\/suggestedcountries\//, suggestedResponse)
  fetchMock.get(/\/export-plan\/api\/country-data\//, populationApiResponse)
  fetchMock.get(/\/api\/data-service\/comtrade\//, economyApiResponse)
  fetchMock.get(/\/export-plan\/api\/society-data\//, societyApiResponse)
})

afterEach(() => {
  document.body.removeChild(container)
  container = null
  jest.clearAllMocks()
})

it('Forces product chooser when no product', () => {

  container.innerHTML = '<span id="cta-container"></span><span id="compare-market-container" ></span>'
  const dataTabs = '{ "population": true, "economy": true, "society": true }'
  container
    .querySelector('#compare-market-container')
    .setAttribute('data-tabs', dataTabs)

  act(() => {
    CompareMarkets({
      element: container.querySelector('span'),
      cta_container: container.querySelector('#cta-container'),
    })
  })
  expect(document.body.querySelector('.product-finder')).toBeFalsy()
  // Click the button and check it opens product finder
  const button = container.querySelector('button')

  expect(button.textContent).toMatch('Select product')
  act(() => {
    Simulate.click(button)
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

  Object.defineProperty(window.document, 'cookie', {
    writable: true,
    value: encodeURI(`comparisonMarkets=${JSON.stringify({
      NL:{country_name:'Netherlands',
        country_iso2_code:'NL'
      },
      DE:{country_name:'Germany',
        country_iso2_code:'DE'
      },
    })}`),
  });

  Services.store.dispatch(
    actions.setInitialState({ exportPlan: { products: [selectedProduct] } })
  )

  container.innerHTML = '<span id="cta-container"></span><span id="compare-market-container" ></span>'
  const dataTabs = '{ "population": true, "economy": true, "society": true }'
  container
    .querySelector('#compare-market-container')
    .setAttribute('data-tabs', dataTabs)

  act(() => {
    CompareMarkets({
      element: container.querySelector('#compare-market-container'),
      cta_container: container.querySelector('#cta-container'),
    })
  })
  // check mock directory api data...
  await waitFor(() => {
    expect( container.querySelector('#market-Germany .name')).toBeTruthy()
  })
  const rowGermany = container.querySelector('#market-Germany')
  expect(rowGermany.querySelector('.name').textContent).toMatch('Germany')
  expect(rowGermany.querySelector('.total_population').textContent).toMatch(
    '60.5 million'
  )
  expect(rowGermany.querySelector('.internet_usage').textContent).toMatch('74%')
  expect(rowGermany.querySelector('.urban_population .primary').textContent).toMatch('69%')
  expect(rowGermany.querySelector('.urban_population .secondary').textContent).toMatch('42.0 million')
  expect(rowGermany.querySelector('.rural_population').textContent).toMatch(
    /28%\s*17.1 million/
  )

  // check economy data
  const economy_tab = container.querySelector('.tab-list-item:nth-of-type(2)')
  expect(economy_tab.textContent).toMatch('ECONOMY')
  act(() => {
    Simulate.click(economy_tab)
  })
  await waitFor(() => {
    expect( container.querySelector('#market-Germany .name')).toBeTruthy()
    expect( container.querySelector('#market-Germany .world-import-value .primary')).toBeTruthy()
  })
  economyTabTests.forEach((test) => {
    let element = container.querySelector(test.selector)
    if(!element) {
      if(!test.fail) {
        expect(test.selector).toEqual('Following selector failed to return an element')
      }
    } else {
      if(test.fail) {
        expect(test.selector).toEqual('Following selector returned an element')
      }
      expect(element.textContent).toMatch(test.expect)
    }
  })
  expect(container.querySelectorAll('.tooltip button').length).toEqual(3) 

  // check society data
  const society_tab = container.querySelector('.tab-list-item:nth-of-type(3)')
  expect(society_tab.textContent).toMatch('SOCIETY')
  act(() => {
    Simulate.click(society_tab)
  })
  await waitFor(() => {
    const rowSocietyGermany = container.querySelector('#market-Germany')
    expect(rowSocietyGermany.querySelector('.name').textContent).toMatch(
      'Germany'
    )
    expect(
      rowSocietyGermany.querySelector('.religion').textContent
    ).toMatch('Roman Catholic - 28%Protestant - 26%Muslim - 5%Orthodox - 2%other Christian - 1%2018')
    expect(
      rowSocietyGermany.querySelector('.language').textContent
    ).toMatch('German2018. Danish, Frisian, Sorbian, and Romani are official minority languages')
    expect(
      rowSocietyGermany.querySelector('.rule-of-law').textContent
    ).toMatch('16 of 131')
  })
})

it('Select market from selection area', async () => {
  container.innerHTML =
    '<span id="cta-container"></span><span id="compare-market-container" data-productname="my product" data-productcode="123456"></span><span id="comparison-market-selector"></span>'
  const dataTabs = '{"population":true, "economy":true, "society": true}'
  container
    .querySelector('#compare-market-container')
    .setAttribute('data-tabs', dataTabs)

  // set up existing product in store
  let selectedProduct = {
    commodity_code: '123456',
    commodity_name: 'my product',
  }

  Object.defineProperty(window.document, 'cookie', {
    writable: true,
    value: 'comparisonMarkets=',
  });

  Services.store.dispatch(
    actions.setInitialState({ exportPlan: { products: [selectedProduct] } })
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
    'Add country to compare'
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
      'Add country 2 of 3'
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
    expect(container.querySelector('button.add-market').textContent).toMatch(
      'Add country 3 of 3'
    )
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
