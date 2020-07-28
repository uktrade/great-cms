import React from 'react'
import { render } from '@testing-library/react'
import props from './FieldWithExample.fixtures'

import FieldWithExample from '.'

const setup = ({...data}) => {
  const actions = {
    handleChange: jest.fn()
  }

  const utils = render(<FieldWithExample
    {...data}
    {...actions}
  />)

  return {
    ...utils,
    actions,
  }
}

describe('FieldWithExample', () => {
  it('Should have a label', () => {
    const { queryByText } = setup(props)
    expect(queryByText(props.label)).toBeInTheDocument()
  })

  describe('Input', () => {
    it('Should have a textarea', () => {
      const { container } = setup(props)
      expect(container.querySelector('textarea')).toBeInTheDocument()
    })

    it('Should have an input', () => {
      const { container } = setup({...props, tag: 'number'})
      expect(container.querySelector('input')).toBeInTheDocument()
    })
  })

  describe('Example', () => {
    it('Should have an example', () => {
      const { queryByText } = setup(props)
      expect(queryByText('An example of the required text')).toBeInTheDocument()
    })

    it('Should not have an example', () => {
      const { queryByText } = setup({...props, example: ''})
      expect(queryByText('An example of the required text')).not.toBeInTheDocument()
    })
  })

  describe('Currency', () => {
    it('Should have a currency', () => {
      const { queryByText } = setup({...props, tag: 'number', currency: 'MUR'})
      expect(queryByText('MUR')).toBeInTheDocument()
    })
    it('Should not have a currency', () => {
      const { queryByText } = setup(props)
      expect(queryByText('MUR')).not.toBeInTheDocument()
    })
  })

  describe('Description', () => {
    it('Should have a description', () => {
      const { queryByText } = setup(props)
      expect(queryByText(props.description)).toBeInTheDocument()
    })
    it('Should not have a description', () => {
      const { queryByText } = setup({...props, description: ''})
      expect(queryByText(props.description)).not.toBeInTheDocument()
    })
  })

  describe('Tooltip', () => {
    it('Should have a tooltip', () => {
      const { queryByRole } = setup(props)
      expect(queryByRole('tooltip')).toBeInTheDocument()
    })
    it('Should not have a tooltip', () => {
      const { queryByRole } = setup({...props, tooltip: ''})
      expect(queryByRole('tooltip')).not.toBeInTheDocument()
    })
  })
})
