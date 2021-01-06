import React from 'react'
import { fireEvent, render } from '@testing-library/react'

import { RouteToMarketSection } from '.'

const props = {
  data: [
    {
      label: 'Route to market 1',
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
  label: 'Explain',
  example: '<p>example</p>',
  name: 'market_promotional_channel',
  field: {
    route: 'JOINT_VENTURES',
    promote: '',
    market_promotional_channel: '',
    companyexportplan: 3,
    pk: 48,
  },
  tooltip: 'tooltip',
}

const setup = ({ data, label, example, name, field, tooltip }) => {
  const actions = {
    onChange: jest.fn(),
    deleteTable: jest.fn(),
  }

  const component = render(
    <RouteToMarketSection
      label={label}
      data={data}
      tooltip={tooltip}
      name={name}
      example={example}
      field={field}
      {...actions}
    />
  )

  return {
    ...component,
    actions,
  }
}

describe('RouteToMarketSection', () => {
  it('Should render, 2 dropdowns and a textarea', () => {
    const { container, getAllByRole } = setup({ ...props })
    expect(getAllByRole('listbox').length).toEqual(2)
    expect(container.querySelectorAll('textarea').length).toEqual(1)
  })

  it('Should fire deleteTable', () => {
    const { actions, container } = setup({ ...props })
    fireEvent.click(container.querySelector('.button--delete'))
    expect(actions.deleteTable).toHaveBeenCalledTimes(1)
    expect(actions.deleteTable).toHaveBeenCalledWith(props.field.pk)
  })

  describe('Should fire onChange', () => {
    it('textarea', () => {
      const { container, actions } = setup({ ...props })
      fireEvent.change(container.querySelectorAll('textarea')[0], {
        target: { value: 'update textarea' },
      })
      expect(actions.onChange).toHaveBeenCalledTimes(1)
      expect(actions.onChange).toHaveBeenCalledWith(48, {
        market_promotional_channel: 'update textarea',
      })
    })

    it('dropdown', () => {
      const { container, actions } = setup({ ...props })
      const dropdownItem = container.querySelectorAll('.select__list--item')[0]
      fireEvent.click(dropdownItem)
      expect(actions.onChange).toHaveBeenCalledTimes(1)
      expect(actions.onChange).toHaveBeenCalledWith(48, {
        route: 'DIRECT_SALES',
      })
    })
  })

  describe('Select', () => {
    it('Should have selected values', () => {
      const { getAllByPlaceholderText } = setup({ ...props })
      const input = getAllByPlaceholderText('Select one')
      expect(input[0].value).toEqual('Joint ventures')
      expect(input[1].value).toEqual('')
    })

    describe('Should have no selected values', () => {
      it('field empty', () => {
        const { getAllByPlaceholderText } = setup({ ...props, field: {} })
        const input = getAllByPlaceholderText('Select one')
        expect(input[0].value).toEqual('')
        expect(input[1].value).toEqual('')
      })

      it('field has inconsistent data', () => {
        const { getAllByPlaceholderText } = setup({
          ...props,
          field: {
            route: 'JOINT',
            promote: 'TEST',
            market_promotional_channel: '',
            companyexportplan: 3,
            pk: 48,
          },
        })
        const input = getAllByPlaceholderText('Select one')
        expect(input[0].value).toEqual('')
        expect(input[1].value).toEqual('')
      })
    })
  })
})
