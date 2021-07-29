import React from 'react'
import { render, waitFor, fireEvent } from '@testing-library/react'
import { MonthYearInput } from '.'

const mockOnChange = jest.fn()

describe('MonthYearInput', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('triggers onChange when month or year are changed', async () => {
    const { getByText, getByLabelText } = render(
      <MonthYearInput label='Foo' onChange={mockOnChange} />,
    )

    getByText('Select one').click()
    getByText('May').click()

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ month: '5' })
    )

    fireEvent.change(getByLabelText('Year'), { target: { value: '2026' } })

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ year: '2026' })
    )
  })

  it('calls onChange with provided field names', async () => {
    const { getByText, getByLabelText } = render(
      <MonthYearInput
        label='Foo'
        onChange={mockOnChange}
        monthName='start_month'
        yearName='start_year'
      />,
    )

    getByText('Select one').click()
    getByText('April').click()

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ start_month: '4' })
    )

    fireEvent.change(getByLabelText('Year'), { target: { value: '2023' } })

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ start_year: '2023' })
    )
  })
})
