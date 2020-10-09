/* eslint-disable */
import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import ExpandCollapse from './ExpandCollapse'
import { waitFor } from '@testing-library/react'

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

it('Opens and closes expander', () => {
  act(() => {
      ReactDOM.render(<ExpandCollapse buttonLabel="test"><div className="hidden-text">Show this text<br/>And this</div></ExpandCollapse>, container)
  })

  const button = container.querySelector('button')
  const expander = container.querySelector('.expander')
  expect(container.querySelector('.expander.expander-collapsed')).toBeTruthy()
  act(() => {
    Simulate.click(button)
  })
  expect(container.querySelector('.expander.expander-expanded')).toBeTruthy()
  expect(container.querySelector('.expander.expander-collapsed')).toBeFalsy()
})


