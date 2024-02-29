import React from 'react'
import { render } from '@testing-library/react'

import { ProductPicker } from '.'

const setup = () => {
  const doc = render(
    <div>
      <label
        className="great-hero__label"
        htmlFor="product-input"
        data-testid="label"
      >
        What do you sell?
      </label>
      <input
        className="great-hero__input"
        type="text"
        name="product-input"
        id="product-input"
        placeholder="For example, Cheese"
      />
      <ProductPicker />
      <button
        id="product-input-submit"
        className="great-hero__button primary-button great-primary-button--chevron"
      >
        <span className="great-hero__button-text">Get started</span>
      </button>
    </div>
  )
  return {
    ...doc,
  }
}

describe('ProductPicker', () => {
  it('Submit button should be disabled', () => {
    const { getByText } = setup()

    expect(getByText('Get started').closest('button')).toBeDisabled()
  })

  it('Text input should be hidden', () => {
    const { getByPlaceholderText } = setup()

    expect(getByPlaceholderText('For example, Cheese')).not.toBeVisible()
  })

  it('Label has correct for attribute value', () => {
    const { getByTestId } = setup()

    expect(getByTestId('label')).toHaveProperty(
      'htmlFor',
      'react-product-input'
    )
  })
})
