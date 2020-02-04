import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { mount, shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import { UserStateModal } from '../src/UserStateModal'
import LoginModal from '../src/LoginModal'
import SignupModal from '../src/SignupModal'



Enzyme.configure({ adapter: new Adapter() })

jest.mock('../src/Services');

const defaultProps = {
  csrfToken: '123',
  handleClose: function () {},
  loginUrl: 'http://www.example.com/login',
  signupUrl: 'http://www.example.com/signup',
  linkedInUrl: 'http://www.example.com/oauth2/linkedin',
  googleUrl: 'http://www.example.com/oauth2/google',
  termsUrl: 'https://www.great.gov.uk/terms-and-conditions/',
}


const createEvent = () => ({ preventDefault: jest.fn() })


beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})

test('Modal handles model open and close', () => {
  const event = createEvent()
  const props = {...defaultProps, handleClose: jest.fn()}
  const component = shallow(<UserStateModal {...props} />)
  // when the user clicks the close button
  act(() => {
    component.find(".account-link.signin").simulate('click', event)
  })
  // then the handler is closed
  expect(event.preventDefault).toHaveBeenCalled()
  expect(component.find(LoginModal).prop('isOpen')).toEqual(true)
  expect(component.find(SignupModal).prop('isOpen')).toEqual(false)

  // when the user clicks the signup button
  act(() => {
    component.find(LoginModal).prop('handleSignupClick')(createEvent())
  })
  // then the signup modal is open
  expect(component.find(LoginModal).prop('isOpen')).toEqual(false)
  expect(component.find(SignupModal).prop('isOpen')).toEqual(true)

  // when the user cloicks the close button
  act(() => {
    component.find(SignupModal).prop('handleClose')(createEvent())
  })

  // then the signup modal is closed
  expect(component.find(LoginModal).prop('isOpen')).toEqual(false)
  expect(component.find(SignupModal).prop('isOpen')).toEqual(false)

})
