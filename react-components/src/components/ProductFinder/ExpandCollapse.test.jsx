import React from 'react'
import { render, waitFor } from '@testing-library/react'
import ExpandCollapse from './ExpandCollapse'

beforeEach(() => {
  Element.prototype.getBoundingClientRect = jest.fn(() => ({
    width: 100,
    height: 100,
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
  }))
})

it('Opens and closes expander', async () => {
  const { container } = render(
    <ExpandCollapse buttonLabel="test">
      <div className="hidden-text">Show this text<br />And this</div>
    </ExpandCollapse>,
  )

  const button = container.querySelector('button')
  const expander = container.querySelector('.expander')

  expect(expander.style['max-height']).toBe('0')

  button.click()

  await waitFor(() => {
    expect(expander.style['max-height']).toBe('100px')
  })

  button.click()

  await waitFor(() => {
    expect(expander.style['max-height']).toBe('0')
  })
})
