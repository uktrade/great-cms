import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { mount, shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import Wizard, {STEP_CREDENTIALS, STEP_VERIFICATION_CODE, STEP_COMPLETE} from '@src/views/SignupModal/Wizard'
import Step1 from '@src/views/SignupModal/Step1'
import Step2 from '@src/views/SignupModal/Step2'
import Success from '@src/views/SignupModal/Success'
import Services from '@src/Services'


Enzyme.configure({ adapter: new Adapter() })

jest.mock('@src/Services');

const createEvent = () => ({ preventDefault: jest.fn() })


beforeEach(() => {
  jest.useFakeTimers()
  Services.setConfig({
    signupUrl: 'http://www.example.com',
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

  test('good credentials results in rendering step 2', done => {
    // given the credentials are correct
    Services.createUser.mockImplementation(() => Promise.resolve())
    const component = mount(<Wizard {...defaultProps} />)

    act(() => {
      component.find(Step1).prop('handleSubmit')()
    })

    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(
        <Step2
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

    expect(component.exists(Step2)).toEqual(true)

    act(() => {
      component.find(Step2).prop('handleCodeChange')('123456')
      component.find(Step2).prop('handleSubmit')()
    })

    // then an error message is displayed
    setImmediate(() => {
      component.update()
      expect(component.find(Step2).prop('errors')).toMatchObject(errors)
      done()
    })
  })

  test('correct verification code results in rendering step 3', done => {
    // given the credentials are correct
    Services.checkVerificationCode.mockImplementation(() => Promise.resolve())
    const props = {...defaultProps, currentStep: STEP_VERIFICATION_CODE}
    const component = mount(<Wizard {...props} />)

    expect(component.exists(Step2)).toEqual(true)

    act(() => {
      component.find(Step2).prop('handleCodeChange')('123456')
      component.find(Step2).prop('handleSubmit')()
    })

    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(<Success />)).toEqual(true)
      done()
    })

  })

  test('submitting final step results in page assign', () => {
    // given the credentials are correct
    const props = {...defaultProps, currentStep: STEP_COMPLETE}
    const component = mount(<Wizard {...props} />)

    act(() => {
      component.find(Success).prop('handleSubmit')()
    })

    expect(location.assign).toHaveBeenCalled()

  })

})