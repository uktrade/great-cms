import React from 'react'
import { render, fireEvent, waitFor } from '@testing-library/react'

import { Learning } from './Learning'

const props = {
  tooltip: {
    content: 'Tooltip content',
    title: 'Tooltip title',
  },
  example: {
    buttonTitle: 'Custom',
    header: 'Example title',
    content: 'Example content',
  },
  lesson: {
    url: '/',
    title: 'Lesson title',
    category: 'Category',
    duration: '90 mins',
  },
}

const setup = ({ ...data }) => {
  const component = render(
    <Learning {...data}>
      <p>The child component</p>
    </Learning>
  )

  return {
    ...component,
  }
}

describe('Learning', () => {
  describe('Should render learning buttons', () => {
    it('Should have a Tooltip button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.tooltip')).toBeTruthy()
    })

    it('Should have an Example button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.button-example')).toBeTruthy()
    })

    it('Should have a Lesson button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.button-lesson')).toBeTruthy()
    })
  })

  describe('Should display learning content', () => {
    it('Should display Tooltip content', async () => {
      const { container } = setup({ ...props })
      const button = container.querySelector('.tooltip__icon button')
      fireEvent.click(button)

      await waitFor(() => {
        expect(container.querySelector('.tooltip__text')).toBeTruthy()
      })
    })

    it('Should display Example content', async () => {
      const { container } = setup({ ...props })
      const button = container.querySelector('.button-example')
      fireEvent.click(button)

      const exampleLearn = container.querySelector('.form-group-example')
      await waitFor(() => {
        expect(exampleLearn).not.toHaveClass('hidden')
      })
    })

    it('Should display Lesson content', async () => {
      const { container } = setup({ ...props })
      const button = container.querySelector('.button-lesson')
      fireEvent.click(button)

      const lessonLearn = container.querySelector('.lesson-learn')
      await waitFor(() => {
        expect(lessonLearn).toHaveClass('inline-block')
      })
    })
  })
})
