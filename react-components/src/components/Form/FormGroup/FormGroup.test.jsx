import React from 'react'
import { render, fireEvent } from '@testing-library/react'

import { FormGroup } from '.'

const props = {
  label: 'Test Label',
  id: 'i am an id',
}

const setup = ({ ...data }) => {
  const component = render(
    <FormGroup {...data}>
      <p>The child component</p>
    </FormGroup>
  )

  return {
    ...component,
  }
}

describe('FormGroup', () => {
  describe('Label', () => {
    it('Should be visible', () => {
      const { queryByText } = setup(props)
      const Label = queryByText(props.label)
      expect(Label).toBeInTheDocument()
      expect(Label).not.toHaveClass('visually-hidden')
    })

    it('Should not be visible', () => {
      const { queryByText } = setup({ ...props, hideLabel: true })
      const Label = queryByText(props.label)
      expect(Label).toBeInTheDocument()
      expect(Label).toHaveClass('visually-hidden')
    })
  })

  it('Should have a child', () => {
    const { queryByText } = setup(props)
    expect(queryByText('The child component')).toBeInTheDocument()
  })

  it('Should have a description', () => {
    const { queryByText } = setup({
      ...props,
      description: '<p>This is description</p>',
    })
    expect(queryByText('This is description')).toBeInTheDocument()
  })

  describe('Example', () => {
    const example = { content: '<p>This is an example</p>' }

    it('Should be hidden', () => {
      const { queryByText, container } = setup({ ...props, example })
      const exampleContainer = container.querySelector('.form-group-example')
      const buttonIcon = container.querySelector('.button-example i')
      expect(exampleContainer).toHaveClass('hidden')
      expect(buttonIcon).toHaveClass('fa-chevron-down')
      expect(queryByText('This is an example')).toBeInTheDocument()
      expect(queryByText('Example')).toBeInTheDocument()
    })

    it('Should be displayed', () => {
      const { queryByText, container } = setup({ ...props, example })
      const exampleContainer = container.querySelector('.form-group-example')
      const buttonIcon = container.querySelector('.button-example i')
      const toggleButton = queryByText('Example')
      fireEvent.click(toggleButton)
      expect(exampleContainer).not.toHaveClass('hidden')
      expect(buttonIcon).toHaveClass('fa-chevron-up')
      expect(queryByText('This is an example')).toBeInTheDocument()
      expect(
        queryByText('A fictional example to help you complete this section')
      ).toBeInTheDocument()
    })

    it('Should have a different button title', () => {
      const { queryByText } = setup({
        ...props,
        example: { ...example, buttonTitle: 'Taxes' },
      })

      expect(queryByText('This is an example')).toBeInTheDocument()
      expect(queryByText('Taxes')).toBeInTheDocument()
    })

    it('Should have a different header', () => {
      const { queryByText } = setup({
        ...props,
        example: { ...example, header: 'A new example' },
      })

      expect(queryByText('This is an example')).toBeInTheDocument()
      expect(queryByText('A new example')).toBeInTheDocument()
    })
  })

  describe('Lesson', () => {
    const lesson = {
      url: 'http://www.exmaple.com/',
      title: 'Lesson Title',
      category: 'Lesson Category',
      duration: '2 min',
    }

    it('Should be hidden', () => {
      const { queryByText, queryByTitle, container } = setup({
        ...props,
        lesson,
      })
      const buttonIcon = container.querySelector('.button-lesson i')
      expect(queryByTitle(lesson.title)).toHaveClass('hidden')
      expect(queryByText('Lesson')).toBeInTheDocument()
      expect(buttonIcon).toHaveClass('fa-chevron-down')
    })

    it('Should be displayed', () => {
      const { queryByText, queryByTitle, container } = setup({
        ...props,
        lesson,
      })
      const toggleButton = queryByText('Lesson')
      const buttonIcon = container.querySelector('.button-lesson i')
      fireEvent.click(toggleButton)
      expect(queryByTitle(lesson.title)).not.toHaveClass('hidden')
      expect(buttonIcon).toHaveClass('fa-chevron-up')
      expect(queryByText(lesson.title)).toBeInTheDocument()
      expect(queryByText(lesson.category)).toBeInTheDocument()
      expect(queryByText(/2 min/)).toBeInTheDocument()
      expect(queryByTitle(lesson.title).href).toEqual(lesson.url)
    })
  })

  it('Should have a Tooltip', () => {
    const { getByTitle } = setup({ ...props, tooltip: 'This is a tooltip' })
    expect(getByTitle('Click to view Educational moment')).toBeInTheDocument()
  })
})
