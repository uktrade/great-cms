import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import { CookiesModal } from '../src/CookiesModal'

jest.mock('../../static/js/dit.components.cookie-notice');
import CookiesManager from '../../static/js/dit.components.cookie-notice'

Enzyme.configure({ adapter: new Adapter() })

CookiesManager.getPreferencesCookie.mockImplementation(() => null)

const createEvent = () => ({ preventDefault: jest.fn() })

const defaultProps = {
   preferencesUrl: 'http://www.example.com/cookies/',
   privacyCookiesUrl: 'http://www.example.com/privacy/'
}

describe('CookiesModal', () => {

  test('handles not being shown', () => {
    const component = shallow(
      <CookiesModal isOpen={false} {...defaultProps} />
    )

    expect(component.find(Modal).prop('isOpen')).toEqual(false)

  })

  test('handles accept all click', () => {
    // given the credentials are incorrect

    const component = shallow(<CookiesModal isOpen={true} {...defaultProps}  />)

    expect(component.find(Modal).prop('isOpen')).toEqual(true)

    act(() => {
      component.find('[href="#"]').simulate('click', createEvent())
    })

    expect(CookiesManager.acceptAllCookiesAndShowSuccess).toHaveBeenCalled()
    expect(component.prop('isOpen')).toEqual(false)
  })

  test('uses the cookies policy page link', () => {
    // given the credentials are incorrect
    const component = shallow(<CookiesModal isOpen={true} {...defaultProps}  />)

    expect(component.containsMatchingElement(
      <a href={defaultProps.privacyCookiesUrl}>cookies to collect information</a>
    )).toEqual(true)

    expect(component.containsMatchingElement(
      <a href={defaultProps.preferencesUrl}>Set cookie preferences</a>
    )).toEqual(true)
  })

})