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
    </Learning>,
  )

  return {
    ...component,
  }
}

describe('Learning', () => {
  describe('Should render', () => {
    it('with a given class', () => {
      const { container } = setup({ ...props, className: 'foo' })
      expect(container.querySelector('.learning')).toHaveClass('foo')
    })

    it('the Tooltip button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.tooltip')).toBeTruthy()
    })

    it('the Example button with custom text', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.button-example').textContent).toBe('Custom')
    })

    it('the Example button with default text', () => {
      const updatedProps = { ...props }
      delete updatedProps.example.buttonTitle
      const { container } = setup({ ...updatedProps })
      expect(container.querySelector('.button-example').textContent).toBe('Example')
    })

    it('the Lesson button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.button-lesson')).toBeTruthy()
    })

    it('with the default Example background colour', () => {
      const { container } = setup({ ...props })

      expect(container.querySelector('.form-group-example')).toHaveClass('bg-blue-deep-10')
    })

    it('with a custom Example background colour', () => {
      const updatedProps = { ...props }
      updatedProps.example.bgColour = 'red-deep-10'
      const { container } = setup({ ...updatedProps })

      expect(container.querySelector('.form-group-example')).toHaveClass('bg-red-deep-10')
    })

    it('with a custom Example header', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.form-group-example dt').textContent)
        .toBe('Example title')
    })

    it('with the default Example header', () => {
      const updatedProps = { ...props }
      delete updatedProps.example.header
      const { container } = setup({ ...updatedProps })

      expect(container.querySelector('.form-group-example dt').textContent)
        .toBe('A fictional example to help you complete this section')
    })
  })

  describe('should not render', () => {
    it('if no example, lesson or tooltip provided', () => {
      const { container } = setup({})
      expect(container.innerHTML).toEqual('')
    })

    it('example if it has no content', () => {
      const { container } = setup({ example: {} })
      expect(container.innerHTML).toEqual('')
    })

    it('lesson if it has no content', () => {
      const { container } = setup({ lesson: {} })
      expect(container.innerHTML).toEqual('')
    })
  })

  describe('Should display learning content', () => {
    it('for Example', async () => {
      const { container } = setup({ ...props })
      const button = container.querySelector('.button-example')
      fireEvent.click(button)

      const exampleLearn = container.querySelector('.form-group-example')
      await waitFor(() => {
        expect(exampleLearn).not.toHaveClass('hidden')
      })
    })

    it('for Lesson', async () => {
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
