/* eslint-disable */
import React from 'react'
import ReactDOM from 'react-dom'
import fetchMock from 'fetch-mock'
import Services from '@src/Services'

import { act, Simulate } from 'react-dom/test-utils'
import Filter from './Filter'

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

const filters = {
  filter1: { label: 'filter 1' },
  filter2: { label: 'filter 2' },
}

it('Renders a filter', () => {
  const setActiveFilter = jest.fn()
  act(() => {
    ReactDOM.render(
      <Filter setActiveFilter={setActiveFilter} filters={filters} />,
      container
    )
  })

  const filter = container.querySelector('.filter')
  expect(filter.textContent).toEqual('filter 1filter 2')
  const cb1 = filter.querySelector('input#cb-filter1')
  const cb2 = filter.querySelector('input#cb-filter2')
  expect(cb1).toBeTruthy()
  expect(cb2).toBeTruthy()
  act(() => {
    Simulate.click(cb1)
  })
  expect(setActiveFilter.mock.calls.length).toEqual(1)
  expect(setActiveFilter.mock.calls[0][0]).toEqual({ filter1: true })
  act(() => {
    Simulate.click(cb2)
  })
  expect(setActiveFilter.mock.calls.length).toEqual(2)
  expect(setActiveFilter.mock.calls[1][0]).toEqual({
    filter1: true,
    filter2: true,
  })
  act(() => {
    Simulate.click(cb1)
  })
  expect(setActiveFilter.mock.calls.length).toEqual(3)
  expect(setActiveFilter.mock.calls[2][0]).toEqual({ filter2: true })
})
