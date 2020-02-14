import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { mount, shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import SignupWizard, {STEP_CREDENTIALS, STEP_VERIFICATION_CODE, STEP_COMPLETE} from '../src/SignupWizard'
import SignupWizardStep1 from '../src/SignupWizardStep1'
import SignupWizardStep2 from '../src/SignupWizardStep2'
import SignupWizardStep3 from '../src/SignupWizardStep3'
import Services from '../src/Services'


Enzyme.configure({ adapter: new Adapter() })

jest.mock('../src/Services');

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
  username: 'username',
  password: 'password',
  handleClose: function () {},
  handleLoginOpen: function () {},
  currentStep: STEP_CREDENTIALS
}

describe('SignupWizard', () => {

  const { reload } = window.location

  beforeEach(() => {
    delete window.location
    window.location = { reload: jest.fn() }
  })

  afterEach(() => {
    window.location.reload = reload
  })

  test('bad credentials results in errors passed down', done => {
    // given the credentials are incorrect
    const errors = {'username': ['An error occured']}
    Services.createUser.mockImplementation(() => Promise.reject(errors))

    const component = mount(<SignupWizard {...defaultProps} />)

    act(() => {
      component.find(SignupWizardStep1).prop('handleSubmit')()
    })

    // then an error message is displayed
    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(
        <SignupWizardStep1
          disabled={false}
          username='username'
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
    const component = mount(<SignupWizard {...defaultProps} />)

    act(() => {
      component.find(SignupWizardStep1).prop('handleSubmit')()
    })

    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(
        <SignupWizardStep2
          errors={{}}
          disabled={false}
        />
      )).toEqual(true)
      done()
    })

  })

  test('incorrect verification code results in errors passed down', done => {
    // given the credentials are incorrect
    const errors = {'username': ['An error occured']}
    Services.checkVerificationCode.mockImplementation(() => Promise.reject(errors))
    const props = {...defaultProps, currentStep: STEP_VERIFICATION_CODE}
    const component = mount(<SignupWizard {...props} />)

    expect(component.exists(SignupWizardStep2)).toEqual(true)

    act(() => {
      component.find(SignupWizardStep2).prop('handleCodeChange')('123456')
      component.find(SignupWizardStep2).prop('handleSubmit')()
    })

    // then an error message is displayed
    setImmediate(() => {
      component.update()
      expect(component.find(SignupWizardStep2).prop('errors')).toMatchObject(errors)
      done()
    })
  })

  test('correct verification code results in rendering step 3', done => {
    // given the credentials are correct
    Services.checkVerificationCode.mockImplementation(() => Promise.resolve())
    const props = {...defaultProps, currentStep: STEP_VERIFICATION_CODE}
    const component = mount(<SignupWizard {...props} />)

    expect(component.exists(SignupWizardStep2)).toEqual(true)

    act(() => {
      component.find(SignupWizardStep2).prop('handleCodeChange')('123456')
      component.find(SignupWizardStep2).prop('handleSubmit')()
    })

    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(<SignupWizardStep3 />)).toEqual(true)
      done()
    })

  })

  test('submitting final step results in page reload', () => {
    // given the credentials are correct
    const props = {...defaultProps, currentStep: STEP_COMPLETE}
    const component = mount(<SignupWizard {...props} />)

    act(() => {
      component.find(SignupWizardStep3).prop('handleSubmit')()
    })

    expect(location.reload).toHaveBeenCalled()

  })

})