import React from 'react'
import Modal from 'react-modal'

import { act } from 'react-dom/test-utils'
import { mount, shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import {Base, STEP_SUCCESS, STEP_COUNTRIES} from '@src/views/CountriesModal/Base'
import StepSuccess from '@src/views/CountriesModal/StepSuccess'
import StepCountries from '@src/views/CountriesModal/StepCountries'
import Services from '@src/Services'


Enzyme.configure({ adapter: new Adapter() })

jest.mock('@src/Services');

const createEvent = () => ({ preventDefault: jest.fn() })


beforeEach(() => {
  jest.useFakeTimers()
  Services.setConfig({
    apiUpdateCompanyUrl: 'http://www.example.com/enrol/',
    csrfToken: '123',
    userCountries: [],
  })
})

afterEach(() => {
  jest.useRealTimers()
  Services.setConfig({})
})

const defaultProps = {
  isOpen: true,
}

describe('Countries Base', () => {

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
    const errors = {'expertise_countries': ['You are denied']}
    const countries = ['some country']

    Services.updateCompany.mockImplementation(() => Promise.reject(errors))
    const component = mount(<Base countries={countries} isOpen={true} />)

    act(() => {
      component.find(StepCountries).prop('handleSubmit')()
    })

    // then an error message is displayed
    setImmediate(() => {
      component.update()
      expect(component.find(StepCountries).prop('errors')).toBe(errors)
      done()
    })
  })

  test('end to end country select', done => {
    // given the credentials are correct
    Services.updateCompany.mockImplementation(() => Promise.resolve())
    // and the user is on the sectors step
    const props = {...defaultProps, currentStep: STEP_COUNTRIES}
    const component = mount(<Base {...props} />)

    // when the user chooses "some industry"
    act(() => {
      component.find(StepCountries).prop('handleChange')(['some country'])
      component.find(StepCountries).prop('handleSubmit')()
    })

    setImmediate(() => {
      // then the company is enrolled
      expect(Services.updateCompany).toHaveBeenCalled()
      component.update()
      // and the user is sent to the success page
      expect(component.containsMatchingElement(<StepSuccess />)).toEqual(true)
      done()
    })
  })
})