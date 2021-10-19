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

    getByText('May').click()

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ month: '5' })
    )

    getByText('2022').click()

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ year: '2022' })
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

    getByText('April').click()

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ start_month: '4' })
    )

    getByText('2023').click()

    await waitFor(() =>
      expect(mockOnChange).toHaveBeenCalledWith({ start_year: '2023' })
    )
  })
})
