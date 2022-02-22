import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import Enzyme, { shallow } from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import { CookiesModal } from './CookiesModal'
import CookiesManager from './dit.components.cookie-notice'

jest.mock('./dit.components.cookie-notice');

Enzyme.configure({ adapter: new Adapter() })

const createEvent = () => ({ preventDefault: jest.fn() })

const defaultProps = {
   preferencesUrl: 'http://www.example.com/cookies/',
   privacyCookiesUrl: 'http://www.example.com/privacy/'
}

describe('CookiesModal', () => {

  test('handles not being shown', () => {
    CookiesManager.getPreferencesCookie.mockImplementation(() => true)
    const component = shallow(
      <CookiesModal isOpen={false} {...defaultProps} />
    )

    expect(component.find(Modal).prop('isOpen')).toEqual(false)

  })

  test('handles accept all click', () => {
    // given the credentials are incorrect
    CookiesManager.getPreferencesCookie.mockImplementation(() => null)
    const component = shallow(<CookiesModal isOpen {...defaultProps} />)

    expect(component.find(Modal).prop('isOpen')).toEqual(true)

    act(() => {
      component.find('[href="#"]').simulate('click', createEvent())
    })

    expect(window.dataLayer).toHaveLength(2)
    expect(window.dataLayer[0].event).toEqual('cookies_policy_accept')
    expect(window.dataLayer[1].event).toEqual('gtm.dom')

    expect(CookiesManager.acceptAllCookiesAndShowSuccess).toHaveBeenCalled()
    expect(component.prop('isOpen')).toEqual(false)
  })

  test('uses the cookies policy page link', () => {
    // given the credentials are incorrect
    CookiesManager.getPreferencesCookie.mockImplementation(() => null)
    const component = shallow(<CookiesModal isOpen {...defaultProps}  />)

    expect(component.containsMatchingElement(
      <a href={defaultProps.privacyCookiesUrl}>cookies to collect information</a>
    )).toEqual(true)

    expect(component.containsMatchingElement(
      <a href={defaultProps.preferencesUrl}>Set cookie preferences</a>
    )).toEqual(true)
  })

})
