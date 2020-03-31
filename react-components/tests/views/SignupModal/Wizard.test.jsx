import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { mount, shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import Wizard, {STEP_CREDENTIALS, STEP_VERIFICATION_CODE, STEP_COMPLETE} from '@src/views/SignupModal/Wizard'
import StepCredentials from '@src/views/SignupModal/StepCredentials'
import StepCode from '@src/views/SignupModal/StepCode'
import StepSuccess from '@src/views/SignupModal/StepSuccess'
import Services from '@src/Services'


Enzyme.configure({ adapter: new Adapter() })

jest.mock('@src/Services');

const createEvent = () => ({ preventDefault: jest.fn() })


beforeEach(() => {
  jest.useFakeTimers()
  Services.setConfig({
    apiSignupUrl: 'http://www.example.com',
    csrfToken: '123',
    linkedInUrl: 'http://www.example.com/oauth2/linkedin',
    googleUrl: 'http://www.example.com/oauth2/google',
    termsUrl: 'https://www.great.gov.uk/terms-and-conditions/',
  })
})

afterEach(() => {
  jest.useRealTimers()
  Services.setConfig({})
})

const defaultProps = {
  email: 'email',
  password: 'password',
  handleClose: function () {},
  handleLoginOpen: function () {},
  currentStep: STEP_CREDENTIALS
}

describe('SignupWizard', () => {

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
    const errors = {'email': ['An error occured']}
    Services.createUser.mockImplementation(() => Promise.reject(errors))

    const component = mount(<Wizard {...defaultProps} />)

    act(() => {
      component.find(StepCredentials).prop('handleSubmit')()
    })

    // then an error message is displayed
    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(
        <StepCredentials
          disabled={false}
          email='email'
          password='password'
          errors={errors}
        />
      )).toEqual(true)

      done()
    })
  })

  test('good credentials results in rendering step 2', done => {
    // given the credentials are correct
    Services.createUser.mockImplementation(() => Promise.resolve())
    const component = mount(<Wizard {...defaultProps} />)

    act(() => {
      component.find(StepCredentials).prop('handleSubmit')()
    })

    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(
        <StepCode
          errors={{}}
          disabled={false}
        />
      )).toEqual(true)
      done()
    })

  })

  test('incorrect verification code results in errors passed down', done => {
    // given the credentials are incorrect
    const errors = {'email': ['An error occured']}
    Services.checkVerificationCode.mockImplementation(() => Promise.reject(errors))
    const props = {...defaultProps, currentStep: STEP_VERIFICATION_CODE}
    const component = mount(<Wizard {...props} />)

    expect(component.exists(StepCode)).toEqual(true)

    act(() => {
      component.find(StepCode).prop('handleCodeChange')('123456')
      component.find(StepCode).prop('handleSubmit')()
    })

    // then an error message is displayed
    setImmediate(() => {
      component.update()
      expect(component.find(StepCode).prop('errors')).toMatchObject(errors)
      done()
    })
  })

  test('correct verification code results in rendering step 3', done => {
    // given the credentials are correct
    Services.checkVerificationCode.mockImplementation(() => Promise.resolve())
    const props = {...defaultProps, currentStep: STEP_VERIFICATION_CODE}
    const component = mount(<Wizard {...props} />)

    expect(component.exists(StepCode)).toEqual(true)

    act(() => {
      component.find(StepCode).prop('handleCodeChange')('123456')
      component.find(StepCode).prop('handleSubmit')()
    })

    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(<StepSuccess />)).toEqual(true)
      done()
    })

  })

  test('submitting final step results in page assign', () => {
    // given the credentials are correct
    const props = {...defaultProps, currentStep: STEP_COMPLETE}
    const component = mount(<Wizard {...props} />)

    act(() => {
      component.find(StepSuccess).prop('handleSubmit')()
    })

    expect(location.assign).toHaveBeenCalled()

  })

})