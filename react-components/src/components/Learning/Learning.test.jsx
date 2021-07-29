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
      expect(container.querySelector('.tooltip')).toBeInTheDocument()
    })

    it('Should have an Example button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.button-example')).toBeInTheDocument()
    })

    it('Should have a Lesson button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.button-lesson')).toBeInTheDocument()
    })
  })

  describe('Should display learning content', () => {
    it('Should display Tooltip content', async () => {
      const { container } = setup({ ...props })
      /*
       Tooltip component should be tested itself for show/hide, so we just need
       to make sure it's being rendered.
      */
      expect(container.querySelector('.tooltip')).toBeInTheDocument()
    })

    it('Should display Example content', async () => {
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
