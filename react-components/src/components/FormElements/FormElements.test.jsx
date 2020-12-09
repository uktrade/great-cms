import React from 'react'
import { render, fireEvent, waitFor, cleanup } from '@testing-library/react'

import Services from '@src/Services'
import { FormElements } from '.'

const props = {
  field: 'target_markets_research',
  formData: {
    story: '',
    average_price: '',
    performance: '',
  },
  formFields: [
    {
      name: 'story',
      label: 'How you started',
      field_type: 'Textarea',
      placeholder: '',
      tooltip: 'best to stick to the facts',
      example: 'Dove Gin was founded in 2012',
      description: '',
      currency: '',
      choices: '',
    },
    {
      choices: '',
      currency: 'GBP',
      description: '',
      example: '',
      field_type: 'NumberInput',
      label: 'average',
      name: 'average_price',
      placeholder: '0.00',
      tooltip: '',
    },
    {
      name: 'performance',
      label: 'Your business performance',
      field_type: 'Select',
      placeholder: '',
      tooltip: '',
      example: '',
      description: 'What is the annual turnover of your business?',
      currency: '',
      choices: [
        {
          value: '<83k',
          label: 'Below £83,000 (Below VAT registered)',
        },
        {
          value: '83k-499.999k',
          label: '£83,000 up to £499,999',
        },
        {
          value: '50k-1999.999k',
          label: '£500,000 up to £1,999,999',
        },
      ],
    },
  ],
}

const setup = ({ formFields, field, formData }) => {
  const component = render(
    <FormElements formFields={formFields} field={field} formData={formData} />
  )

  return {
    ...component,
  }
}

beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
  cleanup()
})

describe('FormElements', () => {
  describe('Should render form elements', () => {
    it('Should have a Textarea', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('textarea'))
    })

    it('Should have an Input', () => {
      const { getByLabelText, container } = setup({ ...props })
      expect(getByLabelText('average'))
      expect(container.querySelectorAll('input')[0])
      expect(container.querySelectorAll('input')[0].id).toEqual('average_price')
    })

    it('Should have a Select', () => {
      const { getByRole, getByLabelText, container } = setup({ ...props })
      expect(getByRole('listbox'))
      expect(getByLabelText('Your business performance'))
      expect(container.querySelectorAll('input')[1])
      expect(container.querySelectorAll('input')[1].id).toEqual(
        'Your business performance'
      )
    })
  })

  it('should update formData', async () => {
    Services.updateExportPlan = jest.fn(() => Promise.resolve())

    const { container, queryByText, getByText } = setup({ ...props })
    fireEvent.change(container.querySelector('textarea'), {
      target: { value: 'Good Day' },
    })
    expect(getByText('Saving...'))
    await waitFor(() => {
      expect(Services.updateExportPlan).toHaveBeenCalledTimes(1)
      expect(Services.updateExportPlan).toHaveBeenLastCalledWith({
        target_markets_research: {
          average_price: '',
          performance: '',
          story: 'Good Day',
        },
      })
      expect(container.querySelector('textarea').value).toEqual('Good Day')
      expect(getByText('Changes saved.'))
      expect(queryByText('Saving...')).not.toBeInTheDocument()
    })
  })

  it('Should fail to update formdata', async () => {
    Services.updateExportPlan = jest.fn(() =>
      Promise.reject({ message: { __all__: ['an error has occurred'] } })
    )
    const { container, getByText } = setup({ ...props })

    fireEvent.change(container.querySelector('textarea'), {
      target: { value: 'Good Day' },
    })
    expect(getByText('Saving...'))
    await waitFor(() => {
      expect(Services.updateExportPlan).toHaveBeenCalledTimes(1)
      expect(Services.updateExportPlan).toHaveBeenLastCalledWith({
        target_markets_research: {
          average_price: '',
          performance: '',
          story: 'Good Day',
        },
      })
      expect(container.querySelector('textarea').value).toEqual('Good Day')
      expect(getByText('an error has occurred'))
    })
  })
})
