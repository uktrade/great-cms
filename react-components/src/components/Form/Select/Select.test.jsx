/* eslint-disable */
import React from 'react'
import { render, waitFor, fireEvent } from '@testing-library/react'

import { Select } from '.'

const props = {
  label: 'label example',
  name: 'input example',
  selected: 'item one',
  options: [
    { value: 'item_one', label: 'item one' },
    { value: 'item_two', label: 'item two' },
  ],
}

const propsCategories = {
  'All forms of transport': [
    { value: 'item_one', label: 'item one' },
    { value: 'item_two', label: 'item two' },
  ],
  'Water transport': [
    { value: 'item_three', label: 'item three' },
    { value: 'item_four', label: 'item four' },
  ],
}

const setup = ({ ...data }) => {
  const actions = {
    update: jest.fn(),
  }

  const utils = render(<Select {...data} {...actions} />)

  return {
    ...utils,
    actions,
  }
}

describe('Select', () => {
  it('Should have a label', () => {
    const { queryByLabelText } = setup(props)
    expect(queryByLabelText(props.label)).toBeInTheDocument()
  })

  describe('Input', () => {
    it('Should have selected value', () => {
      const { getByText } = setup(props)
      expect(getByText(props.label)).toBeInTheDocument()
    })
  })

  describe('Dropdown', () => {
    it('Should show dropdown and 2 items', async () => {
      const { queryByRole, getByText, getByRole } = setup({
        ...props,
        selected: '',
      })

      fireEvent.click(getByRole('button'))

      await waitFor(() => {
        expect(queryByRole('listbox')).toBeInTheDocument()
        expect(getByText(props.options[0].label)).toBeInTheDocument()
        expect(getByText(props.options[1].label)).toBeInTheDocument()
      })
    })
  })

  describe('Dropdown - click on placeholder', () => {
    it('Should show dropdown on placeholder click', async () => {
      const { queryByRole, getByText, container, getByRole } = setup({
        ...props,
        selected: '',
      })

      fireEvent.click(container.querySelector('.select__placeholder--input'))

      await waitFor(() => {
        expect(queryByRole('listbox')).toBeInTheDocument()
        expect(getByText(props.options[0].label)).toBeInTheDocument()
        expect(getByText(props.options[1].label)).toBeInTheDocument()
      })
    })
  })

  describe('Update', () => {
    it('Should fire', async () => {
      const { actions, getByText, getByRole } = setup({
        ...props,
        selected: '',
      })

      fireEvent.click(getByRole('button'))
      await waitFor(() => {
        fireEvent.click(getByText(props.options[0].label))
        expect(actions.update).toHaveBeenCalledTimes(1)
        expect(actions.update).toHaveBeenCalledWith({
          'input example': 'item_one',
        })
      })
    })
  })

  describe('AutoComplete', () => {
    // The only special thing about autocomplete, is that there is a text input
    it('Should have input', () => {
      const inputChange = jest.fn()
      const { actions, getByText, getByRole } = setup({
        ...props,
        autoComplete: true,
        inputChange,
        inputValue: 'initial value',
      })
      const input = getByRole('combobox')
      expect(input.value).toMatch('initial value')
      fireEvent.change(input, { target: { value: 'new value' } })
      expect(inputChange).toHaveBeenCalledTimes(1)
    })
  })

  describe('AutoComplete with keys', () => {
    // The only special thing about autocomplete, is that there is a text input
    it('Should have input', async () => {
      const inputChange = jest.fn()
      const { actions, getByText, getByRole } = setup({
        ...props,
        autoComplete: true,
        inputChange,
        inputValue: 'initial value',
      })
      const input = getByRole('combobox')
      expect(input.value).toMatch('initial value')
      // Nothing focussed
      expect(document.activeElement).toEqual(document.body)
      // Down arrow should open the drop-down and focus first
      fireEvent.keyDown(input, { keyCode: 40 })
      await waitFor(() => {
        expect(document.activeElement.textContent).toEqual('item one')
      })
    })
  })


  describe('with categories', () => {
    it('Should show dropdown with 2 categories', async () => {
      const { queryByRole, getByText, getByRole } = setup({
        ...props,
        options: propsCategories,
      })

      fireEvent.click(getByRole('button'))

      await waitFor(() => {
        expect(queryByRole('listbox')).toBeInTheDocument()
        expect(getByText('All forms of transport')).toBeInTheDocument()
        expect(getByText('Water transport')).toBeInTheDocument()
      })
    })
    it('Should select a sub category', async () => {
      const { actions, getByText, getByRole } = setup({
        ...props,
        selected: '',
        options: propsCategories,
      })

      fireEvent.click(getByRole('button'))
      await waitFor(() => {
        fireEvent.click(getByText(props.options[0].label))
        expect(actions.update).toHaveBeenCalledTimes(1)
        expect(actions.update).toHaveBeenCalledWith({
          'input example': 'item_one',
        })
      })
    })
  })
})
