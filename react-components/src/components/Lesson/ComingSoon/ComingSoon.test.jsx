import React from 'react'
import { render, fireEvent, waitFor } from '@testing-library/react'

import { ComingSoon } from '.'

export const props = {
  title: 'Example placeholder lesson title',
  backUrl: '/module-landing-page'
}

const setup = ({ ...data }) => {
  const utils = render(<ComingSoon {...data} />)

  return {
    ...utils
  }
}

describe('ComingSoon', () => {
  it('Modal should be hidden', () => {
    const { getByText, queryByText } = setup(props)
    expect(getByText('Coming soon')).toBeInTheDocument()
    expect(queryByText('This Lesson is coming soon')).not.toBeInTheDocument()
  })

  it('Modal should be visible', async () => {
    const { getByText } = setup(props)

    fireEvent.click(getByText('Example placeholder lesson title'))

    await waitFor(() => {
      expect(getByText('This Lesson is coming soon')).toBeInTheDocument()
    })
  })
})
