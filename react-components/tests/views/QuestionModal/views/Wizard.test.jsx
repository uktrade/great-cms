import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { mount, shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import Wizard, {STEP_SECTORS, STEP_COUNTRIES} from '@src/views/QuestionModal/Wizard'
import Step1 from '@src/views/QuestionModal/Step1'
import StepSectors from '@src/views/QuestionModal/StepSectors'
import StepCountry from '@src/views/QuestionModal/StepCountry'
import Step4 from '@src/views/QuestionModal/Step4'
import Services from '@src/Services'


Enzyme.configure({ adapter: new Adapter() })

jest.mock('@src/Services');

const createEvent = () => ({ preventDefault: jest.fn() })


beforeEach(() => {
  jest.useFakeTimers()
  Services.setConfig({
    enrolCompanyUrl: 'http://www.example.com/enrol/',
    csrfToken: '123',
  })
})

afterEach(() => {
  jest.useRealTimers()
  Services.setConfig({})
})

const defaultProps = {
  isOpen: true,
}

describe('QuestionWizard', () => {

  const { assign } = window.location

  beforeEach(() => {
    delete window.location
    window.location = { assign: jest.fn() }
  })

  afterEach(() => {
    window.location.assign = assign
  })

  test('bad data results in errors passed down', done => {
    // given the credentials are incorrect
    const errors = {'expertise_sectors': ['You are denied']}
    Services.enrolCompany.mockImplementation(() => Promise.reject(errors))

    const component = mount(<Wizard 
      companyName='some company'
      industries={['some industry']}
      countries={['some country']}
      firstName='jim'
      lastName='example'
      isOpen={true}
    />)

    act(() => {
      component.find(StepSectors).prop('handleSubmit')()
    })

    // then an error message is displayed
    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(
        <StepSectors
          disabled={false}
          value={['some industry']}
          errors={errors}
        />
      )).toEqual(true)

      done()
    })
  })

  test('end to end sector select', done => {
    // given the credentials are correct
    Services.enrolCompany.mockImplementation(() => Promise.resolve())
    // and the user is on the sectors step
    const props = {...defaultProps, currentStep: STEP_SECTORS}
    const component = mount(<Wizard {...props} />)

    // when the user chooses "some industry"
    act(() => {
      component.find(StepSectors).prop('handleChange')(['some industry'])
      component.find(StepSectors).prop('handleSubmit')()
    })

    setImmediate(() => {
      // then the company is enrolled
      expect(Services.enrolCompany).toHaveBeenCalled()
      // and the page is refreshed
      expect(location.assign).toHaveBeenCalled()
      done()
    })
  })

  test('end to end country select', done => {
    // given the credentials are correct
    Services.updateCompany.mockImplementation(() => Promise.resolve())
    // and the user is on the country step
    const props = {...defaultProps, currentStep: STEP_COUNTRIES}
    const component = mount(<Wizard {...props} />)

    // when the user chooses "some country"
    act(() => {
      component.find(StepCountry).prop('handleChange')(['some country'])
      component.find(StepCountry).prop('handleSubmit')()
    })

    setImmediate(() => {
      // then the company is updated
      expect(Services.updateCompany).toHaveBeenCalled()
      // and the page is refreshed
      expect(location.assign).toHaveBeenCalled()
      done()
    })
  })

})