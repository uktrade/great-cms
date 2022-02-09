import React from 'react'
import fetchMock from 'fetch-mock'
import Services from '@src/Services'
import { act, fireEvent, render, waitFor } from '@testing-library/react'

import StartEndPage from './StartEndPage'

const mockResponse = require('./fixtures/product-schedule-cheese.json')

afterEach(() => {
  jest.clearAllMocks()
})

it('Renders a product selection final page', async () => {
  const hsCode = '123456'
  const commodityName = 'default name'
  const newName = ' updated name '
  const saveProduct = jest.fn()

  Services.setConfig({ apiLookupProductScheduleUrl: '/api/lookup-product-schedule/' })
  fetchMock.get(/\/api\/lookup-product-schedule\//, mockResponse)

  const { container } = render(
    <StartEndPage
      commodityCode={hsCode}
      defaultCommodityName={commodityName}
      saveProduct={saveProduct}
      searchCompletedMode
    />,
  )

  await waitFor(() => {
    expect(container.querySelector('input')).toBeTruthy()
  })

  const nameInput = container.querySelector('input')
  expect(nameInput.getAttribute('value')).toEqual(commodityName)

  // to test the clear button - we need to focus the input.
  // We have to change the content and fire a change event to make that happen as
  // focus event doesn't fire on the window in test
  act(() => {
    nameInput.focus()
    fireEvent.change(nameInput, { target: { value: `${commodityName}-` } })
  })

  container.querySelector('button.clear').click()

  expect(nameInput.getAttribute('value')).toEqual('')
  const saveButton = container.querySelector('button.save-product')
  expect(saveButton).toHaveAttribute('disabled')

  fireEvent.change(nameInput, { target: { value: newName } })

  await waitFor(() => {
    expect(saveButton).not.toHaveAttribute('disabled')
  })

  saveButton.click()

  await waitFor(() => {
    expect(saveProduct.mock.calls).toHaveLength(1)
    expect(saveProduct.mock.calls[0][0]).toEqual(hsCode)
    expect(saveProduct.mock.calls[0][1]).not.toEqual(newName)
    expect(saveProduct.mock.calls[0][1]).toEqual(newName.trim())
  })
})
