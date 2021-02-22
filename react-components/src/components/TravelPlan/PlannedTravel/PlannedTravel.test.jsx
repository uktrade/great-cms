import React from 'react'
import { render, fireEvent, waitFor, cleanup } from '@testing-library/react'

import Services from '@src/Services'

import { PlannedTravel } from './PlannedTravel'

const model_name = 'businessplan'
const props = {
  formData: [
    {
      note: 'note',
      companyexportplan: 1,
      pk: 50,
    },
    {
      note: 'note 2',
      companyexportplan: 1,
      pk: 51,
    },
  ],
  companyexportplan: 1,
  model_name,
  lesson: {
    url: '/',
    title: 'Safety when operating abroad',
    category: 'TBD',
    duration: '3 minutes',
  },
  tooltip: {
    content: `
      <p>Visit great.gov.uk market guides to find more information about your target market and its business culture.</p>
    `,
  },
}

const setup = ({ ...data }) => {
  const component = render(
    <PlannedTravel {...data}>
      <p>The child component</p>
    </PlannedTravel>
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

describe('PlannedTravel', () => {
  it('Should render 2 trips', () => {
    const { getByText } = setup({ ...props })
    expect(getByText('Trip 1'))
    expect(getByText('Trip 2'))
  })

  it('Should add a Trip', async () => {
    Services.apiModelObjectManage = jest.fn(() =>
      Promise.resolve(
        {
          companyexportplan: 1,
          model_name,
          pk: 52,
          note: '',
        },
        'POST'
      )
    )

    const { getByText, queryByText } = setup({
      ...props,
    })
    fireEvent.click(getByText('Add a trip'))

    expect(queryByText('Trip 3')).not.toBeInTheDocument()
    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenCalledWith(
        {
          companyexportplan: 1,
          model_name,
          note: '',
        },
        'POST'
      )
      expect(getByText('Trip 1'))
      expect(getByText('Trip 2'))
      expect(getByText('Trip 3'))
    })
  })

  it('Should delete a trip', async () => {
    Services.apiModelObjectManage = jest.fn(() => Promise.resolve())
    const { container, getByText, queryByText } = setup({ ...props })
    const button = container.querySelectorAll('.button--delete')[0]
    fireEvent.click(button)
    expect(getByText('Trip 2'))
    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenCalledWith(
        {
          model_name,
          pk: 50,
        },
        'DELETE'
      )
      expect(queryByText('Trip 2')).not.toBeInTheDocument()
    })
  })

  it('Should update a trip', async () => {
    Services.apiModelObjectManage = jest.fn(() => Promise.resolve())
    const { container } = setup({ ...props })
    const textarea = container.querySelectorAll('textarea')[0]
    fireEvent.change(textarea, {
      target: { value: 'new trip' },
    })

    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenCalledWith(
        {
          companyexportplan: 1,
          model_name,
          pk: 50,
          note: 'new trip',
        },
        'PATCH'
      )
      expect(textarea.value).toEqual('new trip')
    })
  })
})
