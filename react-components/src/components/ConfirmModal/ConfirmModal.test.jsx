import React from 'react'
import ReactModal from 'react-modal'
import { render, fireEvent, waitFor } from '@testing-library/react'

import { ConfirmModal } from '@src/components/ConfirmModal/ConfirmModal'

const deleteItem = jest.fn()

const setup = ({ hasData }) =>
  render(<ConfirmModal hasData={hasData} deleteItem={deleteItem} />)

ReactModal.setAppElement('body')

describe('ConfirmModal', () => {
  afterEach(() => {
    jest.resetAllMocks()
  })

  describe('Delete button', () => {
    it('Should open modal', () => {
      const { getByRole, getByText } = setup({ hasData: true })
      const deleteButton = getByRole('button')
      fireEvent.click(deleteButton)
      getByText('Are you sure?')
    })

    it('Should fire deleteItem', () => {
      const { getByRole } = setup({ hasData: false })
      const deleteButton = getByRole('button')
      fireEvent.click(deleteButton)
      expect(deleteItem).toHaveBeenCalledTimes(1)
    })
  })

  describe('Modal', () => {
    it('Should close modal', async () => {
      const { getByTitle, getByText, queryByText } = setup({
        hasData: true,
      })

      const deleteButton = getByTitle('delete Objective')

      deleteButton.click()

      await waitFor(() => getByText('Are you sure?'))

      const cancelButton = getByText('No')

      cancelButton.click()

      expect(queryByText('Are you sure?')).not.toBeInTheDocument()
    })

    it('Should fire deleteItem', async () => {
      const { getByTitle, getByText, queryByText } = setup({
        hasData: true,
      })

      const deleteButton = getByTitle('delete Objective')

      deleteButton.click()

      await waitFor(() => getByText('Are you sure?'))

      const modalDeleteButton = getByText('Yes')

      modalDeleteButton.click()

      expect(queryByText('Are you sure?')).not.toBeInTheDocument()
      expect(deleteItem).toHaveBeenCalledTimes(1)
    })
  })
})
