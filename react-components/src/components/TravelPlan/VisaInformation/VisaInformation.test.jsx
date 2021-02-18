import React from 'react'
import { render, fireEvent, waitFor, cleanup } from '@testing-library/react'

import Services from '@src/Services'
import { VisaInformation } from './VisaInformation'

const props = {
  formData: {
    how_long: '90 days',
    how_where_visa: 'Embassy',
    notes: 'Notes',
    visa_required: true,
  },
  formFields: [
    {
      field_type: 'Textarea',
      label: 'How and where will you get your visa',
      id: 'how_where_visa',
      name: 'how_where_visa',
      placeholder: 'Add some text',
    },
    {
      field_type: 'Text',
      label: 'How long will it last',
      id: 'how_long',
      name: 'how_long',
      placeholder: '',
    },
    {
      field_type: 'Textarea',
      label: 'Add notes',
      id: 'notes',
      name: 'notes',
      placeholder: 'Add some text',
    },
  ],
  companyexportplan: 1,
  field: 'travel_business_policies',
  name: 'visa_information',
  travel_advice_link: '/',
}

const setup = ({ ...data }) => {
  const component = render(
    <VisaInformation {...data}>
      <p>The child component</p>
    </VisaInformation>
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

describe('VisaInformation', () => {
  it('Should render 3 textareas', () => {
    const { getByText } = setup({ ...props })
    expect(getByText('How and where will you get your visa'))
    expect(getByText('How long will it last'))
    expect(getByText('Add notes'))
  })

  it('Should render no textareas', async () => {
    Services.updateExportPlan = jest.fn(() =>
      Promise.resolve({
        travel_business_policies: {
          visa_information: {
            visa_required: false,
          },
        },
      })
    )

    const { getByText, queryByText } = setup({
      ...props,
    })
    fireEvent.click(getByText("I don't need a visa"))

    expect(queryByText('How long will it last')).not.toBeInTheDocument()
    await waitFor(() => {
      expect(Services.updateExportPlan).toHaveBeenCalledTimes(1)
      expect(Services.updateExportPlan).toHaveBeenCalledWith({
        travel_business_policies: {
          visa_information: {
            visa_required: false,
          },
        },
      })
    })
  })
})
