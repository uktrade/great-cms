import React from 'react'
import { render, fireEvent, waitFor, cleanup } from '@testing-library/react'

import Services from '@src/Services'
import * as redux from 'react-redux'
import ReactModal from 'react-modal'
import { RouteToMarket } from '.'

jest
  .spyOn(redux, 'useSelector')
  .mockReturnValue({ country: { country_name: 'UK' } })

const props = {
  formFields: {
    route: '',
    promote: '',
    market_promotional_channel: '',
    companyexportplan: 3,
  },
  fields: [
    {
      route: 'INTERNATIONAL_E_COMMERCE',
      promote: 'ONLINE_MARKETING',
      market_promotional_channel: 'ffffddd',
      companyexportplan: 3,
      pk: 47,
    },
    {
      route: 'MARKETING_AT_EVENTS',
      promote: 'INTERNATIONAL_E_COMMERCE',
      market_promotional_channel: 'ddddddddd',
      companyexportplan: 3,
      pk: 45,
    },
  ],
  formData: {
    data: [
      {
        label: 'Route to market',
        options: [
          {
            value: 'DIRECT_SALES',
            label: 'Direct sales',
          },
          {
            value: 'INTERNATIONAL_E_COMMERCE',
            label: 'International e-commerce',
          },
          {
            value: 'AGENT_OR_DISTRIBUTOR',
            label: 'Agent or distributor',
          },
          {
            value: 'LICENSING',
            label: 'Licensing',
          },
          {
            value: 'FRANCHISING',
            label: 'Franchising',
          },
          {
            value: 'JOINT_VENTURES',
            label: 'Joint ventures',
          },
          {
            value: 'SET_UP_A_BUSINESS_ABROAD',
            label: 'Set up a business abroad',
          },
          {
            value: 'OTHER',
            label: 'Other',
          },
        ],
        name: 'route',
        tooltip: 'Route to market tooltip',
      },
      {
        label: 'How will we promote your product?',
        options: [
          {
            value: 'MARKETING_AT_EVENTS',
            label: 'Marketing at events',
          },
          {
            value: 'ONLINE_MARKETING',
            label: 'Online marketing',
          },
          {
            value: 'OTHER',
            label: 'Other',
          },
        ],
        name: 'promote',
        tooltip: 'How will we promote your product tooltip',
      },
    ],
    example: "<p>We've found that</p>",
    label: 'Explain in your words',
    name: 'market_promotional_channel',
    tooltip: 'Example tooltip',
  },
}

const setup = ({
  formFields,
  fields,
  formData,
  model_name = 'routeToMarket',
}) => {
  const component = render(
    <RouteToMarket
      fields={fields}
      formData={formData}
      formFields={formFields}
      model_name={model_name}
    />
  )
  ReactModal.setAppElement(component.baseElement)

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

describe('RouteToMarket', () => {
  it('Should render 2 routes to market', () => {
    const { getByText } = setup({ ...props })
    expect(getByText('Route to market 1'))
    expect(getByText('Route to market 2'))
  })

  it('Should add a route to market', async () => {
    Services.apiModelObjectManage = jest.fn(() =>
      Promise.resolve({
        companyexportplan: 3,
        market_promotional_channel: '',
        pk: 48,
        promote: '',
        route: '',
      })
    )

    const { getByText, queryByText } = setup({
      ...props,
    })
    fireEvent.click(getByText('Add route to market'))

    expect(queryByText('Route to market 3')).not.toBeInTheDocument()
    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenCalledWith(
        props.formFields,
        'POST'
      )
      expect(getByText('Route to market 1'))
      expect(getByText('Route to market 2'))
      expect(getByText('Route to market 3'))
    })
  })

  it('Should delete a route to market', async () => {
    Services.apiModelObjectManage = jest.fn(() => Promise.resolve())
    const { container, getByText, queryByText } = setup({
      ...props,
      fields: [
        {
          route: '',
          promote: '',
          market_promotional_channel: '',
          companyexportplan: 3,
          pk: 45,
        },
        {
          route: 'MARKETING_AT_EVENTS',
          promote: 'INTERNATIONAL_E_COMMERCE',
          market_promotional_channel: 'ddddddddd',
          companyexportplan: 3,
          pk: 47,
        },
      ],
    })
    const button = container.querySelectorAll('.delete-button')[0]
    fireEvent.click(button)
    expect(getByText('Route to market 2'))
    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenCalledWith(
        {
          pk: 45,
          model_name: 'routeToMarket',
        },
        'DELETE'
      )
      expect(queryByText('Route to market 2')).not.toBeInTheDocument()
    })
  })

  it('Should update a route to market', async () => {
    Services.apiModelObjectManage = jest.fn(() => Promise.resolve())
    const { container } = setup({ ...props })
    const textarea = container.querySelectorAll('textarea')[0]
    fireEvent.change(textarea, {
      target: { value: 'new route' },
    })

    await waitFor(() => {
      expect(Services.apiModelObjectManage).toHaveBeenCalledTimes(1)
      expect(Services.apiModelObjectManage).toHaveBeenCalledWith({
          route: 'MARKETING_AT_EVENTS',
          promote: 'INTERNATIONAL_E_COMMERCE',
          market_promotional_channel: 'new route',
          companyexportplan: 3,
          pk: 45,
          model_name: 'routeToMarket',
        },
        'PATCH'
      )
      expect(textarea.value).toEqual('new route')
    })
  })
})
