/* eslint-disable */
import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import fetchMock from 'fetch-mock'
import Services from '@src/Services'
import { waitFor } from '@testing-library/react'
import { act, Simulate } from 'react-dom/test-utils'
import StartEndPage from './StartEndPage'

let container

beforeEach(() => {
  container = document.createElement('div')
  document.body.appendChild(container)
})

afterEach(() => {
  document.body.removeChild(container)
  container = null
  jest.clearAllMocks()
})

const mockResponse = {
  type:'one',
  children:[]
}


it('Renders a product selection final page', async () => {
  const hsCode = '123456'
  const commodityName = "default name"
  const newName = "updated name"
  const saveProduct = jest.fn()

  Services.setConfig({ apiLookupProductScheduleUrl: '/api/lookup-product-schedule/' })
  fetchMock.get(/\/api\/lookup-product-schedule\//, mockResponse)

  act(() => {
      ReactDOM.render(
      <StartEndPage 
        commodityCode={hsCode} 
        defaultCommodityName="default name" 
        saveProduct={saveProduct} 
      />, 
      container)
  })
  await waitFor(() => {
    let results = container.querySelector('input');
    expect(results).toBeTruthy()
  })
  let nameInput = container.querySelector('input')
  expect(nameInput.getAttribute('value')).toEqual(commodityName)
  const clearButton = container.querySelector('button.clear')
  act(() => {
    Simulate.click(clearButton)
  })
  expect(nameInput.getAttribute('value')).toEqual('')
  let saveButton = container.querySelector('button.save-product')
  expect(saveButton).toHaveAttribute('disabled')

  act(() => {
    nameInput.value = newName
    Simulate.change(nameInput)
  })
  expect(saveButton).not.toHaveAttribute('disabled')
  act(() => {
    Simulate.click(saveButton)
  })
  expect(saveProduct.mock.calls.length).toEqual(1)
  expect(saveProduct.mock.calls[0][0]).toEqual(hsCode)
  expect(saveProduct.mock.calls[0][1]).toEqual(newName)

})
