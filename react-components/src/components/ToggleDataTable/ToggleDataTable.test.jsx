import React from 'react'
import { mount } from 'enzyme'
import { ToggleDataTable } from '@src/components/ToggleDataTable'
import { mapData } from '@src/components/ToggleDataTable/utils'
import Services from '@src/Services'
import { act } from 'react-dom/test-utils'

jest.mock('@src/Services')

let wrapper

const mockGroups = [
  { key: '0', label: '0-9 year olds' },
  { key: '10', label: '10-19 year olds' },
  { key: '20', label: '20-29 year olds' },
  { key: '30', label: '30-39 year olds' }
]

const mockResponse = {
  cia_factbook_data: {
    languages: {
      language: [{ name: 'English' }, { name: 'French' }, { name: 'Spanish' }]
    }
  },
  country_data: {
    consumer_price_index: {
      value: 123
    },
    internet_usage: {
      value: 80
    }
  },
  population_data: {
    female_target_age_population: 100,
    male_target_age_population: 200,
    total_population: 200,
    urban_percentage: 0.4,
    rural_percentage: 0.6,
    total_target_age_population: 1000,
  }
}

describe('ToggleDataTable', () => {

  beforeEach(() => {
    Services.getCountryAgeGroupData.mockImplementation(() => Promise.resolve())
    wrapper = mount(<ToggleDataTable groups={mockGroups} country="netherlands"><div className='table'>test</div></ToggleDataTable>)
  })

  afterEach(() => {
    wrapper = null
    Services.setConfig({})
    jest.clearAllMocks()
  })

  test('renders heading and select button initially', () => {
    expect(wrapper.find('h3').length).toEqual(1)
    expect(wrapper.find('.button--icon').length).toEqual(1)
    expect(wrapper.find('form').length).toEqual(0)
    expect(wrapper.find('.table').length).toEqual(0)
  })

  test('renders form', () => {
    wrapper.find('.button--icon').simulate('click', { type: 'click' })
    expect(wrapper.find('form').length).toEqual(1)
    expect(wrapper.find('.table').length).toEqual(0)
  })

  test('renders table', async () => {
    Services.getCountryAgeGroupData.mockImplementation(() => Promise.resolve(mockResponse))

    wrapper.find('.button--icon').simulate('click', { type: 'click' })
    wrapper
      .find('form input')
      .first()
      .simulate('change', { type: 'change', target: { value: mockGroups[0]['key'] } })

    await act(async () => {
      wrapper.find('form').simulate('submit', { preventDefault: () => {} })
    })

    wrapper.update()

    expect(wrapper.find('form').length).toEqual(0)
    expect(wrapper.find('.table').length).toEqual(1)
  })
})

describe('utils', () => {
  test('mapData', () => {
    expect(mapData(mockResponse.population_data)).toEqual({
      population: 0.2,
      urban: 40,
      rural: 60,
      female: 0.1,
      male: 0.2,
      targetPopulation: 1,
    })
  })
})
