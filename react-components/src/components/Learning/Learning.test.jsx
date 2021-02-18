import React from 'react'
import { render, fireEvent, waitFor, cleanup } from '@testing-library/react'

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

beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
  cleanup()
})

describe('Learning', () => {
  describe('Should render learning buttons', () => {
    it('Should have a Tooltip button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('tooltip'))
    })

    it('Should have an Example button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('button-example'))
    })

    it('Should have a Lesson button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('button-lesson'))
    })
  })

  describe('Should display learning content', () => {
    it('Should display Tooltip content', async () => {
      const { container } = setup({ ...props })
      const button = container.querySelectorAll('.tooltip__icon')[0]
      fireEvent.click(button)

      await waitFor(() => {
        expect(container.querySelectorAll('.tooltip__text')[0])
      })
    })

    it('Should display Lesson content', async () => {
      const { container } = setup({ ...props })
      const button = container.querySelectorAll('.button-example')[0]
      fireEvent.click(button)

      const exampleLearn = container.querySelectorAll('.form-group-example')[0]
      await waitFor(() => {
        expect(exampleLearn).not.toHaveClass('hidden')
      })
    })

    it('Should display Lesson content', async () => {
      const { container } = setup({ ...props })
      const button = container.querySelectorAll('.button-lesson')[0]
      fireEvent.click(button)

      const lessonLearn = container.querySelectorAll('.lesson-learn')[0]
      await waitFor(() => {
        expect(lessonLearn).toHaveClass('inline-block')
      })
    })
  })
})
