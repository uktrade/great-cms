/* eslint-disable */
import React from 'react'
import { mount } from 'enzyme'
import { ToggleDataTable } from '@src/components/ToggleDataTable'
import Services from '@src/Services'
import { act } from 'react-dom/test-utils'

jest.mock('@src/Services')

let wrapper

const mockGroups = [
  { value: '0-14', label: '0-14 year olds' },
  { value: '15-19', label: '15-19 year olds' },
]

const mockResponse = {
  NL: {
    PopulationData: [
      {
        year: 2020,
        gender: 'male',
        '0-4': 2082,
        '5-9': 1970,
        '10-14': 1979,
        '15-19': 2150,
      },
      {
        year: 2020,
        gender: 'female',
        '0-4': 1976,
        '5-9': 1852,
        '10-14': 1832,
        '15-19': 1969,
      },
    ],
    PopulationUrbanRural: [
      { urban_rural: 'urban', value: 64044, year: 2021 },
      { urban_rural: 'rural', value: 18546, year: 2021 },
    ],
    ConsumerPriceIndex: [{ value: '113.427', year: 2020 }],
    InternetUsage: [{ value: '89.739', year: 2018 }],
    CIAFactbook: [
      {
        languages: {
          note: 'Danish, Frisian, Sorbian, and Romani are official minority languages; Low German, Danish, North Frisian, Sater Frisian, Lower Sorbian, Upper Sorbian, and Romani are recognized as regional languages under the European Charter for Regional or Minority Languages',
          language: [{ name: 'German', note: 'official' }],
        },
        country_key: 'germany',
        country_name: 'Germany',
      },
    ],
  },
}

describe('ToggleDataTable', () => {
  beforeEach(() => {
    Services.getCountryData.mockImplementation(() =>
      Promise.resolve(mockResponse)
    )
    wrapper = mount(
      <ToggleDataTable
        groups={mockGroups}
        countryIso2Code="NL"
        selectedGroups={['5-9']}
        url="/export-plan"
        afterTable={[<div className="table">test</div>]}
      ></ToggleDataTable>
    )
  })

  afterEach(() => {
    wrapper = null
    Services.setConfig({})
    jest.clearAllMocks()
  })

  it('Should fetch country data', () => {
    expect(Services.getCountryData).toHaveBeenCalledWith(
      [{ country_iso2_code: 'NL' }],
      JSON.stringify([
        { model: 'PopulationData', filter: { year: 2020 } },
        { model: 'PopulationUrbanRural', filter: { year: 2021 } },
        { model: 'ConsumerPriceIndex', latest_only: true },
        { model: 'InternetUsage', latest_only: true },
        { model: 'CIAFactbook', latest_only: true },
      ])
    )
  })

  it('renders heading and select button initially', () => {
    expect(wrapper.find('h3').length).toEqual(1)
    expect(wrapper.find('.button--tiny-toggle').length).toEqual(1)
    expect(wrapper.find('.table').length).toEqual(0)
  })

  it('renders table', () => {
    wrapper.find('.button--tiny-toggle').simulate('click', { type: 'click' })
    expect(wrapper.find('.table').length).toEqual(1)
  })

  it('renders table', async () => {
    Services.getCountryAgeGroupData.mockImplementation(() =>
      Promise.resolve(mockResponse)
    )
    await act(async () => {
      wrapper.find('.button--tiny-toggle').simulate('click', { type: 'click' })
    })
    wrapper.update()
    await act(async () => {
      wrapper
        .find('input')
        .first()
        .simulate('change', {
          type: 'change',
          target: { value: mockGroups[0]['value'] },
        })
    })

    wrapper.update()
    expect(wrapper.find('.table').length).toEqual(1)
  })
})
