import React from 'react'
import { render } from '@testing-library/react'
import props from '../TextArea/TextArea.fixtures'

import { Input } from '.'

const setup = ({ ...data }) => render(<Input {...data} onChange={jest.fn} />)

describe('Input', () => {
  it('Should have a label', () => {
    const { queryByText } = setup(props)
    expect(queryByText(props.label)).toBeInTheDocument()
  })

  describe('Example', () => {
    it('Should have an example', () => {
      const { queryByText } = setup(props)
      expect(queryByText('An example of the required text')).toBeInTheDocument()
    })

    it('Should not have an example', () => {
      const { queryByText } = setup({ ...props, example: null })
      expect(
        queryByText('An example of the required text')
      ).not.toBeInTheDocument()
    })
  })

  describe('Description', () => {
    it('Should have a description', () => {
      const { queryByText } = setup(props)
      expect(queryByText(props.description)).toBeInTheDocument()
    })
    it('Should not have a description', () => {
      const { queryByText } = setup({ ...props, description: '' })
      expect(queryByText(props.description)).not.toBeInTheDocument()
    })
  })

  describe('Tooltip', () => {
    it('Should have a tooltip', () => {
      const { getByTitle } = setup(props)
      expect(getByTitle('Click to view Educational moment')).toBeInTheDocument()
    })
    it('Should not have a tooltip', () => {
      const { queryByTitle } = setup({ ...props, tooltip: null })
      expect(
        queryByTitle('Click to view Educational moment')
      ).not.toBeInTheDocument()
    })
  })

  describe('Errors', () => {
    it('Should have errors', () => {
      const { queryByText } = setup({
        ...props,
        errors: ['an error'],
      })
      expect(queryByText('an error')).toBeInTheDocument()
    })
  })

  it('should allow any standard input attributes', () => {
    const { getByLabelText } = setup({
      ...props,
      label: 'Input with attributes',
      placeholder: 'Foo',
      disabled: true,
      inputMode: 'numeric',
      pattern: '[0-9]*',
      size: 4,
      readOnly: true,
    })

    const input = getByLabelText('Input with attributes')
    expect(input.getAttribute('placeholder')).toBe('Foo')
    expect(input).toHaveAttribute('disabled')
    expect(input.getAttribute('inputmode')).toBe('numeric')
    expect(input.getAttribute('pattern')).toBe('[0-9]*')
    expect(input.getAttribute('size')).toBe('4')
  })
})
