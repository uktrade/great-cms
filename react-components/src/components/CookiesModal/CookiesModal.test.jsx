import React from 'react'
import ReactModal from 'react-modal'
import { render, waitFor } from '@testing-library/react'

import { CookiesModal } from './CookiesModal'
import CookiesManager from './dit.components.cookie-notice'

jest.mock('./dit.components.cookie-notice')

ReactModal.setAppElement('body')

const defaultProps = {
  preferencesUrl: 'http://www.example.com/cookies/',
  privacyCookiesUrl: 'http://www.example.com/privacy/',
}

describe('CookiesModal', () => {
  it('does not show if cookie preferences have been set', () => {
    CookiesManager.getPreferencesCookie.mockImplementation(() => true)
    const { queryByText } = render(<CookiesModal {...defaultProps} />)

    expect(queryByText('Tell us whether you accept cookies')).toBeNull()
  })

  it('handles accept all click', async () => {
    CookiesManager.getPreferencesCookie.mockImplementation(() => null)
    const { getByText, queryByText } = render(
      <CookiesModal {...defaultProps} />
    )

    expect(getByText('Tell us whether you accept cookies')).toBeTruthy()

    getByText('Accept all cookies').click()

    await waitFor(() => {
      expect(window.dataLayer).toHaveLength(2)
      expect(window.dataLayer[0].event).toEqual('cookies_policy_accept')
      expect(window.dataLayer[1].event).toEqual('gtm.dom')

      expect(CookiesManager.acceptAllCookiesAndShowSuccess).toHaveBeenCalled()
      expect(queryByText('Tell us whether you accept cookies')).toBeNull()
    })
  })

  it('shows the cookies policy page link', () => {
    CookiesManager.getPreferencesCookie.mockImplementation(() => null)
    const { getByText } = render(<CookiesModal {...defaultProps} />)

    expect(
      getByText('cookies to collect information').getAttribute('href')
    ).toEqual(defaultProps.privacyCookiesUrl)
    expect(getByText('Set cookie preferences').getAttribute('href')).toEqual(
      defaultProps.preferencesUrl
    )
  })
})
