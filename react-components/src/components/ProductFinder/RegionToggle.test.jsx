/* eslint-disable */
import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import RegionToggle from './RegionToggle'
import { waitFor } from '@testing-library/react'
import { debug } from 'webpack'

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

it('Opens and closes region when expandAll is close', () => {
  act(() => {
      ReactDOM.render(
      <RegionToggle expandAllRegions={false} 
        region="Test Region" 
        countries='<span><li>a</li></span><span><li>b</li></span>' />, 
      container)
  })
  
  const button = container.querySelector('button')
  expect(container.querySelector('.expand-section')).toBeTruthy()
  act(() => {
    Simulate.click(button)
  })
  expect(container.querySelector('.expand-section.open')).toBeTruthy()
})