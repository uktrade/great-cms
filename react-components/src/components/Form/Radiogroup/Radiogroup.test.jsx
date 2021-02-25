import React from 'react'
import { render, fireEvent, waitFor } from '@testing-library/react'

import { Radiogroup } from './Radiogroup'

const props = {
  groupName: 'risk_likelihood',
  id: 6,
  label: 'Risk likelihood',
  options: [
    { label: 'Trivial', value: 'TRIVIAL' },
    { label: 'Minor', value: 'MINOR' },
    { label: 'Moderate', value: 'MODERATE' },
    { label: 'Major', value: 'MAJOR' },
    { label: 'Severe', value: 'SEVERE' },
  ],
  selected: 'MINOR',
  update: () => (props.id, props.groupName),
}

const setup = ({ ...data }) => {
  const component = render(
    <Radiogroup {...data}>
      <p>The child component</p>
    </Radiogroup>
  )

  return {
    ...component,
  }
}

describe('Radiogroup', () => {
  describe('Should display radiogroup', () => {
    it('Should display five options', () => {
      const { container } = setup({ ...props })
      const options = container.querySelectorAll('.great-radiogroup__item')

      expect(options).toHaveLength(5)
    })

    it('Should display `Minor` as selected', () => {
      const { container } = setup({ ...props })
      const minor = container.querySelectorAll('.great-radiogroup__input')[1]
      expect(minor.checked).toEqual(true)
    })

    it('Should select `Trival` when clicked, and deselect `Minor`', () => {
      const { container } = setup({ ...props })

      const trivial = container.querySelectorAll('.great-radiogroup__input')[0]
      const minor = container.querySelectorAll('.great-radiogroup__input')[1]

      expect(minor.checked).toEqual(true)
      expect(trivial.checked).toEqual(false)

      fireEvent.click(trivial)

      expect(minor.checked).toEqual(false)
      expect(trivial.checked).toEqual(true)
    })
  })
})
