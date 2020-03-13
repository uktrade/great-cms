import React from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import { SectorChooser } from '@src/components/SectorChooser'

let container

beforeEach(() => {
  container = document.createElement('div')
  document.body.appendChild(container)
})

afterEach(() => {
  document.body.removeChild(container)
  container = null
})

it('renders the sector chooser button with tooltip', () => {

  act(() => {
    ReactDOM.render(<SectorChooser />, container)
  })

  const button = container.querySelector('button')
  const tooltip = container.querySelector('.sector-list-tooltip')

  expect(button.textContent).toBe('')
  expect(tooltip.textContent).toBe('Add sectors')

  expect(tooltip.className).toEqual(expect.stringContaining('hidden'))

  act(() => {
    Simulate.mouseOver(button)
  })

  expect(tooltip.className).not.toEqual(expect.stringContaining('hidden'))
})
