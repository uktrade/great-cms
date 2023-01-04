import React from 'react'
import { act, render, waitFor } from '@testing-library/react'
import { MonthYearInput } from '.'

const mockOnChange = jest.fn()

const currentYear = new Date().getFullYear()
const nextYear = currentYear + 1

describe('MonthYearInput', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('triggers onChange when month or year are changed', async () => {
    const { getByText } = render(
      <MonthYearInput label="Foo" onChange={mockOnChange} />
    )

    getByText('May').click()

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ month: '5' })
    )

    act(() => {
      getByText(currentYear.toString()).click()
    })

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ year: currentYear.toString() })
    )
  })

  it('calls onChange with provided field names', async () => {
    const { getByText } = render(
      <MonthYearInput
        label="Foo"
        onChange={mockOnChange}
        monthName="end_month"
        yearName="end_year"
      />
    )

    getByText('April').click()

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ end_month: '4' })
    )

    act(() => {
      getByText(nextYear.toString()).click()
    })

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ end_year: nextYear.toString() })
    )
  })

  it('can call onChange with the combined fields', async () => {
    const { getAllByText, getByText } = render(
      <MonthYearInput
        label="Foo"
        onChange={mockOnChange}
        monthName="start_month"
        yearName="start_year"
        onChangeCombineFields
      />
    )

    await waitFor(() => getAllByText('Select one'))

    getAllByText('Select one')[0].click()

    await waitFor(() => getByText('April').click())

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith(
        { start_month: '4' },
        { month: '4', year: null }
      )
    )
  })
})
