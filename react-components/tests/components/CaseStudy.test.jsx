import React from 'react'
import { render, waitFor, fireEvent } from '@testing-library/react'

import { CaseStudy } from '../../src/components/CaseStudy/CaseStudy'

const props = {
  content: {
    heading: 'heading example',
    company: 'example company',
    body: '<div></div>'
  }
}

const setup = ({ content }) => {
  const utils = render(<CaseStudy content={content} />)

  return {
    ...utils
  }
}

describe('CaseStudy', () => {
  it('Should have a heading', () => {
    const { getByText } = setup(props)
    expect(getByText(props.content.heading)).toBeInTheDocument()
  })

  it('Should have an open case study button', () => {
    const { getByText } = setup(props)
    expect(getByText('Open case study')).toBeInTheDocument()
  })
})
