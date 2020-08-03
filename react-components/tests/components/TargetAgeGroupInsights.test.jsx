import React from 'react'
import { shallow } from 'enzyme'
import fetchMock from 'fetch-mock'
import { TargetAgeGroupInsights } from '@src/components/TargetAgeGroupInsights/TargetAgeGroupInsights'
import { mapData } from '@src/components/TargetAgeGroupInsights/utils'
import Services from '@src/Services'

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

describe('TargetAgeGroupInsights', () => {
  beforeEach(() => {
    wrapper = shallow(<TargetAgeGroupInsights groups={mockGroups} country="netherlands" />)
  })

  afterEach(() => {
    wrapper = null
  })

  test('renders heading and select button initially', () => {
    expect(wrapper.find('.target-age-group-insights__heading').length).toEqual(1)
    expect(wrapper.find('.target-age-group-insights__select-button').length).toEqual(1)
    expect(wrapper.find('form').length).toEqual(0)
    expect(wrapper.find('Table').length).toEqual(0)
  })

  test('renders form', () => {
    expect(wrapper.instance().state.isOpen).toBe(false)
    wrapper.find('.target-age-group-insights__select-button').simulate('click', { type: 'click' })
    expect(wrapper.instance().state.isOpen).toBe(true)
    expect(wrapper.find('form').length).toEqual(1)
    expect(wrapper.find('Table').length).toEqual(0)
  })

  test('renders table', () => {
    Services.setConfig({
      marketingCountryData: '/api/marketing-country-data'
    })
    fetchMock.get(Services.config.getMarketingCountryData, mockResponse)

    wrapper.find('.target-age-group-insights__select-button').simulate('click', { type: 'click' })
    wrapper
      .find('form input')
      .first()
      .simulate('change', { type: 'change', target: { value: mockGroups[0]['key'] } })

    wrapper.find('form').simulate('submit', { preventDefault: () => {} })

    expect(wrapper.instance().state.isOpen).toBe(false)
    expect(wrapper.find('form').length).toEqual(0)
    expect(wrapper.find('Table').length).toEqual(1)
  })
})

describe('utils', () => {
  test('mapData', () => {
    expect(mapData(mockResponse)).toEqual({
      population: 0.2,
      cpi: '123.00',
      urban: 40,
      rural: 60,
      female: 0.1,
      male: 0.2,
      internet_percentage: 80,
      internet_total: 0.2,
      target_population: 1,
      target_population_percentage: 500,
      languages: 'English, French, Spanish'
    })
  })
})
