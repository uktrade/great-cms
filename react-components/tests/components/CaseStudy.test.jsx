import React from 'react'
import { render, waitFor, fireEvent } from '@testing-library/react'

import { CaseStudy } from '../../src/components/CaseStudy/CaseStudy'

const openButtonText = 'Open case study'
const closeButtonText = 'Close'
const bodyText = 'example body content'

const props = {
  heading: 'heading example',
  company: 'example company',
  body: `<div>${bodyText}</div>`,
}

const setup = (props) => {
  const utils = render(<CaseStudy content={props} />)

  return {
    ...utils,
  }
}

describe('CaseStudy', () => {
  it('Should have a heading', () => {
    const { getByText } = setup(props)
    expect(getByText(props.heading)).toBeInTheDocument()
  })

  it('Should have an open case study button', () => {
    const { getByText } = setup(props)
    expect(getByText(openButtonText)).toBeInTheDocument()
  })

  it('Should toggle body content when buttons clicked', async () => {
    const { getByText, queryByText } = setup(props)

    await waitFor(() => {
      expect(getByText(props.company)).toBeInTheDocument()
    })

    fireEvent.click(getByText(openButtonText))

    await waitFor(() => {
      expect(getByText(closeButtonText)).toBeInTheDocument()
    })
  })
})
