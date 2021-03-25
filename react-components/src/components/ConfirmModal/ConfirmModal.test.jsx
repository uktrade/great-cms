import React from 'react'

import { render, fireEvent } from '@testing-library/react'
import { ConfirmModal } from '@src/components/ConfirmModal/ConfirmModal'

const setup = ({ hasData }) => {
  const actions = {
    deleteItem: jest.fn(),
  }
  const component = render(<ConfirmModal hasData={hasData} {...actions} />)

  return {
    ...component,
    actions,
  }
}

describe('ConfirmModal', () => {
  describe('Delete button', () => {
    it('Should open modal', () => {
      const { getByRole, getByText } = setup({ hasData: true })
      const deleteButton = getByRole('button')
      fireEvent.click(deleteButton)
      getByText('Are you sure?')
    })

    it('Should fire deleteItem', () => {
      const { getByRole, actions } = setup({ hasData: false })
      const deleteButton = getByRole('button')
      fireEvent.click(deleteButton)
      expect(actions.deleteItem).toHaveBeenCalledTimes(1)
    })
  })
  describe('Modal', () => {
    it('Should close modal', () => {
      const { getByRole, getByText, queryByText } = setup({ hasData: true })
      const deleteButton = getByRole('button')
      fireEvent.click(deleteButton)
      getByText('Are you sure?')

      const cancelButton = getByRole('button', { name: /No/i })
      cancelButton.click(deleteButton)
      expect(queryByText('Are you sure?')).not.toBeInTheDocument()
    })

    it('Should fire deleteItem', () => {
      const { getByRole, getByText, queryByText, actions } = setup({
        hasData: true,
      })
      const deleteButton = getByRole('button')
      fireEvent.click(deleteButton)
      getByText('Are you sure?')

      const modalDeleteButton = getByRole('button', { name: /Yes/i })
      fireEvent.click(modalDeleteButton)
      expect(queryByText('Are you sure?')).not.toBeInTheDocument()
      expect(actions.deleteItem).toHaveBeenCalledTimes(1)
    })
  })
})
