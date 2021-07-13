import React from 'react'
import { render, waitFor, fireEvent } from '@testing-library/react'

import { CaseStudy } from '../../src/components/CaseStudy/CaseStudy'

const openButtonText = 'Expand case study'
const closeButtonText = 'Collapse case study'
const bodyText = 'example body content'
const mediaBlock = { type: 'media', content: `<div>${bodyText}</div>` }
const quoteBlock = { type: 'quote', content: `<div>${bodyText}</div>` }
const textBlock = { type: 'text', content: `<div>${bodyText}</div>` }

const props = {
  heading: 'heading example',
  company: 'example company',
  blocks: [mediaBlock, quoteBlock, textBlock],
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
