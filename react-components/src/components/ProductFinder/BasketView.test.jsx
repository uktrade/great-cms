import React from 'react'
import { render, fireEvent } from '@testing-library/react'
import ReactModal from 'react-modal'

import BasketViewer from './BasketView'

const onOpen = jest.fn()

const setup = () => {
  const component = render(
    <BasketViewer
      label="button label"
      onOpen={onOpen}
    >
    <span>Expanded content</span>
    </BasketViewer>
  )
  ReactModal.setAppElement(component.baseElement)
  return {
    ...component,
  }
}

describe('Basket viewer', () => {
  it('Renders basket viewer', () => {
    const { getByText, queryByText } = setup()
    const button = getByText('button label')
    expect(button).toBeTruthy()
    expect(onOpen).not.toHaveBeenCalled()
    expect(queryByText('Expanded content')).toBeNull()
    fireEvent.click(button)
    expect(queryByText('Expanded content')).toBeTruthy()
    expect(onOpen).toHaveBeenCalled()
  })
})
