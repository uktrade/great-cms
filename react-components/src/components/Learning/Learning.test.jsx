import React from 'react'
import { render, waitFor } from '@testing-library/react'
import { uniqueId } from '@src/Helpers'

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

const setup = (propsData) => render(<Learning {...propsData} />)

// Force generated ID to be abcd1234
jest.mock('@src/Helpers', () => ({
  uniqueId: jest.fn().mockReturnValue('abcd1234'),
}))

const getButton = (type, container) => container.querySelector(`[aria-controls="${type}-content-abcd1234"]`)
const getContent = (type, container) => container.querySelector(`#${type}-content-abcd1234`)

describe('Learning', () => {
  describe('Should render', () => {
    it('with a given class', () => {
      const { container } = setup({ ...props, className: 'foo' })
      expect(container.querySelector('.learning')).toHaveClass('foo')
    })

    it('with a unique ID for each button and content', () => {
      const { container } = setup({ ...props })

      expect(container.querySelector('.button-example').getAttribute('aria-controls')).toBe('example-content-abcd1234')
      expect(container.querySelector('.form-group-example').getAttribute('id')).toBe('example-content-abcd1234')

      expect(container.querySelector('.button-lesson').getAttribute('aria-controls')).toBe('lesson-content-abcd1234')
      expect(container.querySelector('.lesson-learn').getAttribute('id')).toBe('lesson-content-abcd1234')
    })

    it('the Tooltip button', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.tooltip')).toBeTruthy()
    })

    it('the Example button with custom text', () => {
      const { container } = setup({ ...props })
      expect(getButton('example', container).textContent).toBe('Custom')
    })

    it('the Example button with default text', () => {
      const updatedProps = { ...props }
      delete updatedProps.example.buttonTitle
      const { container } = setup({ ...updatedProps })
      expect(getButton('example', container).textContent).toBe('Example')
    })

    it('the Lesson button', () => {
      const { container } = setup({ ...props })
      expect(getButton('lesson', container)).toBeTruthy()
    })

    it('with the default Example background colour', () => {
      const { container } = setup({ ...props })

      expect(getContent('example', container)).toHaveClass('form-group-example')
    })

    it('with a custom Example header', () => {
      const { container } = setup({ ...props })
      expect(container.querySelector('.form-group-example h3').textContent)
        .toBe('Example title')
    })

    it('with the default Example header', () => {
      const updatedProps = { ...props }
      delete updatedProps.example.header
      const { container } = setup({ ...updatedProps })

      expect(container.querySelector('.form-group-example h3').textContent)
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

  describe('functionally', () => {
    it('should start with all content hidden', () => {
      const { container } = setup({ ...props })

      expect(getContent('example', container)).toHaveClass('hidden')
      expect(getButton('example', container).getAttribute('aria-expanded')).toBe('false')
      expect(getContent('lesson', container)).toHaveClass('hidden')
      expect(getButton('lesson', container).getAttribute('aria-expanded')).toBe('false')
    })

    it('should reveal the Example or Lesson content only', async () => {
      const { container } = setup({ ...props })
      const exampleButton = getButton('example', container)
      const lessonButton = getButton('lesson', container)
      const exampleContent = getContent('example', container)
      const lessonContent = getContent('lesson', container)

      exampleButton.click()

      await waitFor(() => {
        expect(exampleContent).not.toHaveClass('hidden')
        expect(exampleButton.getAttribute('aria-expanded')).toBe('true')

        expect(lessonContent).toHaveClass('hidden')
        expect(lessonButton.getAttribute('aria-expanded')).toBe('false')
      })

      lessonButton.click()

      await waitFor(() => {
        expect(lessonContent).toHaveClass('inline-block')
        expect(lessonButton.getAttribute('aria-expanded')).toBe('true')

        expect(exampleContent).toHaveClass('hidden')
        expect(exampleButton.getAttribute('aria-expanded')).toBe('false')
      })

      lessonButton.click()

      await waitFor(() => {
        expect(lessonContent).toHaveClass('hidden')
        expect(lessonButton.getAttribute('aria-expanded')).toBe('false')

        expect(exampleContent).toHaveClass('hidden')
        expect(exampleButton.getAttribute('aria-expanded')).toBe('false')
      })
    })

    it('does not regenerate the unique ID when interacting', async () => {
      // Only way to reset this mock?!
      uniqueId.mockImplementation(() => Math.random().toString(16).slice(2, 10))

      const { container } = setup({ ...props })
      const id = container.querySelector('.button-example').getAttribute('aria-controls')

      container.querySelector('.button-example').click()

      await waitFor(() => {
        expect(container.querySelector('.button-example').getAttribute('aria-controls')).toEqual(id)
      })
    })
  })
})
