import React from 'react'

import { shallow } from 'enzyme'
import Enzyme from 'enzyme'
import Adapter from 'enzyme-adapter-react-16'

import ErrorList from '../../src/components/ErrorList'

Enzyme.configure({ adapter: new Adapter() })


beforeEach(() => {
  jest.useFakeTimers()
})

afterEach(() => {
  jest.useRealTimers()
})

test('ErrorList handles no errors', () => {
  const errors = {}
  const component = shallow(<ErrorList errors={errors} />)

  expect(component).toEqual({})
})

test('ErrorList handles one error', () => {
  const errors = {
    'some-field': ['something went wrong'],
  }
  const component = shallow(<ErrorList errors={errors} />)

  expect(component.matchesElement(
    <div className="form-group-error">
      <ul className="errorlist">
        <li key={0}>some-field: something went wrong</li>
      </ul>
    </div>
  )).toEqual(true)
})

test('ErrorList handles multiple errors', () => {
  const errors = {
    'some-field': ['something went wrong', 'something else went wrong'],
    'some-other-field': ['something went wrong', 'something else went wrong'],
  }
  const component = shallow(<ErrorList errors={errors} />)

  expect(component.matchesElement(
    <div className="form-group-error">
      <ul className="errorlist">
        <li key={0}>some-field: something went wrong</li>
        <li key={1}>some-field: something else went wrong</li>
        <li key={2}>some-other-field: something went wrong</li>
        <li key={3}>some-other-field: something else went wrong</li>
      </ul>
    </div>
  )).toEqual(true)
})

test('ErrorList handles multiple errors', () => {
  const errors = {
    '__all__': ['some general error occured'],
  }
  const component = shallow(<ErrorList errors={errors} />)

  expect(component.matchesElement(
    <div className="form-group-error">
      <ul className="errorlist">
        <li key={0}>some general error occured</li>
      </ul>
    </div>
  )).toEqual(true)
})
