import React from 'react'
import { render, fireEvent } from '@testing-library/react'

import Checkbox from '.'

const setup = ({ ...data }) => render(<Checkbox {...data} onChange={jest.fn} />)

describe('Checkbox', () => {
  it('Should have a label', () => {
    const { getByLabelText } = setup({ label: 'Checkbox Label', id: 'checkbox-id' })
    expect(getByLabelText('Checkbox Label')).toBeInTheDocument()
  })

  describe('Description', () => {
    it('Should have a description', () => {
      const { queryByText } = setup({ description: 'Checkbox description' })
      expect(queryByText('Checkbox description')).toBeInTheDocument()
    })
    it('Should not have a description', () => {
      const { queryByText } = setup({ description: '' })
      expect(queryByText('Checkbox description')).not.toBeInTheDocument()
    })
  })

  describe('Errors', () => {
    it('Should have errors', () => {
      const { queryByText } = setup({ errors: ['Checkbox error'] })
      expect(queryByText('Checkbox error')).toBeInTheDocument()
    })
  })

  it('Should be checkable', () => {
    const handleChange = jest.fn()
    const { getByLabelText } = render(
      <Checkbox
        id="checkbox-id"
        label="Checkbox Label"
        checked={false}
        onChange={handleChange}
      />
    )
    const checkbox = getByLabelText('Checkbox Label')
    fireEvent.click(checkbox)
    expect(handleChange).toHaveBeenCalledWith(true)
  })
})