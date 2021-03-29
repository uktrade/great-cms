import React from 'react'
import { mount } from 'enzyme'
import { ToggleDataTable } from '@src/components/ToggleDataTable'
import Services from '@src/Services'
import { act } from 'react-dom/test-utils'

jest.mock('@src/Services')

let wrapper

const mockGroups = [
  { value: '0', label: '0-9 year olds' },
  { value: '10', label: '10-19 year olds' },
  { value: '20', label: '20-29 year olds' },
  { value: '30', label: '30-39 year olds' },
]

const mockResponse = {
  population_data: {
    female_target_age_population: 100,
    male_target_age_population: 200,
    total_population: 200,
    urban_percentage: 0.4,
    rural_percentage: 0.6,
    total_target_age_population: 1000,
  },
}

describe('ToggleDataTable', () => {
  beforeEach(() => {
    Services.getCountryAgeGroupData.mockImplementation(() =>
      Promise.resolve(mockResponse)
    )
    wrapper = mount(
      <ToggleDataTable
        groups={mockGroups}
        countryIso2Code="NL"
        selectedGroups={['30']}
        url="/export-plan"
      >
        <div className="table">test</div>
      </ToggleDataTable>
    )
  })

  afterEach(() => {
    wrapper = null
    Services.setConfig({})
    jest.clearAllMocks()
  })

  test('Should fetch country data', () => {
    expect(Services.getCountryAgeGroupData).toHaveBeenCalledWith({
      country_iso2_code: 'NL',
      section_name: '/export-plan',
      target_age_groups: ['30'],
    })
  })

  test('renders heading and select button initially', () => {
    expect(wrapper.find('h3').length).toEqual(1)
    expect(wrapper.find('.button--tiny-toggle').length).toEqual(1)
    expect(wrapper.find('form').length).toEqual(0)
    expect(wrapper.find('.table').length).toEqual(0)
  })

  test('renders form', () => {
    wrapper.find('.button--tiny-toggle').simulate('click', { type: 'click' })
    expect(wrapper.find('form').length).toEqual(1)
    expect(wrapper.find('.table').length).toEqual(0)
  })

  test('renders table', async () => {
    Services.getCountryAgeGroupData.mockImplementation(() =>
      Promise.resolve(mockResponse)
    )

    wrapper.find('.button--tiny-toggle').simulate('click', { type: 'click' })
    wrapper
      .find('form input')
      .first()
      .simulate('change', {
        type: 'change',
        target: { value: mockGroups[0]['key'] },
      })

    await act(async () => {
      wrapper.find('form').simulate('submit', { preventDefault: () => {} })
    })

    wrapper.update()

    expect(wrapper.find('form').length).toEqual(0)
    expect(wrapper.find('.table').length).toEqual(1)
  })
})
