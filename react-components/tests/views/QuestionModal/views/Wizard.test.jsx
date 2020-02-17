import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { mount, shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import Wizard, {STEP_PERSONAL_DETAILS} from '@src/views/QuestionModal/Wizard'
import Step1 from '@src/views/QuestionModal/Step1'
import Step2 from '@src/views/QuestionModal/Step2'
import Step3 from '@src/views/QuestionModal/Step3'
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
      component.find(Step2).prop('handleSubmit')()
    })

    // then an error message is displayed
    setImmediate(() => {
      component.update()
      expect(component.containsMatchingElement(
        <Step2
          disabled={false}
          value={['some industry']}
          errors={errors}
        />
      )).toEqual(true)

      done()
    })
  })

  test('end to end wizard render', done => {
    // given the credentials are correct
    Services.enrolCompany.mockImplementation(() => Promise.resolve())
    const component = mount(<Wizard {...defaultProps} />)

    expect(component.exists(Step2)).toEqual(true)

    act(() => {
      component.find(Step2).prop('handleChange')(['some industry'])
      component.find(Step2).prop('handleSubmit')()
    })

    setImmediate(() => {
      expect(Services.enrolCompany).toHaveBeenCalled()
      expect(location.assign).toHaveBeenCalled()
      done()
    })

  })

})