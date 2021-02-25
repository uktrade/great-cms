import React from 'react'
import { render, fireEvent, waitFor, cleanup } from '@testing-library/react'

import Services from '@src/Services'
import { GettingPaid } from './GettingPaid'

const props = {
  formFields: [
    {
      field: 'payment_method',
      group: [
        {
          name: 'methods',
          id: 'methods',
          label: 'Payments methods',
          field_type: 'Select',
          options: [
            {
              value: 'INTERNATIONAL_BANK_TRANSFER',
              label: 'International bank transfers',
            },
            {
              value: 'CREDIT_DEBIT',
              label: 'Credit or debit card payments',
            },
          ],
          multiSelect: true,
        },
        {
          name: 'Add notes',
          label: 'Add notes',
          field_type: 'Textarea',
          placeholder: 'Add note',
          id: 'method_notes',
        },
      ],
    },
    {
      field: 'payment_terms',
      group: [
        {
          name: 'terms',
          id: 'terms',
          label: 'Payments terms',
          field_type: 'Select',
          options: [
            {
              value: 'PAYMENT_IN_ADVANCE',
              label: 'Payment in advance',
            },
            {
              value: 'LETTER_OF_CREDIT',
              label: 'Letter of credit',
            },
          ],
        },
        {
          name: 'Add notes',
          label: 'Add notes',
          field_type: 'Textarea',
          placeholder: 'Add note',
          id: 'payments_notes',
        },
      ],
    },
    {
      field: 'incoterms',
      group: [
        {
          name: 'transport',
          id: 'transport',
          label: 'Incoterms®',
          field_type: 'Select',
          options: {
            'All forms of transport': [
              {
                value: 'EX_WORKS',
                label: 'Ex Works (EXW)',
              },
              {
                value: 'FREE_CARRIER',
                label: 'Free Carrier (FCA)',
              },
            ],
            'Water transport': [
              {
                value: 'FREE_ALONG_SHIP',
                label: 'Free Alongside Ship (FAS)',
              },
              {
                value: 'FREE_ON_BOARD',
                label: 'Free on Board (FOB)',
              },
            ],
          },
        },
        {
          name: 'Add notes',
          label: 'Add notes',
          field_type: 'Textarea',
          placeholder: 'Add note',
          id: 'incoterms_notes',
        },
      ],
    },
  ],
  field: 'getting_paid',
  formData: {
    incoterms: {
      notes: 'eeee',
      transport: 'FREE_CARRIER',
    },
    payment_method: {
      methods: ['INTERNATIONAL_BANK_TRANSFER', 'CREDIT_DEBIT'],
      notes: 'de',
    },
    payment_terms: {
      notes: 'ggg',
      terms: 'PAYMENT_IN_ADVANCE',
    },
  },
}

const setup = ({ formFields, field, formData }) => {
  const component = render(
    <GettingPaid field={field} formData={formData} formFields={formFields} />
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

describe('GettingPaid', () => {
  describe('Should have initial values', () => {
    it('Payments methods', () => {
      const { getAllByText, getByText } = setup({ ...props })
      expect(getAllByText('International bank transfers')).toHaveLength(2)
      expect(getAllByText('Credit or debit card payments')).toHaveLength(2)
      getByText('de')
    })
    it('Payments terms', () => {
      const { getAllByText, getByText } = setup({ ...props })
      expect(getAllByText('Payment in advance')).toHaveLength(2)
      getByText('ggg')
    })
    it('Incoterms®', () => {
      const { getAllByText, getByText } = setup({ ...props })
      expect(getAllByText('Free Carrier (FCA)')).toHaveLength(2)
      getByText('eeee')
    })
  })

  describe('Should update export plan', () => {
    it('textarea', async () => {
      Services.updateExportPlan = jest.fn(() => Promise.resolve())
      const { container } = setup({ ...props })
      fireEvent.change(container.querySelector('textarea'), {
        target: { value: 'Good Day' },
      })
      await waitFor(() => {
        expect(Services.updateExportPlan).toHaveBeenCalledTimes(1)
        expect(Services.updateExportPlan).toHaveBeenLastCalledWith({
          getting_paid: {
            payment_method: {
              methods: ['INTERNATIONAL_BANK_TRANSFER', 'CREDIT_DEBIT'],
              notes: 'Good Day',
            },
          },
        })
        expect(container.querySelector('textarea').value).toEqual('Good Day')
      })
    })

    it('dropdown', async () => {
      Services.updateExportPlan = jest.fn(() => Promise.resolve())
      const { getByText, getAllByText } = setup({ ...props })
      expect(getAllByText('Letter of credit')).toHaveLength(1)
      getByText('Letter of credit')
      fireEvent.click(getByText('Letter of credit'))
      await waitFor(() => {
        expect(Services.updateExportPlan).toHaveBeenCalledTimes(1)
        expect(Services.updateExportPlan).toHaveBeenLastCalledWith({
          getting_paid: {
            payment_terms: {
              terms: 'LETTER_OF_CREDIT',
              notes: 'ggg',
            },
          },
        })
        expect(getAllByText('Letter of credit')).toHaveLength(2)
      })
    })
  })
})
