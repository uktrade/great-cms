import React from 'react'
import { render, fireEvent, waitFor } from '@testing-library/react'

import Services from '@src/Services'
import { unexpectedError } from '@src/components/hooks/useUpdateExportPlan/useUpdateExportPlan'
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
      tooltip: { content: 'best to stick to the facts' },
      example: { content: 'Dove Gin was founded in 2012' },
      description: '',
      currency: '',
      choices: '',
    },
    {
      choices: '',
      currency: 'GBP',
      description: '',
      field_type: 'NumberInput',
      label: 'average',
      name: 'average_price',
      placeholder: '0.00',
    },
    {
      name: 'performance',
      label: 'Your business performance',
      field_type: 'Select',
      placeholder: '',
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

const setup = ({ formFields, field, formData }) =>
  render(
    <FormElements formFields={formFields} field={field} formData={formData} />
  )

describe('FormElements', () => {
  describe('Should render form elements', () => {
    it('Should have a Textarea', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('textarea')).toBeTruthy()
    })

    it('Should have an Input', () => {
      const { getByLabelText, container } = setup({ ...props })
      expect(getByLabelText('average')).toBeTruthy()
      expect(container.querySelectorAll('input')[0]).toBeTruthy()
      expect(container.querySelectorAll('input')[0].id).toEqual('average_price')
    })

    it('Should have a Select', () => {
      const { getByRole, getByLabelText, container } = setup({ ...props })
      expect(getByRole('listbox')).toBeTruthy()
      expect(getByLabelText('Your business performance')).toBeTruthy()
      expect(container.querySelectorAll('li')[0].textContent).toEqual(
        'Below £83,000 (Below VAT registered)'
      )
    })
  })

  it('should update formData', async () => {
    Services.updateExportPlan = jest.fn(() => Promise.resolve())

    const { container, queryByText, getByText } = setup({ ...props })
    fireEvent.change(container.querySelector('textarea'), {
      target: { value: 'Good Day' },
    })
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
      expect(getByText('Changes saved.')).toBeTruthy()
      expect(queryByText('Saving...')).not.toBeInTheDocument()
    })
  })

  it('Should fail to update formdata', async () => {
    Services.updateExportPlan = jest.fn(() =>
      Promise.reject({
        message: { __all__: ['An unexpected error has occurred'] },
      })
    )
    const { container, getByText } = setup({ ...props })

    fireEvent.change(container.querySelector('textarea'), {
      target: { value: 'Good Day' },
    })
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
      expect(getByText(unexpectedError)).toBeTruthy()
    })
  })

  it('should be in saving state', async () => {
    Services.updateExportPlan = jest.fn(() => Promise.resolve())

    const { container, getByText } = setup({ ...props })
    fireEvent.change(container.querySelector('textarea'), {
      target: { value: 'Good Day' },
    })

    await waitFor(() => {
      expect(getByText('Saving...')).toBeTruthy()
    })
  })
})
