import React from 'react'
import { render } from '@testing-library/react'
import props from './TextArea.fixtures'

import { TextArea } from '.'

const setup = ({ ...data }) => {
  const actions = {
    handleChange: jest.fn(),
  }

  const utils = render(<TextArea {...data} {...actions} />)

  return {
    ...utils,
    actions,
  }
}

describe('TextArea', () => {
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
      const { queryByRole } = setup({ ...props, tooltip: '' })
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
