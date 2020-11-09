/* eslint-disable */
import React, { useState } from 'react'
import ReactDOM from 'react-dom'
import { act, Simulate } from 'react-dom/test-utils'
import SearchInput from './SearchInput'

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



it('Creates an autofocus input', () => {
  const onChange = jest.fn()
  const search = jest.fn()

  act(() => {
      ReactDOM.render(
      <SearchInput
        onChange={onChange}
        onKeyReturn={search}
        autoFocus
      />, 
      container)
  })
  const input = container.querySelector('input')
  expect(input).toBeTruthy()
  expect(document.activeElement).toEqual(input)
  expect(container.querySelector('button.clear')).toBeFalsy()
  act(() => {
    input.value='cheese'
    Simulate.change(input)
  })
  const clearButton = container.querySelector('button.clear')
  expect(clearButton).toBeTruthy()
    act(() => {
    Simulate.click(clearButton)
  })
  expect(input.value).toEqual('')
})

it('Creates an non-autofocus input', () => {
  const onChange = jest.fn()
  const search = jest.fn()

  act(() => {
      ReactDOM.render(
      <SearchInput
        onChange={onChange}
        onKeyReturn={search}
      />, 
      container)
  })
  const input = container.querySelector('input')
  expect(input).toBeTruthy()
  expect(input === document.activeElement).toBeTruthy
})