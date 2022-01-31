import React from 'react'
import { render, waitFor } from '@testing-library/react'
import { ToggleDataTable } from '@src/components/ToggleDataTable'
import Services from '@src/Services'

jest.mock('@src/Services')

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

  it('renders heading and select button initially', async () => {
    const { container } = render(<ToggleDataTable countryIso2Code="NL" url="/" />)

    await waitFor(() => {
      expect(container.querySelectorAll('h3')).toHaveLength(1)
      expect(container.querySelectorAll('.button--tiny-toggle')).toHaveLength(1)
      expect(container.querySelectorAll('.table')).toHaveLength(0)
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

    expect(queryByText('Target age groups')).toBeNull()

    await waitFor(() => {
      expect(getByText('Target age groups')).toBeTruthy()
      expect(getByText('Choose target age groups')).toBeTruthy()
    })
  })

  it('opens and closes the age range selector', async () => {
    const { getByText } = render(
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
      expect(getByText('Close target age groups')).toBeTruthy()
    })

    getByText('Close target age groups').click()

    await waitFor(() => {
      expect(getByText('Choose target age groups')).toBeTruthy()
    })
  })

  it('updates data when changing selected age ranges', async () => {
    const { container } = render(
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
    container.querySelector('.button--tiny-toggle').click()
    // Select first age group
    // TODO: Fix invalid id attribute
    container.querySelector('[id="0-14"]').click()

    await waitFor(() => {
      expect(getData().target).toEqual(11691000)
    })
  })
})
