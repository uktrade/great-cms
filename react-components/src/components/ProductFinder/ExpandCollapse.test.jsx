import React from 'react'
import { render, waitFor } from '@testing-library/react'
import ExpandCollapse from './ExpandCollapse'

describe('Expand/Collapse', () => {
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
      <ExpandCollapse>
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

  it('starts expanded', () => {
    const { container } = render(
      <ExpandCollapse defaultExpanded>
        Foo
      </ExpandCollapse>,
    )

    const expander = container.querySelector('.expander')

    expect(expander.style['max-height']).toBe('100px')
  })

  it('takes a custom button class and label', () => {
    const { container } = render(
      <ExpandCollapse buttonLabel="Button label" buttonClass="foo">
        Foo
      </ExpandCollapse>,
    )

    const button = container.querySelector('button')

    expect(button).toHaveClass('foo')
    expect(button.textContent).toEqual('Button label')
  })

  it('renders with the button after the expander content', () => {
    const { container } = render(
      <ExpandCollapse buttonBefore={false}>
        Foo
      </ExpandCollapse>,
    )

    expect(container.querySelector('button + .expander')).toBeNull()
    expect(container.querySelector('.expander + button')).toBeTruthy()
  })

  it('renders a different button label when expanded', () => {
    const { container } = render(
      <ExpandCollapse expandedButtonLabel="FooBar" defaultExpanded>
        Foo
      </ExpandCollapse>,
    )

    expect(container.querySelector('button').textContent).toEqual('FooBar')
  })
})
