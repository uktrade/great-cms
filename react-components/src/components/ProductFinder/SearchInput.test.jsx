import React from 'react'
import { act, fireEvent, render } from '@testing-library/react'
import SearchInput from './SearchInput'

describe('SearchInput', () => {
  afterEach(() => {
    jest.clearAllMocks()
  })

  it('Creates an autofocus input', () => {
    const onChange = jest.fn()
    const search = jest.fn()

    const { container } = render(
      <SearchInput onChange={onChange} onKeyReturn={search} autoFocus />
    )

    const input = container.querySelector('input')
    expect(input).toBeTruthy()
    expect(document.activeElement).toEqual(input)
    expect(container.querySelector('button.clear')).toBeFalsy()

    fireEvent.change(input, { target: { value: 'cheese' } })

    const clearButton = container.querySelector('button.clear')

    expect(clearButton).toBeTruthy()

    clearButton.click()

    expect(input.value).toEqual('')
  })

  it('Creates an non-autofocus input', () => {
    const onChange = jest.fn()
    const search = jest.fn()

    const { container } = render(
      <SearchInput onChange={onChange} onKeyReturn={search} />
    )

    const input = container.querySelector('input')

    expect(input).toBeTruthy()
    expect(input === document.activeElement).toBeFalsy()
    expect(container.querySelector('button.clear')).toBeFalsy()

    fireEvent.change(input, { target: { value: 'cheese' } })

    // clear input is still not available as the input is not focussed.
    expect(container.querySelector('button.clear')).toBeFalsy()

    // to test the clear button - we need to focus the input.
    act(() => {
      input.focus()
    })

    const clearButton = container.querySelector('button.clear')

    expect(container.querySelector('button.clear')).toBeTruthy()

    clearButton.click()

    expect(input.getAttribute('value')).toEqual('')
  })

  it('Creates an input with label', () => {
    const onChange = jest.fn()
    const search = jest.fn()

    const { container } = render(
      <SearchInput
        onChange={onChange}
        onKeyReturn={search}
        label="test label"
        placeholder="test placeholder"
      />
    )
    const label = container.querySelector('label')
    expect(label.textContent).toMatch(/test label/)
    const input = container.querySelector('input')
    expect(input.getAttribute('placeholder')).toMatch(/test placeholder/)
  })

  it('Creates an input with a save button', () => {
    const onChange = jest.fn()
    const search = jest.fn()
    const onSave = jest.fn()
    const buttonLabel = 'label on save button'

    const { container } = render(
      <SearchInput
        onChange={onChange}
        onKeyReturn={search}
        label="test label"
        placeholder="test placeholder"
        onSaveButtonClick={onSave}
        saveButtonDisabled={false}
        saveButtonLabel={buttonLabel}
      />
    )

    const label = container.querySelector('label')
    expect(label.textContent).toMatch(/test label/)

    const saveButton = container.querySelector('button.primary-button')
    expect(saveButton).toBeTruthy()
    expect(saveButton.textContent).toMatch(buttonLabel)

    saveButton.click()

    expect(onSave).toHaveBeenCalled()
  })
})
