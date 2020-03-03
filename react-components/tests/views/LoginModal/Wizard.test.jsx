import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { mount, shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import Wizard from '@src/views/LoginModal/Wizard'
import Step1 from '@src/views/LoginModal/Step1'
import Services from '@src/Services'


Enzyme.configure({ adapter: new Adapter() })

jest.mock('@src/Services');

const createEvent = () => ({ preventDefault: jest.fn() })


beforeEach(() => {
  jest.useFakeTimers()

  Services.setConfig({
    apiLoginUrl: 'http://www.example.com/login/',
    csrfToken: '123',
    linkedInUrl: 'http://www.example.com/oauth2/linkedin',
    googleUrl: 'http://www.example.com/oauth2/google',
    dashboardUrl: '/dashboard/',
  })
})

afterEach(() => {
  jest.useRealTimers()
  Services.setConfig({})
})

const defaultProps = {
  email: 'email',
  password: 'password',
  nextUrl: '/thing/',
}

describe('LoginModal', () => {

  const { assign } = window.location

  beforeEach(() => {
    delete window.location
    window.location = { assign: jest.fn() }
  })

  afterEach(() => {
    window.location.assign = assign
  })

  test('bad credentials results in errors passed down', done => {
    // given the credentials are incorrect
    const errors = {'email': ['This field is required']}
    Services.checkCredentials.mockImplementation(() => Promise.reject(errors))

    const component = mount(<Wizard {...defaultProps} />)

    // when the form is submitted
    act(() => {
      component.find(Step1).prop('handleSubmit')()
    })

    // then an error message is displayed
    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(
        <Step1
          disabled={false}
          email='email'
          password='password'
          errors={errors}
        />
      )).toEqual(true)

      done()
    })
  })

  test('good credentials results in next url', done => {
    // given the credentials are correct
    Services.checkCredentials.mockImplementation(() => Promise.resolve())
    const component = mount(<Wizard {...defaultProps} />)

    act(() => {
      component.find(Step1).prop('handleSubmit')()
    })

    setImmediate(() => {
      expect(location.assign).toHaveBeenCalled()
      done()
    })
  })

})
