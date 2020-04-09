import React from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import Sector from '@src/components/Sector'

let container

beforeEach(() => {
  container = document.createElement('div')
  document.body.appendChild(container)
})

afterEach(() => {
  document.body.removeChild(container)
  container = null
})

it('callback alters selected state on click', () => {
  const callback = () => {
    return true
  }

  act(() => {
    ReactDOM.render(<Sector id="sector" name="Sector" selected={false} addRemoveSector={callback} />, container)
  })

  const button = container.querySelector('button')

  expect(button.className).not.toEqual(expect.stringContaining('selected'))

  act(() => {
    Simulate.click(button)
  })

  expect(button.className).toEqual(expect.stringContaining('selected'))
})
