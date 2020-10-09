/* eslint-disable */
import React from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import { waitFor } from '@testing-library/react'
import createCountryFinder from '@src/components/ProductFinder/CountryFinder'
import Services from '@src/Services'
import fetchMock from 'fetch-mock'

let container
let countriesMock

const mockResponse = [
  { id: "AL", name: "Albania", region: "Europe", type: "Country" },
  { id: "DZ", name: "Algeria", region: "Africa", type: "Country" },
  { id: "AT", name: "Austria", region: "Europe", type: "Country" },
]

beforeEach(() => {
  container = document.createElement('div')
  document.body.appendChild(container)
  container.innerHTML = '<span id="set-country-button" data-text="my country"></span>'
  Services.setConfig({ apiCountriesUrl: '/api/countries/' })
  countriesMock = fetchMock.get(/\/api\/countries\//, mockResponse)
})

afterEach(() => {
  document.body.removeChild(container)
  container = null
  jest.clearAllMocks()
})

it('Opens and closes country finder', async () => {

  act(() => {
    createCountryFinder({ element: container })
  })
  expect(document.body.querySelector('.country-chooser')).toBeFalsy()
  const button = container.querySelector('button')

  act(() => {
    Simulate.click(button)
  })
  const finder = document.body.querySelector('.country-chooser');
  const closeButton = finder.querySelector('button.dialog-close');
  expect(finder).toBeTruthy()
  await waitFor(() => {
    const region = finder.querySelector('.country-list h2');
    expect(region.textContent).toEqual('Europe+')
  })
  act(() => {
    Simulate.click(finder.querySelector('button.dialog-close'))
  })
  expect(document.body.querySelector('.country-chooser')).toBeFalsy()
})

it('Opens with confirmation', async () => {
  // opens country chooser with country already set - check for confirmation dialogue
  act(() => {
    container.setAttribute('data-text', 'old country')
    createCountryFinder({ element: container })
    Simulate.click(container.querySelector('button')) // open the modal
  })
  const confirmation = document.body.querySelector('.confirmation-modal')
  expect(confirmation).toBeTruthy()
  expect(confirmation.querySelector('h2').textContent).toMatch('Changing target market?')
  act(() => {
    Simulate.click(confirmation.querySelector('button'))
  })
  const finder = document.body.querySelector('.country-chooser');
  const closeButton = finder.querySelector('button.dialog-close');
  expect(finder).toBeTruthy()
  await waitFor(() => {
    const region = finder.querySelector('.country-list h2');
    expect(region.textContent).toEqual('Europe+')
  })
  act(() => {
    Simulate.click(finder.querySelector('button.dialog-close'))
  })
  expect(document.body.querySelector('.country-chooser')).toBeFalsy()
})


it('Open country finder and type-ahead filter', async () => {
  act(() => {
    createCountryFinder({ element: container })
  })
  expect(document.body.querySelector('.country-chooser')).toBeFalsy()
  const button = container.querySelector('button')

  act(() => {
    Simulate.click(button)
  })
  const finder = document.body.querySelector('.country-chooser');
  const closeButton = finder.querySelector('button.dialog-close');
  expect(finder).toBeTruthy()
  await waitFor(() => {
    const region = finder.querySelector('.country-list h2');
    expect(region.textContent).toEqual('Europe+')
  })
  const searchInput = finder.querySelector('.search-input input');
  const europeBlock = finder.querySelector('.country-list ul');
  expect(finder.querySelector('.country-list ul').textContent).toEqual('AlbaniaAustria')
  act(() => {
    searchInput.value = 'au'
    Simulate.change(searchInput)
  })
  expect(finder.querySelector('.country-list ul').textContent).toEqual('Austria')
  act(() => {
    searchInput.value = ''
    Simulate.change(searchInput)
  })
  expect(finder.querySelector('.country-list ul').textContent).toEqual('AlbaniaAustria')
  act(() => {
    searchInput.value = 'aub'
    Simulate.change(searchInput)
  })
  expect(finder.querySelector('.country-list').textContent).toEqual('No results found')
})
