import React from 'react'
import { render, waitFor, fireEvent } from '@testing-library/react'

import { Select } from '.'

const props = {
  label: 'label example',
  name: 'input example',
  selected: 'item one',
  options: [{value: 'item_one', label: 'item one'}, {value: 'item_two', label: 'item two'}]

}

const setup = ({...data}) => {
  const actions = {
    update: jest.fn()
  }

  const utils = render(<Select
    {...data}
    {...actions}
  />)

  return {
    ...utils,
    actions
  }
}

describe('Select', () => {
  it('Should have a label', () => {
    const { queryByLabelText } = setup(props)
    expect(queryByLabelText(props.label)).toBeInTheDocument()
  })

  describe('Input', () => {

    it('Should have selected value', () => {
      const { getByLabelText } = setup(props)
      const input = getByLabelText(props.label)

      expect(input.value).toEqual(props.selected)
      expect(input.id).toEqual(props.label)
      expect(input.name).toEqual(props.label)
    })

    it('should have no value', () => {
      const { getByLabelText } = setup({...props, selected: ''})
      const input = getByLabelText(props.label)

      expect(input.value).toEqual('')
    })
  })

  describe('Dropdown', () => {

    it('Should not show dropdown', () => {
      const { queryByRole } = setup({...props})
      expect(queryByRole('listbox')).not.toBeInTheDocument()
    })

    it('Should show dropdown and 2 items', async () => {
      const { queryByRole, getByText, getByRole } = setup({...props})

      fireEvent.click(getByRole('button'))

      await waitFor(() => {
        expect(queryByRole('listbox')).toBeInTheDocument()
        expect(getByText(props.options[0].label)).toBeInTheDocument()
        expect(getByText(props.options[1].label)).toBeInTheDocument()
      })
    })
  })

  describe('Update',() => {

    it('Should fire',async () => {
      const { actions, getByText, getByRole } = setup({...props})

      fireEvent.click(getByRole('button'))
      await waitFor(() => {
        fireEvent.click(getByText(props.options[0].label))
        expect(actions.update).toHaveBeenCalledTimes(1)
        expect(actions.update).toHaveBeenCalledWith({ 'input example': 'item_one' })
      })
    })
  })

})
