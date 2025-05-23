import React from 'react'
import { render, waitFor } from '@testing-library/react'
import { ToggleDataTable } from '@src/components/ToggleDataTable'
import Services from '@src/Services'

jest.mock('@src/Services')

const mockGroups = [
  { value: '0-14', label: '0-14 years old' },
  { value: '15-19', label: '15-19 years old' },
  { value: '20-24', label: '20-24 years old' },
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
          note: 'A few languages',
          language: [{ name: 'German', note: 'official' }],
        },
        country_key: 'germany',
        country_name: 'Germany',
      },
    ],
  },
}

// eslint-disable-next-line react/prop-types
const DataComponent = ({ className, ...data }) => <div className={className}>{JSON.stringify(data, null, 2)}</div>

describe('ToggleDataTable', () => {
  beforeEach(() => {
    Services.getCountryData.mockResolvedValue(mockResponse)
  })

  afterEach(() => {
    jest.clearAllMocks()
  })

  it('Should fetch country data', async () => {
    render(<ToggleDataTable countryIso2Code="NL" url="/export-plan" />)

    await waitFor(() => {
      expect(Services.getCountryData).toHaveBeenCalledWith(
        [{ country_iso2_code: 'NL' }],
        JSON.stringify([
          { model: 'PopulationData', filter: { year: 2020 } },
          { model: 'PopulationUrbanRural', filter: { year: 2021 } },
          { model: 'ConsumerPriceIndex', latest_only: true },
          { model: 'InternetUsage', latest_only: true },
          { model: 'CIAFactbook', latest_only: true },
        ]),
      )
    })
  })

  it('renders computed data and selected groups in data panel', async () => {
    const { container } = render(
      <ToggleDataTable
        countryIso2Code="NL"
        url="/"
        groups={mockGroups}
        selectedGroups={['0-14', '15-19']}
        afterTable={[<DataComponent className="after" />]}
      />,
    )

    await waitFor(() => container.querySelector('.after'))

    const data = JSON.parse(container.querySelector('.after').textContent)

    expect(data).toEqual({
        cpi: '113.427',
        internetData: '89.739',
        languages: {
          language: [
            {
              name: 'German',
              note: 'official',
            },
          ],
          note: 'A few languages',
        },
        rural: 18546,
        target: 15810000,
        targetfemale: 7629000,
        targetmale: 8181000,
        totalPopulation: 15810000,
        urban: 64044,
        selectedGroups: ['0-14', '15-19'],
      },
    )
  })

  it('renders a heading if one is provided', async () => {
    const { getByText } = render(
      <ToggleDataTable
        countryIso2Code="NL"
        url="/"
        heading="Custom heading"
      />,
    )

    await waitFor(() => {
      expect(getByText('Custom heading').tagName).toBe('H3')
    })
  })

  it('renders content before and after when data is available', async () => {
    const { container } = render(
      <ToggleDataTable
        countryIso2Code="NL"
        url="/"
        beforeTable={[<DataComponent className="before" />]}
        afterTable={[<DataComponent className="after" />]}
      />,
    )

    await waitFor(() => {
      expect(container.querySelector('.before')).toBeTruthy()
      expect(container.querySelector('.after')).toBeTruthy()
    })
  })

  it('renders the age range selector when data is available', async () => {
    const { queryByText, getByText } = render(
      <ToggleDataTable
        countryIso2Code="NL"
        url="/"
        groups={mockGroups}
        afterTable={[<DataComponent className="after" />]}
      />,
    )

    expect(queryByText('Selected target age groups')).toBeNull()

    await waitFor(() => {
      expect(getByText('Choose target age groups')).toBeTruthy()
    })
  })

  it('opens and closes the age range selector', async () => {
    const { getByText, container } = render(
      <ToggleDataTable
        countryIso2Code="NL"
        url="/"
        groups={mockGroups}
        afterTable={[<DataComponent className="after" />]}
      />,
    )

    await waitFor(() => getByText('Choose target age groups'))

    getByText('Choose target age groups').click()

    await waitFor(() => {
      expect(getByText('Close target age groups').closest('button').getAttribute('aria-expanded')).toBe('true')
      expect(container.querySelector('#target-age-groups')).toBeTruthy()
    })

    getByText('Close target age groups').click()

    await waitFor(() => {
      expect(getByText('Choose target age groups').closest('button').getAttribute('aria-expanded')).toBe('false')
      expect(container.querySelector('#target-age-groups')).toBeNull()
    })
  })

  it('updates list of selected age ranges', async () => {
    const { container, getByText } = render(
      <ToggleDataTable
        countryIso2Code="NL"
        url="/"
        groups={mockGroups}
        afterTable={[<DataComponent className="after" />]}
      />,
    )

    await waitFor(() => getByText('Choose target age groups'))

    expect(container.querySelector('.selected-groups')).toBeNull()

    getByText('Choose target age groups').click()

    await waitFor(() => {
      container.querySelector('[id="age-range-20-24"]').click()
    })

    await waitFor(() => {
      expect(getByText('Selected target age groups')).toBeTruthy()
      expect(container.querySelectorAll('.selected-groups__item')).toHaveLength(1)
      expect(container.querySelectorAll('.selected-groups__item')[0].textContent).toMatch('20-24 years old')
    })

    container.querySelector('[id="age-range-0-14"]').click()

    await waitFor(() => {
      expect(container.querySelectorAll('.selected-groups__item')).toHaveLength(2)
      expect(container.querySelectorAll('.selected-groups__item')[0].textContent).toMatch('0-14 years old')
    })
  })

  it('removes selected age range when clicking remove', async () => {
    const { container, getByText } = render(
      <ToggleDataTable
        countryIso2Code="NL"
        url="/"
        groups={mockGroups}
        afterTable={[<DataComponent className="after" />]}
      />,
    )

    await waitFor(() => getByText('Choose target age groups'))

    getByText('Choose target age groups').click()
    container.querySelector('[id="age-range-20-24"]').click()

    await waitFor(() => {
      expect(container.querySelector('[id="age-range-20-24"]').checked).toBeTruthy()
      expect(container.querySelector('.selected-groups__item').textContent).toMatch('20-24 years old')
    })

    container.querySelector('.selected-groups__item .button').click()

    await waitFor(() => {
      expect(container.querySelector('[id="age-range-20-24"]').checked).toBeFalsy()
      expect(container.querySelector('.selected-groups__item')).toBeNull()
    })
  })

  it('updates data when changing selected age ranges', async () => {
    const { getByText, container } = render(
      <ToggleDataTable
        countryIso2Code="NL"
        url="/"
        groups={mockGroups}
        afterTable={[<DataComponent className="after" />]}
      />,
    )

    const getData = () => JSON.parse(container.querySelector('.after').textContent)

    await waitFor(() => {
      expect(getData().target).toEqual(15810000)
    })

    // Open age group selector
    getByText('Choose target age groups').click()
    // Select first age group
    // TODO: Fix invalid id attribute
    container.querySelector('[id="age-range-0-14"]').click()

    await waitFor(() => {
      expect(getData().target).toEqual(11691000)
    })
  })
})
