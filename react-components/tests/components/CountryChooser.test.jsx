import React from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import CountryChooser from '@src/components/CountryChooser'

let container

beforeEach(() => {
  container = document.createElement('div')
  document.body.appendChild(container)
})

afterEach(() => {
  document.body.removeChild(container)
  container = null
})

it('shows the select component on click', () => {
  const countryList = [
    { value: 'Australia', label: 'Australia' },
    { value: 'India', label: 'India' },
    { value: 'Japan', label: 'Japan' },
  ]

  act(() => {
    ReactDOM.render(<CountryChooser countryList={countryList} selectedCountries={[]} addCountry={function(){}} />, container)
  })

  expect(container.querySelector('#country-autocomplete')).toBeFalsy()

  const button = container.querySelector('#country-chooser-button')

  act(() => {
    Simulate.click(button)
  })

  expect(container.querySelector('#country-autocomplete')).toBeTruthy()
})
