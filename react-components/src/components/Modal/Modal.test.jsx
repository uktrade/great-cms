import React from  'react'
import { render, fireEvent } from '@testing-library/react'

import { Modal } from '.'

const props = {
  backUrl: 'https://www.yahoo.com',
  header: 'This is a header',
  content: 'This is a content',
  buttonText: 'I am a button'
}

const setup = ({...data}) => {
  const actions = {
    onClick: jest.fn()
  }

  const component = render(<Modal
    {...data}
    {...actions}
  />)

  return {
    ...component,
    actions
  }
}

describe('Modal', () => {
  describe('Footer', () => {
    it('Should have no footer', () => {
      const { getByTitle, getByText, queryByText  } = setup(props)
      expect(getByTitle('navigate back')).toBeInTheDocument()
      expect(getByText(props.header)).toBeInTheDocument()
      expect(getByText(props.content)).toBeInTheDocument()
      expect(getByText(props.buttonText)).toBeInTheDocument()
      expect(queryByText('Select a market you’ve already researched')).not.toBeInTheDocument()
    })

    it('Should have a footer', () => {
      const { getByText } = setup({...props, footer: true } )
      expect(getByText('Select a market you’ve already researched')).toBeInTheDocument()
    })
  })

  it('Should fire onClick', () => {
    const { getByText, actions } = setup(props)
    fireEvent.click(getByText(props.buttonText))
    expect(actions.onClick).toHaveBeenCalled()
  })
})
