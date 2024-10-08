import React from 'react'
import { render, fireEvent, waitFor } from '@testing-library/react'
import ReactModal from 'react-modal'

import { ComingSoon } from '.'

export const props = {
  title: 'Example placeholder lesson title',
  backUrl: '/module-landing-page'
}

const setup = ({ ...data }) => {
  const doc = render(<ComingSoon {...data} />)
  ReactModal.setAppElement(doc.baseElement)
  return {
    ...doc
  }
}

describe('ComingSoon', () => {
  it('Modal should be hidden', () => {
    const { getByText, queryByText } = setup(props)
    expect(getByText('Coming soon')).toBeInTheDocument()
    expect(queryByText('Some lessons aren’t available yet')).not.toBeInTheDocument()
  })

  it('Modal should be visible', async () => {
    const { getByText } = setup(props)

    fireEvent.click(getByText('Example placeholder lesson title'))

    await waitFor(() => {
      expect(getByText('Some lessons aren’t available yet')).toBeInTheDocument()
    })
  })
})
