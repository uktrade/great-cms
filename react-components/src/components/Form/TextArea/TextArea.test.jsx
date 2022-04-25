import React from 'react'
import { render, fireEvent, waitFor } from '@testing-library/react'
import props from './TextArea.fixtures'

import { TextArea } from '.'

const onChange = jest.fn()

const setup = ({ ...data }) =>
  render(<TextArea {...data} onChange={onChange} />)

describe('TextArea', () => {
  it('Should call using onChange with Name', async () => {
    const { container } = await setup(props)
    const textarea = container.querySelectorAll('textarea')[0]

    fireEvent.change(textarea, { target: { value: 'tested' } })

    await waitFor(() => {
      expect(onChange).toHaveBeenCalledTimes(1)
      expect(onChange).toHaveBeenCalledWith({
        test_name: 'tested',
      })
    })
  })

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
      const { queryByText } = setup({ ...props, example: '' })
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
      const { queryByRole } = setup({ ...props, tooltip: null })
      expect(
        queryByRole('Click to view Educational moment')
      ).not.toBeInTheDocument()
    })
  })

  describe('Errors', () => {
    it('Should have errors', () => {
      const { queryByText } = setup({ ...props, errors: ['an error'] })
      expect(queryByText('an error')).toBeInTheDocument()
    })
  })
})
