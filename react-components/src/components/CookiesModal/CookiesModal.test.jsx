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

  describe.each([
    ['en', 'Tell us whether you accept cookies'],
    ['es', 'Dinos si aceptas cookies'],
    ['ar', "أخبرنا ما إذا كنت توافق على ملفات تعريف الارتباط"],
    ['fr', 'Dites-nous si vous acceptez les cookies'],
    ['pt', 'Diga-nos se você aceita cookies'],
    ['ko', '쿠키 사용 여부 알려주세요'],
    ['zh', '告诉我们您是否接受 cookie'],
    ['ms', 'Beritahu kami sama ada anda menerima kuki']
  ])('displays translated header on cookie modal', (lang, expectedString)=>{
    test(`lang ${lang} displays ${expectedString}`, ()=>{
      CookiesManager.getPreferencesCookie.mockImplementation(() => null)
      const { getByText } = render(<CookiesModal {...defaultProps} lang={lang} />)
      expect(document.body.textContent).toContain(expectedString);
    })
  })

  it('reverts to en for invalid language code', () => {
    CookiesManager.getPreferencesCookie.mockImplementation(() => null)
    const { getByText } = render(<CookiesModal {...defaultProps} lang = {'!!'}/>)
    expect(document.body.textContent).toContain('Tell us whether you accept cookies');
  })

  it('ignores locale', () => {
    CookiesManager.getPreferencesCookie.mockImplementation(() => null)
    const { getByText } = render(<CookiesModal {...defaultProps} lang = {'es-US'}/>)
    expect(document.body.textContent).toContain('Dinos si aceptas cookies');
  })

  it('reverts to en for unimplemented language code', () => {
    CookiesManager.getPreferencesCookie.mockImplementation(() => null)
    const { getByText } = render(<CookiesModal {...defaultProps} lang = {'bi'}/>)
    expect(document.body.textContent).toContain('Tell us whether you accept cookies');
  })

})
