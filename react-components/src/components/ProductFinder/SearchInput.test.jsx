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
  let input = container.querySelector('input')
  expect(input).toBeTruthy()
  expect(input === document.activeElement).toBeFalsy()
  expect(container.querySelector('button.clear')).toBeFalsy()
  act(() => {
    input.value='cheese'
    Simulate.change(input)
  })
  // clear input is still not available as the input is not focussed.
  expect(container.querySelector('button.clear')).toBeFalsy()
  // to test the clear button - we need to focus the input.
  // We have to change the content and fire a change event to make that happen as
  // focus event doesn't fire on the window in test
  input.focus()
  act(() => {
    input.value='different'
    Simulate.change(input)
  })
  const clearButton = container.querySelector('button.clear')
  expect(container.querySelector('button.clear')).toBeTruthy()
  act(() => {
    Simulate.click(clearButton)
  })
  expect(input.getAttribute('value')).toEqual('')
})

it('Creates an input with label', () => {
  const onChange = jest.fn()
  const search = jest.fn()

  act(() => {
      ReactDOM.render(
      <SearchInput
        onChange={onChange}
        onKeyReturn={search}
        label="test label"
        placeholder="test placeholder"
      />,
      container)
  })
  const label = container.querySelector('label')
  expect(label.textContent).toMatch(/test label/)
  const input = container.querySelector('input')
  expect(input.getAttribute('placeholder')).toMatch(/test placeholder/)
})

it('Creates an input with a save button', () => {
  const onChange = jest.fn()
  const search = jest.fn()
  const onSave = jest.fn()
  const buttonLabel = "label on save button"

  act(() => {
      ReactDOM.render(
      <SearchInput
        onChange={onChange}
        onKeyReturn={search}
        label="test label"
        placeholder="test placeholder"
        onSaveButtonClick={onSave}
        saveButtonDisabled={false}
        saveButtonLabel={buttonLabel}
      />,
      container)
  })
  const label = container.querySelector('label')
  expect(label.textContent).toMatch(/test label/)
  const saveButton = container.querySelector('button.button--primary')
  expect(saveButton).toBeTruthy()
  expect(saveButton.textContent).toMatch(buttonLabel)
  act(() => {
    Simulate.click(saveButton)
  })
  expect(onSave).toHaveBeenCalled()
})
